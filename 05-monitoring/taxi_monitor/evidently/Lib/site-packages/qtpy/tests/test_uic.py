import contextlib
import os
import sys
import warnings

import pytest
from packaging.version import parse

from qtpy import PYSIDE2, PYSIDE6, PYSIDE_VERSION, QtWidgets
from qtpy.QtWidgets import QComboBox
from qtpy.tests.utils import using_conda

if PYSIDE2:
    pytest.importorskip("pyside2uic", reason="pyside2uic not installed")

from qtpy import uic

QCOMBOBOX_SUBCLASS = """
from qtpy.QtWidgets import QComboBox
class _QComboBoxSubclass(QComboBox):
    pass
"""


@contextlib.contextmanager
def enabled_qcombobox_subclass(temp_dir_path):
    """
    Context manager that sets up a temporary module with a QComboBox subclass
    and then removes it once we are done.
    """

    with open(
        temp_dir_path / "qcombobox_subclass.py",
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(QCOMBOBOX_SUBCLASS)

    sys.path.insert(0, str(temp_dir_path))

    yield

    sys.path.pop(0)


def test_load_ui(qtbot):
    """
    Make sure that the patched loadUi function behaves as expected with a
    simple .ui file.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=".*mode.*",
        )
        ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "test.ui"))

    assert isinstance(ui.pushButton, QtWidgets.QPushButton)
    assert isinstance(ui.comboBox, QComboBox)


@pytest.mark.skipif(
    PYSIDE6
    and using_conda()
    and parse(PYSIDE_VERSION) < parse("6.5")
    and (sys.platform in ("darwin", "linux")),
    reason="pyside6-uic command not contained in all conda-forge packages.",
)
def test_load_ui_type(qtbot):
    """
    Make sure that the patched loadUiType function behaves as expected with a
    simple .ui file.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=".*mode.*",
        )
        ui_type, ui_base_type = uic.loadUiType(
            os.path.join(os.path.dirname(__file__), "test.ui"),
        )
    assert ui_type.__name__ == "Ui_Form"

    class Widget(ui_base_type, ui_type):
        def __init__(self):
            super().__init__()
            self.setupUi(self)

    ui = Widget()
    assert isinstance(ui, QtWidgets.QWidget)
    assert isinstance(ui.pushButton, QtWidgets.QPushButton)
    assert isinstance(ui.comboBox, QComboBox)


def test_load_ui_custom_auto(qtbot, tmp_path):
    """
    Test that we can load a .ui file with custom widgets without having to
    explicitly specify a dictionary of custom widgets, even in the case of
    PySide.
    """
    with enabled_qcombobox_subclass(tmp_path):
        from qcombobox_subclass import _QComboBoxSubclass

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                message=".*mode.*",
            )
            ui = uic.loadUi(
                os.path.join(os.path.dirname(__file__), "test_custom.ui"),
            )

    assert isinstance(ui.pushButton, QtWidgets.QPushButton)
    assert isinstance(ui.comboBox, _QComboBoxSubclass)


def test_load_full_uic():
    """Test that we load the full uic objects."""
    QT_API = os.environ.get("QT_API", "").lower()
    if QT_API.startswith("pyside"):
        assert hasattr(uic, "loadUi")
        assert hasattr(uic, "loadUiType")
    else:
        objects = [
            "compileUi",
            "compileUiDir",
            "loadUi",
            "loadUiType",
            "widgetPluginPath",
        ]
        assert all(hasattr(uic, o) for o in objects)
