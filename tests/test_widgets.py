# most of the tests don't destroy the widgets they use, all widgets are
# destroyed the next time quit() is called or python exits anyway
import contextlib
import platform
import itertools
import os
import pythotk as tk

import pytest

_flatten = itertools.chain.from_iterable


@contextlib.contextmanager
def _tkinter_hint(bad, assigning):
    with pytest.raises(TypeError) as error:
        yield

    good = "widget.config['option']"
    if assigning:
        good += " = value"
    assert str(error.value) == "use %s, not %s" % (good, bad)


def test_tkinter_hints():
    window = tk.Window()

    with _tkinter_hint("widget['option']", assigning=False):
        window['whatever']

    # this uses assigning=False because the error message is supposed to
    # be just like the one above
    with _tkinter_hint("widget['option']", assigning=False):
        window['whatever'] = 'blah'

    with _tkinter_hint("widget.config(option=value)", assigning=True):
        window.config(whatever='blah')

    with _tkinter_hint("widget.configure(option=value)", assigning=True):
        window.configure(whatever='blah')


def test_destroy():
    window = tk.Window()
    label = tk.Label(window)
    frame = tk.Frame(window)
    button = tk.Button(frame)
    widgets = [window, label, button]

    assert window.winfo_children() == [label, frame]
    assert frame.winfo_children() == [button]

    for widget in widgets:
        assert widget.winfo_exists()

    window.destroy()
    for widget in widgets:
        assert not widget.winfo_exists()
        assert repr(widget).startswith('<destroyed ')

    with pytest.raises(RuntimeError) as error:
        label.config['text'] = 'lel'
    assert str(error.value) == 'the widget has been destroyed'


def test_window():
    windows = [
        (tk.Window("hello hello"), "hello hello"),
        (tk.Window(), None),
    ]

    for window, default_title in windows:
        assert window.winfo_toplevel() is window.toplevel
        assert isinstance(window.toplevel, tk.Toplevel)
        tk.update()     # you can add more of these if the tests don't work

        assert window.wm_state == 'normal'
        if default_title is not None:
            assert window.title == default_title
            assert repr(default_title) in repr(window)

        window.title = "hello hello"
        assert window.title == "hello hello"

    not_a_window = tk.Frame(tk.Window())
    assert not hasattr(not_a_window, 'title')


@pytest.mark.skipif('CI' in os.environ,
                    reason=("relies on non-guaranteed details about how "
                            "window managers work or something like that"))
def test_window_states():
    window = tk.Window()
    for method, state in [(window.withdraw, 'withdrawn'),
                          (window.iconify, 'iconic')]:
        method()
        tk.update()
        assert window.wm_state == state
        assert ("wm_state='%s'" % state) in repr(window)
        window.deiconify()
        tk.update()
        assert window.wm_state == 'normal'
        assert "wm_state='normal'" not in repr(window)

        window.wm_state = state        # should do same as method()
        tk.update()
        assert window.wm_state == state
        window.deiconify()
        tk.update()
        assert window.wm_state == 'normal'


def test_window_closing():
    for window in [tk.Window(), tk.Toplevel()]:
        # raises an error if not connected, so this also tests the
        # implicit connecting
        window.on_delete_window.disconnect(tk.quit)

        assert window.winfo_exists()
        window.destroy()
        assert not window.winfo_exists()


@pytest.mark.skipif(platform.system() == "Windows",
                    reason=("actual windows window manager behavior"
                            "is different than the test expects"))
def test_geometry():
    window = tk.Window()

    # namedtuple features
    geometry = window.geometry()
    geometry2 = window.geometry()
    assert geometry == geometry2
    assert hash(geometry) == hash(geometry2)
    assert repr(geometry) == repr(geometry2)
    assert repr(geometry).startswith('Geometry(')

    window.geometry(300, 400)
    tk.update()
    assert window.geometry()[:2] == (300, 400)

    window.geometry(x=123, y=456)
    tk.update()
    assert window.geometry() == (300, 400, 123, 456)

    window.geometry(100, 200, 300, 400)
    #lintplox
    tk.update()
    assert window.geometry() == (100, 200, 300, 400)

    for pair in [('width', 'height'), ('x', 'y')]:
        with pytest.raises(TypeError) as error:
            window.geometry(**{pair[0]: 123})
        assert str(error.value) == 'specify both %s and %s, or neither' % pair

# this is commented out because ttk widgets don't have color options
#
#_COLOR_OPTIONS = [
#    'foreground', 'fg', 'background', 'bg',
#    'activeforeground', 'activebackground',
#    'disabledforeground', 'disabledbackground',
#    'highlightcolor', 'highlightbackground',
#    'selectforeground', 'selectbackground',
#    'insertbackground',
#]
#_ALIASES = [('fg', 'foreground'), ('bg', 'background')]
#_COLORS = ['red', 'Red', '#ff0000', '#F00', '#fFf000000']


