import teek

root = teek.Window()
root.on_delete_window.connect(teek.quit)

treeview = teek.Treeview(root)
treeview.pack()

treeview.columns.append(teek.TreeviewColumn(text='a', anchor='e'))
treeview.columns.append('b')

treeview.columns[1].config['command'].connect(lambda: print('click'))

treeview.rows.append(teek.TreeviewRow(values=(1, 2)))
treeview.rows.append([3, 4])

treeview.rows[0].config['text'] = 'text'

teek.run()
