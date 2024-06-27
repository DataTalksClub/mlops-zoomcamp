import pytest


def test_shiboken():
    """Test the qtpy.shiboken namespace"""
    shiboken = pytest.importorskip("qtpy.shiboken")

    assert shiboken.isValid is not None
    assert shiboken.wrapInstance is not None
    assert shiboken.getCppPointer is not None
    assert shiboken.delete is not None
    assert shiboken.dump is not None
