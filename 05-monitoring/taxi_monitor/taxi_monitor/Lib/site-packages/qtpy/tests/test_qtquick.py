from qtpy import PYQT5, PYSIDE2


def test_qtquick():
    """Test the qtpy.QtQuick namespace"""
    from qtpy import QtQuick

    if PYQT5:
        assert QtQuick.QQuickCloseEvent is not None
        assert QtQuick.QSGFlatColorMaterial is not None
        assert QtQuick.QSGImageNode is not None
        assert QtQuick.QSGMaterial is not None
        assert QtQuick.QSGMaterialShader is not None
        assert QtQuick.QSGOpaqueTextureMaterial is not None
        assert QtQuick.QSGRectangleNode is not None
        assert QtQuick.QSGRenderNode is not None
        assert QtQuick.QSGRendererInterface is not None
        assert QtQuick.QSGTextureMaterial is not None
        assert QtQuick.QSGVertexColorMaterial is not None

    assert QtQuick.QQuickAsyncImageProvider is not None
    assert QtQuick.QQuickFramebufferObject is not None
    assert QtQuick.QQuickImageProvider is not None
    assert QtQuick.QQuickImageResponse is not None
    assert QtQuick.QQuickItem is not None
    assert QtQuick.QQuickItemGrabResult is not None
    assert QtQuick.QQuickPaintedItem is not None
    assert QtQuick.QQuickRenderControl is not None
    assert QtQuick.QQuickTextDocument is not None
    assert QtQuick.QQuickTextureFactory is not None
    assert QtQuick.QQuickView is not None
    assert QtQuick.QQuickWindow is not None
    if PYQT5 or PYSIDE2:
        assert QtQuick.QSGAbstractRenderer is not None
        assert QtQuick.QSGEngine is not None
    assert QtQuick.QSGBasicGeometryNode is not None
    assert QtQuick.QSGClipNode is not None
    assert QtQuick.QSGDynamicTexture is not None
    assert QtQuick.QSGGeometry is not None
    assert QtQuick.QSGGeometryNode is not None
    assert QtQuick.QSGMaterialType is not None
    assert QtQuick.QSGNode is not None
    assert QtQuick.QSGOpacityNode is not None
    assert QtQuick.QSGSimpleRectNode is not None
    assert QtQuick.QSGSimpleTextureNode is not None
    assert QtQuick.QSGTexture is not None
    assert QtQuick.QSGTextureProvider is not None
    assert QtQuick.QSGTransformNode is not None
