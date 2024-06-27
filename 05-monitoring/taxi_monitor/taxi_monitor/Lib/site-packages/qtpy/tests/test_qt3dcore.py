import pytest

from qtpy import PYQT6, PYSIDE6


@pytest.mark.skipif(PYQT6, reason="Not complete in PyQt6")
@pytest.mark.skipif(PYSIDE6, reason="Not complete in PySide6")
def test_qt3dcore():
    """Test the qtpy.Qt3DCore namespace"""
    Qt3DCore = pytest.importorskip("qtpy.Qt3DCore")

    assert Qt3DCore.QPropertyValueAddedChange is not None
    assert Qt3DCore.QSkeletonLoader is not None
    assert Qt3DCore.QPropertyNodeRemovedChange is not None
    assert Qt3DCore.QPropertyUpdatedChange is not None
    assert Qt3DCore.QAspectEngine is not None
    assert Qt3DCore.QPropertyValueAddedChangeBase is not None
    assert Qt3DCore.QStaticPropertyValueRemovedChangeBase is not None
    assert Qt3DCore.QPropertyNodeAddedChange is not None
    assert Qt3DCore.QDynamicPropertyUpdatedChange is not None
    assert Qt3DCore.QStaticPropertyUpdatedChangeBase is not None
    assert Qt3DCore.ChangeFlags is not None
    assert Qt3DCore.QAbstractAspect is not None
    assert Qt3DCore.QBackendNode is not None
    assert Qt3DCore.QTransform is not None
    assert Qt3DCore.QPropertyUpdatedChangeBase is not None
    assert Qt3DCore.QNodeId is not None
    assert Qt3DCore.QJoint is not None
    assert Qt3DCore.QSceneChange is not None
    assert Qt3DCore.QNodeIdTypePair is not None
    assert Qt3DCore.QAbstractSkeleton is not None
    assert Qt3DCore.QComponentRemovedChange is not None
    assert Qt3DCore.QComponent is not None
    assert Qt3DCore.QEntity is not None
    assert Qt3DCore.QNodeCommand is not None
    assert Qt3DCore.QNode is not None
    assert Qt3DCore.QPropertyValueRemovedChange is not None
    assert Qt3DCore.QPropertyValueRemovedChangeBase is not None
    assert Qt3DCore.QComponentAddedChange is not None
    assert Qt3DCore.QNodeCreatedChangeBase is not None
    assert Qt3DCore.QNodeDestroyedChange is not None
    assert Qt3DCore.QArmature is not None
    assert Qt3DCore.QStaticPropertyValueAddedChangeBase is not None
    assert Qt3DCore.ChangeFlag is not None
    assert Qt3DCore.QSkeleton is not None
