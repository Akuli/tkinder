"""Teek is a pythonic alternative to tkinter."""
# flake8: noqa

import os as _os
import sys as _sys

__version__ = '0.5'

if _os.environ.get('READTHEDOCS', None) == 'True':   # pragma: no cover
    # readthedocs must be able to import everything without _tkinter
    import types
    _sys.modules['_tkinter'] = types.SimpleNamespace(
        TclError=None,
        TCL_VERSION='8.6',
        TK_VERSION='8.6',
    )
else:       # pragma: no cover
    # python 3.4's tkinter does this BEFORE importing _tkinter
    if _sys.platform.startswith("win32") and _sys.version_info < (3, 5):
        import tkinter._fix


# not to be confused with _tkinter's TclError, this is defined here because
# this way error messages say teek.TclError instead of
# teek._something.TclError, or worse yet, _tkinter.TclError
class TclError(Exception):
    """This is raised when a Tcl command fails."""


# _platform_info does a version check, it must be first
from teek._platform_info import TCL_VERSION, TK_VERSION, windowingsystem
from teek._font import Font, NamedFont
from teek._structures import (
    Callback, Color, Image, ScreenDistance, TclVariable, StringVar, IntVar,
    FloatVar, BooleanVar, before_quit, after_quit)
from teek._tcl_calls import (
    tcl_call, tcl_eval, create_command, delete_command, run, quit, update,
    init_threads, make_thread_safe)
from teek._timeouts import after, after_idle
from teek._widgets.base import Widget
from teek._widgets.canvas import Canvas
from teek._widgets.menu import Menu, MenuItem
from teek._widgets.misc import (
    Button, Checkbutton, Combobox, Entry, Frame, Label, LabelFrame,
    Progressbar, Scrollbar, Separator, Spinbox)
from teek._widgets.notebook import Notebook, NotebookTab
from teek._widgets.text import Text
from teek._widgets.treeview import Treeview, TreeviewColumn, TreeviewRow
from teek._widgets.windows import Window, Toplevel
from teek import dialog, extras
