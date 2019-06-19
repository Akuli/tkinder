import functools
from collections.abc import MutableSequence, Iterable

import teek
from teek._widgets.base import Widget, ChildMixin
from teek._structures import ConfigDict
from teek._tcl_calls import make_thread_safe


class FallbackConfigDict(ConfigDict):
    """
    Config dictionary which uses fallback values if the given handler
    function cannot be executed
    """

    def __init__(self):
        super().__init__()

        # Handler functions
        self._handlers = {}

        # Fallback values (used if handler function cannot be executed)
        self._fallbacks = {}

    def _set(self, option, value):
        if option not in self._types:
            raise KeyError('option %s not existing' % option)

        try:
            # Set value of fallback
            self._fallbacks[option] = value
            # Look for handler function(s)
            handlers = self._handlers[option] if option in self._handlers \
                       else self._handlers['*']
            
            if not isinstance(handlers, Iterable):
                handlers = [handlers]

            for handler in handlers:
                handler(None, option, value)
        except:
            pass

    def _get(self, option):
        if option not in self._types:
            raise KeyError('option %s not found' % option)

        try:
            # Look for handler function
            handler = self._handlers[option] if option in self._handlers \
                      else self._handlers['*']

            if isinstance(handler, Iterable):
                handler = handler[0]

            return handler(self._types.get(option, str), option)
        except Exception as ex:
            # If exception, return fallback value
            return self._fallbacks[option] if option in self._fallbacks \
                   else None

    def _list_options(self):
        return self._handlers.keys()

    def _check_option(self, option):
        # Only check if master handler function is not defined
        if '*' not in self._list_options():
            super()._check_option(option)

    def push(self):
        """
        Update all values (specified in fallback dict) on remote side
        """
        for option, value in self._fallbacks.items():
            self._set(option, value)


class TreeviewColumn:
    """
    Represents a column of a treeview widget or one which is ready to be added
    to a treeview widget. A column specifies the title, content anchor and size
    options.

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
    same tab.

    .. attribute:: config

        Similar to the ``config`` attribute that widgets have. The available
        options are documented as ``TAB OPTIONS`` in :man:`ttk_treeview(3tk)`.
    """

    next_col_num = 0

    @make_thread_safe
    def __init__(self, name=None, command=None, **kwargs):
        self._name = name or 'C%d' % TreeviewColumn.next_col_num
        self._treeview = kwargs.pop('treeview', None)

        TreeviewColumn.next_col_num += 1

        self.config = FallbackConfigDict()
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
        self.config._fallbacks.update({
            'anchor': 'center'
        })
        self.config._handlers.update({
            'text': self._heading_handler,
            'image': self._heading_handler,
            'anchor': [self._column_handler, self._heading_handler],
            '*': self._column_handler
        })

        for name, value in kwargs.items():
            self.config[name] = value

    def __repr__(self):
        return "%s('%s', text='%s')" % (
            self.__class__.__name__,
            self._name,
            self.config['text']
        )

    def _heading_handler(self, rettype, option, *args):
        return self._treeview._call(rettype, self._treeview, 'heading', self, '-' + option, *args)

    def _column_handler(self, rettype, option, *args):
        return self._treeview._call(rettype, self._treeview, 'column', self, '-' + option, *args)

    def _create_click_command(self):
        result = teek.Callback()
        command_string = teek.create_command(result.run)
        self._heading_handler(None, 'command', command_string)
        return result

    @make_thread_safe
    def assign(self, treeview):
        self._treeview = treeview

    @make_thread_safe
    def to_tcl(self):
        return self._name


class TreeviewRow:
    next_row_num = 0

    @make_thread_safe
    def __init__(self, name=None, **kwargs):
        self._treeview = kwargs.pop('treeview', None)
        self._name = name or 'R%d' % TreeviewRow.next_row_num

        TreeviewRow.next_row_num += 1

        self.config = FallbackConfigDict()
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

        for name, value in kwargs.items():
            self.config[name] = value

    def __repr__(self):
        return "%s('%s', text='%s', values=%s)" % (
            self.__class__.__name__,
            self._name,
            self.config['text'],
            repr(self.config['values'])
        )

    def _item_handler(self, rettype, option, *args):
        return self._treeview._call(rettype, self._treeview, 'item', self, '-' + option, *args)

    @make_thread_safe
    def assign(self, treeview):
        self._treeview = treeview

    @make_thread_safe
    def to_tcl(self):
        return self._name

    @make_thread_safe
    def select(self):
        self._treeview._call(None, self._treeview, 'selection', 'add', self)

    @make_thread_safe
    def deselect(self):
        self._treeview._call(None, self._treeview, 'selection', 'remove', self)


class TreeviewColumnList(MutableSequence):
    def __init__(self, treeview):
        super().__init__()

        self._data = [TreeviewColumn('#0', treeview=treeview)]
        self._treeview = treeview

    def __setitem__(self, index, column):
        if index == 0:
            raise KeyError('cannot set column #0')

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
        return len(self._data)

    def _update(self):
        self._treeview._call(None, self._treeview, 'configure', '-columns', self._data[1:])

        for column in self._data:
            column.config.push()

    def insert(self, index, column):
        if index == 0:
            raise KeyError('cannot insert column at index 0')

        if not isinstance(column, TreeviewColumn):
            column = TreeviewColumn(text=column)

        column.assign(self._treeview)
        self._data.insert(index, column)
        self._update()


class TreeviewRowList(MutableSequence):
    def __init__(self, treeview):
        super().__init__()

        self._data = []
        self._treeview = treeview

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, row):
        raise NotImplementedError('use insert() instead')

    def __delitem__(self, index):
        self._treeview._call(None, self._treeview, 'delete', self._data[index])
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def insert(self, index, row):
        if not isinstance(row, TreeviewRow):
            row = TreeviewRow(values=row)

        row.assign(self._treeview)
        self._treeview._call(None, self._treeview, 'insert', '', index, '-id', row)
        row.config.push()
        self._data.insert(index, row)

    def move(self, from_pos, to_pos):
        row = self._data[from_pos]
        del self[from_pos]
        self.insert(to_pos, row)


class Treeview(ChildMixin, Widget):
    _widget_name = 'ttk::treeview'
    tk_class_name = 'Treeview'

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.rows = TreeviewRowList(self)
        self.columns = TreeviewColumnList(self)

    def _init_config(self):
        super()._init_config()

        self.config._types.update({
            'selectmode': str,
            'height': int,
            'show': [str]
        })

    def _repr_parts(self):
        return ["contains %d columns & %d rows" % (len(self.columns), len(self.rows))]

    def _xview_or_yview(self, xview_or_yview, *args):
        if not args:
            return self._call((float, float), self, xview_or_yview)

        self._call(None, self, xview_or_yview, *args)
        return None

    xview = functools.partialmethod(_xview_or_yview, 'xview')
    yview = functools.partialmethod(_xview_or_yview, 'yview')

    def sort(self, column_pos, reverse=False):
        if column_pos < 1:
            raise KeyError('column position must be greater or equal 1')

        sorted_rows = self.rows._data.copy()
        sorted_rows.sort(key=lambda r: r.config['values'][column_pos-1], reverse=reverse)

        for old, row in enumerate(self.rows):
            self.rows.move(old, sorted_rows.index(row))