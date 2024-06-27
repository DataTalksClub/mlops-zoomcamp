import unittest

import pytest

from qtpy import QtWidgets
from qtconsole.frontend_widget import FrontendWidget
from qtpy.QtTest import QTest
from . import no_display


@pytest.mark.skipif(no_display, reason="Doesn't work without a display")
class TestFrontendWidget(unittest.TestCase):

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

    def test_transform_classic_prompt(self):
        """ Test detecting classic prompts.
        """
        w = FrontendWidget(kind='rich')
        t = w._highlighter.transform_classic_prompt

        # Base case
        self.assertEqual(t('>>> test'), 'test')
        self.assertEqual(t(' >>> test'), 'test')
        self.assertEqual(t('\t >>> test'), 'test')

        # No prompt
        self.assertEqual(t(''), '')
        self.assertEqual(t('test'), 'test')

        # Continuation prompt
        self.assertEqual(t('... test'), 'test')
        self.assertEqual(t(' ... test'), 'test')
        self.assertEqual(t('  ... test'), 'test')
        self.assertEqual(t('\t ... test'), 'test')

        # Prompts that don't match the 'traditional' prompt
        self.assertEqual(t('>>>test'), '>>>test')
        self.assertEqual(t('>> test'), '>> test')
        self.assertEqual(t('...test'), '...test')
        self.assertEqual(t('.. test'), '.. test')

        # Prefix indicating input from other clients
        self.assertEqual(t('[remote] >>> test'), 'test')

        # Random other prefix
        self.assertEqual(t('[foo] >>> test'), '[foo] >>> test')

    def test_transform_ipy_prompt(self):
        """ Test detecting IPython prompts.
        """
        w = FrontendWidget(kind='rich')
        t = w._highlighter.transform_ipy_prompt

        # In prompt
        self.assertEqual(t('In [1]: test'), 'test')
        self.assertEqual(t('In [2]: test'), 'test')
        self.assertEqual(t('In [10]: test'), 'test')
        self.assertEqual(t(' In [1]: test'), 'test')
        self.assertEqual(t('\t In [1]: test'), 'test')

        # No prompt
        self.assertEqual(t(''), '')
        self.assertEqual(t('test'), 'test')

        # Continuation prompt
        self.assertEqual(t('   ...: test'), 'test')
        self.assertEqual(t('    ...: test'), 'test')
        self.assertEqual(t('     ...: test'), 'test')
        self.assertEqual(t('\t   ...: test'), 'test')

        # Prompts that don't match the in-prompt
        self.assertEqual(t('In [1]:test'), 'In [1]:test')
        self.assertEqual(t('[1]: test'), '[1]: test')
        self.assertEqual(t('In: test'), 'In: test')
        self.assertEqual(t(': test'), ': test')
        self.assertEqual(t('...: test'), '...: test')

        # Prefix indicating input from other clients
        self.assertEqual(t('[remote] In [1]: test'), 'test')

        # Random other prefix
        self.assertEqual(t('[foo] In [1]: test'), '[foo] In [1]: test')
