import contextlib
import platform
import sys
from unittest import mock

import pytest

from qtpy import PYQT5, PYSIDE2


@pytest.mark.skipif(not PYQT5, reason="Targeted to PyQt5")
@mock.patch.object(platform, "mac_ver")
def test_qt59_exception(mac_ver, monkeypatch):
    # Remove qtpy to reimport it again
    with contextlib.suppress(KeyError):
        del sys.modules["qtpy"]

    # Patch stdlib to emulate a macOS system
    monkeypatch.setattr("sys.platform", "darwin")
    mac_ver.return_value = ("10.9.2",)

    # Patch Qt version
    monkeypatch.setattr("PyQt5.QtCore.QT_VERSION_STR", "5.9.1")

    # This should raise an Exception
    with pytest.raises(Exception) as e:
        import qtpy

    assert "10.10" in str(e.value)
    assert "5.9" in str(e.value)


@pytest.mark.skipif(not PYQT5, reason="Targeted to PyQt5")
@mock.patch.object(platform, "mac_ver")
def test_qt59_no_exception(mac_ver, monkeypatch):
    # Remove qtpy to reimport it again
    with contextlib.suppress(KeyError):
        del sys.modules["qtpy"]

    # Patch stdlib to emulate a macOS system
    monkeypatch.setattr("sys.platform", "darwin")
    mac_ver.return_value = ("10.10.1",)

    # Patch Qt version
    monkeypatch.setattr("PyQt5.QtCore.QT_VERSION_STR", "5.9.5")

    # This should not raise an Exception
    try:
        import qtpy
    except Exception:  # noqa: BLE001
        pytest.fail("Error!")


@pytest.mark.skipif(
    not (PYQT5 or PYSIDE2),
    reason="Targeted to PyQt5 or PySide2",
)
@mock.patch.object(platform, "mac_ver")
def test_qt511_exception(mac_ver, monkeypatch):
    # Remove qtpy to reimport it again
    with contextlib.suppress(KeyError):
        del sys.modules["qtpy"]

    # Patch stdlib to emulate a macOS system
    monkeypatch.setattr("sys.platform", "darwin")
    mac_ver.return_value = ("10.10.3",)

    # Patch Qt version
    if PYQT5:
        monkeypatch.setattr("PyQt5.QtCore.QT_VERSION_STR", "5.11.1")
    else:
        monkeypatch.setattr("PySide2.QtCore.__version__", "5.11.1")

    # This should raise an Exception
    with pytest.raises(Exception) as e:
        import qtpy

    assert "10.11" in str(e.value)
    assert "5.11" in str(e.value)


@pytest.mark.skipif(
    not (PYQT5 or PYSIDE2),
    reason="Targeted to PyQt5 or PySide2",
)
@mock.patch.object(platform, "mac_ver")
def test_qt511_no_exception(mac_ver, monkeypatch):
    # Remove qtpy to reimport it again
    with contextlib.suppress(KeyError):
        del sys.modules["qtpy"]

    # Patch stdlib to emulate a macOS system
    monkeypatch.setattr("sys.platform", "darwin")
    mac_ver.return_value = ("10.13.2",)

    # Patch Qt version
    if PYQT5:
        monkeypatch.setattr("PyQt5.QtCore.QT_VERSION_STR", "5.11.1")
    else:
        monkeypatch.setattr("PySide2.QtCore.__version__", "5.11.1")

    # This should not raise an Exception
    try:
        import qtpy
    except Exception:  # noqa: BLE001
        pytest.fail("Error!")
