# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtSql classes and functions."""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtSql import *
elif PYQT6:
    from PyQt6.QtSql import *

    QSqlDatabase.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
    QSqlQuery.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QSqlResult.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
elif PYSIDE6:
    from PySide6.QtSql import *

    # Map DeprecationWarning methods
    QSqlDatabase.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
    QSqlQuery.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QSqlResult.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
elif PYSIDE2:
    from PySide2.QtSql import *
