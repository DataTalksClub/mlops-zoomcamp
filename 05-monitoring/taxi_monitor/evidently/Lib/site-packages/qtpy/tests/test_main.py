import contextlib
import os
import subprocess
import sys

import pytest

from qtpy import API_NAMES, QtCore, QtGui, QtWidgets

with contextlib.suppress(Exception):
    # removed in qt 6.0
    from qtpy import QtWebEngineWidgets


def assert_pyside2():
    """
    Make sure that we are using PySide
    """
    import PySide2

    assert QtCore.QEvent is PySide2.QtCore.QEvent
    assert QtGui.QPainter is PySide2.QtGui.QPainter
    assert QtWidgets.QWidget is PySide2.QtWidgets.QWidget
    assert (
        QtWebEngineWidgets.QWebEnginePage
        is PySide2.QtWebEngineWidgets.QWebEnginePage
    )
    assert os.environ["QT_API"] == "pyside2"


def assert_pyside6():
    """
    Make sure that we are using PySide
    """
    import PySide6

    assert QtCore.QEvent is PySide6.QtCore.QEvent
    assert QtGui.QPainter is PySide6.QtGui.QPainter
    assert QtWidgets.QWidget is PySide6.QtWidgets.QWidget
    # Only valid for qt>=6.2
    # assert QtWebEngineWidgets.QWebEnginePage is PySide6.QtWebEngineCore.QWebEnginePage
    assert os.environ["QT_API"] == "pyside6"


def assert_pyqt5():
    """
    Make sure that we are using PyQt5
    """
    import PyQt5

    assert QtCore.QEvent is PyQt5.QtCore.QEvent
    assert QtGui.QPainter is PyQt5.QtGui.QPainter
    assert QtWidgets.QWidget is PyQt5.QtWidgets.QWidget
    assert os.environ["QT_API"] == "pyqt5"


def assert_pyqt6():
    """
    Make sure that we are using PyQt6
    """
    import PyQt6

    assert QtCore.QEvent is PyQt6.QtCore.QEvent
    assert QtGui.QPainter is PyQt6.QtGui.QPainter
    assert QtWidgets.QWidget is PyQt6.QtWidgets.QWidget
    assert os.environ["QT_API"] == "pyqt6"


def test_qt_api():
    """
    If QT_API is specified, we check that the correct Qt wrapper was used
    """

    QT_API = os.environ.get("QT_API", "").lower()

    if QT_API == "pyqt5":
        assert_pyqt5()
    elif QT_API == "pyside2":
        assert_pyside2()
    elif QT_API == "pyqt6":
        assert_pyqt6()
    elif QT_API == "pyside6":
        assert_pyside6()
    else:
        # If the tests are run locally, USE_QT_API and QT_API may not be
        # defined, but we still want to make sure qtpy is behaving sensibly.
        # We should then be loading, in order of decreasing preference, PyQt5,
        # PySide2, PyQt6 and PySide6.
        try:
            import PyQt5
        except ImportError:
            try:
                import PySide2
            except ImportError:
                try:
                    import PyQt6
                except ImportError:
                    import PySide6

                    assert_pyside6()
                else:
                    assert_pyqt6()
            else:
                assert_pyside2()
        else:
            assert_pyqt5()


@pytest.mark.parametrize("api", API_NAMES.values())
def test_qt_api_environ(api):
    """
    If no QT_API is specified but some Qt is imported, ensure QT_API is set properly.
    """
    mod = f"{api}.QtCore"
    pytest.importorskip(mod, reason=f"Requires {api}")
    # clean env
    env = os.environ.copy()
    for key in ("QT_API", "USE_QT_API"):
        if key in env:
            del env[key]
    cmd = f"""
import {mod}
from qtpy import API
import os
print(API)
print(os.environ['QT_API'])
"""
    output = subprocess.check_output([sys.executable, "-c", cmd], env=env)
    got_api, env_qt_api = output.strip().decode("utf-8").splitlines()
    assert got_api == api.lower()
    assert env_qt_api == api.lower()
    # Also ensure we raise a nice error
    env["QT_API"] = "bad"
    cmd = """
try:
    import qtpy
except ValueError as exc:
    assert 'Specified QT_API' in str(exc), str(exc)
else:
    raise AssertionError('QtPy imported despite bad QT_API')
"""
    subprocess.check_call([sys.executable, "-Oc", cmd], env=env)
