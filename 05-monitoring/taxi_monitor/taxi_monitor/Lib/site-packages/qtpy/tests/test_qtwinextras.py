"""Test QtWinExtras."""

import sys

import pytest

from qtpy import PYQT6, PYSIDE2, PYSIDE6
from qtpy.tests.utils import using_conda


@pytest.mark.skipif(
    PYQT6 or PYSIDE6,
    reason="Not available on Qt6-based bindings",
)
@pytest.mark.skipif(
    sys.platform != "win32" or using_conda(),
    reason="Only available in Qt5 bindings > 5.9 with pip on Windows in CIs",
)
def test_qtwinextras():
    """Test the qtpy.QtWinExtras namespace"""
    from qtpy import QtWinExtras

    assert QtWinExtras.QWinJumpList is not None
    assert QtWinExtras.QWinJumpListCategory is not None
    assert QtWinExtras.QWinJumpListItem is not None
    assert QtWinExtras.QWinTaskbarButton is not None
    assert QtWinExtras.QWinTaskbarProgress is not None
    assert QtWinExtras.QWinThumbnailToolBar is not None
    assert QtWinExtras.QWinThumbnailToolButton is not None
    if not PYSIDE2:  # See https://bugreports.qt.io/browse/PYSIDE-1047
        assert QtWinExtras.QtWin is not None

    if PYSIDE2:
        assert QtWinExtras.QWinColorizationChangeEvent is not None
        assert QtWinExtras.QWinCompositionChangeEvent is not None
        assert QtWinExtras.QWinEvent is not None
