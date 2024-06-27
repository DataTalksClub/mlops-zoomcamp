import pytest


def test_qtscxml():
    """Test the qtpy.QtScxml namespace"""
    QtScxml = pytest.importorskip("qtpy.QtScxml")

    assert QtScxml.QScxmlCompiler is not None
    assert QtScxml.QScxmlDynamicScxmlServiceFactory is not None
    assert QtScxml.QScxmlExecutableContent is not None
