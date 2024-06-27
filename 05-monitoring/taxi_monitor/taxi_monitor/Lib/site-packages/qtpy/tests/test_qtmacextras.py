import sys

import pytest

from qtpy import PYQT6, PYSIDE6
from qtpy.tests.utils import using_conda


@pytest.mark.skipif(
    PYQT6 or PYSIDE6,
    reason="Not available on Qt6-based bindings",
)
@pytest.mark.skipif(
    sys.platform != "darwin" or using_conda(),
    reason="Only available in Qt5 bindings > 5.9 with pip on mac in CIs",
)
def test_qtmacextras():
    """Test the qtpy.QtMacExtras namespace"""
    QtMacExtras = pytest.importorskip("qtpy.QtMacExtras")

    assert QtMacExtras.QMacPasteboardMime is not None
    assert QtMacExtras.QMacToolBar is not None
    assert QtMacExtras.QMacToolBarItem is not None
