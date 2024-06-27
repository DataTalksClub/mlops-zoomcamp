import pytest

from qtpy import PYQT5, PYSIDE2


@pytest.mark.skipif(PYSIDE2 or PYQT5, reason="Not available in PySide2/PyQt5")
def test_qtopenglwidgets():
    """Test the qtpy.QtOpenGLWidgets namespace"""
    from qtpy import QtOpenGLWidgets

    assert QtOpenGLWidgets.QOpenGLWidget is not None
