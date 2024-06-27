"""Test QtCore."""

import enum
import sys
from datetime import date, datetime, time

import pytest
from packaging.version import parse

from qtpy import (
    PYQT5,
    PYQT6,
    PYQT_VERSION,
    PYSIDE2,
    PYSIDE_VERSION,
    QtCore,
)

_now = datetime.now()
# Make integer milliseconds; `floor` here, don't `round`!
NOW = _now.replace(microsecond=(_now.microsecond // 1000 * 1000))


def test_qtmsghandler():
    """Test qtpy.QtMsgHandler"""
    assert QtCore.qInstallMessageHandler is not None


@pytest.mark.parametrize("method", ["toPython", "toPyDateTime"])
def test_QDateTime_toPython_and_toPyDateTime(method):
    """Test `QDateTime.toPython` and `QDateTime.toPyDateTime`"""
    q_datetime = QtCore.QDateTime(NOW)
    py_datetime = getattr(q_datetime, method)()
    assert isinstance(py_datetime, datetime)
    assert py_datetime == NOW


@pytest.mark.parametrize("method", ["toPython", "toPyDate"])
def test_QDate_toPython_and_toPyDate(method):
    """Test `QDate.toPython` and `QDate.toPyDate`"""
    q_date = QtCore.QDateTime(NOW).date()
    py_date = getattr(q_date, method)()
    assert isinstance(py_date, date)
    assert py_date == NOW.date()


@pytest.mark.parametrize("method", ["toPython", "toPyTime"])
def test_QTime_toPython_and_toPyTime(method):
    """Test `QTime.toPython` and `QTime.toPyTime`"""
    q_time = QtCore.QDateTime(NOW).time()
    py_time = getattr(q_time, method)()
    assert isinstance(py_time, time)
    assert py_time == NOW.time()


def test_qeventloop_exec(qtbot):
    """Test `QEventLoop.exec_` and `QEventLoop.exec`"""
    assert QtCore.QEventLoop.exec_ is not None
    assert QtCore.QEventLoop.exec is not None
    event_loop = QtCore.QEventLoop(None)
    QtCore.QTimer.singleShot(100, event_loop.quit)
    event_loop.exec_()
    QtCore.QTimer.singleShot(100, event_loop.quit)
    event_loop.exec()


def test_qthread_exec():
    """Test `QThread.exec_` and `QThread.exec_`"""
    assert QtCore.QThread.exec_ is not None
    assert QtCore.QThread.exec is not None


@pytest.mark.skipif(
    PYSIDE2 and parse(PYSIDE_VERSION) < parse("5.15"),
    reason="QEnum macro doesn't seem to be present on PySide2 <5.15",
)
def test_qenum():
    """Test QEnum macro"""

    class EnumTest(QtCore.QObject):
        class Position(enum.IntEnum):
            West = 0
            North = 1
            South = 2
            East = 3

        QtCore.QEnum(Position)

    obj = EnumTest()
    assert obj.metaObject().enumerator(0).name() == "Position"


def test_QLibraryInfo_location_and_path():
    """Test `QLibraryInfo.location` and `QLibraryInfo.path`"""
    assert QtCore.QLibraryInfo.location is not None
    assert (
        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PrefixPath)
        is not None
    )
    assert QtCore.QLibraryInfo.path is not None
    assert QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.PrefixPath) is not None


def test_QLibraryInfo_LibraryLocation_and_LibraryPath():
    """Test `QLibraryInfo.LibraryLocation` and `QLibraryInfo.LibraryPath`"""
    assert QtCore.QLibraryInfo.LibraryLocation is not None
    assert QtCore.QLibraryInfo.LibraryPath is not None


def test_QCoreApplication_exec_(qapp):
    """Test `QtCore.QCoreApplication.exec_`"""
    assert QtCore.QCoreApplication.exec_ is not None
    app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtCore.QCoreApplication.instance().quit)
    QtCore.QCoreApplication.exec_()
    app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtCore.QCoreApplication.instance().quit)
    app.exec_()


def test_QCoreApplication_exec(qapp):
    """Test `QtCore.QCoreApplication.exec`"""
    assert QtCore.QCoreApplication.exec is not None
    app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtCore.QCoreApplication.instance().quit)
    QtCore.QCoreApplication.exec()
    app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtCore.QCoreApplication.instance().quit)
    app.exec()


@pytest.mark.skipif(
    PYQT5 or PYQT6,
    reason="Doesn't seem to be present on PyQt5 and PyQt6",
)
def test_qtextstreammanipulator_exec():
    """Test `QTextStreamManipulator.exec_` and `QTextStreamManipulator.exec`"""
    assert QtCore.QTextStreamManipulator.exec_ is not None
    assert QtCore.QTextStreamManipulator.exec is not None


@pytest.mark.skipif(
    PYSIDE2 or PYQT6,
    reason="Doesn't seem to be present on PySide2 and PyQt6",
)
def test_QtCore_SignalInstance():
    class ClassWithSignal(QtCore.QObject):
        signal = QtCore.Signal()

    instance = ClassWithSignal()

    assert isinstance(instance.signal, QtCore.SignalInstance)


@pytest.mark.skipif(
    PYQT5 and PYQT_VERSION.startswith("5.9"),
    reason="A specific setup with at least sip 4.9.9 is needed for PyQt5 5.9.*"
    "to work with scoped enum access",
)
def test_enum_access():
    """Test scoped and unscoped enum access for qtpy.QtCore.*."""
    assert (
        QtCore.QAbstractAnimation.Stopped
        == QtCore.QAbstractAnimation.State.Stopped
    )
    assert QtCore.QEvent.ActionAdded == QtCore.QEvent.Type.ActionAdded
    assert QtCore.Qt.AlignLeft == QtCore.Qt.AlignmentFlag.AlignLeft
    assert QtCore.Qt.Key_Return == QtCore.Qt.Key.Key_Return
    assert QtCore.Qt.transparent == QtCore.Qt.GlobalColor.transparent
    assert QtCore.Qt.Widget == QtCore.Qt.WindowType.Widget
    assert QtCore.Qt.BackButton == QtCore.Qt.MouseButton.BackButton
    assert QtCore.Qt.XButton1 == QtCore.Qt.MouseButton.XButton1
    assert (
        QtCore.Qt.BackgroundColorRole
        == QtCore.Qt.ItemDataRole.BackgroundColorRole
    )
    assert QtCore.Qt.TextColorRole == QtCore.Qt.ItemDataRole.TextColorRole
    assert QtCore.Qt.MidButton == QtCore.Qt.MouseButton.MiddleButton


@pytest.mark.skipif(
    PYSIDE2 and PYSIDE_VERSION.startswith("5.12.0"),
    reason="Utility functions unavailable for PySide2 5.12.0",
)
def test_qtgui_namespace_mightBeRichText():
    """
    Test included elements (mightBeRichText) from module QtGui.

    See: https://doc.qt.io/qt-5/qt-sub-qtgui.html
    """
    assert QtCore.Qt.mightBeRichText is not None


def test_itemflags_typedef():
    """
    Test existence of `QFlags<ItemFlag>` typedef `ItemFlags` that was removed from PyQt6
    """
    assert QtCore.Qt.ItemFlags is not None
    assert QtCore.Qt.ItemFlags() == QtCore.Qt.ItemFlag(0)
