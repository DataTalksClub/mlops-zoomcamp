import unittest

from qtconsole.styles import dark_color, dark_style


class TestStyles(unittest.TestCase):
    def test_dark_color(self):
        self.assertTrue(dark_color('#000000'))  # black
        self.assertTrue(not dark_color('#ffff66'))  # bright yellow
        self.assertTrue(dark_color('#80807f'))  # < 50% gray
        self.assertTrue(not dark_color('#808080'))  # = 50% gray

    def test_dark_style(self):
        self.assertTrue(dark_style('monokai'))
        self.assertTrue(not dark_style('default'))
