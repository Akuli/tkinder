import functools
from collections.abc import MutableSequence

import teek
from teek._widgets.base import Widget, ChildMixin
from teek._structures import ConfigDict
from teek._tcl_calls import make_thread_safe


class OptionConfigDict(ConfigDict):
    """
    Configuration dictionary like :class:`CgetConfigureConfigDict` but
    usable for command options.
    """
    def __init__(self, caller_func):
        super().__init__()
        self._caller_func = caller_func

    def _set(self, option, value):
        self._caller_func(None, '-' + option, value)

    def _get(self, option):
        return self._caller_func(self._types.get(option, str), '-' + option)

    def _list_options(self):
        infos = self._caller_func([str])
        return (infos[i].lstrip('-') for i in range(0, len(infos), 2))


class TreeviewColumnHeading:
    """
    Heading for :class:`TreeviewColumn`. Please note that config options can
    only be retrieved or set if the associated column is connected to a
    :class:`Treeview`.
    """
    def __init__(self, column):
        self._column = column

        self.config = OptionConfigDict(self._config_handler)
        self.config._types.update({
            'text': str,
            'image': teek.Image,
            'anchor': str
        })
        self.config._special.update({
            'command': self._create_click_command
        })

    def __repr__(self):
        if self._column._treeview:
            info = 'text=%r' % self.config['text']
        else:
            info = 'not added to treeview'

        return '%s(%s)' % (self.__class__.__name__, info)

    def _config_handler(self, rettype, *args):
        self._column._check_added()
        return self._column._treeview._call(
            rettype, self._column._treeview, 'heading', self._column, *args
        )

    def _create_click_command(self):
        result = teek.Callback()
        command_string = teek.create_command(result.run)
        self._config_handler(None, '-command', command_string)
        return result


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

    _next_col_num = 0

    def __init__(self, name=None, *, text=None, **kwargs):
        self._name = name or 'C%d' % TreeviewColumn._next_col_num
        self._text = text
        self._creation_opts = kwargs
        self._treeview = None

        TreeviewColumn._next_col_num += 1

        self.heading = TreeviewColumnHeading(self)

        self.config = OptionConfigDict(self._config_handler)
        self.config._types.update({
            'anchor': str,
            'minwidth': int,
            'width': int,
            'stretch': bool
        })

    def __repr__(self):
        repr_str = '%s(%s' % (
            self.__class__.__name__,
            self._name
        )

        if self._treeview is None:
            repr_str += ', not added to treeview'
        else:
            repr_str += ', text=%r' % self.heading.config['text']

        return repr_str + ')'

    def __eq__(self, other):
        return isinstance(other, TreeviewColumn) and self._name == other._name

    def _check_added(self):
        """
        Check if column is added to treeview
        """
        if self._treeview is None:
            raise RuntimeError(
                "the column hasn't been added to a treeview yet"
            )

    def _config_handler(self, rettype, *args):
        self._check_added()
        return self._treeview._call(
            rettype, self._treeview, 'column', self, *args
        )

    def _assign(self, treeview):
        """
        Assign column to given treeview
        """
        self._treeview = treeview

        for name, value in self._creation_opts.items():
            self.config[name] = value

        if self._text is not None:
            self.heading.config['text'] = self._text

    def to_tcl(self):
        # Only name in column list
        return self._name


