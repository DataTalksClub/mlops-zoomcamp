"""Test QtGui."""

import sys

import pytest

from qtpy import (
    PYQT5,
    PYQT_VERSION,
    PYSIDE2,
    PYSIDE6,
    QtCore,
    QtGui,
    QtWidgets,
)
from qtpy.tests.utils import not_using_conda


def test_qfontmetrics_width(qtbot):
    """Test QFontMetrics and QFontMetricsF width"""
    assert QtGui.QFontMetrics.width is not None
    assert QtGui.QFontMetricsF.width is not None
    font = QtGui.QFont("times", 24)
    font_metrics = QtGui.QFontMetrics(font)
    font_metricsF = QtGui.QFontMetricsF(font)
    width = font_metrics.width("Test")
    widthF = font_metricsF.width("Test")
    assert width in range(40, 62)
    assert 39 <= widthF <= 63


def test_qdrag_functions(qtbot):
    """Test functions mapping for QtGui.QDrag."""
    assert QtGui.QDrag.exec_ is not None
    drag = QtGui.QDrag(None)
    drag.exec_()


def test_QGuiApplication_exec_():
    """Test `QtGui.QGuiApplication.exec_`"""
    assert QtGui.QGuiApplication.exec_ is not None
    app = QtGui.QGuiApplication.instance() or QtGui.QGuiApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtGui.QGuiApplication.instance().quit)
    QtGui.QGuiApplication.exec_()
    app = QtGui.QGuiApplication.instance() or QtGui.QGuiApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtGui.QGuiApplication.instance().quit)
    app.exec_()


def test_what_moved_to_qtgui_in_qt6():
    """Test what has been moved to QtGui in Qt6"""
    assert QtGui.QAction is not None
    assert QtGui.QActionGroup is not None
    assert QtGui.QFileSystemModel is not None
    assert QtGui.QShortcut is not None
    assert QtGui.QUndoCommand is not None


def test_qtextdocument_functions(pdf_writer):
    """Test functions mapping for QtGui.QTextDocument."""
    assert QtGui.QTextDocument.print_ is not None
    text_document = QtGui.QTextDocument("Test")
    print_device, output_path = pdf_writer
    text_document.print_(print_device)
    assert output_path.exists()


@pytest.mark.skipif(
    PYQT5 and PYQT_VERSION.startswith("5.9"),
    reason="A specific setup with at least sip 4.9.9 is needed for PyQt5 5.9.*"
    "to work with scoped enum access",
)
def test_enum_access():
    """Test scoped and unscoped enum access for qtpy.QtWidgets.*."""
    assert QtGui.QColor.Rgb == QtGui.QColor.Spec.Rgb
    assert QtGui.QFont.AllUppercase == QtGui.QFont.Capitalization.AllUppercase
    assert QtGui.QIcon.Normal == QtGui.QIcon.Mode.Normal
    assert QtGui.QImage.Format_Invalid == QtGui.QImage.Format.Format_Invalid


@pytest.mark.skipif(
    sys.platform == "darwin" and sys.version_info[:2] == (3, 7),
    reason="Stalls on macOS CI with Python 3.7",
)
def test_QSomethingEvent_pos_functions(qtbot):
    """
    Test `QMouseEvent.pos` and related functions removed in Qt 6,
    and `QMouseEvent.position`, etc., missing from Qt 5.
    """

    class Window(QtWidgets.QMainWindow):
        def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
            assert event.globalPos() - event.pos() == self.mapToParent(
                QtCore.QPoint(0, 0),
            )
            assert event.pos().x() == event.x()
            assert event.pos().y() == event.y()
            assert event.globalPos().x() == event.globalX()
            assert event.globalPos().y() == event.globalY()
            assert event.position().x() == event.pos().x()
            assert event.position().y() == event.pos().y()
            assert event.globalPosition().x() == event.globalPos().x()
            assert event.globalPosition().y() == event.globalPos().y()

            event.accept()

    window = Window()
    window.setMinimumSize(320, 240)  # ensure the window is of sufficient size
    window.show()

    with qtbot.waitExposed(window):
        qtbot.mouseMove(window, QtCore.QPoint(42, 6 * 9))
        qtbot.mouseDClick(window, QtCore.Qt.LeftButton)

    # the rest of the functions are not actually tested
    # QSinglePointEvent (Qt6) child classes checks
    for _class in ("QNativeGestureEvent", "QEnterEvent", "QTabletEvent"):
        for _function in (
            "pos",
            "x",
            "y",
            "globalPos",
            "globalX",
            "globalY",
            "position",
            "globalPosition",
        ):
            assert hasattr(getattr(QtGui, _class), _function)

    # QHoverEvent checks
    for _function in ("pos", "x", "y", "position"):
        assert hasattr(QtGui.QHoverEvent, _function)

    # QDropEvent and child classes checks
    for _class in ("QDropEvent", "QDragMoveEvent", "QDragEnterEvent"):
        for _function in ("pos", "posF", "position"):
            assert hasattr(getattr(QtGui, _class), _function)


@pytest.mark.skipif(
    not (PYSIDE2 or PYSIDE6),
    reason="PySide{2,6} specific test",
)
def test_qtextcursor_moveposition():
    """Test monkeypatched QTextCursor.movePosition"""
    doc = QtGui.QTextDocument("foo bar baz")
    cursor = QtGui.QTextCursor(doc)

    assert not cursor.movePosition(QtGui.QTextCursor.Start)
    assert cursor.movePosition(
        QtGui.QTextCursor.EndOfWord,
        mode=QtGui.QTextCursor.KeepAnchor,
    )
    assert cursor.selectedText() == "foo"

    assert cursor.movePosition(QtGui.QTextCursor.Start)
    assert cursor.movePosition(
        QtGui.QTextCursor.WordRight,
        n=2,
        mode=QtGui.QTextCursor.KeepAnchor,
    )
    assert cursor.selectedText() == "foo bar "

    assert cursor.movePosition(QtGui.QTextCursor.Start)
    assert cursor.position() == cursor.anchor()
    assert cursor.movePosition(
        QtGui.QTextCursor.NextWord,
        QtGui.QTextCursor.KeepAnchor,
        3,
    )
    assert cursor.selectedText() == "foo bar baz"


def test_opengl_imports():
    """
    Test for presence of QOpenGL* classes.

    These classes were members of QtGui in Qt5, but moved to QtOpenGL in Qt6.
    QtPy makes them available in QtGui to maintain compatibility.
    """

    assert QtGui.QOpenGLBuffer is not None
    assert QtGui.QOpenGLContext is not None
    assert QtGui.QOpenGLContextGroup is not None
    assert QtGui.QOpenGLDebugLogger is not None
    assert QtGui.QOpenGLDebugMessage is not None
    assert QtGui.QOpenGLFramebufferObject is not None
    assert QtGui.QOpenGLFramebufferObjectFormat is not None
    assert QtGui.QOpenGLPixelTransferOptions is not None
    assert QtGui.QOpenGLShader is not None
    assert QtGui.QOpenGLShaderProgram is not None
    assert QtGui.QOpenGLTexture is not None
    assert QtGui.QOpenGLTextureBlitter is not None
    assert QtGui.QOpenGLVersionProfile is not None
    assert QtGui.QOpenGLVertexArrayObject is not None
    assert QtGui.QOpenGLWindow is not None
