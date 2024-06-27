"""Defines a KernelManager that provides signals and slots."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from qtpy import QtCore

from traitlets import HasTraits, Type
from .util import MetaQObjectHasTraits, SuperQObject
from .comms import CommManager


class QtKernelRestarterMixin(MetaQObjectHasTraits('NewBase', (HasTraits, SuperQObject), {})):

    _timer = None


class QtKernelManagerMixin(MetaQObjectHasTraits('NewBase', (HasTraits, SuperQObject), {})):
    """ A KernelClient that provides signals and slots.
    """

    kernel_restarted = QtCore.Signal()


class QtKernelClientMixin(MetaQObjectHasTraits('NewBase', (HasTraits, SuperQObject), {})):
    """ A KernelClient that provides signals and slots.
    """

    # Emitted when the kernel client has started listening.
    started_channels = QtCore.Signal()

    # Emitted when the kernel client has stopped listening.
    stopped_channels = QtCore.Signal()

    #---------------------------------------------------------------------------
    # 'KernelClient' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comm_manager = None
    #------ Channel management -------------------------------------------------

    def start_channels(self, *args, **kw):
        """ Reimplemented to emit signal.
        """
        super().start_channels(*args, **kw)
        self.started_channels.emit()
        self.comm_manager = CommManager(parent=self, kernel_client=self)

    def stop_channels(self):
        """ Reimplemented to emit signal.
        """
        super().stop_channels()
        self.stopped_channels.emit()
        self.comm_manager = None
