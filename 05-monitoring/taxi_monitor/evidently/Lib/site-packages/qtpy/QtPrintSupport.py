# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtPrintSupport classes and functions."""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtPrintSupport import *
elif PYQT6:
    from PyQt6.QtPrintSupport import *

    QPageSetupDialog.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
    QPrintDialog.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
    QPrintPreviewWidget.print_ = lambda self, *args, **kwargs: self.print(
        *args,
        **kwargs,
    )
elif PYSIDE6:
    from PySide6.QtPrintSupport import *

    # Map DeprecationWarning methods
    QPageSetupDialog.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
    QPrintDialog.exec_ = lambda self, *args, **kwargs: self.exec(
        *args,
        **kwargs,
    )
elif PYSIDE2:
    from PySide2.QtPrintSupport import *
