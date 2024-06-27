import pytest

from qtpy import PYSIDE2


@pytest.mark.skipif(PYSIDE2, reason="Not available in CI")
def test_qtserialport():
    """Test the qtpy.QtSerialPort namespace"""
    QtSerialPort = pytest.importorskip("qtpy.QtSerialPort")

    assert QtSerialPort.QSerialPort is not None
    assert QtSerialPort.QSerialPortInfo is not None
