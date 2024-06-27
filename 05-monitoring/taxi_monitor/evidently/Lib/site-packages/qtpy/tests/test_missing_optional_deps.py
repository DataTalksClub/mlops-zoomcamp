"""Test the deferred import error mechanism"""


# See https://github.com/spyder-ide/qtpy/pull/387/


import pytest

from qtpy import QtModuleNotInstalledError


def test_missing_optional_deps():
    """Test importing a module that uses the deferred import error mechanism"""
    from . import optional_deps

    assert optional_deps.ExampleClass is not None

    with pytest.raises(QtModuleNotInstalledError) as excinfo:
        from .optional_deps import MissingClass

    msg = "The optional_dep.MissingClass module was not found. It must be installed separately as test_package_please_ignore."
    assert msg == str(excinfo.value)
