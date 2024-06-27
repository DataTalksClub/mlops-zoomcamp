import os
import unittest
import sys

from flaky import flaky
import pytest

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtTest import QTest

from qtconsole.console_widget import ConsoleWidget
from qtconsole.qtconsoleapp import JupyterQtConsoleApp

from . import no_display

from IPython.core.inputtransformer2 import TransformerManager


SHELL_TIMEOUT = 20000


@pytest.fixture
def qtconsole(qtbot):
    """Qtconsole fixture."""
    # Create a console
    console = JupyterQtConsoleApp()
    console.initialize(argv=[])

    console.window.confirm_exit = False
    console.window.show()

    yield console

    console.window.close()


@flaky(max_runs=3)
@pytest.mark.parametrize(
    "debug", [True, False])
def test_scroll(qtconsole, qtbot, debug):
    """
    Make sure the scrolling works.
    """
    window = qtconsole.window
    shell = window.active_frontend
    control = shell._control
    scroll_bar = control.verticalScrollBar()

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    assert scroll_bar.value() == 0

    # Define a function with loads of output
    # Check the outputs are working as well
    code = ["import time",
            "def print_numbers():",
            "    for i in range(1000):",
            "       print(i)",
            "       time.sleep(.01)"]
    for line in code:
        qtbot.keyClicks(control, line)
        qtbot.keyClick(control, QtCore.Qt.Key_Enter)

    with qtbot.waitSignal(shell.executed):
        qtbot.keyClick(control, QtCore.Qt.Key_Enter,
                       modifier=QtCore.Qt.ShiftModifier)

    def run_line(line, block=True):
        qtbot.keyClicks(control, line)
        if block:
            with qtbot.waitSignal(shell.executed):
                qtbot.keyClick(control, QtCore.Qt.Key_Enter,
                               modifier=QtCore.Qt.ShiftModifier)
        else:
            qtbot.keyClick(control, QtCore.Qt.Key_Enter,
                               modifier=QtCore.Qt.ShiftModifier)

    if debug:
        # Enter debug
        run_line('%debug print()', block=False)
        qtbot.keyClick(control, QtCore.Qt.Key_Enter)
        # redefine run_line
        def run_line(line, block=True):
            qtbot.keyClicks(control, '!' + line)
            qtbot.keyClick(control, QtCore.Qt.Key_Enter,
                           modifier=QtCore.Qt.ShiftModifier)
            if block:
                qtbot.waitUntil(
                    lambda: control.toPlainText().strip(
                        ).split()[-1] == "ipdb>")

    prev_position = scroll_bar.value()

    # Create a bunch of inputs
    for i in range(20):
        run_line('a = 1')

    assert scroll_bar.value() > prev_position

    # Put the scroll bar higher and check it doesn't move
    prev_position = scroll_bar.value() + scroll_bar.pageStep() // 2
    scroll_bar.setValue(prev_position)

    for i in range(2):
        run_line('a')

    assert scroll_bar.value() == prev_position

    # add more input and check it moved
    for i in range(10):
        run_line('a')

    assert scroll_bar.value() > prev_position

    prev_position = scroll_bar.value()

    # Run the printing function
    run_line('print_numbers()', block=False)

    qtbot.wait(1000)

    # Check everything advances
    assert scroll_bar.value() > prev_position

    # move up
    prev_position = scroll_bar.value() - scroll_bar.pageStep()
    scroll_bar.setValue(prev_position)

    qtbot.wait(1000)

    # Check position stayed the same
    assert scroll_bar.value() == prev_position

    # reset position
    prev_position = scroll_bar.maximum() - (scroll_bar.pageStep() * 8) // 10
    scroll_bar.setValue(prev_position)

    qtbot.wait(1000)
    assert scroll_bar.value() > prev_position


