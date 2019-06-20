.. _tkinter:

Porting from Tkinter
====================

If you have some tkinter code and you would like to switch to teek, you came
to the right place. This page lists differences between tkinter and teek.
You might also find this page interesting if you are an experienced tkinter
programmer.


Before you begin
----------------

Make sure you have good test coverage. If you don't know what test coverage is,
I hope your project is quite small. In that case, make sure that you know how
every part and feature of the GUI is supposed to work and how to check if it
works well. Running a linter like flake8_ may also help, and understanding how
the code works doesn't hurt either.

.. _flake8: http://flake8.pycqa.org/en/latest/

Currently these tkinter widgets are missing in teek:

* ``tkinter.Listbox``
* ``tkinter.Menubutton``, ``tkinter.ttk.Menubutton``
* ``tkinter.OptionMenu``
* ``tkinter.PanedWindow``, ``tkinter.ttk.Panedwindow``
* ``tkinter.Radiobutton``, ``tkinter.ttk.Radiobutton``
* ``tkinter.Scale``, ``tkinter.ttk.Scale``
* ``tkinter.ttk.Sizegrip``

If the project uses some of these, you can still use them with
:ref:`Tcl calls <tcl-calls>`. However, that's kind of painful, so if the
project uses these widgets a lot, it's probably best to use tkinter for now or
`ask me <https://github.com/Akuli/teek/issues/new>`_ to add the widget to
teek.


To Get Started
--------------

If you find a file that contains ``from tkinter import *``, you should
immediately fix that. It is very bad style. Change the import to
``import teek``, and then replace things like ``Label`` with
``teek.Label``.

If you find code like ``import tkinter as tk``, you can just change ``tkinter``
to ``teek``, but I prefer changing it to ``import teek`` and then replacing
``tk`` with ``teek`` everywhere. That way, if you see ``teek.Label`` somewhere
in the code you know right away that it's not a tkinter label. If there is
``import tkinter``, change it to ``import teek`` and replace
``tkinter.something`` with ``teek.something`` everywhere.

Sometimes you may see this::

    import tkinter as tk
    from tkinter import ttk

Or much worse::

    from tkinter import *
    from tkinter.ttk import *

In these cases, you should replace both ``tkinter.something`` and
``tkinter.ttk.something`` with ``teek.something`` and do the
``import teek``. The ``teek`` module contains everything you need, including
Ttk widgets and a few non-Ttk widgets.

After this, try it out. It probably doesn't work yet, so keep reading.


Widget Name Differences
-----------------------

All tkinter GUIs use a ``tkinter.Tk`` object. There is no ``Tk`` object in
teek; instead, you should create a :class:`.Window` object and use that.
Usually you should also use :class:`.Window` instead of a :class:`.Toplevel` as
explained in :class:`.Window` documentation. You can create as many teek
windows as you want, and they actually use toplevels under the hood.

If the tkinter code creates multiple ``tkinter.Tk`` instances, it is probably
broken. Replace all of them with :class:`teek.Window <.Window>`.

If you have code that uses ``tkinter.Message``, you should use a ``Label``
instead. I believe message widgets were a thing before labels could handle
multiline text, but nowadays the text of labels can contain ``\n`` characters.

If you have code that uses ``ttk.Labelframe``, use ``LabelFrame`` instead. Look
carefully: ``Labelframe`` and ``LabelFrame`` are not the same. Non-ttk tkinter
supports ``LabelFrame`` only, but for some reason, ``tkinter/ttk.py`` has
``Labelframe`` in addition to ``LabelFrame``.


Quitting
--------

In tkinter, destroying the root window destroys the whole GUI and usually the
program terminates soon after that. In teek, destroying a window doesn't
quit the GUI, so instead of ``root.destroy()`` you need :func:`teek.quit`.

Trying to close a teek window does nothing by default. If you want the whole
program to end instead, do this::

    window.on_delete_window.connect(teek.quit)

If you want to close only the window that the user is closing (which is the
case for dialogs and other such things), do this::

    window.on_delete_window.connect(window.destroy)


Constants
---------

Tkinter has lots of constants like ``tkinter.BOTH``, but their values are just
similar strings::

    >>> import tkinter
    >>> tkinter.BOTH
    'both'

