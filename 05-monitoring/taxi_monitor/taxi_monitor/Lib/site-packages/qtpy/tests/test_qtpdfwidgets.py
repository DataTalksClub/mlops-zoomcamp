import pytest


def test_qtpdfwidgets():
    """Test the qtpy.QtPdfWidgets namespace"""
    QtPdfWidgets = pytest.importorskip("qtpy.QtPdfWidgets")

    assert QtPdfWidgets.QPdfView is not None
