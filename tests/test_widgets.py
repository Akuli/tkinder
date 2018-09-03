import contextlib
import pythotk as tk
import re

import pytest


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


def test_bind(handy_callback):
    widget = tk.Window()
    assert not widget.bindings.keys()

    @handy_callback
    def tcl_call_bound_callback():
        pass

    @handy_callback
    def pythotk_bound_callback():
        pass

    command = tk.create_command(tcl_call_bound_callback)

    tk.tcl_call(None, 'bind', widget, '<<Asd>>', command)
    assert widget.bindings.keys() == {'<<Asd>>'}
    widget.bind('<<Asd>>', pythotk_bound_callback)
    tk.update()
    tk.tcl_call(None, 'event', 'generate', widget, '<<Asd>>')

    tk.delete_command(command)

    assert tcl_call_bound_callback.ran_once()    # tests binding with +
    assert pythotk_bound_callback.ran_once()

    # some binding strings are equivalent
    assert widget.bindings['<Button-3>'] is widget.bindings['<Button-3>']
    assert widget.bindings['<3>'] is widget.bindings['<Button-3>']

    assert repr(widget.bindings) == '<a bindings object, behaves like a dict>'


def test_event_objects():
    events = []

    widget = tk.Window()
    widget.bind('<<Asd>>', events.append, event=True)
    tk.update()     # needed for virtual events to work
    widget.event_generate('<<Asd>>', data='asd asd')
    event = events.pop()
    assert not events

    # if some of these checks fail, feel free to make them less strict
    assert event.data(str) == 'asd asd'
    assert event.above is None
    assert event.borderwidth is None
    assert event.button is None
    assert event.char == '??'
    assert event.count is None
    assert event.delta is None
    assert event.focus is None
    assert event.height is None
    assert isinstance(event.i_window, int)
    assert event.keycode is None
    assert event.keysym == '??'
    assert event.keysym_num is None
    assert event.mode == '??'
    assert event.override is None
    assert event.place == '??'
    assert event.property_name == '??'
    assert event.root == 0
    assert event.rootx == -1
    assert event.rooty == -1
    assert event.sendevent is False
    assert isinstance(event.serial, int)
    assert event.state == '0'
    assert event.subwindow == 0
    assert event.time == 0
    assert event.type == 35     # see some docs somewhere i dunno why 35
    assert event.widget is widget
    assert event.width is None
    assert event.x == 0
    assert event.y == 0

    regex = r"<Event: data='asd asd', serial=\d+, type=35>"
    assert re.fullmatch(regex, repr(event)) is not None


def test_bind_deletes_tcl_commands(handy_callback):
    widget = tk.Window()
    widget.bind('<Button-1>', print)
    command_string = tk.tcl_call([str], 'bind', widget, '<Button-1>')[0]
    assert command_string.startswith('pythotk_command_')
    assert command_string in tk.tcl_call([str], 'info', 'commands')
    widget.destroy()
    assert command_string not in tk.tcl_call([str], 'info', 'commands')


def test_config_types(check_config_types):
    window = tk.Window()
    widgets = [window, window.toplevel, tk.Frame(window), tk.Separator(window),
               tk.Label(window), tk.Button(window), tk.Entry(window),
               tk.LabelFrame(window), tk.Checkbutton(window),
               tk.Scrollbar(window), tk.Menu()]
    for widget in widgets:
        check_config_types(widget.config, type(widget).__name__)


def test_from_tcl():
    window = tk.Window()
    widget_path = window.to_tcl()
    assert isinstance(widget_path, str)

    assert tk.Window.from_tcl(widget_path) is window
    assert tk.Widget.from_tcl(widget_path) is window

    with pytest.raises(TypeError) as error:
        tk.Label.from_tcl(widget_path)
    assert str(error.value).endswith(" is a Window, not a Label")


@pytest.mark.skipif(tk.TK_VERSION < (8, 6), reason="busy is new in Tk 8.6")
def test_busy():
    for widget in [tk.Frame(tk.Window()), tk.Window()]:
        assert widget.busy_status() is False
        widget.busy_hold()
        assert widget.busy_status() is True
        widget.busy_forget()
        assert widget.busy_status() is False

        with pytest.raises(ZeroDivisionError):
            with widget.busy():
                assert widget.busy_status() is True
                1 / 0

        assert widget.busy_status() is False


def get_counter_value(widget):
    match = re.search(r'\d+$', widget.to_tcl())
    assert match
    return int(match.group(0))


def test_widget_name_bug():
    # this bug occurs when we have 2 classes with the same name
    class Asd(tk.Label):
        pass

    AsdLabel = Asd

    class Asd(tk.Button):
        pass

    AsdButton = Asd

    # it must not be possible to have two Asds with same to_tcl() widget path,
    window = tk.Window()
    label = AsdLabel(window)
    button = AsdButton(window)

    while get_counter_value(label) < get_counter_value(button):
        label = AsdLabel(window)
        assert label.to_tcl() != button.to_tcl()

    while get_counter_value(button) < get_counter_value(label):
        button = AsdButton(window)
        assert label.to_tcl() != button.to_tcl()


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

    for option in ['padx', 'pady']:
        assert isinstance(pack_info[option], list)
        assert len(pack_info[option]) in {1, 2}
        for item in pack_info[option]:
            assert isinstance(item, tk.ScreenDistance)
    for option in ['ipadx', 'ipady']:
        assert isinstance(pack_info[option], tk.ScreenDistance)

    button.pack_forget()
    with pytest.raises(tk.TclError):
        button.pack_info()

    button.pack(**pack_info)
    assert button.pack_info() == pack_info
    button.pack_forget()

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
