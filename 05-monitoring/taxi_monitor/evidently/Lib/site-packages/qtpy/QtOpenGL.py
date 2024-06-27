# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtOpenGL classes and functions."""

import contextlib

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtGui import (
        QOpenGLBuffer,
        QOpenGLContext,
        QOpenGLContextGroup,
        QOpenGLDebugLogger,
        QOpenGLDebugMessage,
        QOpenGLFramebufferObject,
        QOpenGLFramebufferObjectFormat,
        QOpenGLPixelTransferOptions,
        QOpenGLShader,
        QOpenGLShaderProgram,
        QOpenGLTexture,
        QOpenGLTextureBlitter,
        QOpenGLVersionProfile,
        QOpenGLVertexArrayObject,
        QOpenGLWindow,
    )
    from PyQt5.QtOpenGL import *

    # These are not present on some architectures such as armhf
    with contextlib.suppress(ImportError):
        from PyQt5.QtGui import QOpenGLTimeMonitor, QOpenGLTimerQuery

elif PYQT6:
    from PyQt6.QtGui import QOpenGLContext, QOpenGLContextGroup
    from PyQt6.QtOpenGL import *
elif PYSIDE6:
    from PySide6.QtGui import QOpenGLContext, QOpenGLContextGroup
    from PySide6.QtOpenGL import *
elif PYSIDE2:
    from PySide2.QtGui import (
        QOpenGLBuffer,
        QOpenGLContext,
        QOpenGLContextGroup,
        QOpenGLDebugLogger,
        QOpenGLDebugMessage,
        QOpenGLFramebufferObject,
        QOpenGLFramebufferObjectFormat,
        QOpenGLPixelTransferOptions,
        QOpenGLShader,
        QOpenGLShaderProgram,
        QOpenGLTexture,
        QOpenGLTextureBlitter,
        QOpenGLVersionProfile,
        QOpenGLVertexArrayObject,
        QOpenGLWindow,
    )
    from PySide2.QtOpenGL import *

    # These are not present on some architectures such as armhf
    with contextlib.suppress(ImportError):
        from PySide2.QtGui import QOpenGLTimeMonitor, QOpenGLTimerQuery
