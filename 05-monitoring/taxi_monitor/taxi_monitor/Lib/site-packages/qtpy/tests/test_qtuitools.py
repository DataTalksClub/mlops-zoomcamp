import pytest


def test_qtuitools():
    """Test the qtpy.QtUiTools namespace"""
    QtUiTools = pytest.importorskip("qtpy.QtUiTools")

    assert QtUiTools.QUiLoader is not None
