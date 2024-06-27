import pytest


def test_qtwebenginecore():
    """Test the qtpy.QtWebEngineCore namespace"""
    QtWebEngineCore = pytest.importorskip("qtpy.QtWebEngineCore")

    assert QtWebEngineCore.QWebEngineHttpRequest is not None
