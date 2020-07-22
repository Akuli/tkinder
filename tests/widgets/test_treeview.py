import pytest

import teek


def test_option_config_dict():
    args = []
    cfg_dict = teek._widgets.treeview.OptionConfigDict(
        lambda *a: args.extend(a)
    )

    args = []
    cfg_dict._set('option', 'value')
    assert args == [None, '-option', 'value']

    args = []
    cfg_dict._get('option')
    assert args == [str, '-option']

    cfg_dict._caller_func = lambda *a: ['-option', 'value']
    assert list(cfg_dict._list_options()) == ['option']


def test_reprs():
    values = ['a']
    treeview = teek.Treeview(teek.Window())
    col = teek.TreeviewColumn('testcol', text='Test')
    not_added_col = teek.TreeviewColumn()
    row_root = teek.TreeviewRow('root', text='Root', values=values)
    row_sub = teek.TreeviewRow('sub', text='Sub')

    assert repr(col) == 'TreeviewColumn(testcol, not added to treeview)'
    assert repr(row_root) == 'TreeviewRow(root, not added to treeview)'
    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 0 rows>'
    treeview.rows.append(row_root)
    assert repr(row_root) == "TreeviewRow(root, text='Root', values=" \
                             + repr(values) + ', subrows=0)'
    assert repr(treeview) == '<teek.Treeview widget: contains 1 columns ' \
                             '& 1 rows>'
    assert repr(treeview.rows) == 'TreeviewRowList(root=None, rows=1)'
    assert repr(treeview.columns) == 'TreeviewColumnList(columns=1)'
    treeview.rows[0].subrows.append(row_sub)
    assert repr(row_sub) == "TreeviewRow(sub, text='Sub', values=[], " \
                            'subrows=0)'
    assert repr(row_root) == "TreeviewRow(root, text='Root', values=['a'], " \
                             'subrows=1)'
    treeview.columns.append(col)
    assert repr(col) == "TreeviewColumn(testcol, text='Test')"
    assert repr(treeview) == '<teek.Treeview widget: contains 2 columns ' \
                             '& 1 rows>'

    assert repr(not_added_col.heading) == 'TreeviewColumnHeading(not added ' \
                                          'to treeview)'
    assert repr(col.heading) == "TreeviewColumnHeading(text='Test')"


def test_compare():
    assert teek.TreeviewColumn('a') == teek.TreeviewColumn('a')
    assert teek.TreeviewRow('b') == teek.TreeviewRow('b')


def test_treeview_columns_creation():
    treeview = teek.Treeview(teek.Window(), columns=[
        'a',
        teek.TreeviewColumn(text='b')
    ])

    treeview.columns.append('c')
    treeview.columns.append(teek.TreeviewColumn(
        text='d',
        anchor='w',
        minwidth=100,
        width=120,
        stretch=True
    ))
    treeview.columns[3].heading.config['command'].connect(print)
    treeview.columns[3].heading.config['anchor'] = 'w'

    assert len(treeview.columns) == 5
    assert treeview.columns[1].heading.config['text'] == 'a'
    assert treeview.columns[2].heading.config['text'] == 'b'
    assert treeview.columns[3].heading.config['text'] == 'c'
    assert treeview.columns[4].heading.config['text'] == 'd'


def test_treeview_rows_creation():
    treeview = teek.Treeview(teek.Window(), rows=[
        [1, 2],
        teek.TreeviewRow(values=[3, 4])
    ])

    treeview.rows.append(['5', '6'])
    treeview.rows.append(teek.TreeviewRow(values=[7, '8']))
    treeview.rows[2].subrows.append(['9', '10'])
    treeview.rows[2].subrows.append(['11', '12'])

    assert len(treeview.rows) == 4
    assert treeview.rows[0].config['values'] == ['1', '2']
    assert treeview.rows[1].config['values'] == ['3', '4']
    assert treeview.rows[2].config['values'] == ['5', '6']
    assert treeview.rows[3].config['values'] == ['7', '8']
    assert len(treeview.rows[2].subrows) == 2
    assert treeview.rows[2].subrows[0].config['values'] == ['9', '10']
    assert treeview.rows[2].subrows[1].config['values'] == ['11', '12']


def test_treeview_not_added():
    row = teek.TreeviewRow()
    col = teek.TreeviewColumn()

    with pytest.raises(RuntimeError):
        row.config['values'] = ['1', '2']

    with pytest.raises(RuntimeError):
        col.config['stretch'] = True

    with pytest.raises(RuntimeError):
        col.heading.config['text'] = 'title'


def test_treeview_columns_list():
    treeview = teek.Treeview(teek.Window())

    treeview.columns.append('a')
    assert len(treeview.columns) == 2
    assert treeview.columns[1].heading.config['text'] == 'a'
    treeview.columns.insert(1, 'b')
    assert len(treeview.columns) == 3
    assert treeview.columns[1].heading.config['text'] == 'b'
    assert treeview.columns[2].heading.config['text'] == 'a'
    treeview.columns[1] = teek.TreeviewColumn(text='c')
    treeview.columns[2] = 'd'
    assert len(treeview.columns) == 3
    assert treeview.columns[1].heading.config['text'] == 'c'
    assert treeview.columns[2].heading.config['text'] == 'd'
    del treeview.columns[1]
    assert len(treeview.columns) == 2
    assert treeview.columns[1].heading.config['text'] == 'd'


