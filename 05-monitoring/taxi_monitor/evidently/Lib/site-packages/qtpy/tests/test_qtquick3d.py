import pytest


def test_qtquick3d():
    """Test the qtpy.QtQuick3D namespace"""
    QtQuick3D = pytest.importorskip("qtpy.QtQuick3D")

    assert QtQuick3D.QQuick3D is not None
    assert QtQuick3D.QQuick3DGeometry is not None
    assert QtQuick3D.QQuick3DObject is not None
