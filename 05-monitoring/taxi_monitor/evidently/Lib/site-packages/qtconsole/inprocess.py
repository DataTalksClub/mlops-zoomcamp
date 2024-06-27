""" Defines an in-process KernelManager with signals and slots.
"""

from qtpy import QtCore
from ipykernel.inprocess import (
    InProcessHBChannel, InProcessKernelClient, InProcessKernelManager,
)
from ipykernel.inprocess.channels import InProcessChannel

from traitlets import Type
from .util import SuperQObject
from .kernel_mixins import (
    QtKernelClientMixin, QtKernelManagerMixin,
)
from .rich_jupyter_widget import RichJupyterWidget

class QtInProcessChannel(SuperQObject, InProcessChannel):
    # Emitted when the channel is started.
    started = QtCore.Signal()

    # Emitted when the channel is stopped.
    stopped = QtCore.Signal()

    # Emitted when any message is received.
    message_received = QtCore.Signal(object)

    def start(self):
        """ Reimplemented to emit signal.
        """
        super().start()
        self.started.emit()

    def stop(self):
        """ Reimplemented to emit signal.
        """
        super().stop()
        self.stopped.emit()

    def call_handlers_later(self, *args, **kwds):
        """ Call the message handlers later.
        """
        do_later = lambda: self.call_handlers(*args, **kwds)
        QtCore.QTimer.singleShot(0, do_later)

    def call_handlers(self, msg):
        self.message_received.emit(msg)

    def process_events(self):
        """ Process any pending GUI events.
        """
        QtCore.QCoreApplication.instance().processEvents()

    def flush(self, timeout=1.0):
        """ Reimplemented to ensure that signals are dispatched immediately.
        """
        super().flush()
        self.process_events()

    def closed(self):
        """ Function to ensure compatibility with the QtZMQSocketChannel."""
        return False


class QtInProcessHBChannel(SuperQObject, InProcessHBChannel):
    # This signal will never be fired, but it needs to exist
    kernel_died = QtCore.Signal()


class QtInProcessKernelClient(QtKernelClientMixin, InProcessKernelClient):
    """ An in-process KernelManager with signals and slots.
    """

    iopub_channel_class = Type(QtInProcessChannel)
    shell_channel_class = Type(QtInProcessChannel)
    stdin_channel_class = Type(QtInProcessChannel)
    hb_channel_class = Type(QtInProcessHBChannel)

class QtInProcessKernelManager(QtKernelManagerMixin, InProcessKernelManager):
    client_class = __module__ + '.QtInProcessKernelClient'


class QtInProcessRichJupyterWidget(RichJupyterWidget):
    """ An in-process Jupyter Widget that enables multiline editing
    """

    def _is_complete(self, source, interactive=True):
        shell = self.kernel_manager.kernel.shell
        status, indent_spaces = \
            shell.input_transformer_manager.check_complete(source)
        if indent_spaces is None:
            indent = ''
        else:
            indent = ' ' * indent_spaces
        return status != 'incomplete', indent
