.. _widgets:

Widget Reference
================

This is a big list of widgets and explanations of what they do. As usual, don't
try to read all of it, unless you're very bored; it's best to find what you're
looking for, and ignore rest of this.

.. toctree::
    :hidden:

    canvas
    menu
    notebook
    treeview
    textwidget

.. autoclass:: teek.Widget
    :members: from_tcl, to_tcl, destroy, focus, winfo_exists, winfo_children, winfo_toplevel, winfo_width, winfo_height, winfo_reqwidth, winfo_reqheight, winfo_x, winfo_y, winfo_rootx, winfo_rooty, winfo_id

.. autoclass:: teek.Button
    :members:

.. class:: teek.Canvas
    :noindex:

    See :ref:`canvaswidget`.

.. autoclass:: teek.Checkbutton
    :members:
.. autoclass:: teek.Combobox
    :members:
.. autoclass:: teek.Entry
    :members:
.. autoclass:: teek.Frame
    :members:
.. autoclass:: teek.Label
    :members:
.. autoclass:: teek.LabelFrame
    :members:

.. class:: teek.Menu
    :noindex:

    See :ref:`menu`.

.. class:: teek.Notebook
    :noindex:

    See :ref:`notebook`.

.. class:: teek.Treeview
    :noindex:

    See :ref:`treeview`.

.. autoclass:: teek.Progressbar
    :members:
.. autoclass:: teek.Scrollbar
    :members:
.. autoclass:: teek.Separator
    :members:
.. autoclass:: teek.Spinbox
    :members:

.. class:: teek.Text
    :noindex:

    See :ref:`textwidget`.

.. autoclass:: teek.Toplevel
    :members:
.. autoclass:: teek.Window
    :members:
