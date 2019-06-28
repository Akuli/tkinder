import pytest

import teek
from teek._tcl_calls import to_tcl


def get_test_family():
    """Get font family with actual size equal to given size
    """
    for family in teek.Font.families():
        font = teek.Font((family, 42))

        if font.size == 42:
            return family

    return teek.Font.families()[0]


def test_font_magic_new_method():
    font = teek.Font('a_font_with_this_name_does_not_exist')
    assert isinstance(font, teek.Font)
    assert not isinstance(font, teek.NamedFont)

    teek.tcl_eval(None, 'font create test_font_name')
    named_font = teek.Font('test_font_name')
    assert isinstance(named_font, teek.NamedFont)
    named_font.delete()


def test_repr_eq_hash():
    font_family = get_test_family()
    font = teek.Font((font_family, 12))
    named_font = teek.NamedFont('asda')
    assert repr(font) == "Font(('%s', 12))" % font_family
    assert repr(named_font) == "NamedFont('asda')"

    another_named_font = teek.NamedFont('asda')
    assert named_font == another_named_font
    assert {named_font: 'toot'}[another_named_font] == 'toot'

    def all_names():
        return (font.to_tcl()
                for font in teek.NamedFont.get_all_named_fonts())

    assert 'asda' in all_names()
    named_font.delete()
    assert 'asda' not in all_names()

    assert font != 'toot'
    assert named_font != 'toot'


def test_from_and_to_tcl():
    description = [get_test_family(), 42, 'bold']
    descriptiony_font = teek.Font(description)
    assert descriptiony_font.to_tcl() == to_tcl(description)
    assert teek.Font.from_tcl(description) == descriptiony_font

    teek.tcl_eval(None, 'font create test_font_name')
    named_font = teek.NamedFont.from_tcl('test_font_name')
    assert isinstance(named_font, teek.NamedFont)
    assert named_font.to_tcl() == 'test_font_name'
    named_font.delete()


def test_properties():
    font_family = get_test_family()
    anonymous_font = teek.Font((font_family, 42, 'bold', 'underline'))
    named_font = teek.NamedFont(
        family=font_family, size=42, weight='bold', underline=True)

    # just to make debugging easier because these facts are needed below
    assert not isinstance(anonymous_font, teek.NamedFont)
    assert isinstance(named_font, teek.NamedFont)

    for font in [anonymous_font, named_font]:
        assert font.size == 42
        assert font.weight == 'bold'
        assert font.slant == 'roman'
        assert font.underline is True
        assert font.overstrike is False

        # the actual properties might differ from the font specification, e.g.
        # "Helvetica" is "Nimbus Sans L" on my system
        assert isinstance(font.family, str)

    # test setting error
    with pytest.raises(AttributeError) as error:
        anonymous_font.weight = 'normal'
    assert '.to_named_font()' in str(error.value)

    # test successful setting
    assert named_font.underline is True
    named_font.underline = False
    assert named_font.underline is False

    assert not hasattr(anonymous_font, 'delete')
    named_font.delete()


def test_measure():
    assert teek.Font((get_test_family(), 42, 'bold')).measure('') == 0


def test_metrics():
    metrics = teek.Font((get_test_family(), 42, 'bold')).metrics()
    assert isinstance(metrics['ascent'], int)
    assert isinstance(metrics['descent'], int)
    assert isinstance(metrics['linespace'], int)
    assert isinstance(metrics['fixed'], bool)


def test_families():
    for at in [True, False]:
        families = teek.Font.families(allow_at_prefix=at)
        assert isinstance(families, list)
        assert families
        for family in families:
            assert isinstance(family, str)
            if not at:
                assert not family.startswith('@')

        # default should be False
        if not at:
            assert set(teek.Font.families()) == set(families)


def fonts_are_similar(font1, font2):
    return (font1.family == font2.family and
            font1.size == font2.size and
            font1.weight == font2.weight and
            font1.slant == font2.slant and
            font1.underline is font2.underline and
            font1.overstrike is font2.overstrike)


def test_to_named_font():
    anonymous = teek.Font((get_test_family(), 42))
    named = anonymous.to_named_font()
    assert isinstance(named, teek.NamedFont)
    assert fonts_are_similar(anonymous, named)

    named2 = named.to_named_font()      # creates a copy
    assert isinstance(named2, teek.NamedFont)
    assert named != named2      # it is a copy
    assert fonts_are_similar(named, named2)

    named2.size = 18
    assert named.size != named2.size
    named2.size = 42
    assert fonts_are_similar(named, named2)

    named.delete()
    named2.delete()


def test_special_font_names():
    assert isinstance(teek.Font('TkFixedFont'), teek.NamedFont)
    assert isinstance(teek.Font.from_tcl('TkFixedFont'), teek.NamedFont)