class TreeviewRowList(MutableSequence):
    """
    List containing all rows of a treeview. This class is used for all rows and
    nested rows (subrows).

    Note, that instances of :class:`TreeviewRowList` must not be created
    manually. It is accessible through the `.rows` and `.subrows` attributes.
    """
    def __init__(self, treeview, root=None):
        super().__init__()

        self._root = root
        self._treeview = treeview

    def __repr__(self):
        return '%s(root=%r, rows=%d)' % (
            self.__class__.__name__,
            self._root,
            len(self)
        )

    @make_thread_safe
    def __getitem__(self, index):
        return self._get_all_rows()[index]

    @make_thread_safe
    def __setitem__(self, index, row):
        del self[index]
        self.insert(index, row)

    @make_thread_safe
    def __delitem__(self, index):
        self._treeview._call(None, self._treeview, 'delete', self[index])

    @make_thread_safe
    def __len__(self):
        return len(self._get_all_rows())

    def _get_all_rows(self):
        """
        Get a list of all rows created for a root node.
        """
        ids = self._treeview._call([str], self._treeview, 'children',
                                   self._root)
        rows = []

        for id_ in ids:
            row = TreeviewRow(name=id_)
            row._assign(treeview=self._treeview, root=self._root,
                        set_config=False)
            rows.append(row)

        return rows

    @make_thread_safe
    def insert(self, index, row):
        """
        Insert a row or values converted to a row at the given index.
        """
        # Convert to row
        if not isinstance(row, TreeviewRow):
            row = TreeviewRow(values=row)

        self._treeview._call(
            None, self._treeview, 'insert', self._root, index, '-id', row
        )

        row._assign(treeview=self._treeview, root=self._root)

    @make_thread_safe
    def sort(self, column_pos, reverse=False):
        """
        Sort all rows according to value of column with given ``column_pos``.
        The direction of the sorting can be set with ``reverse``. If this value
        is true, the rows are sorted in ascending order.
        """
        if column_pos < 1:
            raise IndexError('column position must be greater or equal 1')

        sorted_rows = list(self).copy()
        sorted_rows.sort(key=lambda r: r.config['values'][column_pos - 1],
                         reverse=reverse)

        for to_pos, row in enumerate(sorted_rows):
            from_pos = self.index(row)

            if from_pos != to_pos:
                row.move(to_pos)

            row.subrows.sort(column_pos, reverse)


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

    :class:`TreeviewRow` objects can also contain nested rows (subrows). They
    are created like normal rows but with the `.subrows` attribute:
    ::

        treeview.rows[0].subrows.append(teek.TreeviewRow(values=['a', 'b'])

    .. attribute:: config

        Similar to the ``config`` attribute that widgets have. The available
        options are documented as ``ITEM OPTIONS`` in :man:`ttk_treeview(3tk)`.
    """
    _next_row_num = 0

    def __init__(self, name=None, **kwargs):
        self._name = name or 'R%d' % TreeviewRow._next_row_num
        self._creation_opts = kwargs
        self._treeview = None
        self._root = None

        TreeviewRow._next_row_num += 1

        self.config = OptionConfigDict(self._config_handler)
        self.config._types.update({
            'values': [str],
            'text': str,
            'open': bool,
            'tags': [str],
            'image': teek.Image
        })

        self.subrows = TreeviewRowList(treeview=self._treeview, root=self)

    def __repr__(self):
        repr_str = '%s(%s' % (self.__class__.__name__, self._name)

        if self._treeview:
            repr_str += ', text=%r, values=%r, subrows=%d' % (
                self.config['text'],
                self.config['values'],
                len(self.subrows)
            )
        else:
            repr_str += ', not added to treeview'

        return repr_str + ')'

    def __eq__(self, other):
        return isinstance(other, TreeviewRow) and self._name == other._name

    def _config_handler(self, rettype, option=None, *args):
        self._check_added()

        if option is not None:
            args = [option] + list(args)

        return self._treeview._call(
            rettype, self._treeview, 'item', self, *args
        )

    def _check_added(self):
        """
        Check if row is added to treeview.
        """
        if self._treeview is None:
            raise RuntimeError(
                "this row hasn't been added to a treeview yet")

    def _assign(self, treeview, root=None, set_config=True):
        """
        Internal method for assigning a treeview and a root node to current
        row.
        The `set_config` argument specifies if init options should be set.
        """
        self._treeview = treeview
        self._root = root

        self.subrows._treeview = treeview

        if treeview is not None and set_config:
            for name, value in self._creation_opts.items():
                self.config[name] = value

    @property
    def selected(self):
        """
        Get current selection state.
        """
        self._check_added()
        return self._name in self._treeview._call([str], self._treeview,
                                                  'selection')

    @make_thread_safe
    def select(self):
        """
        Add row to current selection.
        """
        self._check_added()
        self._treeview._call(None, self._treeview, 'selection', 'add', self)

    @make_thread_safe
    def deselect(self):
        """
        Remove row from current selection.
        """
        self._check_added()
        self._treeview._call(None, self._treeview, 'selection', 'remove', self)

    @make_thread_safe
    def move(self, to_pos):
        """
        Move row at index to other position.
        """
        self._treeview._call(
            None, self._treeview, 'move', self, self._root, to_pos
        )

    def to_tcl(self):
        # Represented by name
        return self._name


class TreeviewColumnList(MutableSequence):
    """
    List containing all columns of a treeview.

    Note, that instances of :class:`TreeviewColumnList` must not be created
    manually. It is accessible through the `.columns` attribute.
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

    def __repr__(self):
        return '%s(columns=%d)' % (
            self.__class__.__name__,
            len(self)
        )

    @make_thread_safe
    def __setitem__(self, index, column):
        if index == 0 or index <= -len(self):
            raise KeyError('cannot set column #0')

        if not isinstance(column, TreeviewColumn):
            column = TreeviewColumn(text=column)

        self._data[index] = column
        self._assign()

    @make_thread_safe
    def __delitem__(self, index):
        if index == 0:
            raise KeyError('cannot delete column #0')

        del self._data[index]
        self._assign()

    @make_thread_safe
    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        # Length includes column 0
        return len(self._data)

    def _assign(self):
        """
        Update columns of widget and rebuild column objects.
        """
        self._treeview._call(None, self._treeview, 'configure', '-columns',
                             self._data[1:])

        for column in self._data:
            column._assign(self._treeview)

    @make_thread_safe
    def insert(self, index, column):
        """
        Insert column or column text converted to a column at given index.
        Note that the column at index 0 cannot be replaced!
        """
        if index == 0 or index <= -len(self):
            raise KeyError('cannot insert column at position 0')

        # Convert to column
        if not isinstance(column, TreeviewColumn):
            column = TreeviewColumn(text=column)

        self._data.insert(index, column)
        self._assign()


class Treeview(ChildMixin, Widget):
    """
    This is the treeview widget.

    :class:`TreeviewRow` and :class:`TreeviewColumn` objects can be added to
    this widget by calling ``insert`` or ``append`` of the ``rows`` or
    ``column`` property. In general, these properties behave like a
    :class:`list` of :class:`TreeviewRow` or :class:`TreeviewColumn` objects.

    Manual page: :man:`ttk_treeview(3tk)`
    """
    _widget_name = 'ttk::treeview'
    tk_class_name = 'Treeview'

    def __init__(self, parent, *, rows=[], columns=[], **kwargs):
        super().__init__(parent, **kwargs)

        self.rows = TreeviewRowList(treeview=self)
        self.columns = TreeviewColumnList(self, columns)

        for row in rows:
            self.rows.append(row)

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
