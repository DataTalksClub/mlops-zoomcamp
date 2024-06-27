"""Test QtMultimediaWidgets."""


from qtpy import PYQT5, PYSIDE2


def test_qtmultimediawidgets():
    """Test the qtpy.QtMultimediaWidgets namespace"""
    from qtpy import QtMultimediaWidgets

    if PYQT5 or PYSIDE2:
        assert QtMultimediaWidgets.QCameraViewfinder is not None
        # assert QtMultimediaWidgets.QVideoWidgetControl is not None
    assert QtMultimediaWidgets.QGraphicsVideoItem is not None
    assert QtMultimediaWidgets.QVideoWidget is not None
