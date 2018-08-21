from ._tcl_calls import call as tcl_call, to_tcl
from . import TclError


def _dict2options(dict_):
    tcl_options = []
    for k, v in dict_.items():
        tcl_options.append("-" + k)
        tcl_options.append(to_tcl(v))
    return tcl_options


def _options2dict(options):
    return {k.lstrip("-"): v for k, v in options.items()}


def _font_property(attribute):
    def fget(self):
        if self.name is None:
            return self._description[attribute]
        else:
            ty = self._OPTIONS_TYPE["-" + attribute]
            return tcl_call(ty, "font", "configure", self.name, "-" + attribute)

    def fset(self, value):
        if self.name is None:
            raise RuntimeError("You can't change an AnonymousFont's properties.")
        else:
            tcl_call(None, "font", "configure", self.name, "-" + attribute, value)

    return property(fget, fset)


class AnonymousFont:
    # XXX: Akuli, please add docs.
    _OPTIONS_TYPE = {
        "-family": str,
        "-size": int,
        "-weight": str,
        "-slant": str,
        "-underline": bool,
        "-overstrike": bool,
    }

    def __init__(self, **description):
        if description:
            options = _dict2options(description)
            description = tcl_call(
                self._OPTIONS_TYPE, "font", "actual", options
            )
        else:
            description = tcl_call(
                self._OPTIONS_TYPE, "font", "actual", "TkDefaultFont"
            )

        self.name = None
        self._description = _options2dict(description)

    family = _font_property("family")
    size = _font_property("size")
    weight = _font_property("weight")
    slant = _font_property("slant")
    underline = _font_property("underline")
    overstrike = _font_property("overstrike")

    def actual(self):
        if self.name is None:
            return self._description
        else:
            actual = tcl_call(self._OPTIONS_TYPE, "font", "actual", self.name)
            return _options2dict(actual)

    def delete(self):
        if self.name is None:
            raise RuntimeError("Can't delete an AnonymousFont!")

        tcl_call(None, "font", "delete", self.name)

    def measure(self, text):
        if self.name is None:
            return tcl_call(
                int, "font", "measure", _dict2options(self._description), text
            )
        else:
            return tcl_call(int, "font", "measure", self.name, text)

    def metrics(self):
        ty = {"ascent": int, "descent": int, "linespace": int, "fixed": bool}
        if self.name is None:
            return tcl_call(ty, "font", "metrics", self.name)
        else:
            return tcl_call(
                ty, "font", "metrics", _dict2options(self._description)
            )

    @classmethod
    def families(self):
        return tcl_call([str], "font", "families")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           ", ".join("%s=%r" % key, value
                                     for key, value in self._description))

    def __eq__(self, other):
        return self._description == other._description

    @classmethod
    def from_tcl(cls, data):
        options = tcl_call(cls._OPTIONS_TYPE, "font", "actual", data)
        return cls(**_options2dict(options))

    def to_tcl(self):
        return _dict2options(self._description)


class NamedFont(AnonymousFont):
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if name is None:
            options = _dict2options(self._description)
            self.name = tcl_call(str, "font", "create", *options)
        else:
            self.name = name
            options = _dict2options(self._description)
            try:
                tcl_call(str, "font", "create", name, *options)
            except TclError:
                # font already exists
                pass

    @classmethod
    def names(self):
        return tcl_call([str], "font", "names")

    @classmethod
    def from_tcl(cls, data):
        if data in cls.names():
            return cls(data)
        else:
            return super().from_tcl(data)

    def to_tcl(self):
        return self.name

    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)

    def __eq__(self, other):
        return self.name == other.name
