import time
from queue import Empty
import unittest

from flaky import flaky

from qtconsole.manager import QtKernelManager


class Tests(unittest.TestCase):

    def setUp(self):
        """Open a kernel."""
        self.kernel_manager = QtKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels(shell=True, iopub=True)
        self.blocking_client = self.kernel_client.blocking_client()
        self.blocking_client.start_channels(shell=True, iopub=True)
        self.comm_manager = self.kernel_client.comm_manager

        # Check if client is working
        self.blocking_client.execute('print(0)')
        try:
            self._get_next_msg()
            self._get_next_msg()
        except TimeoutError:
            # Maybe it works now?
            self.blocking_client.execute('print(0)')
            self._get_next_msg()
            self._get_next_msg()

    def tearDown(self):
        """Close the kernel."""
        if self.kernel_manager:
            self.kernel_manager.shutdown_kernel(now=True)
        if self.kernel_client:
            self.kernel_client.shutdown()

    def _get_next_msg(self, timeout=10):
        # Get status messages
        timeout_time = time.time() + timeout
        msg_type = 'status'
        while msg_type == 'status':
            if timeout_time < time.time():
                raise TimeoutError
            try:
                msg = self.blocking_client.get_iopub_msg(timeout=3)
                msg_type = msg['header']['msg_type']
            except Empty:
                pass
        return msg
    
    @flaky(max_runs=10)
    def test_kernel_to_frontend(self):
        """Communicate from the kernel to the frontend."""
        comm_manager = self.comm_manager
        blocking_client = self.blocking_client

        class DummyCommHandler():
            def __init__(self):
                comm_manager.register_target('test_api', self.comm_open)
                self.last_msg = None
        
            def comm_open(self, comm, msg):
                comm.on_msg(self.comm_message)
                comm.on_close(self.comm_message)
                self.last_msg = msg['content']['data']
                self.comm = comm
        
            def comm_message(self, msg):
                self.last_msg = msg['content']['data']
        
        handler = DummyCommHandler()
        blocking_client.execute(
        "from ipykernel.comm import Comm\n"
        "comm = Comm(target_name='test_api', data='open')\n"
        "comm.send('message')\n"
        "comm.close('close')\n"
        "del comm\n"
        "print('Done')\n"
        )
        # Get input
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'execute_input'
        # Open comm
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'comm_open'
        comm_manager._dispatch(msg)
        assert handler.last_msg == 'open'
        assert handler.comm.comm_id == msg['content']['comm_id']
        # Get message
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'comm_msg'
        comm_manager._dispatch(msg)
        assert handler.last_msg == 'message'
        assert handler.comm.comm_id == msg['content']['comm_id']
        # Get close
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'comm_close'
        comm_manager._dispatch(msg)
        assert handler.last_msg == 'close'
        assert handler.comm.comm_id == msg['content']['comm_id']
        # Get close
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'stream'

    @flaky(max_runs=10)
    def test_frontend_to_kernel(self):
        """Communicate from the frontend to the kernel."""
        comm_manager = self.comm_manager
        blocking_client = self.blocking_client
        blocking_client.execute(
            "class DummyCommHandler():\n"
            "    def __init__(self):\n"
            "        get_ipython().kernel.comm_manager.register_target(\n"
            "            'test_api', self.comm_open)\n"
            "    def comm_open(self, comm, msg):\n"
            "        comm.on_msg(self.comm_message)\n"
            "        comm.on_close(self.comm_message)\n"
            "        print(msg['content']['data'])\n"
            "    def comm_message(self, msg):\n"
            "        print(msg['content']['data'])\n"
            "dummy = DummyCommHandler()\n"
        )
        # Get input
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'execute_input'
        # Open comm
        comm = comm_manager.new_comm('test_api', data='open')
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'stream'
        assert msg['content']['text'] == 'open\n'
        # Get message
        comm.send('message')
        msg = self._get_next_msg()
        assert msg['header']['msg_type'] == 'stream'
        assert msg['content']['text'] == 'message\n'
        # Get close
        comm.close('close')
        msg = self._get_next_msg()

        # Received message has a header and parent header. The parent header has
        # the info about the close message type in Python 3
        assert msg['parent_header']['msg_type'] == 'comm_close'
        assert msg['msg_type'] == 'stream'
        assert msg['content']['text'] == 'close\n'


if __name__ == "__main__":
    unittest.main()
