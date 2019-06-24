import functools
from collections.abc import MutableSequence, Iterable

import teek
from teek._widgets.base import Widget, ChildMixin
from teek._structures import ConfigDict
from teek._tcl_calls import make_thread_safe


class MultiHandlerConfigDict(ConfigDict):
    """
    Config dictionary which allows multiple handler functions for getting and
    setting options
    """

    def __init__(self):
        super().__init__()

        # Handler functions
        self._handlers = {}

    def _set(self, option, value):
        handlers = (self._handlers[option] if option in self._handlers
                    else self._handlers['*'])

        if not isinstance(handlers, Iterable):
            handlers = [handlers]

        for handler in handlers:
            handler(None, option, value)

    def _get(self, option):
        handler = (self._handlers[option]
                   if option in self._handlers else self._handlers['*'])

        if isinstance(handler, Iterable):
            handler = handler[0]

        return handler(self._types.get(option, str), option)

    def _list_options(self):
        return set(list(self._types.keys()) + list(
            self._special.keys()) + list(self._special_values.keys()))


class TreeviewColumn:
    """
    Represents a column of a treeview widget or one which is ready to be added
    to a treeview widget. A column specifies the title, content anchor and size
    options. Please note that options can only be set or retrieved if the
    column is connected to a :class:`Treeview`.

    If you create a :class:`TreeviewColumn` instance, it is not initially
    connected to a :class:`Treeview`. This is automatically done when it is
    appended to the *columns* list of the :class:`Treeview` instance like this:
    ::

        treeview.columns.append(teek.TreeviewColumn())

    A column can be created without any arguments. Then the name of the column
    is automatically generated. If the first argument is given, then this name
    is taken.

    For convenience, a column can also be created using...
    ::

        treeview.columns.append('title')

    ...which is exactly the same as this:
    ::

        treeview.columns.append(teek.TreeviewColumn(title='title'))

    There are never multiple :class:`TreeviewColumn` objects that represent the
    same column.

    .. attribute:: config

        Similar to the ``config`` attribute that widgets have. The available
        options can be seen at the ``column`` and ``heading`` command section
        in :man:`ttk_treeview(3tk)`.
    """

    next_col_num = 0

    @make_thread_safe
    def __init__(self, name=None, **kwargs):
        self._name = name or 'C%d' % TreeviewColumn.next_col_num
        self._creation_opts = kwargs
        self._treeview = None

        TreeviewColumn.next_col_num += 1

        self.config = MultiHandlerConfigDict()
        self.config._types.update({
            'text': str,
            'anchor': str,
            'minwidth': int,
            'width': int,
            'stretch': bool,
            'image': teek.Image
        })
        self.config._special.update({
            'command': self._create_click_command
        })
        self.config._handlers.update({
            'text': self._heading_handler,
            'image': self._heading_handler,
            'anchor': [self._column_handler, self._heading_handler],
            '*': self._column_handler
        })

    def __repr__(self):
        if self._treeview:
            parts = "text='%s'" % self.config['text']
        else:
            parts = 'not added to treeview'

        return "%s('%s', %s)" % (self.__class__.__name__, self._name, parts)

    def _check_added(self):
        if self._treeview is None:
            raise RuntimeError(
                "this column hasn't been added to a treeview yet")

    def _heading_handler(self, rettype, option, *args):
        self._check_added()

        if args:
            self._creation_opts[option] = args[0]

        return self._treeview._call(rettype, self._treeview, 'heading', self,
                                    '-' + option, *args)

    def _column_handler(self, rettype, option, *args):
        self._check_added()

        if args:
            self._creation_opts[option] = args[0]

        return self._treeview._call(rettype, self._treeview, 'column', self,
                                    '-' + option, *args)

    def _create_click_command(self):
        result = teek.Callback()
        command_string = teek.create_command(result.run)
        self._heading_handler(None, 'command', command_string)
        return result

    @make_thread_safe
    def _assign(self, treeview):
        # Assign column to given treeview
        self._treeview = treeview
        command_handler = self._creation_opts.pop('command', None)

        if command_handler:
            self.config['command'].connect(command_handler)

        for name, value in self._creation_opts.items():
            self.config[name] = value

    @make_thread_safe
    def to_tcl(self):
        # Only name in column list
        return self._name


