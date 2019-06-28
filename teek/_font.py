import itertools

import teek
from teek._tcl_calls import to_tcl

flatten = itertools.chain.from_iterable


def _font_property(type_spec, option):

    def getter(self):
        return teek.tcl_call(type_spec, "font", "actual", self, "-" + option)

    def setter(self, value):
        if not isinstance(self, NamedFont):
            raise AttributeError(
                "cannot change options of non-named fonts, but you can use "
                "the_font.to_named_font() to create a mutable font object")
        teek.tcl_call(None, "font", "configure", self, "-" + option, value)

    return property(getter, setter)


def _anonymous_font_new_helper(font_description):
    # magic: Font(a_font_name) returns a NamedFont
    # is the font description a font name? configure works only with
    # font names, not other kinds of font descriptions
    try:
        teek.tcl_call(None, 'font', 'configure', font_description)
    except teek.TclError:
        return None

    # it is a font name
    return NamedFont(font_description)


class Font:
    """Represents an anonymous font.

    Creating a :class:`.Font` object with a valid font name as an argument
    returns a :class:`.NamedFont` object. For example:

    >>> teek.Font('Helvetica 12')  # not a font name
    Font('Helvetica 12')
    >>> teek.Font('TkFixedFont')   # special font name for default monospace \
font
    NamedFont('TkFixedFont')
    >>> teek.NamedFont('TkFixedFont')    # does the same thing
    NamedFont('TkFixedFont')

    .. attribute:: family
                   size
                   weight
                   slant
                   underline
                   overstrike

        See :man:`font(3tk)` for a description of each attribute. ``size`` is
        an integer, ``underline`` and ``overstrike`` are bools, and other
        attributes are strings. You can set values to these attributes only
        with :class:`.NamedFont`.

        The values of these attributes are looked up with ``font actual`` in
        :man:`font(3tk)`, so they might differ from the values passed to
        ``Font()``. For example, the ``'Helvetica'`` family can meany any
        Helvetica-like font, so this line of code gives different values
        platform-specifically:

        >>> teek.Font('Helvetica 12').family     # doctest: +SKIP
        'Nimbus Sans L'
    """

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, NamedFont):     # Font, but not NamedFont
            named_font = _anonymous_font_new_helper(*args, **kwargs)
            if named_font is not None:
                return named_font

        return super(Font, cls).__new__(cls)

    def __init__(self, font_description):
        # the _font_description of NamedFont is the font name
        self._font_description = font_description

    family = _font_property(str, 'family')
    size = _font_property(int, 'size')
    weight = _font_property(str, 'weight')
    slant = _font_property(str, 'slant')
    underline = _font_property(bool, 'underline')
    overstrike = _font_property(bool, 'overstrike')

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self._font_description)

    def __eq__(self, other):
        if not isinstance(other, Font):
            return False
        return self._font_description == other._font_description

    def __hash__(self):
        return hash(self._font_description)

    @classmethod
    def from_tcl(cls, font_description):
        """
        ``Font.from_tcl(font_description)`` returns ``Font(font_description)``.

        This is just for compatibility with
        :ref:`type specifications <type-spec>`.
        """
        return cls(font_description)

    def to_tcl(self):
        """
        Returns the font description passed to ``Font(font_description)``.
        """
        return to_tcl(self._font_description)

    def measure(self, text):
        """
        Calls ``font measure`` documented in :man:`font(3tk)`, and returns an
        integer.
        """
        return teek.tcl_call(int, "font", "measure", self, text)

    def metrics(self):
        """
        Calls ``font metrics`` documented in :man:`font(3tk)`, and returns
        a dictionary that has at least the following keys:

        * The values of ``'ascent'``, ``'descent'`` and ``'linespace'`` are
          integers.
        * The value of ``'fixed'`` is True or False.
        """
        result = teek.tcl_call(
            {"-ascent": int, "-descent": int,
             "-linespace": int, "-fixed": bool},
            "font", "metrics", self)
        return {name.lstrip('-'): value for name, value in result.items()}

    def to_named_font(self):
        """Returns a :class:`.NamedFont` object created from this font.

        If this font is already a :class:`.NamedFont`, a copy of it is created
        and returned.
        """
        options = teek.tcl_call({}, 'font', 'actual', self)
        kwargs = {name.lstrip('-'): value for name, value in options.items()}
        return NamedFont(**kwargs)

    @classmethod
    def families(self, *, allow_at_prefix=False):
        """Returns a list of font families as strings.

        On Windows, some font families start with ``'@'``. I don't know what
        those families are and how they might be useful, but most of the time
        tkinter users (including me) ignore those, so this method ignores them
        by default. Pass ``allow_at_prefix=True`` to get a list that includes
        the ``'@'`` fonts.
        """
        result = teek.tcl_call([str], "font", "families")
        if allow_at_prefix:
            return result
        return [family for family in result if not family.startswith('@')]


class NamedFont(Font):
    """A font that has a name in Tcl.

    :class:`.NamedFont` is a subclass of :class:`.Font`; that is, all
    NamedFonts are Fonts, but not all Fonts are NamedFonts:

    >>> isinstance(teek.NamedFont('toot'), teek.Font)
    True
    >>> isinstance(teek.Font('Helvetica 12'), teek.NamedFont)
    False

    If ``name`` is not given, Tk will choose a font name that is not in use
    yet. If ``name`` is given, it can be a name of an existing font, but if a
    font with the given name doesn't exist, it'll be created instead.

    The ``kwargs`` are values for ``family``, ``size``, ``weight``, ``slant``,
    ``underline`` and ``overstrike`` attributes. For example, this...
    ::

        shouting_font = teek.NamedFont(size=30, weight='bold')

    ...does the same thing as this::

        shouting_font = teek.NamedFont()
        shouting_font.size = 30
        shouting_font.weight = 'bold'
    """

    def __init__(self, name=None, **kwargs):
        options_with_dashes = []
        for option_name, value in kwargs.items():
            options_with_dashes.extend(['-' + option_name, value])

        if name is None:
            # let tk choose a name that's not used yet
            name = teek.tcl_call(str, 'font', 'create', *options_with_dashes)
        else:
            # do we need to create a font with the given name?
            try:
                teek.tcl_call(None, 'font', 'create', name,
                              *options_with_dashes)
            except teek.TclError:
                # no, it exists already, but we must do something with the
                # options
                teek.tcl_call(None, 'font', 'configure', name,
                              *options_with_dashes)

        super().__init__(name)

    # __repr__, __eq__, __hash__, and event to_named_font, {from,to}_tcl are
    # fine, to_named_font creates a copy of this font

    # TODO: rename this less verbosely if it's possible while keeping the
    #       meaning obvious
    @classmethod
    def get_all_named_fonts(cls):
        """Returns a list of all :class:`.NamedFont` objects."""
        return list(map(cls, teek.tcl_call([str], 'font', 'names')))

    def delete(self):
        """Calls ``font delete``.

        The font object is useless after this, and most things will raise
        :exc:`.TclError`.
        """
        teek.tcl_call(None, "font", "delete", self)
