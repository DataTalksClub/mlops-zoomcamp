# -----------------------------------------------------------------------------
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides widget classes and functions."""
from functools import partialmethod

from packaging.version import parse

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6
from . import QT_VERSION as _qt_version
from ._utils import (
    add_action,
    getattr_missing_optional_dep,
    possibly_static_exec,
    static_method_kwargs_wrapper,
)

_missing_optional_names = {}


def __getattr__(name):
    """Custom getattr to chain and wrap errors due to missing optional deps."""
    raise getattr_missing_optional_dep(
        name,
        module_name=__name__,
        optional_names=_missing_optional_names,
    )


if PYQT5:
    from PyQt5.QtWidgets import *
elif PYQT6:
    from PyQt6 import QtWidgets
    from PyQt6.QtGui import (
        QAction,
        QActionGroup,
        QFileSystemModel,
        QShortcut,
        QUndoCommand,
    )
    from PyQt6.QtWidgets import *

    # Attempt to import QOpenGLWidget, but if that fails,
    # don't raise an exception until the name is explicitly accessed.
    # See https://github.com/spyder-ide/qtpy/pull/387/
    try:
        from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    except ImportError as error:
        _missing_optional_names["QOpenGLWidget"] = {
            "name": "PyQt6.QtOpenGLWidgets",
            "missing_package": "pyopengl",
            "import_error": error,
        }

    # Map missing/renamed methods
    QTextEdit.setTabStopWidth = (
        lambda self, *args, **kwargs: self.setTabStopDistance(*args, **kwargs)
    )
    QTextEdit.tabStopWidth = (
        lambda self, *args, **kwargs: self.tabStopDistance(*args, **kwargs)
    )
    QTextEdit.print_ = lambda self, *args, **kwargs: self.print(
        *args,
        **kwargs,
    )
    QPlainTextEdit.setTabStopWidth = (
        lambda self, *args, **kwargs: self.setTabStopDistance(*args, **kwargs)
    )
    QPlainTextEdit.tabStopWidth = (
        lambda self, *args, **kwargs: self.tabStopDistance(*args, **kwargs)
    )
    QPlainTextEdit.print_ = lambda self, *args, **kwargs: self.print(
        *args,
        **kwargs,
    )
    QApplication.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QApplication,
        *args,
        **kwargs,
    )
    QDialog.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QMenu.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QMenu,
        *args,
        **kwargs,
    )
    QLineEdit.getTextMargins = lambda self: (
        self.textMargins().left(),
        self.textMargins().top(),
        self.textMargins().right(),
        self.textMargins().bottom(),
    )

    # Add removed definition for `QFileDialog.Options` as an alias of `QFileDialog.Option`
    # passing as default value 0 in the same way PySide6 6.5+ does.
    # Note that for PyQt5 and PySide2 those definitions are two different classes
    # (one is the flag definition and the other the enum definition)
    QFileDialog.Options = lambda value=0: QFileDialog.Option(value)

    # Allow unscoped access for enums inside the QtWidgets module
    from .enums_compat import promote_enums

    promote_enums(QtWidgets)
    del QtWidgets
elif PYSIDE2:
    from PySide2.QtWidgets import *
elif PYSIDE6:
    from PySide6.QtGui import QAction, QActionGroup, QShortcut, QUndoCommand
    from PySide6.QtWidgets import *

    # Attempt to import QOpenGLWidget, but if that fails,
    # don't raise an exception until the name is explicitly accessed.
    # See https://github.com/spyder-ide/qtpy/pull/387/
    try:
        from PySide6.QtOpenGLWidgets import QOpenGLWidget
    except ImportError as error:
        _missing_optional_names["QOpenGLWidget"] = {
            "name": "PySide6.QtOpenGLWidgets",
            "missing_package": "pyopengl",
            "import_error": error,
        }

    # Map missing/renamed methods
    QTextEdit.setTabStopWidth = (
        lambda self, *args, **kwargs: self.setTabStopDistance(*args, **kwargs)
    )
    QTextEdit.tabStopWidth = (
        lambda self, *args, **kwargs: self.tabStopDistance(*args, **kwargs)
    )
    QPlainTextEdit.setTabStopWidth = (
        lambda self, *args, **kwargs: self.setTabStopDistance(*args, **kwargs)
    )
    QPlainTextEdit.tabStopWidth = (
        lambda self, *args, **kwargs: self.tabStopDistance(*args, **kwargs)
    )
    QLineEdit.getTextMargins = lambda self: (
        self.textMargins().left(),
        self.textMargins().top(),
        self.textMargins().right(),
        self.textMargins().bottom(),
    )

    # Map DeprecationWarning methods
    QApplication.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QApplication,
        *args,
        **kwargs,
    )
    QDialog.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QMenu.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QMenu,
        *args,
        **kwargs,
    )

    # Passing as default value 0 in the same way PySide6 < 6.3.2 does for the `QFileDialog.Options` definition.
    if parse(_qt_version) > parse("6.3"):
        QFileDialog.Options = lambda value=0: QFileDialog.Option(value)


if PYSIDE2 or PYSIDE6:
    # Make PySide2/6 `QFileDialog` static methods accept the `directory` kwarg as `dir`
    QFileDialog.getExistingDirectory = static_method_kwargs_wrapper(
        QFileDialog.getExistingDirectory,
        "directory",
        "dir",
    )
    QFileDialog.getOpenFileName = static_method_kwargs_wrapper(
        QFileDialog.getOpenFileName,
        "directory",
        "dir",
    )
    QFileDialog.getOpenFileNames = static_method_kwargs_wrapper(
        QFileDialog.getOpenFileNames,
        "directory",
        "dir",
    )
    QFileDialog.getSaveFileName = static_method_kwargs_wrapper(
        QFileDialog.getSaveFileName,
        "directory",
        "dir",
    )
else:
    # Make PyQt5/6 `QFileDialog` static methods accept the `dir` kwarg as `directory`
    QFileDialog.getExistingDirectory = static_method_kwargs_wrapper(
        QFileDialog.getExistingDirectory,
        "dir",
        "directory",
    )
    QFileDialog.getOpenFileName = static_method_kwargs_wrapper(
        QFileDialog.getOpenFileName,
        "dir",
        "directory",
    )
    QFileDialog.getOpenFileNames = static_method_kwargs_wrapper(
        QFileDialog.getOpenFileNames,
        "dir",
        "directory",
    )
    QFileDialog.getSaveFileName = static_method_kwargs_wrapper(
        QFileDialog.getSaveFileName,
        "dir",
        "directory",
    )

# Make `addAction` compatible with Qt6 >= 6.3
if PYQT5 or PYSIDE2 or parse(_qt_version) < parse("6.3"):
    QMenu.addAction = partialmethod(add_action, old_add_action=QMenu.addAction)
    QToolBar.addAction = partialmethod(
        add_action,
        old_add_action=QToolBar.addAction,
    )
