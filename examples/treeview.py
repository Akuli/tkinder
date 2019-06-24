import teek

root = teek.Window()
root.on_delete_window.connect(teek.quit)

treeview = teek.Treeview(
    root,
    columns=[
        teek.TreeviewColumn(text='a', anchor='e'),
        'b'
    ],
    rows=[
        teek.TreeviewRow(values=(1, 2, 3, 4)),
        (5, 6, 7, 8)
    ]
)
treeview.pack()

treeview.columns.append(teek.TreeviewColumn(text='c', anchor='w'))
treeview.columns.append('d')

treeview.columns[1].config['command'].connect(lambda: print('click'))

treeview.rows.append(teek.TreeviewRow(values=(9, 10, 11, 12)))
treeview.rows.append([13, 14, 15, 16])

treeview.rows[0].config['text'] = 'text'

teek.run()
