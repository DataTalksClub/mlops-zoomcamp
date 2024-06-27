def test_qtquickwidgets():
    """Test the qtpy.QtQuickWidgets namespace"""
    from qtpy import QtQuickWidgets

    assert QtQuickWidgets.QQuickWidget is not None
