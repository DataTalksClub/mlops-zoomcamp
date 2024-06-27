# -----------------------------------------------------------------------------
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtCore classes and functions."""
import contextlib
from typing import TYPE_CHECKING

from packaging.version import parse

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6
from . import QT_VERSION as _qt_version
from ._utils import possibly_static_exec, possibly_static_exec_

if PYQT5:
    from PyQt5.QtCore import *
    from PyQt5.QtCore import pyqtBoundSignal as SignalInstance
    from PyQt5.QtCore import pyqtProperty as Property
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot

    try:
        from PyQt5.QtCore import Q_ENUM as QEnum

        del Q_ENUM
    except ImportError:  # fallback for Qt5.9
        from PyQt5.QtCore import Q_ENUMS as QEnum

        del Q_ENUMS
    from PyQt5.QtCore import QT_VERSION_STR as __version__

    # Those are imported from `import *`
    del pyqtSignal, pyqtBoundSignal, pyqtSlot, pyqtProperty, QT_VERSION_STR

elif PYQT6:
    from PyQt6 import QtCore
    from PyQt6.QtCore import *
    from PyQt6.QtCore import QT_VERSION_STR as __version__
    from PyQt6.QtCore import pyqtBoundSignal as SignalInstance
    from PyQt6.QtCore import pyqtEnum as QEnum
    from PyQt6.QtCore import pyqtProperty as Property
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtCore import pyqtSlot as Slot

    # For issue #311
    # Seems like there is an error with sip. Without first
    # trying to import `PyQt6.QtGui.Qt`, some functions like
    # `PyQt6.QtCore.Qt.mightBeRichText` are missing.
    if not TYPE_CHECKING:
        with contextlib.suppress(ImportError):
            from PyQt6.QtGui import Qt

    # Map missing methods
    QCoreApplication.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QCoreApplication,
        *args,
        **kwargs,
    )
    QEventLoop.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QThread.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)

    # Those are imported from `import *`
    del (
        pyqtSignal,
        pyqtBoundSignal,
        pyqtSlot,
        pyqtProperty,
        pyqtEnum,
        QT_VERSION_STR,
    )

    # Allow unscoped access for enums inside the QtCore module
    from .enums_compat import promote_enums

    promote_enums(QtCore)
    del QtCore

    # Alias deprecated ItemDataRole enum values removed in Qt6
    Qt.BackgroundColorRole = (
        Qt.ItemDataRole.BackgroundColorRole
    ) = Qt.BackgroundRole
    Qt.TextColorRole = Qt.ItemDataRole.TextColorRole = Qt.ForegroundRole

    # Alias for MiddleButton removed in PyQt6 but available in PyQt5, PySide2 and PySide6
    Qt.MidButton = Qt.MiddleButton

    # Add removed definition for `Qt.ItemFlags` as an alias of `Qt.ItemFlag`
    # passing as default value 0 in the same way PySide6 6.5+ does.
    # Note that for PyQt5 and PySide2 those definitions are two different classes
    # (one is the flag definition and the other the enum definition)
    Qt.ItemFlags = lambda value=0: Qt.ItemFlag(value)

elif PYSIDE2:
    import PySide2.QtCore
    from PySide2.QtCore import *

    __version__ = PySide2.QtCore.__version__

    # Missing QtGui utility functions on Qt
    if getattr(Qt, "mightBeRichText", None) is None:
        try:
            from PySide2.QtGui import Qt as guiQt

            Qt.mightBeRichText = guiQt.mightBeRichText
            del guiQt
        except ImportError:
            # Fails with PySide2 5.12.0
            pass

    QCoreApplication.exec = lambda *args, **kwargs: possibly_static_exec_(
        QCoreApplication,
        *args,
        **kwargs,
    )
    QEventLoop.exec = lambda self, *args, **kwargs: self.exec_(*args, **kwargs)
    QThread.exec = lambda self, *args, **kwargs: self.exec_(*args, **kwargs)
    QTextStreamManipulator.exec = lambda self, *args, **kwargs: self.exec_(
        *args,
        **kwargs,
    )

elif PYSIDE6:
    import PySide6.QtCore
    from PySide6.QtCore import *

    __version__ = PySide6.QtCore.__version__

    # Missing QtGui utility functions on Qt
    if getattr(Qt, "mightBeRichText", None) is None:
        from PySide6.QtGui import Qt as guiQt

        Qt.mightBeRichText = guiQt.mightBeRichText
        del guiQt

    # Alias deprecated ItemDataRole enum values removed in Qt6
    Qt.BackgroundColorRole = (
        Qt.ItemDataRole.BackgroundColorRole
    ) = Qt.BackgroundRole
    Qt.TextColorRole = Qt.ItemDataRole.TextColorRole = Qt.ForegroundRole
    Qt.MidButton = Qt.MiddleButton

    # Map DeprecationWarning methods
    QCoreApplication.exec_ = lambda *args, **kwargs: possibly_static_exec(
        QCoreApplication,
        *args,
        **kwargs,
    )
    QEventLoop.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QThread.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QTextStreamManipulator.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )

    # Passing as default value 0 in the same way PySide6 6.3.2 does for the `Qt.ItemFlags` definition.
    if parse(_qt_version) > parse("6.3"):
        Qt.ItemFlags = lambda value=0: Qt.ItemFlag(value)

# For issue #153 and updated for issue #305
if PYQT5 or PYQT6:
    QDate.toPython = lambda self, *args, **kwargs: self.toPyDate(
        *args,
        **kwargs,
    )
    QDateTime.toPython = lambda self, *args, **kwargs: self.toPyDateTime(
        *args,
        **kwargs,
    )
    QTime.toPython = lambda self, *args, **kwargs: self.toPyTime(
        *args,
        **kwargs,
    )
if PYSIDE2 or PYSIDE6:
    QDate.toPyDate = lambda self, *args, **kwargs: self.toPython(
        *args,
        **kwargs,
    )
    QDateTime.toPyDateTime = lambda self, *args, **kwargs: self.toPython(
        *args,
        **kwargs,
    )
    QTime.toPyTime = lambda self, *args, **kwargs: self.toPython(
        *args,
        **kwargs,
    )

# Mirror https://github.com/spyder-ide/qtpy/pull/393
if PYQT5 or PYSIDE2:
    QLibraryInfo.path = QLibraryInfo.location
    QLibraryInfo.LibraryPath = QLibraryInfo.LibraryLocation
if PYQT6 or PYSIDE6:
    QLibraryInfo.location = QLibraryInfo.path
    QLibraryInfo.LibraryLocation = QLibraryInfo.LibraryPath
