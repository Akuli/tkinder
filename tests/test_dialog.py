import contextlib
import random
import re
import time

import pythotk as tk


@contextlib.contextmanager
def fake_tcl_command(name, options, return_value):
    randomness = re.sub(r'\W', '', str(random.random()) + str(time.time()))
    temp_name = 'temporary_command_' + randomness
    ran = 0

    def callback(*args):
        assert len(args) % 2 == 0
        assert dict(zip(args[0::2], args[1::2])) == options

        nonlocal ran
        ran += 1
        return return_value

    fake_command = tk.create_command(callback, extra_args_type=str)

    # here comes the magic
    tk.tcl_call(None, 'rename', name, temp_name)
    tk.tcl_call(None, 'rename', fake_command, name)
    try:
        yield
    finally:
        tk.delete_command(name)
        tk.tcl_call(None, 'rename', temp_name, name)

    assert ran == 1


def test_message_boxes():
    with fake_tcl_command('tk_messageBox', {
                '-type': 'ok',
                '-icon': 'info',
                '-message': 'a',
                '-detail': 'b'}, 'ok'):
        assert tk.dialog.info('a', 'b') is None

    for icon in ['info', 'warning', 'error']:
        with fake_tcl_command('tk_messageBox', {
                '-type': 'ok',
                '-icon': icon,
                '-message': 'a'}, 'ok'):
            assert getattr(tk.dialog, icon)('a') is None

    for func, ok, icon in [(tk.dialog.ok_cancel, 'ok', 'question'),
                           (tk.dialog.retry_cancel, 'retry', 'warning')]:
        with fake_tcl_command('tk_messageBox', {
                '-type': ok + 'cancel',
                '-icon': icon,
                '-message': 'a'}, ok):
            assert func('a') is True

        with fake_tcl_command('tk_messageBox', {
                '-type': ok + 'cancel',
                '-icon': icon,
                '-message': 'a'}, 'cancel'):
            assert func('a') is False

    for string, boolean in [('yes', True), ('no', False)]:
        with fake_tcl_command('tk_messageBox', {
                '-type': 'yesno',
                '-icon': 'question',
                '-message': 'a'}, string):
            assert tk.dialog.yes_no('a') is boolean

    for function_name, icon in [('yes_no_cancel', 'question'),
                                ('abort_retry_ignore', 'error')]:
        for answer in function_name.split('_'):
            with fake_tcl_command('tk_messageBox', {
                    '-type': function_name.replace('_', ''),
                    '-icon': icon,
                    '-message': 'a'}, answer):
                assert getattr(tk.dialog, function_name)('a') == answer


def test_color():
    with fake_tcl_command('tk_chooseColor', {}, '#ffffff'):
        assert tk.dialog.color() == tk.Color('white')

    window = tk.Window()
    expected_kwargs = {
        '-title': 'toot',
        '-initialcolor': tk.Color('maroon').to_tcl(),
        '-parent': window.toplevel.to_tcl(),
    }
    with fake_tcl_command('tk_chooseColor', expected_kwargs, '#ffffff'):
        assert tk.dialog.color(
            initialcolor=tk.Color('maroon'),
            parent=window,
            title='toot',
        ) == tk.Color('white')

    with fake_tcl_command('tk_chooseColor', {}, ''):
        assert tk.dialog.color() is None
