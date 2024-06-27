import pytest


def test_qt3dinput():
    """Test the qtpy.Qt3DInput namespace"""
    Qt3DInput = pytest.importorskip("qtpy.Qt3DInput")

    assert Qt3DInput.QAxisAccumulator is not None
    assert Qt3DInput.QInputSettings is not None
    assert Qt3DInput.QAnalogAxisInput is not None
    assert Qt3DInput.QAbstractAxisInput is not None
    assert Qt3DInput.QMouseHandler is not None
    assert Qt3DInput.QButtonAxisInput is not None
    assert Qt3DInput.QInputSequence is not None
    assert Qt3DInput.QWheelEvent is not None
    assert Qt3DInput.QActionInput is not None
    assert Qt3DInput.QKeyboardDevice is not None
    assert Qt3DInput.QMouseDevice is not None
    assert Qt3DInput.QAxis is not None
    assert Qt3DInput.QInputChord is not None
    assert Qt3DInput.QMouseEvent is not None
    assert Qt3DInput.QKeyboardHandler is not None
    assert Qt3DInput.QKeyEvent is not None
    assert Qt3DInput.QAbstractActionInput is not None
    assert Qt3DInput.QInputAspect is not None
    assert Qt3DInput.QLogicalDevice is not None
    assert Qt3DInput.QAction is not None
    assert Qt3DInput.QAbstractPhysicalDevice is not None
    assert Qt3DInput.QAxisSetting is not None
