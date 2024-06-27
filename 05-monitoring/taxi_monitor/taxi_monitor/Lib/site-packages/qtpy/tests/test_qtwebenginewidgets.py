import pytest
from packaging import version

from qtpy import PYQT5, PYQT6, PYQT_VERSION, PYSIDE2, PYSIDE6, PYSIDE_VERSION


@pytest.mark.skipif(
    not (
        (PYQT6 and version.parse(PYQT_VERSION) >= version.parse("6.2"))
        or (PYSIDE6 and version.parse(PYSIDE_VERSION) >= version.parse("6.2"))
        or PYQT5
        or PYSIDE2
    ),
    reason="Only available in Qt<6,>=6.2 bindings",
)
def test_qtwebenginewidgets():
    """Test the qtpy.QtWebEngineWidget namespace"""

    QtWebEngineWidgets = pytest.importorskip("qtpy.QtWebEngineWidgets")

    assert QtWebEngineWidgets.QWebEnginePage is not None
    assert QtWebEngineWidgets.QWebEngineView is not None
    assert QtWebEngineWidgets.QWebEngineSettings is not None
    assert QtWebEngineWidgets.QWebEngineScript is not None
