"""Package used for testing the deferred import error mechanism."""


# See https://github.com/spyder-ide/qtpy/pull/387/


from qtpy._utils import getattr_missing_optional_dep

from .optional_dep import ExampleClass

_missing_optional_names = {}


try:
    from .optional_dep import MissingClass
except ImportError as error:
    _missing_optional_names["MissingClass"] = {
        "name": "optional_dep.MissingClass",
        "missing_package": "test_package_please_ignore",
        "import_error": error,
    }


def __getattr__(name):
    """Custom getattr to chain and wrap errors due to missing optional deps."""
    raise getattr_missing_optional_dep(
        name,
        module_name=__name__,
        optional_names=_missing_optional_names,
    )