This means that ``some_widget.pack(fill=tkinter.BOTH)`` does the same thing as
``some_widget.pack(fill='both')``. Some programmers use constants like
``tkinter.BOTH`` while others prefer to just write ``'both'``. I think these
constants are dumb, which is why teek doesn't have them. Use strings like
``'both'`` in teek.


Run
---

Use :func:`teek.run() <.run>` instead of tkinter's ``root.mainloop()``
or ``tkinter.mainloop()``.


Options
-------

Options are used differently in tkinter and teek. For example,
``button['text']``, ``button.cget('text')``, ``button.config('text')[-1]`` and
``button.configure('text')[-1]`` are all valid ways to get the text of a button.
In teek, none of these work, and you instead do ``button.config['text']``.
However, teek raises good error messages:

>>> button = teek.Button(teek.Window(), "some text")
>>> button.cget('text')
Traceback (most recent call last):
    ...
TypeError: use widget.config['option'], not widget.cget('option')
>>> button['text']
Traceback (most recent call last):
    ...
TypeError: use widget.config['option'], not widget['option']
>>> button.config['text']
'some text'


Widget-specific Differences
---------------------------

Most widgets work more or less the same way in teek and tkinter, but not all
widgets do. Some of the biggest differences are listed here, but not everything
is; refer to :ref:`the documentation <widgets>` of the widget that is causing
errors for more details.

Button and CheckButton
    Tkinter buttons and checkbuttons have a ``command`` option that is set to a
    function that runs when the button is clicked, but that's a
    :class:`.Callback` object in teek:

    >>> button.config['command'] = print
    Traceback (most recent call last):
        ...
    ValueError: cannot set the value of 'command', maybe use widget.config['command'].connect() instead?
    >>> button.config['command'].connect(print)

    This way more than one callback can be easily connected to the button.

Text and Notebook
    Many things are very different (read: much better and more pythonic) in
    teek. You probably need to read most of teek's
    :ref:`text widget docs <textwidget>` or :ref:`notebook docs <notebook>`
    anyway, so I won't even try to summarize everything here.

Entry
    Instead of ``insert``, ``delete`` and ``get`` methods, there is a settable
    :attr:`~.Entry.text` attribute.


Dialogs
-------

Dialog functions are named differently in teek. For example, instead of
``filedialog.askopenfilename()`` you use
:func:`teek.dialog.open_file() <.dialog.open_file>`. Unlike in tkinter, you don't
need to import anything special in order to use the dialog functions;
``import teek`` is all you need, and after that, you can do
``teek.dialog.open_file()``.


.. _tkinter-binding:

Binding
-------

Teek's bind stuff is documented :ref:`here <binding>`. As you can see there,
we have some differences to tkinter. First of all, if you want anything to work
at all, you need to pass ``event=True`` to :meth:`~.Widget.bind` to get
tkinter-like event objects. However, this is a common thing to do in tkinter::

    widget.bind('<SomeEvent>', lambda event: some_function())

Tkinter always gives an ``event`` argument to bind callbacks, and the lambda
discards it because ``some_function`` must be called like ``some_function()``,
not ``some_function(event)``. If you just pass ``event=True``, you end up with
code like this...
::

    widget.bind('<SomeEvent>', (lambda event: some_function()), event=True)

...which can be simplified a lot because not using ``event=True`` does the same
thing as the lambda::

    widget.bind('<SomeEvent>', some_function)

If you do need the event object, watch out for differences in the attributes.
For example, tkinter's ``event.x_root`` is ``event.rootx`` in teek. This is
for consistency with :meth:`~.Widget.event_generate`.

Note that tkinter's ``bind`` discards all old bindings, but this doesn't happen
in teek. For example, if you do this...
::

    widget.bind('<SomeEvent>', func1)
    widget.bind('<SomeEvent>', func2)

...only ``func2`` is bound in tkinter, but both are bound in teek.

Tkinter's bind takes an ``add=True`` argument that tells it to not forget old
bindings, and you can safely get rid of it. If you see some tkinter code that
relies on the discarding behaviour, which I don't see very often, you need to
use :attr:`.Widget.bindings` to unbind the old function.

