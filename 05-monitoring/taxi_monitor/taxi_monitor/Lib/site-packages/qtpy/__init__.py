#
# Copyright © 2009- The Spyder Development Team
# Copyright © 2014-2015 Colin Duquesnoy
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
**QtPy** is a shim over the various Python Qt bindings. It is used to write
Qt binding independent libraries or applications.

If one of the APIs has already been imported, then it will be used.

Otherwise, the shim will automatically select the first available API (PyQt5, PySide2,
PyQt6 and PySide6); in that case, you can force the use of one
specific bindings (e.g. if your application is using one specific bindings and
you need to use library that use QtPy) by setting up the ``QT_API`` environment
variable.

PyQt5
=====

For PyQt5, you don't have to set anything as it will be used automatically::

    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PySide2
======

Set the QT_API environment variable to 'pyside2' before importing other
packages::

    >>> import os
    >>> os.environ['QT_API'] = 'pyside2'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PyQt6
=====

    >>> import os
    >>> os.environ['QT_API'] = 'pyqt6'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

PySide6
=======

    >>> import os
    >>> os.environ['QT_API'] = 'pyside6'
    >>> from qtpy import QtGui, QtWidgets, QtCore
    >>> print(QtWidgets.QWidget)

"""

import contextlib
import os
import platform
import sys
import warnings

from packaging.version import parse

# Version of QtPy
__version__ = "2.4.1"


class PythonQtError(RuntimeError):
    """Generic error superclass for QtPy."""


class PythonQtWarning(RuntimeWarning):
    """Warning class for QtPy."""


class PythonQtValueError(ValueError):
    """Error raised if an invalid QT_API is specified."""


class QtBindingsNotFoundError(PythonQtError, ImportError):
    """Error raised if no bindings could be selected."""

    _msg = "No Qt bindings could be found"

    def __init__(self):
        super().__init__(self._msg)


class QtModuleNotFoundError(ModuleNotFoundError, PythonQtError):
    """Raised when a Python Qt binding submodule is not installed/supported."""

    _msg = "The {name} module was not found."
    _msg_binding = "{binding}"
    _msg_extra = ""

    def __init__(self, *, name, msg=None, **msg_kwargs):
        global API_NAME
        binding = self._msg_binding.format(binding=API_NAME)
        msg = msg or f"{self._msg} {self._msg_extra}".strip()
        msg = msg.format(name=name, binding=binding, **msg_kwargs)
        super().__init__(msg, name=name)


class QtModuleNotInOSError(QtModuleNotFoundError):
    """Raised when a module is not supported on the current operating system."""

    _msg = "{name} does not exist on this operating system."


class QtModuleNotInQtVersionError(QtModuleNotFoundError):
    """Raised when a module is not implemented in the current Qt version."""

    _msg = "{name} does not exist in {version}."

    def __init__(self, *, name, msg=None, **msg_kwargs):
        global QT5, QT6
        version = "Qt5" if QT5 else "Qt6"
        super().__init__(name=name, version=version)


class QtBindingMissingModuleError(QtModuleNotFoundError):
    """Raised when a module is not supported by a given binding."""

    _msg_extra = "It is not currently implemented in {binding}."


class QtModuleNotInstalledError(QtModuleNotFoundError):
    """Raise when a module is supported by the binding, but not installed."""

    _msg_extra = "It must be installed separately"

    def __init__(self, *, missing_package=None, **superclass_kwargs):
        self.missing_package = missing_package
        if missing_package is not None:
            self._msg_extra += " as {missing_package}."
        super().__init__(missing_package=missing_package, **superclass_kwargs)


# Qt API environment variable name
QT_API = "QT_API"

# Names of the expected PyQt5 api
PYQT5_API = ["pyqt5"]

PYQT6_API = ["pyqt6"]

# Names of the expected PySide2 api
PYSIDE2_API = ["pyside2"]

# Names of the expected PySide6 api
PYSIDE6_API = ["pyside6"]

# Minimum supported versions of Qt and the bindings
QT5_VERSION_MIN = PYQT5_VERSION_MIN = "5.9.0"
PYSIDE2_VERSION_MIN = "5.12.0"
QT6_VERSION_MIN = PYQT6_VERSION_MIN = PYSIDE6_VERSION_MIN = "6.2.0"

QT_VERSION_MIN = QT5_VERSION_MIN
PYQT_VERSION_MIN = PYQT5_VERSION_MIN
PYSIDE_VERSION_MIN = PYSIDE2_VERSION_MIN

# Detecting if a binding was specified by the user
binding_specified = QT_API in os.environ

API_NAMES = {
    "pyqt5": "PyQt5",
    "pyside2": "PySide2",
    "pyqt6": "PyQt6",
    "pyside6": "PySide6",
}
API = os.environ.get(QT_API, "pyqt5").lower()
initial_api = API
if API not in API_NAMES:
    raise PythonQtValueError(
        f"Specified QT_API={QT_API.lower()!r} is not in valid options: "
        f"{API_NAMES}",
    )

is_old_pyqt = is_pyqt46 = False
QT5 = PYQT5 = True
QT4 = QT6 = PYQT4 = PYQT6 = PYSIDE = PYSIDE2 = PYSIDE6 = False

PYQT_VERSION = None
PYSIDE_VERSION = None
QT_VERSION = None

# Unless `FORCE_QT_API` is set, use previously imported Qt Python bindings
if not os.environ.get("FORCE_QT_API"):
    if "PyQt5" in sys.modules:
        API = initial_api if initial_api in PYQT5_API else "pyqt5"
    elif "PySide2" in sys.modules:
        API = initial_api if initial_api in PYSIDE2_API else "pyside2"
    elif "PyQt6" in sys.modules:
        API = initial_api if initial_api in PYQT6_API else "pyqt6"
    elif "PySide6" in sys.modules:
        API = initial_api if initial_api in PYSIDE6_API else "pyside6"

if API in PYQT5_API:
    try:
        from PyQt5.QtCore import (
            PYQT_VERSION_STR as PYQT_VERSION,
        )
        from PyQt5.QtCore import (
            QT_VERSION_STR as QT_VERSION,
        )

        QT5 = PYQT5 = True

        if sys.platform == "darwin":
            macos_version = parse(platform.mac_ver()[0])
            qt_ver = parse(QT_VERSION)
            if macos_version < parse("10.10") and qt_ver >= parse("5.9"):
                raise PythonQtError(
                    "Qt 5.9 or higher only works in "
                    "macOS 10.10 or higher. Your "
                    "program will fail in this "
                    "system.",
                )
            elif macos_version < parse("10.11") and qt_ver >= parse("5.11"):
                raise PythonQtError(
                    "Qt 5.11 or higher only works in "
                    "macOS 10.11 or higher. Your "
                    "program will fail in this "
                    "system.",
                )

            del macos_version
            del qt_ver
    except ImportError:
        API = "pyside2"
    else:
        os.environ[QT_API] = API

if API in PYSIDE2_API:
    try:
        from PySide2 import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide2.QtCore import __version__ as QT_VERSION  # analysis:ignore

        PYQT5 = False
        QT5 = PYSIDE2 = True

        if sys.platform == "darwin":
            macos_version = parse(platform.mac_ver()[0])
            qt_ver = parse(QT_VERSION)
            if macos_version < parse("10.11") and qt_ver >= parse("5.11"):
                raise PythonQtError(
                    "Qt 5.11 or higher only works in "
                    "macOS 10.11 or higher. Your "
                    "program will fail in this "
                    "system.",
                )

            del macos_version
            del qt_ver
    except ImportError:
        API = "pyqt6"
    else:
        os.environ[QT_API] = API

if API in PYQT6_API:
    try:
        from PyQt6.QtCore import (
            PYQT_VERSION_STR as PYQT_VERSION,
        )
        from PyQt6.QtCore import (
            QT_VERSION_STR as QT_VERSION,
        )

        QT5 = PYQT5 = False
        QT6 = PYQT6 = True

    except ImportError:
        API = "pyside6"
    else:
        os.environ[QT_API] = API

if API in PYSIDE6_API:
    try:
        from PySide6 import __version__ as PYSIDE_VERSION  # analysis:ignore
        from PySide6.QtCore import __version__ as QT_VERSION  # analysis:ignore

        QT5 = PYQT5 = False
        QT6 = PYSIDE6 = True

    except ImportError:
        raise QtBindingsNotFoundError from None
    else:
        os.environ[QT_API] = API


# If a correct API name is passed to QT_API and it could not be found,
# switches to another and informs through the warning
if initial_api != API and binding_specified:
    warnings.warn(
        f"Selected binding {initial_api!r} could not be found; "
        f"falling back to {API!r}",
        PythonQtWarning,
        stacklevel=2,
    )


# Set display name of the Qt API
API_NAME = API_NAMES[API]

with contextlib.suppress(ImportError, PythonQtError):
    # QtDataVisualization backward compatibility (QtDataVisualization vs. QtDatavisualization)
    # Only available for Qt5 bindings > 5.9 on Windows
    from . import QtDataVisualization as QtDatavisualization  # analysis:ignore


def _warn_old_minor_version(name, old_version, min_version):
    """Warn if using a Qt or binding version no longer supported by QtPy."""
    warning_message = (
        f"{name} version {old_version} is not supported by QtPy. "
        "To ensure your application works correctly with QtPy, "
        f"please upgrade to {name} {min_version} or later."
    )
    warnings.warn(warning_message, PythonQtWarning, stacklevel=2)


# Warn if using an End of Life or unsupported Qt API/binding minor version
if QT_VERSION:
    if QT5 and (parse(QT_VERSION) < parse(QT5_VERSION_MIN)):
        _warn_old_minor_version("Qt5", QT_VERSION, QT5_VERSION_MIN)
    elif QT6 and (parse(QT_VERSION) < parse(QT6_VERSION_MIN)):
        _warn_old_minor_version("Qt6", QT_VERSION, QT6_VERSION_MIN)

if PYQT_VERSION:
    if PYQT5 and (parse(PYQT_VERSION) < parse(PYQT5_VERSION_MIN)):
        _warn_old_minor_version("PyQt5", PYQT_VERSION, PYQT5_VERSION_MIN)
    elif PYQT6 and (parse(PYQT_VERSION) < parse(PYQT6_VERSION_MIN)):
        _warn_old_minor_version("PyQt6", PYQT_VERSION, PYQT6_VERSION_MIN)
elif PYSIDE_VERSION:
    if PYSIDE2 and (parse(PYSIDE_VERSION) < parse(PYSIDE2_VERSION_MIN)):
        _warn_old_minor_version("PySide2", PYSIDE_VERSION, PYSIDE2_VERSION_MIN)
    elif PYSIDE6 and (parse(PYSIDE_VERSION) < parse(PYSIDE6_VERSION_MIN)):
        _warn_old_minor_version("PySide6", PYSIDE_VERSION, PYSIDE6_VERSION_MIN)