class TreeviewRow:
    """
    Represents a row of a treeview widget or one which is ready to be added
    to a treeview widget. The row holds all the column values and additional
    options like title text or icon. Like a :class:`TreeviewColumn`, options
    can only be get/set or methods can be executed if the :class:`TreeviewRow`
    is connected to a :class:`Treeview`.

    If you create a :class:`TreeviewRow` instance, it is not initially
    connected to a :class:`Treeview`. This is automatically done when it is
    appended to the *row* list of the :class:`Treeview` instance like this:
    ::

        treeview.rows.append(teek.TreeviewRow())

    A row can be created without any arguments. Then the name of the row
    is automatically generated. If the first argument is given, then this name
    is taken.

    For convenience, a column can also be created using...
    ::

        treeview.rows.append(['a', 'b', 'c'])

    ...which is exactly the same as this:
    ::

        treeview.rows.append(teek.TreeviewRow(values=['a', 'b', 'c']))

    There are never multiple :class:`TreeviewRow` objects that represent the
    same row.

    .. attribute:: config

        Similar to the ``config`` attribute that widgets have. The available
        options are documented as ``ITEM OPTIONS`` in :man:`ttk_treeview(3tk)`.
    """

    next_row_num = 0

    @make_thread_safe
    def __init__(self, name=None, **kwargs):
        self._name = name or 'R%d' % TreeviewRow.next_row_num
        self._creation_opts = kwargs
        self._treeview = None

        TreeviewRow.next_row_num += 1

        self.config = MultiHandlerConfigDict()
        self.config._types.update({
            'values': [str],
            'text': str,
            'open': bool,
            'tags': [str],
            'image': teek.Image
        })
        self.config._handlers.update({
            '*': self._item_handler
        })

    def __repr__(self):
        if self._treeview:
            parts = "text='%s', values=%s" % (
                self.config['text'],
                repr(self.config['values'])
            )
        else:
            parts = 'not added to treeview'

        return "%s('%s', %s)" % (self.__class__.__name__, self._name, parts)

    def _check_added(self):
        if self._treeview is None:
            raise RuntimeError(
                "this column hasn't been added to a treeview yet")

    def _item_handler(self, rettype, option, *args):
        self._check_added()
        return self._treeview._call(rettype, self._treeview, 'item', self,
                                    '-' + option, *args)

    @make_thread_safe
    def _assign(self, treeview):
        # Assign row to given treeview
        self._treeview = treeview

        for name, value in self._creation_opts.items():
            self.config[name] = value

    @make_thread_safe
    def to_tcl(self):
        # Represented by name
        return self._name

    @property
    def selected(self):
        """
        Get current selection state
        """
        self._check_added()
        return self._name in self._treeview._call([str], self._treeview,
                                                  'selection')

    @make_thread_safe
    def select(self):
        """
        Add row to current selection
        """
        self._check_added()
        self._treeview._call(None, self._treeview, 'selection', 'add', self)

    @make_thread_safe
    def deselect(self):
        """
        Remove row from current selection
        """
        self._check_added()
        self._treeview._call(None, self._treeview, 'selection', 'remove', self)


