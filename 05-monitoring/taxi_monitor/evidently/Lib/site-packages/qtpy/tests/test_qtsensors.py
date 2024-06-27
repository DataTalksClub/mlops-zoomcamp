import pytest


def test_qtsensors():
    """Test the qtpy.QtSensors namespace"""
    QtSensors = pytest.importorskip("qtpy.QtSensors")

    assert QtSensors.QAccelerometer is not None
    assert QtSensors.QAccelerometerFilter is not None
    assert QtSensors.QAccelerometerReading is not None
