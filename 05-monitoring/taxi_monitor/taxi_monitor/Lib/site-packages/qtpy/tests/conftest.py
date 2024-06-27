import os

import pytest


def pytest_configure(config):
    """Configure the test environment."""

    if "USE_QT_API" in os.environ:
        os.environ["QT_API"] = os.environ["USE_QT_API"].lower()

    # We need to import qtpy here to make sure that the API versions get set
    # straight away.
    import qtpy


def pytest_report_header(config):
    """Insert a customized header into the test report."""

    versions = os.linesep
    versions += "PyQt5: "

    try:
        from PyQt5 import Qt

        versions += f"PyQt: {Qt.PYQT_VERSION_STR} - Qt: {Qt.QT_VERSION_STR}"
    except ImportError:
        versions += "not installed"
    except AttributeError:
        versions += "unknown version"

    versions += os.linesep
    versions += "PySide2: "

    try:
        import PySide2
        from PySide2 import QtCore

        versions += f"PySide: {PySide2.__version__} - Qt: {QtCore.__version__}"
    except ImportError:
        versions += "not installed"
    except AttributeError:
        versions += "unknown version"

    versions += os.linesep
    versions += "PyQt6: "

    try:
        from PyQt6 import QtCore

        versions += (
            f"PyQt: {QtCore.PYQT_VERSION_STR} - Qt: {QtCore.QT_VERSION_STR}"
        )
    except ImportError:
        versions += "not installed"
    except AttributeError:
        versions += "unknown version"

    versions += os.linesep
    versions += "PySide6: "

    try:
        import PySide6
        from PySide6 import QtCore

        versions += f"PySide: {PySide6.__version__} - Qt: {QtCore.__version__}"
    except ImportError:
        versions += "not installed"
    except AttributeError:
        versions += "unknown version"

    versions += os.linesep

    return versions


@pytest.fixture
def pdf_writer(qtbot):
    from pathlib import Path

    from qtpy import QtGui

    output_path = Path("test.pdf")
    device = QtGui.QPdfWriter(str(output_path))
    yield device, output_path
    output_path.unlink()