def test_options():
    window = tk.Window()

    for widget in [tk.Button(window), tk.Label(window)]:
        assert 'behaves like a dict' in repr(widget.config)
        assert len(widget.config) == len(list(widget.config))

        # abbreviations aren't allowed, it simplifies the implementation
        # and people aren't aware of abbreviating things in tk anyway
        assert 'text' in widget.config
        assert 'tex' not in widget.config
        with pytest.raises(KeyError):
            widget.config['tex']

#        for option in (_COLOR_OPTIONS & widget.config.keys()):
#            for color in _COLORS:
#                widget.config[option] = color
#                assert widget.config[option] == '#ff0000', option
#
#                if option in _flatten(_ALIASES):
#                    for a, b in _ALIASES:
#                        assert widget.config[a] == widget.config[b]

        with pytest.raises(TypeError):
            widget.config.pop('text')

        # buttons are tested below, this makes sure that windows and
        # labels don't do something weird when they get an option that
        # they shouldn't support
        if not isinstance(widget, tk.Button):
            with pytest.raises(KeyError):
                widget.config['command'] = print

    widget1 = tk.Label(window, 'lol')
    widget1.config.update({'text': 'asd'})
    widget2 = tk.Label(window, text='asd')
    assert widget1.config == widget2.config
    widget2.config['text'] = 'tootie'
    assert widget1.config != widget2.config


def test_labels():
    window = tk.Window()

    label = tk.Label(window)
    assert "text=''" in repr(label)
    assert label.config['text'] == ''

    label.config.update({'text': 'new text'})
    assert label.config['text'] == 'new text'
    assert "text='new text'" in repr(label)

    label2 = tk.Label(window, 'new text')
    assert label.config == label2.config


def test_buttons(capsys):
    window = tk.Window()
    stuff = []

    button1 = tk.Button(window)
    button2 = tk.Button(window, 'click me')
    button3 = tk.Button(window, 'click me', (lambda: stuff.append(3)))

    assert "text=''" in repr(button1)
    assert "text='click me'" in repr(button2)
    assert "text='click me'" in repr(button3)

    assert button1.config['text'] == ''
    assert button2.config['text'] == button3.config['text'] == 'click me'

    for button in [button1, button2, button3]:
        assert 'command' not in button.config
        with pytest.raises(ValueError) as error:
            button.config['command'] = print
        assert str(error.value).endswith(
            "use the on_click attribute or an initialization argument instead")

    # ideally there would be some way to click the button virtually and
    # let tk handle it, but i haven't gotten anything like that to work
    button1.on_click.run()
    button2.on_click.run()
    assert stuff == []
    button3.on_click.run()
    assert stuff == [3]

    button1.on_click.connect(stuff.append, args=[1])
    button2.on_click.connect(stuff.append, args=[2])
    button3.on_click.connect(stuff.append, args=['wolo'])
    button3.on_click.connect(stuff.append, args=['wolo'])

    stuff.clear()
    for button in [button1, button2, button3]:
        button.on_click.run()
    assert stuff == [1, 2, 3, 'wolo', 'wolo']

    def oops():
        raise ValueError("shit")

    assert capsys.readouterr() == ('', '')
    button1.on_click.connect(oops)
    button1.on_click.run()
    output, errors = capsys.readouterr()
    assert not output
    assert 'button1.on_click.connect(oops)' in errors


def test_button_invoke():
    button = tk.Button(tk.Window())
    stuff = []
    button.on_click.connect(stuff.append, args=[1])
    button.on_click.connect(stuff.append, args=[2])
    button.invoke()
    assert stuff == [1, 2]


def test_separator():
    assert tk.Separator(tk.Window()).config['orient'] == 'horizontal'


def test_from_tcl():
    window = tk.Window()
    widget_path = window.to_tcl()
    assert isinstance(widget_path, str)

    assert tk.Window.from_tcl(widget_path) is window
    assert tk.Widget.from_tcl(widget_path) is window

    with pytest.raises(TypeError) as error:
        tk.Label.from_tcl(widget_path)
    assert str(error.value).endswith(" is a Window, not a Label")


def test_packing():
    window = tk.Window()
    button = tk.Button(window)
    button.pack(fill='both', expand=True)

    pack_info = button.pack_info()
    assert pack_info['in'] is window
    assert pack_info['side'] == 'top'
    assert pack_info['fill'] == 'both'
    assert pack_info['expand'] is True
    assert pack_info['anchor'] == 'center'
    for string_key in ['padx', 'pady', 'ipadx', 'ipady']:
        assert isinstance(pack_info[string_key], str)

    button.pack_forget()
    with pytest.raises(tk.TclError):
        button.pack_info()

    assert window.pack_slaves() == []
    label1 = tk.Label(window, 'label one')
    label1.pack()
    label2 = tk.Label(window, 'label two')
    label2.pack()
    assert window.pack_slaves() == [label1, label2]

    frame = tk.Frame(window)
    label2.pack(in_=frame)
    assert window.pack_slaves() == [label1]
    assert frame.pack_slaves() == [label2]
