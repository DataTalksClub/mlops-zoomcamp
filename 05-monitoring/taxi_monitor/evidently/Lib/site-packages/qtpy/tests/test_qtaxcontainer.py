import pytest


def test_qtaxcontainer():
    """Test the qtpy.QtAxContainer namespace"""
    QtAxContainer = pytest.importorskip("qtpy.QtAxContainer")

    assert QtAxContainer.QAxSelect is not None
    assert QtAxContainer.QAxWidget is not None
