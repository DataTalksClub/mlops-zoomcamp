""" Defines a KernelClient that provides signals and slots.
"""

# Third-party imports
from jupyter_client.channels import HBChannel
from jupyter_client.threaded import ThreadedKernelClient, ThreadedZMQSocketChannel
from qtpy import QtCore
from traitlets import Type

# Local imports
from .kernel_mixins import QtKernelClientMixin
from .util import SuperQObject


class QtHBChannel(SuperQObject, HBChannel):
    # A longer timeout than the base class
    time_to_dead = 3.0

    # Emitted when the kernel has died.
    kernel_died = QtCore.Signal(object)

    def call_handlers(self, since_last_heartbeat):
        """ Reimplemented to emit signals instead of making callbacks.
        """
        # Emit the generic signal.
        self.kernel_died.emit(since_last_heartbeat)


class QtZMQSocketChannel(ThreadedZMQSocketChannel, SuperQObject):
    """A ZMQ socket emitting a Qt signal when a message is received."""
    message_received = QtCore.Signal(object)

    def process_events(self):
        """ Process any pending GUI events.
        """
        QtCore.QCoreApplication.instance().processEvents()

    def call_handlers(self, msg):
        """This method is called in the ioloop thread when a message arrives.

        It is important to remember that this method is called in the thread
        so that some logic must be done to ensure that the application level
        handlers are called in the application thread.
        """
        # Emit the generic signal.
        self.message_received.emit(msg)

    def closed(self):
        """Check if the channel is closed."""
        return self.stream is None or self.stream.closed()


class QtKernelClient(QtKernelClientMixin, ThreadedKernelClient):
    """ A KernelClient that provides signals and slots.
    """
    iopub_channel_class = Type(QtZMQSocketChannel)
    shell_channel_class = Type(QtZMQSocketChannel)
    stdin_channel_class = Type(QtZMQSocketChannel)
    hb_channel_class = Type(QtHBChannel)
