"""Test QtConsoleApp"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import sys
from subprocess import check_output

from jupyter_core import paths
import pytest
from traitlets.tests.utils import check_help_all_output

from . import no_display


@pytest.mark.skipif(no_display, reason="Doesn't work without a display")
def test_help_output():
    """jupyter qtconsole --help-all works"""
    check_help_all_output('qtconsole')


@pytest.mark.skipif(no_display, reason="Doesn't work without a display")
@pytest.mark.skipif(os.environ.get('CI', None) is None,
                    reason="Doesn't work outside of our CIs")
def test_generate_config():
    """jupyter qtconsole --generate-config"""
    config_dir = paths.jupyter_config_dir()
    check_output([sys.executable, '-m', 'qtconsole', '--generate-config'])
    assert os.path.isfile(os.path.join(config_dir,
                                       'jupyter_qtconsole_config.py'))
