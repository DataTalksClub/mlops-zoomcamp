"""Test the QtPy CLI."""

import subprocess
import sys
import textwrap

import pytest

import qtpy

SUBCOMMANDS = [
    [],
    ["mypy-args"],
]


@pytest.mark.parametrize(
    argnames=["subcommand"],
    argvalues=[[subcommand] for subcommand in SUBCOMMANDS],
    ids=[" ".join(subcommand) for subcommand in SUBCOMMANDS],
)
def test_cli_help_does_not_fail(subcommand):
    subprocess.run(
        [sys.executable, "-m", "qtpy", *subcommand, "--help"],
        check=True,
    )


def test_cli_version():
    output = subprocess.run(
        [sys.executable, "-m", "qtpy", "--version"],
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    assert output.stdout.strip().split()[-1] == qtpy.__version__


def test_cli_mypy_args():
    output = subprocess.run(
        [sys.executable, "-m", "qtpy", "mypy-args"],
        capture_output=True,
        check=True,
        encoding="utf-8",
    )

    if qtpy.PYQT5:
        expected = " ".join(
            [
                "--always-true=PYQT5",
                "--always-false=PYSIDE2",
                "--always-false=PYQT6",
                "--always-false=PYSIDE6",
            ],
        )
    elif qtpy.PYSIDE2:
        expected = " ".join(
            [
                "--always-false=PYQT5",
                "--always-true=PYSIDE2",
                "--always-false=PYQT6",
                "--always-false=PYSIDE6",
            ],
        )
    elif qtpy.PYQT6:
        expected = " ".join(
            [
                "--always-false=PYQT5",
                "--always-false=PYSIDE2",
                "--always-true=PYQT6",
                "--always-false=PYSIDE6",
            ],
        )
    elif qtpy.PYSIDE6:
        expected = " ".join(
            [
                "--always-false=PYQT5",
                "--always-false=PYSIDE2",
                "--always-false=PYQT6",
                "--always-true=PYSIDE6",
            ],
        )
    else:
        pytest.fail("No Qt bindings detected")

    assert output.stdout.strip() == expected.strip()


def test_cli_pyright_config():
    output = subprocess.run(
        [sys.executable, "-m", "qtpy", "pyright-config"],
        capture_output=True,
        check=True,
        encoding="utf-8",
    )

    if qtpy.PYQT5:
        expected = textwrap.dedent(
            """
            pyrightconfig.json:
            {"defineConstant": {"PYQT5": true, "PYSIDE2": false, "PYQT6": false, "PYSIDE6": false}}

            pyproject.toml:
            [tool.pyright.defineConstant]
            PYQT5 = true
            PYSIDE2 = false
            PYQT6 = false
            PYSIDE6 = false
        """,
        )
    elif qtpy.PYSIDE2:
        expected = textwrap.dedent(
            """
            pyrightconfig.json:
            {"defineConstant": {"PYQT5": false, "PYSIDE2": true, "PYQT6": false, "PYSIDE6": false}}

            pyproject.toml:
            [tool.pyright.defineConstant]
            PYQT5 = false
            PYSIDE2 = true
            PYQT6 = false
            PYSIDE6 = false
        """,
        )
    elif qtpy.PYQT6:
        expected = textwrap.dedent(
            """
            pyrightconfig.json:
            {"defineConstant": {"PYQT5": false, "PYSIDE2": false, "PYQT6": true, "PYSIDE6": false}}

            pyproject.toml:
            [tool.pyright.defineConstant]
            PYQT5 = false
            PYSIDE2 = false
            PYQT6 = true
            PYSIDE6 = false
        """,
        )
    elif qtpy.PYSIDE6:
        expected = textwrap.dedent(
            """
            pyrightconfig.json:
            {"defineConstant": {"PYQT5": false, "PYSIDE2": false, "PYQT6": false, "PYSIDE6": true}}

            pyproject.toml:
            [tool.pyright.defineConstant]
            PYQT5 = false
            PYSIDE2 = false
            PYQT6 = false
            PYSIDE6 = true
        """,
        )
    else:
        pytest.fail("No valid API to test")

    assert output.stdout.strip() == expected.strip()
