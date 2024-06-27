import pytest


def test_qtsvgwidgets():
    """Test the qtpy.QtSvgWidgets namespace"""
    QtSvgWidgets = pytest.importorskip("qtpy.QtSvgWidgets")

    assert QtSvgWidgets.QGraphicsSvgItem is not None
    assert QtSvgWidgets.QSvgWidget is not None
