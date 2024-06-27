"""Test QtWidgets."""
import contextlib
import sys
from time import sleep

import pytest
from pytestqt.exceptions import TimeoutError

from qtpy import (
    PYQT5,
    PYQT6,
    PYQT_VERSION,
    PYSIDE2,
    PYSIDE6,
    QtCore,
    QtGui,
    QtWidgets,
)
from qtpy.tests.utils import not_using_conda, using_conda


def test_qtextedit_functions(qtbot, pdf_writer):
    """Test functions mapping for QtWidgets.QTextEdit."""
    assert QtWidgets.QTextEdit.setTabStopWidth
    assert QtWidgets.QTextEdit.tabStopWidth
    assert QtWidgets.QTextEdit.print_
    textedit_widget = QtWidgets.QTextEdit(None)
    textedit_widget.setTabStopWidth(90)
    assert textedit_widget.tabStopWidth() == 90
    print_device, output_path = pdf_writer
    textedit_widget.print_(print_device)
    assert output_path.exists()


def test_qlineedit_functions():
    """Test functions mapping for QtWidgets.QLineEdit"""
    assert QtWidgets.QLineEdit.getTextMargins


def test_what_moved_to_qtgui_in_qt6():
    """Test that we move back what has been moved to QtGui in Qt6"""
    assert QtWidgets.QAction is not None
    assert QtWidgets.QActionGroup is not None
    assert QtWidgets.QFileSystemModel is not None
    assert QtWidgets.QShortcut is not None
    assert QtWidgets.QUndoCommand is not None


def test_qplaintextedit_functions(qtbot, pdf_writer):
    """Test functions mapping for QtWidgets.QPlainTextEdit."""
    assert QtWidgets.QPlainTextEdit.setTabStopWidth
    assert QtWidgets.QPlainTextEdit.tabStopWidth
    assert QtWidgets.QPlainTextEdit.print_
    plaintextedit_widget = QtWidgets.QPlainTextEdit(None)
    plaintextedit_widget.setTabStopWidth(90)
    assert plaintextedit_widget.tabStopWidth() == 90
    print_device, output_path = pdf_writer
    plaintextedit_widget.print_(print_device)
    assert output_path.exists()


def test_QApplication_exec_():
    """Test `QtWidgets.QApplication.exec_`"""
    assert QtWidgets.QApplication.exec_ is not None
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtWidgets.QApplication.instance().quit)
    QtWidgets.QApplication.exec_()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
        [sys.executable, __file__],
    )
    assert app is not None
    QtCore.QTimer.singleShot(100, QtWidgets.QApplication.instance().quit)
    app.exec_()


@pytest.mark.skipif(
    sys.platform == "darwin" and sys.version_info[:2] == (3, 7),
    reason="Stalls on macOS CI with Python 3.7",
)
def test_qdialog_functions(qtbot):
    """Test functions mapping for QtWidgets.QDialog."""
    assert QtWidgets.QDialog.exec_
    dialog = QtWidgets.QDialog(None)
    QtCore.QTimer.singleShot(100, dialog.accept)
    dialog.exec_()


@pytest.mark.skipif(
    sys.platform == "darwin" and sys.version_info[:2] == (3, 7),
    reason="Stalls on macOS CI with Python 3.7",
)
def test_qdialog_subclass(qtbot):
    """Test functions mapping for QtWidgets.QDialog when using a subclass"""
    assert QtWidgets.QDialog.exec_

    class CustomDialog(QtWidgets.QDialog):
        def __init__(self):
            super().__init__(None)
            self.setWindowTitle("Testing")

    assert CustomDialog.exec_
    dialog = CustomDialog()
    QtCore.QTimer.singleShot(100, dialog.accept)
    dialog.exec_()


@pytest.mark.skipif(
    sys.platform == "darwin" and sys.version_info[:2] == (3, 7),
    reason="Stalls on macOS CI with Python 3.7",
)
def test_QMenu_functions(qtbot):
    """Test functions mapping for `QtWidgets.QMenu`."""
    # A window is required for static calls
    window = QtWidgets.QMainWindow()
    menu = QtWidgets.QMenu(window)
    menu.addAction("QtPy")
    menu.addAction("QtPy with a shortcut", QtGui.QKeySequence.UnknownKey)
    menu.addAction(
        QtGui.QIcon(),
        "QtPy with an icon and a shortcut",
        QtGui.QKeySequence.UnknownKey,
    )
    window.show()

    with qtbot.waitExposed(window):
        # Call `exec_` of a `QMenu` instance
        QtCore.QTimer.singleShot(100, menu.close)
        menu.exec_()

        # Call static `QMenu.exec_`
        QtCore.QTimer.singleShot(
            100,
            lambda: qtbot.keyClick(
                QtWidgets.QApplication.widgetAt(1, 1),
                QtCore.Qt.Key_Escape,
            ),
        )
        QtWidgets.QMenu.exec_(menu.actions(), QtCore.QPoint(1, 1))


