import unittest
import sys

import pytest
from qtpy import QT6
from qtpy import QtWidgets, QtGui

from qtconsole.jupyter_widget import JupyterWidget

from . import no_display


@pytest.mark.skipif(no_display, reason="Doesn't work without a display")
class TestJupyterWidget(unittest.TestCase):

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

    def test_stylesheet_changed(self):
        """ Test changing stylesheets.
        """
        w = JupyterWidget(kind='rich')

        # By default, the background is light. White text is rendered as black
        self.assertEqual(w._ansi_processor.get_color(15).name(), '#000000')

        # Change to a dark colorscheme. White text is rendered as white
        w.syntax_style = 'monokai'
        self.assertEqual(w._ansi_processor.get_color(15).name(), '#ffffff')

    @pytest.mark.skipif(not sys.platform.startswith('linux'),
                        reason="Works only on Linux")
    def test_other_output(self):
        """ Test displaying output from other clients.
        """
        w = JupyterWidget(kind='rich')
        w._append_plain_text('Header\n')
        w._show_interpreter_prompt(1)
        w.other_output_prefix = '[other] '
        w.syntax_style = 'default'

        msg = dict(
            execution_count=1,
            code='a = 1 + 1\nb = range(10)',
        )
        w._append_custom(w._insert_other_input, msg, before_prompt=True)

        control = w._control
        document = control.document()

        self.assertEqual(document.blockCount(), 6)
        self.assertEqual(document.toPlainText(), (
            'Header\n'
            '\n'
            '[other] In [1]: a = 1 + 1\n'
            '           ...: b = range(10)\n'
            '\n'
            'In [2]: '
        ))

        # Check proper syntax highlighting.
        # This changes with every Qt6 release, that's why we don't test it on it.
        if not QT6:
            html = (
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                'p, li { white-space: pre-wrap; }\n'
                '</style></head><body style=" font-family:\'Monospace\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Header</p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000080;">[other] In [</span><span style=" font-weight:600; color:#000080;">1</span><span style=" color:#000080;">]:</span> a = 1 + 1</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000080;">\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0...:</span> b = range(10)</p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000080;">In [</span><span style=" font-weight:600; color:#000080;">2</span><span style=" color:#000080;">]:</span> </p></body></html>'
            )
        
            self.assertEqual(document.toHtml(), html)

    def test_copy_paste_prompt(self):
        """Test copy/paste removes partial and full prompts."""
        w = JupyterWidget(kind='rich')
        w._show_interpreter_prompt(1)
        control = w._control

        code = "    if True:\n        print('a')"
        w._set_input_buffer(code)
        assert code not in control.toPlainText()

        cursor = w._get_prompt_cursor()

        pos = cursor.position()
        cursor.setPosition(pos - 3)
        cursor.movePosition(QtGui.QTextCursor.End,
                            QtGui.QTextCursor.KeepAnchor)
        control.setTextCursor(cursor)
        control.hasFocus = lambda: True
        w.copy()
        clipboard = QtWidgets.QApplication.clipboard()
        assert clipboard.text() == code
        w.paste()
        expected = "In [1]: if True:\n   ...:     print('a')"
        assert expected in control.toPlainText()
