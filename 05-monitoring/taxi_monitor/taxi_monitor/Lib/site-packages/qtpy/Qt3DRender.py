# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides Qt3DRender classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5.Qt3DRender import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="Qt3DRender",
            missing_package="PyQt3D",
        ) from error
elif PYQT6:
    try:
        from PyQt6.Qt3DRender import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="Qt3DRender",
            missing_package="PyQt6-3D",
        ) from error
elif PYSIDE2:
    # https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1026
    import inspect

    import PySide2.Qt3DRender as __temp

    for __name in inspect.getmembers(__temp.Qt3DRender):
        globals()[__name[0]] = __name[1]
elif PYSIDE6:
    # https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1026
    import inspect

    import PySide6.Qt3DRender as __temp

    for __name in inspect.getmembers(__temp.Qt3DRender):
        globals()[__name[0]] = __name[1]
