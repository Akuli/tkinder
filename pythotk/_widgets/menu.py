import collections.abc

import pythotk as tk
from pythotk._structures import CgetConfigureConfigDict
from pythotk._tcl_calls import needs_main_thread
from pythotk._widgets.base import Widget


# all menu item things that do something run in the main thread to avoid any
# kind of use of menu items that are in an inconsistent state, and the Menu
# class also does this... think of it as poor man's locking or something
class MenuItem:

    def __init__(self, *args, **kwargs):
        self._options = kwargs.copy()

        if not args:
            self.type = 'separator'
        elif len(args) == 2:
            self._options['label'], second_object = args
            if isinstance(second_object, tk.BooleanVar):
                self.type = 'checkbutton'
                self._options['variable'] = second_object
            elif callable(second_object):
                self.type = 'command'
                self._command_callback = second_object  # see _adding_finalizer
            elif isinstance(second_object, Menu):
                self.type = 'cascade'
                self._options['menu'] = second_object
            else:   # assume an iterable
                self.type = 'cascade'
                self._options['menu'] = Menu(second_object)
        elif len(args) == 3:
            self.type = 'radiobutton'
            (self._options['label'],
             self._options['variable'],
             self._options['value']) = args
        else:
            raise TypeError(
                "expected 0, 2 or 3 arguments to MenuItem, got " + len(args))

        self._args = args
        self._kwargs = kwargs
        self._menu = None
        self._index = None

        self.config = CgetConfigureConfigDict(self._config_entrycommand_caller)
        self.config._types.update({
            'activebackground': tk.Color,
            'activeforeground': tk.Color,
            'accelerator': str,
            'background': tk.Color,
            #'bitmap': ???,
            'columnbreak': bool,
            'compound': str,
            'font': tk.Font,
            'foreground': tk.Color,
            'hidemargin': bool,
            'image': tk.Image,
            'indicatoron': bool,
            'label': str,
            'menu': Menu,
            'offvalue': bool,
            'onvalue': bool,
            'selectcolor': tk.Color,
            'selectimage': tk.Image,
            'state': str,
            'underline': bool,
            'value': str,
            'variable': (tk.BooleanVar if self.type == 'checkbutton'
                         else tk.StringVar),
        })
        self.config._special['command'] = self._create_command

    def __repr__(self):
        parts = list(map(repr, self._args))
        parts.extend('%s=%r' % pair for pair in self._kwargs.items())
        return 'MenuItem(%s)' % ', '.join(parts)

    def _get_insert_args(self):
        for option, value in self._kwargs.items():
            yield '-' + option
            yield value

    def _after_adding(self, menu, index):
        self._menu = menu
        self._index = index
        self.config.update(self._options)
        if self.type == 'command':
            self.config['command'].connect(self._command_callback)

    def _after_removing(self):
        self._menu = None
        self._index = None

    def _check_in_menu(self):
        assert (self._menu is None) == (self._index is None)
        if self._menu is None:
            raise RuntimeError("the MenuItem hasn't been added to a Menu yet")

    @needs_main_thread
    def _config_entrycommand_caller(self, returntype, subcommand, *args):
        assert subcommand in {'cget', 'configure'}
        self._check_in_menu()
        return tk.tcl_call(returntype, self._menu, 'entry' + subcommand,
                           self._index, *args)

    def _create_command(self):
        self._check_in_menu()
        result = tk.Callback()
        command_string = tk.create_command(result.run)
        tk.tcl_call(None, self._menu, 'entryconfigure', self._index,
                    '-command', command_string)
        self._menu._command_list.append(command_string)
        return result


# does not use ChildMixin because usually it's a bad idea to e.g. pack a menu
# TODO: document that this class assumes that nothing else changes the
#       underlying Tcl widget
class Menu(Widget, collections.abc.MutableSequence):
    """A menu widget that can be e.g. added to a :class:`.Window`."""

    def __init__(self, items=(), **kwargs):
        kwargs.setdefault('tearoff', False)
        super().__init__('menu', None, **kwargs)
        self._items = []
        self.extend(items)

    def _repr_parts(self):
        return ['contains %d items' % len(self)]

    @needs_main_thread
    def __getitem__(self, index):
        if isinstance(index, slice):
            raise TypeError("slicing a Menu widget is not supported")
        return self._items[index]

    @needs_main_thread
    def __delitem__(self, index):
        if isinstance(index, slice):
            raise TypeError("slicing a Menu widget is not supported")

        index = range(len(self))[index]    # handle indexes like python does it
        self._call(None, self, 'delete', index)
        item = self._items.pop(index)
        item._after_removing()

        # indexes after the deleted item are messed up
        for index in range(index, len(self._items)):
            self._items[index]._index = index

    @needs_main_thread
    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise TypeError("slicing a Menu widget is not supported")

        # this is needed because otherwise this breaks with a negative index,
        # and this code handles indexes like python does it
        index = range(len(self))[index]

        del self[index]
        self.insert(index, value)

    @needs_main_thread
    def __len__(self):
        return len(self._items)

    @needs_main_thread
    def insert(self, index, item: MenuItem):
        if not isinstance(item, MenuItem):
            # TODO: test that tuples are handled correctly here because that
            #       might be a common mistake
            raise TypeError("expected a MenuItem, got %r" % (item,))

        # handle the index line python does it
        self._items.insert(index, item)
        index = self._items.index(item)
        self._call(None, self, 'insert', index, item.type,
                   *item._get_insert_args())
        item._after_adding(self, index)

        # inserting to self._items messed up items after the index
        for index2 in range(index + 1, len(self._items)):
            self._items[index2]._index = index2