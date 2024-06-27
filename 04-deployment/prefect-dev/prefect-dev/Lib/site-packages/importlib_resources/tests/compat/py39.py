"""
Backward-compatability shims to support Python 3.9 and earlier.
"""

import types

from jaraco.collections import Projection


def from_test_support(*names):
    """
    Return a SimpleNamespace of names from test.support.
    """
    import test.support

    return types.SimpleNamespace(**Projection(names, vars(test.support)))


try:
    from test.support import import_helper  # type: ignore
except ImportError:
    import_helper = from_test_support(
        'modules_setup', 'modules_cleanup', 'DirsOnSysPath'
    )


try:
    from test.support import os_helper  # type: ignore
except ImportError:
    os_helper = from_test_support('temp_dir')
