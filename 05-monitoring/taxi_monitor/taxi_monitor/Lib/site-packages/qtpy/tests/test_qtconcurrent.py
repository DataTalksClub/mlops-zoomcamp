import pytest
from packaging.version import parse

from qtpy import PYSIDE2, PYSIDE_VERSION


def test_qtconcurrent():
    """Test the qtpy.QtConcurrent namespace"""
    QtConcurrent = pytest.importorskip("qtpy.QtConcurrent")

    assert QtConcurrent.QtConcurrent is not None

    if PYSIDE2 and parse(PYSIDE_VERSION) >= parse("5.15.2"):
        assert QtConcurrent.QFutureQString is not None
        assert QtConcurrent.QFutureVoid is not None
        assert QtConcurrent.QFutureWatcherQString is not None
        assert QtConcurrent.QFutureWatcherVoid is not None