Speaking of unbinding, tkinter also has an ``unbind()`` method. It works like
this when used correctly::

    func_id = widget.bind('<SomeEvent>', func)
    ...
    widget.unbind('<SomeEvent>', func_id)

Searching for ``def unbind`` in
`tkinter's source code <https://github.com/python/cpython/blob/master/Lib/tkinter/__init__.py>`_
reveals that ``widget.unbind`` actually discards all bindings of
``<SomeEvent>``, and if the ``func_id`` is given, it also cleans things up.
Teek does the cleanup automatically for you when the widget is destroyed
(see :meth:`~.Widget.destroy`).


Widget Methods
--------------

Tkinter's widgets have some methods that are available in all widgets, and they
don't actually do anything with the widget. For example,
``any_widget.after(1000, func)`` runs ``func()`` in the
:ref:`event loop <eventloop>` after waiting for 1 second. In teek, things
that don't need a widget in order to work are functions, not widget methods.
Here is a list of them:

+-------------------------------------------+-------------------------------+
| Tkinter                                   | Teek                          |
+===========================================+===============================+
| ``any_widget.after(milliseconds, cb)``    | :func:`teek.after`            |
+-------------------------------------------+-------------------------------+
| ``any_widget.after_idle(cb)``             | :func:`teek.after_idle`       |
+-------------------------------------------+-------------------------------+
| ``any_widget.update()``                   | :func:`teek.update`           |
+-------------------------------------------+-------------------------------+
| ``any_widget.tk.call()``                  | :func:`teek.tcl_call`         |
+-------------------------------------------+-------------------------------+
| ``any_widget.tk.eval()``                  | :func:`teek.tcl_eval`         |
+-------------------------------------------+-------------------------------+
| ``any_widget.tk.createcommand()``         | :func:`teek.create_command`   |
+-------------------------------------------+-------------------------------+
| ``any_widget.tk.deletecommand()``         | :func:`teek.delete_command`   |
+-------------------------------------------+-------------------------------+
| ``any_widget.mainloop()``                 | :func:`teek.run`              |
+-------------------------------------------+-------------------------------+
| ``root.destroy()``                        | :func:`teek.quit`             |
+-------------------------------------------+-------------------------------+

There are also some things that must be done with ``any_widget.tk.call()`` in
tkinter, but teek has nicer support for them:

+-----------------------------------------------+--------------------------------+
| Tkinter                                       | Teek                           |
+===============================================+================================+
| ``any_widget.call('tk', 'windowingsystem')``  | :func:`teek.windowingsystem`   |
+-----------------------------------------------+--------------------------------+


Variable Objects
----------------

``DoubleVar`` is :class:`.FloatVar` in teek because not all python users
know that ``double`` means a precise ``float`` in programming languages like C.
Other variable classes have same names.

There is no ``trace()`` method, but there is a
:attr:`~.TclVariable.write_trace` attribute.


Font Objects
------------

Tkinter has one font class, ``tkinter.font.Font``, which represents a font that
has a name in Tcl. There are two font classes in teek, and usually you
should use :class:`.NamedFont` in teek when ``tkinter.font.Font`` is used in
tkinter. See :ref:`font documentation <font-objs>` for details.


Tcl Calls
---------

In tkinter, you might see code like this::

    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        ...some mac specific code...

Here ``root.tk.call('tk', 'windowingsystem')`` calls ``tk windowingsystem`` in
Tcl, and that returns ``'win32'``, ``'aqua'`` or ``'x11'`` as documented in
:man:`tk(3tk)`. Notice that the return type is a string, but it's not specified
anywhere. Teek is more explicit::

    if tk.tcl_call(str, 'tk', 'windowingsystem') == 'aqua':
        ...

``1.2 == '1.2'`` is false in python, but there is no distinction like that in
Tcl; all objects are essentially strings, and ``1.2`` is literally the same
thing as ``'1.2'``. There is no good way to figure out what type tkinter's
``root.tk.call`` will return, and it's easiest to try it and see.

Teek gets rid of this problem by requiring explicit return types everywhere.
If you want a Tcl call to return a string, you pass it ``str``. See
:ref:`tcl-calls` for more documentation.
