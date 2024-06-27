"""
Usage information for QtConsole
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.


gui_reference = """\
=====================
The Jupyter QtConsole
=====================

This console is designed to emulate the look, feel and workflow of a terminal
environment. Beyond this basic design, the console also implements
functionality not currently found in most terminal emulators. Some examples of
these console enhancements are inline syntax highlighting, multiline editing,
inline graphics, and others.

This quick reference document contains the basic information you'll need to
know to make the most efficient use of it.  For the various command line
options available at startup, type ``jupyter qtconsole --help`` at the command
line.


Multiline editing
=================

The graphical console is capable of true multiline editing, but it also tries
to behave intuitively like a terminal when possible.  If you are used to
IPython's old terminal behavior, you should find the transition painless. If
you learn to use a few basic keybindings, the console provides even greater
efficiency.

For single expressions or indented blocks, the console behaves almost like the
IPython terminal: single expressions are immediately evaluated, and indented
blocks are evaluated once a single blank line is entered::

    In [1]: print ("Hello Jupyter!")  # Enter was pressed at the end of the line
    Hello Jupyter!

    In [2]: for num in range(10):
       ...:     print(num)
       ...:
    0 1 2 3 4 5 6 7 8 9

If you want to enter more than one expression in a single input block
(something not possible in the terminal), you can use ``Control-Enter`` at the
end of your first line instead of ``Enter``.  At that point the console goes
into 'cell mode' and even if your inputs are not indented, it will continue
accepting lines until either you enter an extra blank line or
you hit ``Shift-Enter`` (the key binding that forces execution).  When a
multiline cell is entered, the console analyzes it and executes its code producing
an ``Out[n]`` prompt only for the last expression in it, while the rest of the
cell is executed as if it was a script.  An example should clarify this::

    In [3]: x=1  # Hit Ctrl-Enter here
       ...: y=2  # from now on, regular Enter is sufficient
       ...: z=3
       ...: x**2  # This does *not* produce an Out[] value
       ...: x+y+z  # Only the last expression does
       ...:
    Out[3]: 6

The behavior where an extra blank line forces execution is only active if you
are actually typing at the keyboard each line, and is meant to make it mimic
the IPython terminal behavior.  If you paste a long chunk of input (for example
a long script copied form an editor or web browser), it can contain arbitrarily
many intermediate blank lines and they won't cause any problems.  As always,
you can then make it execute by appending a blank line *at the end* or hitting
``Shift-Enter`` anywhere within the cell.

With the up arrow key, you can retrieve previous blocks of input that contain
multiple lines.  You can move inside of a multiline cell like you would in any
text editor.  When you want it executed, the simplest thing to do is to hit the
force execution key, ``Shift-Enter`` (though you can also navigate to the end
and append a blank line by using ``Enter`` twice).

If you are editing a multiline cell and accidentally navigate out of it using the
up or down arrow keys, the console clears the cell and replaces it with the
contents of the cell which the up or down arrow key stopped on.  If you wish to
to undo this action,  perhaps because of an accidental keypress, use the Undo
keybinding, ``Control-z``, to restore the original cell.


Key bindings
============

The Jupyter QtConsole supports most of the basic Emacs line-oriented keybindings,
in addition to some of its own.

The keybindings themselves are:

- ``Enter``: insert new line (may cause execution, see above).
- ``Ctrl-Enter``: *force* new line, *never* causes execution.
- ``Shift-Enter``: *force* execution regardless of where cursor is, no newline added.
- ``Up``: step backwards through the history.
- ``Down``: step forwards through the history.
- ``Shift-Up``: search backwards through the history (like ``Control-r`` in bash).
- ``Shift-Down``: search forwards through the history.
- ``Control-c``: copy highlighted text to clipboard (prompts are automatically stripped).
- ``Control-Shift-c``: copy highlighted text to clipboard (prompts are not stripped).
- ``Control-v``: paste text from clipboard.
- ``Control-z``: undo (retrieves lost text if you move out of a cell with the arrows).
- ``Control-Shift-z``: redo.
- ``Control-o``: move to 'other' area, between pager and terminal.
- ``Control-l``: clear terminal.
- ``Control-a``: go to beginning of line.
- ``Control-e``: go to end of line.
- ``Control-u``: kill from cursor to the begining of the line.
- ``Control-k``: kill from cursor to the end of the line.
- ``Control-y``: yank (paste)
- ``Control-p``: previous line (like up arrow)
- ``Control-n``: next line (like down arrow)
- ``Control-f``: forward (like right arrow)
- ``Control-b``: back (like left arrow)
- ``Control-d``: delete next character, or exits if input is empty
- ``Alt-<``: move to the beginning of the input region.
- ``alt->``: move to the end of the input region.
- ``Alt-d``: delete next word.
- ``Alt-Backspace``: delete previous word.
- ``Control-.``: force a kernel restart (a confirmation dialog appears).
- ``Control-+``: increase font size.
- ``Control--``: decrease font size.
- ``Control-Alt-Space``: toggle full screen. (Command-Control-Space on Mac OS X)

The pager
=========

The Jupyter QtConsole will show long blocks of text from many sources using a
built-in pager. You can control where this pager appears with the ``--paging``
command-line flag:

- ``inside`` [default]: the pager is overlaid on top of the main terminal. You
  must quit the pager to get back to the terminal (similar to how a pager such
  as ``less`` or ``more`` pagers behave).

- ``vsplit``: the console is made double height, and the pager appears on the
  bottom area when needed.  You can view its contents while using the terminal.

- ``hsplit``: the console is made double width, and the pager appears on the
  right area when needed.  You can view its contents while using the terminal.

- ``none``: the console displays output without paging.

If you use the vertical or horizontal paging modes, you can navigate between
terminal and pager as follows:

- Tab key: goes from pager to terminal (but not the other way around).
- Control-o: goes from one to another always.
- Mouse: click on either.

In all cases, the ``q`` or ``Escape`` keys quit the pager (when used with the
focus on the pager area).

Running subprocesses
====================

When running a subprocess from the kernel, you can not interact with it as if
it was running in a terminal.  So anything that invokes a pager or expects
you to type input into it will block and hang (you can kill it with ``Control-C``).

The console can use magics provided by the IPython kernel. These magics include
``%less`` to page files (aliased to ``%more``),
``%clear`` to clear the terminal, and ``%man`` on Linux/OSX.  These cover the
most common commands you'd want to call in your subshell and that would cause
problems if invoked via ``!cmd``, but you need to be aware of this limitation.

Display
=======

For example, if using the IPython kernel, there are functions available for
object display:


    In [4]: from IPython.display import display

    In [5]: from IPython.display import display_png, display_svg

Python objects can simply be passed to these functions and the appropriate
representations will be displayed in the console as long as the objects know
how to compute those representations. The easiest way of teaching objects how
to format themselves in various representations is to define special methods
such as: ``_repr_svg_`` and ``_repr_png_``. IPython's display formatters
can also be given custom formatter functions for various types::

    In [6]: ip = get_ipython()

    In [7]: png_formatter = ip.display_formatter.formatters['image/png']

    In [8]: png_formatter.for_type(Foo, foo_to_png)

For further details, see ``IPython.core.formatters``.
"""
