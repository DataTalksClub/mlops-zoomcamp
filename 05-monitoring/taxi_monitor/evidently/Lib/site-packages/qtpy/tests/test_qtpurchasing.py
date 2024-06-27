import pytest


def test_qtpurchasing():
    """Test the qtpy.QtPurchasing namespace"""
    QtPurchasing = pytest.importorskip("qtpy.QtPurchasing")

    assert QtPurchasing.QInAppProduct is not None
    assert QtPurchasing.QInAppStore is not None
    assert QtPurchasing.QInAppTransaction is not None
