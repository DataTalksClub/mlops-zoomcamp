"""Test Qsci."""

import pytest

from qtpy import PYSIDE2, PYSIDE6
from qtpy.tests.utils import using_conda


@pytest.mark.skipif(
    PYSIDE2 or PYSIDE6 or using_conda(),
    reason="Qsci bindings not available under PySide 2/6 and conda installations",
)
def test_qsci():
    """Test the qtpy.Qsci namespace"""
    Qsci = pytest.importorskip("qtpy.Qsci")
    assert Qsci.QSCINTILLA_VERSION is not None
    assert Qsci.QSCINTILLA_VERSION_STR is not None
    assert Qsci.QsciAPIs is not None
    assert Qsci.QsciAbstractAPIs is not None
    assert Qsci.QsciCommand is not None
    assert Qsci.QsciCommandSet is not None
    assert Qsci.QsciDocument is not None
    assert Qsci.QsciLexer is not None
    assert Qsci.QsciLexerAVS is not None
    assert Qsci.QsciLexerBash is not None
    assert Qsci.QsciLexerBatch is not None
    assert Qsci.QsciLexerCMake is not None
    assert Qsci.QsciLexerCPP is not None
    assert Qsci.QsciLexerCSS is not None
    assert Qsci.QsciLexerCSharp is not None
    assert Qsci.QsciLexerCoffeeScript is not None
    assert Qsci.QsciLexerCustom is not None
    assert Qsci.QsciLexerD is not None
    assert Qsci.QsciLexerDiff is not None
    assert Qsci.QsciLexerFortran is not None
    assert Qsci.QsciLexerFortran77 is not None
    assert Qsci.QsciLexerHTML is not None
    assert Qsci.QsciLexerIDL is not None
    assert Qsci.QsciLexerJSON is not None
    assert Qsci.QsciLexerJava is not None
    assert Qsci.QsciLexerJavaScript is not None
    assert Qsci.QsciLexerLua is not None
    assert Qsci.QsciLexerMakefile is not None
    assert Qsci.QsciLexerMarkdown is not None
    assert Qsci.QsciLexerMatlab is not None
    assert Qsci.QsciLexerOctave is not None
    assert Qsci.QsciLexerPO is not None
    assert Qsci.QsciLexerPOV is not None
    assert Qsci.QsciLexerPascal is not None
    assert Qsci.QsciLexerPerl is not None
    assert Qsci.QsciLexerPostScript is not None
    assert Qsci.QsciLexerProperties is not None
    assert Qsci.QsciLexerPython is not None
    assert Qsci.QsciLexerRuby is not None
    assert Qsci.QsciLexerSQL is not None
    assert Qsci.QsciLexerSpice is not None
    assert Qsci.QsciLexerTCL is not None
    assert Qsci.QsciLexerTeX is not None
    assert Qsci.QsciLexerVHDL is not None
    assert Qsci.QsciLexerVerilog is not None
    assert Qsci.QsciLexerXML is not None
    assert Qsci.QsciLexerYAML is not None
    assert Qsci.QsciMacro is not None
    assert Qsci.QsciPrinter is not None
    assert Qsci.QsciScintilla is not None
    assert Qsci.QsciScintillaBase is not None
    assert Qsci.QsciStyle is not None
    assert Qsci.QsciStyledText is not None
