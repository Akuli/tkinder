import pytest

import teek


def test_reprs():
    values = ['a']
    treeview = teek.Treeview(teek.Window())
    col = teek.TreeviewColumn('testcol', text='Test')
    row = teek.TreeviewRow('testrow', text='Row', values=values)

    assert repr(col) == "TreeviewColumn('testcol', not added to treeview)"
    assert repr(row) == "TreeviewRow('testrow', not added to treeview)"
    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 0 rows>'
    treeview.rows.append(row)
    assert repr(row) == "TreeviewRow('testrow', text='Row', values=" \
                        + repr(values) + ")"
    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 1 rows>'
    treeview.columns.append(col)
    assert repr(col) == "TreeviewColumn('testcol', text='Test')"
    assert repr(treeview) == '<teek.Treeview widget: contains 2 columns ' \
                             '& 1 rows>'


def test_multi_handler_config_dict():
    def success_handler(rettype, option, value=None):
        return 'success1'

    def success2_handler(rettype, option, value=None):
        return 'success2'

    def generic_handler(rettype, option, value=None):
        return 'generic'

    config = teek._widgets.treeview.MultiHandlerConfigDict()
    config._types['test'] = str
    config._types['generic'] = str
    config._handlers['test'] = success_handler
    config._handlers['*'] = generic_handler

    assert config['test'] == 'success1'
    assert config['generic'] == 'generic'
    config._handlers['test'] = [success_handler, success2_handler]
    assert config['test'] == 'success1'


def test_treeview_columns_creation():
    treeview = teek.Treeview(teek.Window(), columns=[
        'a',
        teek.TreeviewColumn(text='b')
    ])

    treeview.columns.append('c')
    treeview.columns.append(teek.TreeviewColumn(text='d'))
    assert len(treeview.columns) == 5
    assert treeview.columns[1].config['text'] == 'a'
    assert treeview.columns[2].config['text'] == 'b'
    assert treeview.columns[3].config['text'] == 'c'
    assert treeview.columns[4].config['text'] == 'd'


def test_treeview_rows_creation():
    treeview = teek.Treeview(teek.Window(), rows=[
        [1, 2],
        teek.TreeviewRow(values=[3, 4])
    ])

    treeview.rows.append(['5', '6'])
    treeview.rows.append(teek.TreeviewRow(values=[7, '8']))
    assert len(treeview.rows) == 4
    assert treeview.rows[0].config['values'] == ['1', '2']
    assert treeview.rows[1].config['values'] == ['3', '4']
    assert treeview.rows[2].config['values'] == ['5', '6']
    assert treeview.rows[3].config['values'] == ['7', '8']


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
    treeview.columns[2] = 'd'
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
    treeview.rows[0] = teek.TreeviewRow(values=['3'])
    treeview.rows[1] = ['4']
    assert len(treeview.rows) == 2
    assert treeview.rows[0].config['values'] == ['3']
    assert treeview.rows[1].config['values'] == ['4']
    del treeview.rows[0]
    assert len(treeview.rows) == 1
    assert treeview.rows[0].config['values'] == ['4']


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


def test_treeview_scroll():
    treeview = teek.Treeview(teek.Window())

    assert treeview.xview() == (0.0, 1.0)
    assert treeview.yview() == (0.0, 1.0)
    treeview.xview('moveto', 0.5)
    treeview.yview('moveto', 0.5)