@flaky(max_runs=3)
def test_input(qtconsole, qtbot):
    """
    Test input function
    """
    window = qtconsole.window
    shell = window.active_frontend
    control = shell._control

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    with qtbot.waitSignal(shell.executed):
        shell.execute("import time")

    input_function = 'input'
    shell.execute("print(" + input_function + "('name: ')); time.sleep(3)")

    qtbot.waitUntil(lambda: control.toPlainText().split()[-1] == 'name:')

    qtbot.keyClicks(control, 'test')
    qtbot.keyClick(control, QtCore.Qt.Key_Enter)
    qtbot.waitUntil(lambda: not shell._reading)
    qtbot.keyClick(control, 'z', modifier=QtCore.Qt.ControlModifier)
    for i in range(10):
        qtbot.keyClick(control, QtCore.Qt.Key_Backspace)
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    assert 'name: test\ntest' in control.toPlainText()


@flaky(max_runs=3)
def test_debug(qtconsole, qtbot):
    """
    Make sure the cursor works while debugging

    It might not because the console is "_executing"
    """
    window = qtconsole.window
    shell = window.active_frontend
    control = shell._control

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Enter execution
    code = "%debug range(1)"
    qtbot.keyClicks(control, code)
    qtbot.keyClick(control, QtCore.Qt.Key_Enter,
                   modifier=QtCore.Qt.ShiftModifier)

    qtbot.waitUntil(
        lambda: control.toPlainText().strip().split()[-1] == "ipdb>",
        timeout=SHELL_TIMEOUT)

    # We should be able to move the cursor while debugging
    qtbot.keyClicks(control, "abd")
    qtbot.wait(100)
    qtbot.keyClick(control, QtCore.Qt.Key_Left)
    qtbot.keyClick(control, 'c')
    qtbot.wait(100)
    assert control.toPlainText().strip().split()[-1] == "abcd"


@flaky(max_runs=15)
def test_input_and_print(qtconsole, qtbot):
    """
    Test that we print correctly mixed input and print statements.

    This is a regression test for spyder-ide/spyder#17710.
    """
    window = qtconsole.window
    shell = window.active_frontend
    control = shell._control

    def wait_for_input():
        qtbot.waitUntil(
            lambda: control.toPlainText().splitlines()[-1] == 'Write input: '
        )

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Run a for loop with mixed input and print statements
    code = """
user_input = None
while user_input != '':
    user_input = input('Write input: ')
    print('Input was entered!')
"""
    shell.execute(code)
    wait_for_input()

    # Interact with the 'for' loop for a certain number of repetitions
    repetitions = 3
    for _ in range(repetitions):
        qtbot.keyClicks(control, '1')
        qtbot.keyClick(control, QtCore.Qt.Key_Enter)
        wait_for_input()

    # Get out of the for loop
    qtbot.keyClick(control, QtCore.Qt.Key_Enter)
    qtbot.waitUntil(lambda: not shell._reading)
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Assert that printed correctly the expected output in the console.
    output = (
        "   ...: \n" +
        "Write input: 1\nInput was entered!\n" * repetitions +
        "Write input: \nInput was entered!\n"
    )
    assert output in control.toPlainText()


@flaky(max_runs=5)
@pytest.mark.skipif(os.name == 'nt', reason="no SIGTERM on Windows")
def test_restart_after_kill(qtconsole, qtbot):
    """
    Test that the kernel correctly restarts after a kill.
    """
    window = qtconsole.window
    shell = window.active_frontend
    control = shell._control

    def wait_for_restart():
        qtbot.waitUntil(
            lambda: 'Kernel died, restarting' in control.toPlainText()
        )

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # This checks that we are able to restart the kernel even after the number
    # of consecutive auto-restarts is reached (which by default is five).
    for _ in range(10):
        # Clear console
        with qtbot.waitSignal(shell.executed):
            shell.execute('%clear')
        qtbot.wait(500)

        # Run some code that kills the kernel
        code = "import os, signal; os.kill(os.getpid(), signal.SIGTERM)"
        shell.execute(code)

        # Check that the restart message is printed
        qtbot.waitUntil(
            lambda: 'Kernel died, restarting' in control.toPlainText()
        )

        # Check that a new prompt is available after the restart
        qtbot.waitUntil(
            lambda: control.toPlainText().splitlines()[-1] == 'In [1]: '
        )
        qtbot.wait(500)


