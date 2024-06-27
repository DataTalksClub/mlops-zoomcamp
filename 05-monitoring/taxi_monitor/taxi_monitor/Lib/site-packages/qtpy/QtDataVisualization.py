# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtDataVisualization classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5.QtDataVisualization import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtDataVisualization",
            missing_package="PyQtDataVisualization",
        ) from error
elif PYQT6:
    try:
        from PyQt6.QtDataVisualization import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtDataVisualization",
            missing_package="PyQt6-DataVisualization",
        ) from error
elif PYSIDE2:
    # https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1026
    import inspect

    import PySide2.QtDataVisualization as __temp

    for __name in inspect.getmembers(__temp.QtDataVisualization):
        globals()[__name[0]] = __name[1]
elif PYSIDE6:
    from PySide6.QtDataVisualization import *
