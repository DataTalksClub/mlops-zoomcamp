def test_qtopengl():
    """Test the qtpy.QtOpenGL namespace"""
    from qtpy import QtOpenGL

    assert QtOpenGL.QOpenGLBuffer is not None
    assert QtOpenGL.QOpenGLContext is not None
    assert QtOpenGL.QOpenGLContextGroup is not None
    assert QtOpenGL.QOpenGLDebugLogger is not None
    assert QtOpenGL.QOpenGLDebugMessage is not None
    assert QtOpenGL.QOpenGLFramebufferObject is not None
    assert QtOpenGL.QOpenGLFramebufferObjectFormat is not None
    assert QtOpenGL.QOpenGLPixelTransferOptions is not None
    assert QtOpenGL.QOpenGLShader is not None
    assert QtOpenGL.QOpenGLShaderProgram is not None
    assert QtOpenGL.QOpenGLTexture is not None
    assert QtOpenGL.QOpenGLTextureBlitter is not None
    assert QtOpenGL.QOpenGLVersionProfile is not None
    assert QtOpenGL.QOpenGLVertexArrayObject is not None
    assert QtOpenGL.QOpenGLWindow is not None
    # We do not test for QOpenGLTimeMonitor or QOpenGLTimerQuery as
    # they are not present on some architectures such as armhf
