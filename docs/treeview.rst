.. _treeview:

Treeview Widget
===============

**Manual page:** :man:`ttk_treeview(3tk)`

This widget is useful for creating tabular lists or tree structures.
Let's look at an example.

::

    import teek

    window = teek.Window('Treeview Example')
    treeview = teek.Treeview(window)
    treeview.pack(fill='both', expand=True)

    treeview.columns.append('forename')
    treeview.columns.append('surname')
    treeview.columns.append('age')

    treeview.rows.append(['John', 'Star', 32])
    treeview.rows.append(['Patrick', 'Tram', 19])

    window.geometry(300, 200)
    window.on_delete_window.connect(teek.quit)
    teek.run()

This program displays a treeview widget with overall 4 columns (first + value 
columns) and 2 rows. The first column is for description purposes only and 
cannot contain any data. Let's go trough some of the code.

::

    treeview.columns.append('forename')

This line creates a :class:`.TreeviewColumn` with the title *forename* and 
appends it to the column list of the treeview.

::

    treeview.rows.append(['John', 'Star', 32])

This code creates a :class:`.TreeviewRow` with the given values (1. column: 
*John*, 2. column: *Star*, 3. column: *32*) and appends it to the rows of the 
treeview.

The *rows* and *columns* attributes of the :class:`.Treeview` behave like normal
 lists and therefore, items can be inserted and deleted as with lists. The only 
exceptions are considering the direct setting of rows (*__setitem__*) and the 
manipulation of the first column which are both prohibited. 

Here is some reference:

.. autoclass:: teek.Treeview
    :members:
.. autoclass:: teek.TreeviewColumn
    :members:
.. autoclass:: teek.TreeviewRow
    :members:
