import pytest


def test_qtquickcontrols2():
    """Test the qtpy.QtQuickControls2 namespace"""
    QtQuickControls2 = pytest.importorskip("qtpy.QtQuickControls2")

    assert QtQuickControls2.QQuickStyle is not None
