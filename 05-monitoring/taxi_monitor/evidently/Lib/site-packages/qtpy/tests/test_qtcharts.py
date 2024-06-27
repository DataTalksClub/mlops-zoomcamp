import pytest

from qtpy import PYSIDE2, PYSIDE6


@pytest.mark.skipif(
    not (PYSIDE2 or PYSIDE6),
    reason="Only available by default in PySide",
)
def test_qtcharts():
    """Test the qtpy.QtCharts namespace"""
    QtCharts = pytest.importorskip("qtpy.QtCharts")

    assert QtCharts.QChart is not None
    assert QtCharts.QtCharts.QChart is not None
