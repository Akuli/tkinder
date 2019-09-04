import teek


class _TooltipManager:

    # This needs to be shared by all instances because there's only one
    # mouse pointer.
    tipwindow = None

    def __init__(self, widget: teek.Widget):
        widget.bind('<Enter>', self.enter, event=True)
        widget.bind('<Leave>', self.leave, event=True)
        widget.bind('<Motion>', self.motion, event=True)
        self.widget = widget
        self.got_mouse = False
        self.text = None

    @classmethod
    def destroy_tipwindow(cls):
        if cls.tipwindow is not None:
            cls.tipwindow.destroy()
            cls.tipwindow = None

    def enter(self, event):
        # For some reason, toplevels get also notified of their
        # childrens' events.
        if event.widget is self.widget:
            self.destroy_tipwindow()
            self.got_mouse = True
            teek.after(1000, self.show)

            # these are important, it's possible to enter without mouse move
            self.mousex = event.rootx
            self.mousey = event.rooty

    def leave(self, event):
        if event.widget is self.widget:
            self.destroy_tipwindow()
            self.got_mouse = False

    def motion(self, event):
        self.mousex = event.rootx
        self.mousey = event.rooty

    def show(self):
        if not self.got_mouse:
            return

        self.destroy_tipwindow()
        if self.text is not None:
            # the label and the tipwindow are not ttk widgets because that way
            # they can look different than other widgets, which is what
            # tooltips are usually like
            tipwindow = type(self).tipwindow = teek.Toplevel()
            tipwindow.geometry(x=(self.mousex + 10), y=(self.mousey - 10))
            tipwindow.bind('<Motion>', self.destroy_tipwindow)

            # TODO: add overrideredirect to teek
            teek.tcl_call(None, 'wm', 'overrideredirect', tipwindow, 1)

            # i don't think there's a need to add better support for things
            # like non-ttk labels because they are not needed very often
            #
            # refactoring note: if you change this, make sure that either BOTH
            # of fg and bg are set, or NEITHER is set, because e.g. bg='white'
            # with no fg gives white text on white background on systems with
            # white default foreground, but works fine on systems with black
            # default foreground
            label = teek.tcl_call(str, 'label', tipwindow.to_tcl() + '.label',
                                  '-text', self.text, '-bd', 1, '-relief',
                                  'solid', '-fg', 'black', '-bg', '#ffc',
                                  '-padx', 2, '-pady', 2)
            teek.tcl_call(None, 'pack', label)


def set_tooltip(widget, text):
    """Create tooltips for a widget.

    After calling ``set_tooltip(some_widget, "hello")``, "hello" will be
    displayed in a small window when the user moves the mouse over the
    widget and waits for a small period of time. Do
    ``set_tooltip(some_widget, None)`` to get rid of a tooltip.
    """
    if text is None:
        if hasattr(widget, '_tooltip_manager'):
            widget._tooltip_manager.text = None
    else:
        if not hasattr(widget, '_tooltip_manager'):
            widget._tooltip_manager = _TooltipManager(widget)
        widget._tooltip_manager.text = text
