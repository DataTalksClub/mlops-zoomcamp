import sys

import pytest

from qtpy import PYQT6, PYSIDE6


def test_qtmultimedia():
    """Test the qtpy.QtMultimedia namespace"""
    from qtpy import QtMultimedia

    assert QtMultimedia.QAudio is not None
    assert QtMultimedia.QAudioInput is not None

    if not (PYSIDE6 or PYQT6):
        assert QtMultimedia.QAbstractVideoBuffer is not None
        assert QtMultimedia.QAudioDeviceInfo is not None
        assert QtMultimedia.QSound is not None