def test_treeview_rows_list():
    treeview = teek.Treeview(teek.Window())

    treeview.rows.append(['1'])
    treeview.rows[0].subrows.append(['11'])

    assert len(treeview.rows) == 1
    assert len(treeview.rows[0].subrows) == 1
    assert treeview.rows[0].config['values'] == ['1']
    assert treeview.rows[0].subrows[0].config['values'] == ['11']

    treeview.rows.insert(0, ['2'])
    treeview.rows[0].subrows.insert(0, ['22'])

    assert len(treeview.rows) == 2
    assert len(treeview.rows[0].subrows) == 1
    assert len(treeview.rows[1].subrows) == 1
    assert treeview.rows[0].config['values'] == ['2']
    assert treeview.rows[1].config['values'] == ['1']
    assert treeview.rows[0].subrows[0].config['values'] == ['22']
    assert treeview.rows[1].subrows[0].config['values'] == ['11']

    treeview.rows[0] = teek.TreeviewRow(values=['3'])
    treeview.rows[1] = ['4']
    treeview.rows[0].subrows.insert(0, teek.TreeviewRow(values=['11']))
    treeview.rows[1].subrows.insert(0, ['22'])
    treeview.rows[0].subrows[0] = teek.TreeviewRow(values=['33'])
    treeview.rows[1].subrows[0] = ['44']

    assert len(treeview.rows) == 2
    assert len(treeview.rows[0].subrows) == 1
    assert len(treeview.rows[1].subrows) == 1
    assert treeview.rows[0].config['values'] == ['3']
    assert treeview.rows[1].config['values'] == ['4']
    assert treeview.rows[0].subrows[0].config['values'] == ['33']
    assert treeview.rows[1].subrows[0].config['values'] == ['44']

    del treeview.rows[0]
    del treeview.rows[0].subrows[0]

    assert len(treeview.rows) == 1
    assert len(treeview.rows[0].subrows) == 0
    assert treeview.rows[0].config['values'] == ['4']


def test_treeview_first_column():
    treeview = teek.Treeview(teek.Window())

    assert len(treeview.columns) == 1
    treeview.columns[0].heading.config['text'] = 'first'
    assert treeview.columns[0].heading.config['text'] == 'first'
    treeview.columns.append('second')
    assert len(treeview.columns) == 2

    with pytest.raises(KeyError):
        del treeview.columns[0]

    with pytest.raises(KeyError):
        treeview.columns[0] = teek.TreeviewColumn()

    with pytest.raises(KeyError):
        treeview.columns.insert(0, teek.TreeviewColumn())


def test_treeview_row_selection():
    treeview = teek.Treeview(teek.Window())
    row = teek.TreeviewRow(values=['a'])

    with pytest.raises(RuntimeError):
        row.selected

    with pytest.raises(RuntimeError):
        row.select()

    with pytest.raises(RuntimeError):
        row.deselect()

    treeview.rows.append(row)

    assert not row.selected
    row.select()
    assert row.selected
    row.deselect()
    assert not row.selected


def test_treeview_sort():
    treeview = teek.Treeview(teek.Window())
    treeview.rows.append(['b'])
    treeview.rows.append(['a'])
    treeview.rows.append(['c'])
    treeview.rows[1].subrows.append(['e'])
    treeview.rows[1].subrows.append(['d'])

    assert len(treeview.rows) == 3
    assert len(treeview.rows[1].subrows) == 2
    assert treeview.rows[0].config['values'] == ['b']
    assert treeview.rows[1].config['values'] == ['a']
    assert treeview.rows[2].config['values'] == ['c']
    assert treeview.rows[1].subrows[0].config['values'] == ['e']
    assert treeview.rows[1].subrows[1].config['values'] == ['d']

    with pytest.raises(IndexError):
        treeview.rows.sort(0)

    treeview.rows.sort(1, reverse=False)

    assert len(treeview.rows) == 3
    assert len(treeview.rows[0].subrows) == 2
    assert treeview.rows[0].config['values'] == ['a']
    assert treeview.rows[1].config['values'] == ['b']
    assert treeview.rows[2].config['values'] == ['c']
    assert treeview.rows[0].subrows[0].config['values'] == ['d']
    assert treeview.rows[0].subrows[1].config['values'] == ['e']

    treeview.rows.sort(1, reverse=True)

    assert len(treeview.rows) == 3
    assert len(treeview.rows[2].subrows) == 2
    assert treeview.rows[0].config['values'] == ['c']
    assert treeview.rows[1].config['values'] == ['b']
    assert treeview.rows[2].config['values'] == ['a']
    assert treeview.rows[2].subrows[0].config['values'] == ['e']
    assert treeview.rows[2].subrows[1].config['values'] == ['d']


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