@pytest.mark.skipif(
    sys.platform == "darwin" and sys.version_info[:2] == (3, 7),
    reason="Stalls on macOS CI with Python 3.7",
)
def test_QToolBar_functions(qtbot):
    """Test `QtWidgets.QToolBar.addAction` compatibility with Qt6 arguments' order."""
    toolbar = QtWidgets.QToolBar()
    toolbar.addAction("QtPy with a shortcut", QtGui.QKeySequence.UnknownKey)
    toolbar.addAction(
        QtGui.QIcon(),
        "QtPy with an icon and a shortcut",
        QtGui.QKeySequence.UnknownKey,
    )


@pytest.mark.skipif(
    PYQT5 and PYQT_VERSION.startswith("5.9"),
    reason="A specific setup with at least sip 4.9.9 is needed for PyQt5 5.9.*"
    "to work with scoped enum access",
)
def test_enum_access():
    """Test scoped and unscoped enum access for qtpy.QtWidgets.*."""
    assert (
        QtWidgets.QFileDialog.AcceptOpen
        == QtWidgets.QFileDialog.AcceptMode.AcceptOpen
    )
    assert (
        QtWidgets.QMessageBox.InvalidRole
        == QtWidgets.QMessageBox.ButtonRole.InvalidRole
    )
    assert QtWidgets.QStyle.State_None == QtWidgets.QStyle.StateFlag.State_None
    assert (
        QtWidgets.QSlider.TicksLeft
        == QtWidgets.QSlider.TickPosition.TicksAbove
    )
    assert (
        QtWidgets.QStyle.SC_SliderGroove
        == QtWidgets.QStyle.SubControl.SC_SliderGroove
    )


def test_opengl_imports():
    """
    Test for presence of QOpenGLWidget.

    QOpenGLWidget was a member of QtWidgets in Qt5, but moved to QtOpenGLWidgets in Qt6.
    QtPy makes QOpenGLWidget available in QtWidgets to maintain compatibility.
    """
    assert QtWidgets.QOpenGLWidget is not None


@pytest.mark.skipif(
    sys.platform == "darwin"
    and sys.version_info[:2] == (3, 7)
    and (PYQT5 or PYSIDE2),
    reason="Crashes on macOS with Python 3.7 with 'Illegal instruction: 4'",
)
@pytest.mark.parametrize("keyword", ["dir", "directory"])
@pytest.mark.parametrize("instance", [True, False])
def test_qfiledialog_dir_compat(tmp_path, qtbot, keyword, instance):
    """
    This function is testing if the decorators that renamed the dir/directory
    keyword are working.

    It may stop working if the Qt bindings do some overwriting of the methods
    in constructor. It should not happen, but the PySide team
    did similar things in the past (like overwriting enum module in
    PySide6==6.3.2).

    keyword: str
        The keyword that should be used in the function call.
    instance: bool
        If True, the function is called on the instance of the QFileDialog,
        otherwise on the class.
    """

    class CloseThread(QtCore.QThread):
        """
        On some implementations the `getExistingDirectory` functions starts own
        event loop that will not trigger QTimer started before the call. Until
        the dialog is closed the main event loop will be stopped.

        Because of this it is required to use the thread to interact with the
        dialog.
        """

        def run(self, allow_restart=True):
            sleep(0.5)
            need_restart = allow_restart
            app = QtWidgets.QApplication.instance()
            for dlg in app.topLevelWidgets():
                if (
                    not isinstance(dlg, QtWidgets.QFileDialog)
                    or dlg.isHidden()
                ):
                    continue
                # "when implemented this I try to use:
                # * dlg.close() - On Qt6 it will close the dialog, but it will
                #   not restart the main event loop.
                # * dlg.accept() - It ends with information thar `accept` and
                #   `reject` of such created dialog can not be called.
                # * accept dialog with enter - It works, but it cannot be
                #   called to early after dialog is shown
                qtbot.keyClick(dlg, QtCore.Qt.Key_Enter)
                need_restart = False
            sleep(0.1)
            for dlg in app.topLevelWidgets():
                # As described above, it may happen that dialog is not closed after first using enter.
                # in such case we call `run` function again. The 0.5s sleep is enough for the second enter to close the dialog.
                if (
                    not isinstance(dlg, QtWidgets.QFileDialog)
                    or dlg.isHidden()
                ):
                    continue
                self.run(allow_restart=False)
                return

            if need_restart:
                self.run()

    # We need to use the `DontUseNativeDialog` option to be able to interact
    # with it from code.
    try:
        opt = QtWidgets.QFileDialog.Option.DontUseNativeDialog
    except AttributeError:
        # old qt5 bindings
        opt = QtWidgets.QFileDialog.DontUseNativeDialog

    kwargs = {
        "caption": "Select a directory",
        keyword: str(tmp_path),
        "options": opt,
    }

    thr = CloseThread()
    thr.start()
    qtbot.waitUntil(thr.isRunning, timeout=1000)
    dlg = QtWidgets.QFileDialog() if instance else QtWidgets.QFileDialog
    dlg.getExistingDirectory(**kwargs)
    qtbot.waitUntil(thr.isFinished, timeout=3000)


def test_qfiledialog_flags_typedef():
    """
    Test existence of `QFlags<Option>` typedef `Options` that was removed from PyQt6
    """
    assert QtWidgets.QFileDialog.Options is not None
    assert QtWidgets.QFileDialog.Options() == QtWidgets.QFileDialog.Option(0)
