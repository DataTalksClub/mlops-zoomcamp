# -----------------------------------------------------------------------------
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtWebEngineWidgets classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInstalledError,
)

# To test if we are using WebEngine or WebKit
# NOTE: This constant is imported by other projects (e.g. Spyder), so please
# don't remove it.
WEBENGINE = True


if PYQT5:
    try:
        # Based on the work at https://github.com/spyder-ide/qtpy/pull/203
        from PyQt5.QtWebEngineWidgets import (
            QWebEnginePage,
            QWebEngineProfile,
            QWebEngineScript,
            QWebEngineSettings,
            QWebEngineView,
        )
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngineWidgets",
            missing_package="PyQtWebEngine",
        ) from error
elif PYQT6:
    try:
        from PyQt6.QtWebEngineCore import (
            QWebEnginePage,
            QWebEngineProfile,
            QWebEngineScript,
            QWebEngineSettings,
        )
        from PyQt6.QtWebEngineWidgets import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngineWidgets",
            missing_package="PyQt6-WebEngine",
        ) from error
elif PYSIDE2:
    # Based on the work at https://github.com/spyder-ide/qtpy/pull/203
    from PySide2.QtWebEngineWidgets import (
        QWebEnginePage,
        QWebEngineProfile,
        QWebEngineScript,
        QWebEngineSettings,
        QWebEngineView,
    )
elif PYSIDE6:
    from PySide6.QtWebEngineCore import (
        QWebEnginePage,
        QWebEngineProfile,
        QWebEngineScript,
        QWebEngineSettings,
    )
    from PySide6.QtWebEngineWidgets import *