class TreeviewColumnList(MutableSequence):
    """
    List containing all columns of a treeview
    """

    def __init__(self, treeview, init_columns=[]):
        super().__init__()

        # Default column 0
        first_column = TreeviewColumn('#0')
        first_column._assign(treeview)

        self._data = [first_column]
        self._treeview = treeview

        for column in init_columns:
            self.append(column)

    def __setitem__(self, index, column):
        if index == 0:
            raise KeyError('cannot set column #0')

        if not isinstance(column, TreeviewColumn):
            column = TreeviewColumn(text=column)

        self._data[index] = column
        self._update()

    def __delitem__(self, index):
        if index == 0:
            raise KeyError('cannot delete column #0')

        del self._data[index]
        self._update()

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        # Length includes column 0
        return len(self._data)

    def _update(self):
        """
        Update columns of widget and rebuild column objects
        """
        self._treeview._call(None, self._treeview, 'configure', '-columns',
                             self._data[1:])

        for column in self._data:
            column._assign(self._treeview)

    def insert(self, index, column):
        """
        Insert column or column text converted to a column at given index.
        Note that the column at index 0 cannot be replaced!
        """
        if index == 0:
            raise KeyError('cannot insert column at index 0')

        # Convert to column
        if not isinstance(column, TreeviewColumn):
            column = TreeviewColumn(text=column)

        self._data.insert(index, column)
        self._update()


class TreeviewRowList(MutableSequence):
    """
    List containing all rows of a treeview
    """

    def __init__(self, treeview, init_rows=[]):
        super().__init__()

        self._data = []
        self._treeview = treeview

        for row in init_rows:
            self.append(row)

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, row):
        del self[index]
        self.insert(index, row)

    def __delitem__(self, index):
        self._treeview._call(None, self._treeview, 'delete', self._data[index])
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def insert(self, index, row):
        """
        Insert a row or values converted to a row at the given index.
        """
        # Convert to row
        if not isinstance(row, TreeviewRow):
            row = TreeviewRow(values=row)

        self._treeview._call(None, self._treeview, 'insert', '', index, '-id',
                             row)
        row._assign(self._treeview)
        self._data.insert(index, row)

    def move(self, from_pos, to_pos):
        """
        Move row at index to other position
        """
        row = self._data[from_pos]
        del self[from_pos]
        self.insert(to_pos, row)


class Treeview(ChildMixin, Widget):
    """
    This is the treeview widget.

    :class:`TreeviewRow` and :class:`TreeviewColumn` objects can be added to
    this widget by calling ``insert`` or ``append`` of the ``rows`` or
    ``column`` property. In general, these properties behave like a
    :class:`list` of :class:`TreeviewRow` or :class:`TreeviewColumn` objects.

    If you want to move a row, use the ``move`` method of the ``rows`` property
    like this:
    ::

        treeview.rows.move(2, 0) # move row at index 2 to index 0

    Manual page: :man:`ttk_treeview(3tk)`
    """

    _widget_name = 'ttk::treeview'
    tk_class_name = 'Treeview'

    def __init__(self, parent, *, rows=[], columns=[], **kwargs):
        super().__init__(parent, **kwargs)

        self.rows = TreeviewRowList(self, rows)
        self.columns = TreeviewColumnList(self, columns)

    def _init_config(self):
        super()._init_config()

        self.config._types.update({
            'selectmode': str,
            'height': int,
            'show': [str]
        })

    def _repr_parts(self):
        return ["contains %d columns & %d rows" % (len(self.columns),
                                                   len(self.rows))]

    def _xview_or_yview(self, xview_or_yview, *args):
        if not args:
            return self._call((float, float), self, xview_or_yview)

        self._call(None, self, xview_or_yview, *args)
        return None

    xview = functools.partialmethod(_xview_or_yview, 'xview')
    yview = functools.partialmethod(_xview_or_yview, 'yview')

    def sort(self, column_pos, reverse=False):
        """
        Sort all rows according to value of column with given ``column_pos``.
        The direction of the sorting can be set with ``reverse``. If this value
        is true, the rows are sorted in ascending order.
        """
        if column_pos < 1:
            raise KeyError('column position must be greater or equal 1')

        sorted_rows = self.rows._data.copy()
        sorted_rows.sort(key=lambda r: r.config['values'][column_pos - 1],
                         reverse=reverse)

        for old, row in enumerate(self.rows):
            self.rows.move(old, sorted_rows.index(row))
