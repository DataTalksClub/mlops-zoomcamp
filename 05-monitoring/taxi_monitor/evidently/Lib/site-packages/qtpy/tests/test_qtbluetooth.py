import pytest


def test_qtbluetooth():
    """Test the qtpy.QtBluetooth namespace"""
    QtBluetooth = pytest.importorskip("qtpy.QtBluetooth")

    assert QtBluetooth.QBluetooth is not None
    assert QtBluetooth.QBluetoothDeviceInfo is not None
    assert QtBluetooth.QBluetoothServer is not None
    assert QtBluetooth.QBluetoothSocket is not None
    assert QtBluetooth.QBluetoothAddress is not None
    assert QtBluetooth.QBluetoothUuid is not None
    assert QtBluetooth.QBluetoothServiceDiscoveryAgent is not None
