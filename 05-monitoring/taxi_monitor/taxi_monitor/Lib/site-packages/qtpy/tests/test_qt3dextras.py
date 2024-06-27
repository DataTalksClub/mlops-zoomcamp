import pytest


def test_qt3dextras():
    """Test the qtpy.Qt3DExtras namespace"""
    Qt3DExtras = pytest.importorskip("qtpy.Qt3DExtras")

    assert Qt3DExtras.QTextureMaterial is not None
    assert Qt3DExtras.QPhongAlphaMaterial is not None
    assert Qt3DExtras.QOrbitCameraController is not None
    assert Qt3DExtras.QAbstractSpriteSheet is not None
    assert Qt3DExtras.QNormalDiffuseMapMaterial is not None
    assert Qt3DExtras.QDiffuseSpecularMaterial is not None
    assert Qt3DExtras.QSphereGeometry is not None
    assert Qt3DExtras.QCuboidGeometry is not None
    assert Qt3DExtras.QForwardRenderer is not None
    assert Qt3DExtras.QPhongMaterial is not None
    assert Qt3DExtras.QSpriteGrid is not None
    assert Qt3DExtras.QDiffuseMapMaterial is not None
    assert Qt3DExtras.QConeGeometry is not None
    assert Qt3DExtras.QSpriteSheetItem is not None
    assert Qt3DExtras.QPlaneGeometry is not None
    assert Qt3DExtras.QSphereMesh is not None
    assert Qt3DExtras.QNormalDiffuseSpecularMapMaterial is not None
    assert Qt3DExtras.QCuboidMesh is not None
    assert Qt3DExtras.QGoochMaterial is not None
    assert Qt3DExtras.QText2DEntity is not None
    assert Qt3DExtras.QTorusMesh is not None
    assert Qt3DExtras.Qt3DWindow is not None
    assert Qt3DExtras.QPerVertexColorMaterial is not None
    assert Qt3DExtras.QExtrudedTextGeometry is not None
    assert Qt3DExtras.QSkyboxEntity is not None
    assert Qt3DExtras.QAbstractCameraController is not None
    assert Qt3DExtras.QExtrudedTextMesh is not None
    assert Qt3DExtras.QCylinderGeometry is not None
    assert Qt3DExtras.QTorusGeometry is not None
    assert Qt3DExtras.QMorphPhongMaterial is not None
    assert Qt3DExtras.QPlaneMesh is not None
    assert Qt3DExtras.QDiffuseSpecularMapMaterial is not None
    assert Qt3DExtras.QSpriteSheet is not None
    assert Qt3DExtras.QConeMesh is not None
    assert Qt3DExtras.QFirstPersonCameraController is not None
    assert Qt3DExtras.QMetalRoughMaterial is not None
    assert Qt3DExtras.QCylinderMesh is not None
