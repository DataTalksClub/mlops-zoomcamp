import pytest


def test_qt3dlogic():
    """Test the qtpy.Qt3DLogic namespace"""
    Qt3DLogic = pytest.importorskip("qtpy.Qt3DLogic")

    assert Qt3DLogic.QLogicAspect is not None
    assert Qt3DLogic.QFrameAction is not None