@pytest.mark.skipif(no_display, reason="Doesn't work without a display")
class TestConsoleWidget(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Create the application for the test case.
        """
        cls._app = QtWidgets.QApplication.instance()
        if cls._app is None:
            cls._app = QtWidgets.QApplication([])
        cls._app.setQuitOnLastWindowClosed(False)

    @classmethod
    def tearDownClass(cls):
        """ Exit the application.
        """
        QtWidgets.QApplication.quit()

    def assert_text_equal(self, cursor, text):
        cursor.select(QtGui.QTextCursor.Document)
        selection = cursor.selectedText()
        self.assertEqual(selection, text)

    def test_special_characters(self):
        """ Are special characters displayed correctly?
        """
        w = ConsoleWidget()
        cursor = w._get_prompt_cursor()

        test_inputs = ['xyz\b\b=\n',
                       'foo\b\nbar\n',
                       'foo\b\nbar\r\n',
                       'abc\rxyz\b\b=']
        expected_outputs = ['x=z\u2029',
                            'foo\u2029bar\u2029',
                            'foo\u2029bar\u2029',
                            'x=z']
        for i, text in enumerate(test_inputs):
            w._insert_plain_text(cursor, text)
            self.assert_text_equal(cursor, expected_outputs[i])
            # clear all the text
            cursor.insertText('')

    def test_erase_in_line(self):
        """ Do control sequences for clearing the line work?
        """
        w = ConsoleWidget()
        cursor = w._get_prompt_cursor()

        test_inputs = ['Hello\x1b[1KBye',
                       'Hello\x1b[0KBye',
                       'Hello\r\x1b[0KBye',
                       'Hello\r\x1b[1KBye',
                       'Hello\r\x1b[2KBye',
                       'Hello\x1b[2K\rBye']

        expected_outputs = ['     Bye',
                            'HelloBye',
                            'Bye',
                            'Byelo',
                            'Bye',
                            'Bye']
        for i, text in enumerate(test_inputs):
            w._insert_plain_text(cursor, text)
            self.assert_text_equal(cursor, expected_outputs[i])
            # clear all the text
            cursor.insertText('')

    def test_link_handling(self):
        noButton = QtCore.Qt.NoButton
        noButtons = QtCore.Qt.NoButton
        noModifiers = QtCore.Qt.NoModifier
        MouseMove = QtCore.QEvent.MouseMove
        QMouseEvent = QtGui.QMouseEvent

        w = ConsoleWidget()
        cursor = w._get_prompt_cursor()
        w._insert_html(cursor, '<a href="http://python.org">written in</a>')
        obj = w._control
        tip = QtWidgets.QToolTip
        self.assertEqual(tip.text(), '')

        # should be somewhere else
        elsewhereEvent = QMouseEvent(MouseMove, QtCore.QPointF(50, 50),
                                     noButton, noButtons, noModifiers)
        w.eventFilter(obj, elsewhereEvent)
        self.assertEqual(tip.isVisible(), False)
        self.assertEqual(tip.text(), '')
        # should be over text
        overTextEvent = QMouseEvent(MouseMove, QtCore.QPointF(1, 5),
                                    noButton, noButtons, noModifiers)
        w.eventFilter(obj, overTextEvent)
        self.assertEqual(tip.isVisible(), True)
        self.assertEqual(tip.text(), "http://python.org")

        # should still be over text
        stillOverTextEvent = QMouseEvent(MouseMove, QtCore.QPointF(1, 5),
                                         noButton, noButtons, noModifiers)
        w.eventFilter(obj, stillOverTextEvent)
        self.assertEqual(tip.isVisible(), True)
        self.assertEqual(tip.text(), "http://python.org")

    def test_width_height(self):
        # width()/height() QWidget properties should not be overridden.
        w = ConsoleWidget()
        self.assertEqual(w.width(), QtWidgets.QWidget.width(w))
        self.assertEqual(w.height(), QtWidgets.QWidget.height(w))

    def test_prompt_cursors(self):
        """Test the cursors that keep track of where the prompt begins and
        ends"""
        w = ConsoleWidget()
        w._prompt = 'prompt>'
        doc = w._control.document()

        # Fill up the QTextEdit area with the maximum number of blocks
        doc.setMaximumBlockCount(10)
        for _ in range(9):
            w._append_plain_text('line\n')

        # Draw the prompt, this should cause the first lines to be deleted
        w._show_prompt()
        self.assertEqual(doc.blockCount(), 10)

        # _prompt_pos should be at the end of the document
        self.assertEqual(w._prompt_pos, w._get_end_pos())

        # _append_before_prompt_pos should be at the beginning of the prompt
        self.assertEqual(w._append_before_prompt_pos,
                         w._prompt_pos - len(w._prompt))

        # insert some more text without drawing a new prompt
        w._append_plain_text('line\n')
        self.assertEqual(w._prompt_pos,
                         w._get_end_pos() - len('line\n'))
        self.assertEqual(w._append_before_prompt_pos,
                         w._prompt_pos - len(w._prompt))

        # redraw the prompt
        w._show_prompt()
        self.assertEqual(w._prompt_pos, w._get_end_pos())
        self.assertEqual(w._append_before_prompt_pos,
                         w._prompt_pos - len(w._prompt))

        # insert some text before the prompt
        w._append_plain_text('line', before_prompt=True)
        self.assertEqual(w._prompt_pos, w._get_end_pos())
        self.assertEqual(w._append_before_prompt_pos,
                         w._prompt_pos - len(w._prompt))

    def test_select_all(self):
        w = ConsoleWidget()
        w._append_plain_text('Header\n')
        w._prompt = 'prompt>'
        w._show_prompt()
        control = w._control
        app = QtWidgets.QApplication.instance()

        cursor = w._get_cursor()
        w._insert_plain_text_into_buffer(cursor, "if:\n    pass")

        cursor.clearSelection()
        control.setTextCursor(cursor)

        # "select all" action selects cell first
        w.select_all_smart()
        QTest.keyClick(control, QtCore.Qt.Key_C, QtCore.Qt.ControlModifier)
        copied = app.clipboard().text()
        self.assertEqual(copied,  'if:\n>     pass')

        # # "select all" action triggered a second time selects whole document
        w.select_all_smart()
        QTest.keyClick(control, QtCore.Qt.Key_C, QtCore.Qt.ControlModifier)
        copied = app.clipboard().text()
        self.assertEqual(copied,  'Header\nprompt>if:\n>     pass')

    @pytest.mark.skipif(sys.platform == 'darwin', reason="Fails on macOS")
    def test_keypresses(self):
        """Test the event handling code for keypresses."""
        w = ConsoleWidget()
        w._append_plain_text('Header\n')
        w._prompt = 'prompt>'
        w._show_prompt()
        app = QtWidgets.QApplication.instance()
        control = w._control

        # Test setting the input buffer
        w._set_input_buffer('test input')
        self.assertEqual(w._get_input_buffer(), 'test input')

        # Ctrl+K kills input until EOL
        w._set_input_buffer('test input')
        c = control.textCursor()
        c.setPosition(c.position() - 3)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_K, QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(), 'test in')

        # Ctrl+V pastes
        w._set_input_buffer('test input ')
        app.clipboard().setText('pasted text')
        QTest.keyClick(control, QtCore.Qt.Key_V, QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(), 'test input pasted text')
        self.assertEqual(control.document().blockCount(), 2)

        # Paste should strip indentation
        w._set_input_buffer('test input ')
        app.clipboard().setText('    pasted text')
        QTest.keyClick(control, QtCore.Qt.Key_V, QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(), 'test input pasted text')
        self.assertEqual(control.document().blockCount(), 2)

        # Multiline paste, should also show continuation marks
        w._set_input_buffer('test input ')
        app.clipboard().setText('line1\nline2\nline3')
        QTest.keyClick(control, QtCore.Qt.Key_V, QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         'test input line1\nline2\nline3')
        self.assertEqual(control.document().blockCount(), 4)
        self.assertEqual(control.document().findBlockByNumber(1).text(),
                         'prompt>test input line1')
        self.assertEqual(control.document().findBlockByNumber(2).text(),
                         '> line2')
        self.assertEqual(control.document().findBlockByNumber(3).text(),
                         '> line3')

        # Multiline paste should strip indentation intelligently
        # in the case where pasted text has leading whitespace on first line
        # and we're pasting into indented position
        w._set_input_buffer('    ')
        app.clipboard().setText('    If 1:\n        pass')
        QTest.keyClick(control, QtCore.Qt.Key_V, QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         '    If 1:\n        pass')

        # Ctrl+Backspace should intelligently remove the last word
        w._set_input_buffer("foo = ['foo', 'foo', 'foo',    \n"
                            "       'bar', 'bar', 'bar']")
        QTest.keyClick(control, QtCore.Qt.Key_Backspace,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', 'foo',    \n"
                          "       'bar', 'bar', '"))
        QTest.keyClick(control, QtCore.Qt.Key_Backspace,
                       QtCore.Qt.ControlModifier)
        QTest.keyClick(control, QtCore.Qt.Key_Backspace,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', 'foo',    \n"
                          "       '"))
        QTest.keyClick(control, QtCore.Qt.Key_Backspace,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', 'foo',    \n"
                          ""))
        QTest.keyClick(control, QtCore.Qt.Key_Backspace,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         "foo = ['foo', 'foo', 'foo',")

        # Ctrl+Delete should intelligently remove the next word
        w._set_input_buffer("foo = ['foo', 'foo', 'foo',    \n"
                            "       'bar', 'bar', 'bar']")
        c = control.textCursor()
        c.setPosition(35)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Delete,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', ',    \n"
                          "       'bar', 'bar', 'bar']"))
        QTest.keyClick(control, QtCore.Qt.Key_Delete,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', \n"
                          "       'bar', 'bar', 'bar']"))
        QTest.keyClick(control, QtCore.Qt.Key_Delete,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         "foo = ['foo', 'foo', 'bar', 'bar', 'bar']")
        w._set_input_buffer("foo = ['foo', 'foo', 'foo',    \n"
                            "       'bar', 'bar', 'bar']")
        c = control.textCursor()
        c.setPosition(48)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Delete,
                       QtCore.Qt.ControlModifier)
        self.assertEqual(w._get_input_buffer(),
                         ("foo = ['foo', 'foo', 'foo',    \n"
                          "'bar', 'bar', 'bar']"))

        # Left and right keys should respect the continuation prompt
        w._set_input_buffer("line 1\n"
                            "line 2\n"
                            "line 3")
        c = control.textCursor()
        c.setPosition(20)  # End of line 1
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Right)
        # Cursor should have moved after the continuation prompt
        self.assertEqual(control.textCursor().position(), 23)
        QTest.keyClick(control, QtCore.Qt.Key_Left)
        # Cursor should have moved to the end of the previous line
        self.assertEqual(control.textCursor().position(), 20)

        # TODO: many more keybindings

    def test_indent(self):
        """Test the event handling code for indent/dedent keypresses ."""
        w = ConsoleWidget()
        w._append_plain_text('Header\n')
        w._prompt = 'prompt>'
        w._show_prompt()
        control = w._control

        # TAB with multiline selection should block-indent
        w._set_input_buffer("")
        c = control.textCursor()
        pos=c.position()
        w._set_input_buffer("If 1:\n    pass")
        c.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Tab)
        self.assertEqual(w._get_input_buffer(),"    If 1:\n        pass")

        # TAB with multiline selection, should block-indent to next multiple
        # of 4 spaces, if first line has 0 < indent < 4
        w._set_input_buffer("")
        c = control.textCursor()
        pos=c.position()
        w._set_input_buffer(" If 2:\n     pass")
        c.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Tab)
        self.assertEqual(w._get_input_buffer(),"    If 2:\n        pass")

        # Shift-TAB with multiline selection should block-dedent
        w._set_input_buffer("")
        c = control.textCursor()
        pos=c.position()
        w._set_input_buffer("    If 3:\n        pass")
        c.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        control.setTextCursor(c)
        QTest.keyClick(control, QtCore.Qt.Key_Backtab)
        self.assertEqual(w._get_input_buffer(),"If 3:\n    pass")

    def test_complete(self):
        class TestKernelClient(object):
            def is_complete(self, source):
                calls.append(source)
                return msg_id
        w = ConsoleWidget()
        cursor = w._get_prompt_cursor()
        w._execute = lambda *args: calls.append(args)
        w.kernel_client = TestKernelClient()
        msg_id = object()
        calls = []

        # test incomplete statement (no _execute called, but indent added)
        w.execute("thing", interactive=True)
        self.assertEqual(calls, ["thing"])
        calls = []
        w._handle_is_complete_reply(
            dict(parent_header=dict(msg_id=msg_id),
                 content=dict(status="incomplete", indent="!!!")))
        self.assert_text_equal(cursor, "thing\u2029> !!!")
        self.assertEqual(calls, [])

        # test complete statement (_execute called)
        msg_id = object()
        w.execute("else", interactive=True)
        self.assertEqual(calls, ["else"])
        calls = []
        w._handle_is_complete_reply(
            dict(parent_header=dict(msg_id=msg_id),
                 content=dict(status="complete", indent="###")))
        self.assertEqual(calls, [("else", False)])
        calls = []
        self.assert_text_equal(cursor, "thing\u2029> !!!else\u2029")

        # test missing answer from is_complete
        msg_id = object()
        w.execute("done", interactive=True)
        self.assertEqual(calls, ["done"])
        calls = []
        self.assert_text_equal(cursor, "thing\u2029> !!!else\u2029")
        w._trigger_is_complete_callback()
        self.assert_text_equal(cursor, "thing\u2029> !!!else\u2029\u2029> ")

        # assert that late answer isn't destroying anything
        w._handle_is_complete_reply(
            dict(parent_header=dict(msg_id=msg_id),
                 content=dict(status="complete", indent="###")))
        self.assertEqual(calls, [])

    def test_complete_python(self):
        """Test that is_complete is working correctly for Python."""
        # Kernel client to test the responses of is_complete
        class TestIPyKernelClient(object):
            def is_complete(self, source):
                tm = TransformerManager()
                check_complete = tm.check_complete(source)
                responses.append(check_complete)

        # Initialize widget
        responses = []
        w = ConsoleWidget()
        w._append_plain_text('Header\n')
        w._prompt = 'prompt>'
        w._show_prompt()
        w.kernel_client = TestIPyKernelClient()

        # Execute incomplete statement inside a block
        code = '\n'.join(["if True:", "    a = 1"])
        w._set_input_buffer(code)
        w.execute(interactive=True)
        assert responses == [('incomplete', 4)]

        # Execute complete statement inside a block
        responses = []
        code = '\n'.join(["if True:", "    a = 1\n\n"])
        w._set_input_buffer(code)
        w.execute(interactive=True)
        assert responses == [('complete', None)]
