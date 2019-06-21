import pytest

import teek


def test_reprs():
    values = ['a']
    treeview = teek.Treeview(teek.Window())
    col = teek.TreeviewColumn('testcol', text='Test')
    row = teek.TreeviewRow('testrow', text='Row', values=values)

    assert repr(col) == "TreeviewColumn('testcol', text='Test')"
    assert repr(row) == "TreeviewRow('testrow', text='Row', values=" \
                        + repr(values) + ")"

    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 0 rows>'
    treeview.rows.append(row)
    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 1 rows>'
    treeview.columns.append(col)
    assert repr(treeview) == '<teek.Treeview widget: contains 2 columns ' \
                             '& 1 rows>'


def test_fallback_config_dict():
    def error_handler(rettype, option, value=None):
        raise RuntimeError()

    def success_handler(rettype, option, value=None):
        return 'success'

    def success2_handler(rettype, option, value=None):
        return 'success'

    config = teek._widgets.treeview.FallbackConfigDict()
    config._types['test'] = str
    config._fallbacks['test'] = ''
    config._handlers['test'] = error_handler

    with pytest.raises(KeyError):
        config['invalid']

    with pytest.raises(KeyError):
        config['invalid'] = 'test'

    assert config['test'] == ''
    config._handlers['test'] = success_handler
    assert config['test'] == 'success'
    config._handlers['test'] = [success_handler, success2_handler]
    assert config['test'] == 'success'


def test_treeview_columns_creation():
    treeview = teek.Treeview(teek.Window())

    treeview.columns.append('a')
    treeview.columns.append(teek.TreeviewColumn(text='b'))
    assert len(treeview.columns) == 3
    assert treeview.columns[1].config['text'] == 'a'
    assert treeview.columns[2].config['text'] == 'b'


def test_treeview_rows_creation():
    treeview = teek.Treeview(teek.Window())

    treeview.rows.append(['1', '2'])
    treeview.rows.append(teek.TreeviewRow(values=['3', '4']))
    assert len(treeview.rows) == 2
    assert treeview.rows[0].config['values'] == ['1', '2']
    assert treeview.rows[1].config['values'] == ['3', '4']


def test_treeview_columns_list():
    treeview = teek.Treeview(teek.Window())

    treeview.columns.append('a')
    assert len(treeview.columns) == 2
    assert treeview.columns[1].config['text'] == 'a'
    treeview.columns.insert(1, 'b')
    assert len(treeview.columns) == 3
    assert treeview.columns[1].config['text'] == 'b'
    assert treeview.columns[2].config['text'] == 'a'
    treeview.columns[1] = teek.TreeviewColumn(text='c')
    treeview.columns[2] = teek.TreeviewColumn(text='d')
    assert len(treeview.columns) == 3
    assert treeview.columns[1].config['text'] == 'c'
    assert treeview.columns[2].config['text'] == 'd'
    del treeview.columns[1]
    assert len(treeview.columns) == 2
    assert treeview.columns[1].config['text'] == 'd'


def test_treeview_rows_list():
    treeview = teek.Treeview(teek.Window())

    treeview.rows.append(['1'])
    assert len(treeview.rows) == 1
    assert treeview.rows[0].config['values'] == ['1']
    treeview.rows.insert(0, ['2'])
    assert len(treeview.rows) == 2
    assert treeview.rows[0].config['values'] == ['2']
    assert treeview.rows[1].config['values'] == ['1']
    del treeview.rows[0]
    assert len(treeview.rows) == 1
    assert treeview.rows[0].config['values'] == ['1']

    with pytest.raises(NotImplementedError):
        treeview.rows[0] = teek.TreeviewRow()


def test_treeview_first_column():
    treeview = teek.Treeview(teek.Window())

    assert len(treeview.columns) == 1
    treeview.columns[0].config['text'] = 'first'
    assert treeview.columns[0].config['text'] == 'first'
    treeview.columns.append('second')
    assert len(treeview.columns) == 2

    with pytest.raises(KeyError):
        del treeview.columns[0]

    with pytest.raises(KeyError):
        treeview.columns[0] = teek.TreeviewColumn()

    with pytest.raises(KeyError):
        treeview.columns.insert(0, teek.TreeviewColumn())


def test_treeview_rows_move():
    treeview = teek.Treeview(teek.Window())
    treeview.rows.append(['a'])
    treeview.rows.append(['b'])

    assert len(treeview.rows) == 2
    assert treeview.rows[0].config['values'] == ['a']
    assert treeview.rows[1].config['values'] == ['b']
    treeview.rows.move(1, 0)
    assert len(treeview.rows) == 2
    assert treeview.rows[0].config['values'] == ['b']
    assert treeview.rows[1].config['values'] == ['a']


def test_treeview_row_selection():
    treeview = teek.Treeview(teek.Window())
    treeview.rows.append(['a'])

    assert not treeview.rows[0].selected
    treeview.rows[0].select()
    assert treeview.rows[0].selected
    treeview.rows[0].deselect()
    assert not treeview.rows[0].selected


def test_treeview_sort():
    treeview = teek.Treeview(teek.Window())
    treeview.rows.append(['b'])
    treeview.rows.append(['a'])
    treeview.rows.append(['c'])

    assert len(treeview.rows) == 3
    assert treeview.rows[0].config['values'] == ['b']
    assert treeview.rows[1].config['values'] == ['a']
    assert treeview.rows[2].config['values'] == ['c']

    with pytest.raises(KeyError):
        treeview.sort(0)

    treeview.sort(1, reverse=False)
    assert len(treeview.rows) == 3
    assert treeview.rows[0].config['values'] == ['a']
    assert treeview.rows[1].config['values'] == ['b']
    assert treeview.rows[2].config['values'] == ['c']
    treeview.sort(1, reverse=True)
    assert len(treeview.rows) == 3
    assert treeview.rows[0].config['values'] == ['c']
    assert treeview.rows[1].config['values'] == ['b']
    assert treeview.rows[2].config['values'] == ['a']


def test_treeview_tcl():
    col = teek.TreeviewColumn('testcol')
    row = teek.TreeviewRow('testrow')

    assert col.to_tcl() == 'testcol'
    assert row.to_tcl() == 'testrow'
