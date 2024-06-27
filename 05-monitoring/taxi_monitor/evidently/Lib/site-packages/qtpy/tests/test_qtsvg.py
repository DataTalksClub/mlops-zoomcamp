import pytest

from qtpy import PYQT6, PYSIDE6


def test_qtsvg():
    """Test the qtpy.QtSvg namespace"""
    QtSvg = pytest.importorskip("qtpy.QtSvg")

    if not (PYSIDE6 or PYQT6):
        assert QtSvg.QGraphicsSvgItem is not None
        assert QtSvg.QSvgWidget is not None
    assert QtSvg.QSvgGenerator is not None
    assert QtSvg.QSvgRenderer is not None
