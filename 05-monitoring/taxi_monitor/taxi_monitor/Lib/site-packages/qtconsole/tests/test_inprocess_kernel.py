"""Test QtInProcessKernel"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import unittest

from qtconsole.inprocess import QtInProcessKernelManager


class InProcessTests(unittest.TestCase):

    def setUp(self):
        """Open an in-process kernel."""
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel_client = self.kernel_manager.client()

    def tearDown(self):
        """Shutdown the in-process kernel. """
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()

    def test_execute(self):
        """Test execution of shell commands."""
        # check that closed works as expected
        assert not self.kernel_client.iopub_channel.closed()
        
        # check that running code works
        self.kernel_client.execute('a=1')
        assert self.kernel_manager.kernel.shell.user_ns.get('a') == 1
