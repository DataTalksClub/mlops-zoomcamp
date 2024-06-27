"""
Based on
https://github.com/jupyter/notebook/blob/master/notebook/static/services/kernels/comm.js
https://github.com/ipython/ipykernel/blob/master/ipykernel/comm/manager.py
https://github.com/ipython/ipykernel/blob/master/ipykernel/comm/comm.py


Which are distributed under the terms of the Modified BSD License.
"""
import logging

from traitlets.config import LoggingConfigurable


import uuid

from qtpy import QtCore

from qtconsole.util import MetaQObjectHasTraits, SuperQObject, import_item


class CommManager(MetaQObjectHasTraits(
        'NewBase', (LoggingConfigurable, SuperQObject), {})):
    """
    Manager for Comms in the Frontend
    """

    def __init__(self, kernel_client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comms = {}
        self.targets = {}
        if kernel_client:
            self.init_kernel_client(kernel_client)

    def init_kernel_client(self, kernel_client):
        """
        connect the kernel, and register message handlers
        """
        self.kernel_client = kernel_client
        kernel_client.iopub_channel.message_received.connect(self._dispatch)

    @QtCore.Slot(object)
    def _dispatch(self, msg):
        """Dispatch messages"""
        msg_type = msg['header']['msg_type']
        handled_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        if msg_type in handled_msg_types:
            getattr(self, msg_type)(msg)

    def new_comm(self, target_name, data=None, metadata=None,
                 comm_id=None, buffers=None):
        """
        Create a new Comm, register it, and open its Kernel-side counterpart
        Mimics the auto-registration in `Comm.__init__` in the Jupyter Comm.

        argument comm_id is optional
        """
        comm = Comm(target_name, self.kernel_client, comm_id)
        self.register_comm(comm)
        try:
            comm.open(data, metadata, buffers)
        except Exception:
            self.unregister_comm(comm)
            raise
        return comm

    def register_target(self, target_name, f):
        """Register a callable f for a given target name

        f will be called with two arguments when a comm_open message is
        received with `target`:

        - the Comm instance
        - the `comm_open` message itself.

        f can be a Python callable or an import string for one.
        """
        if isinstance(f, str):
            f = import_item(f)

        self.targets[target_name] = f

    def unregister_target(self, target_name, f):
        """Unregister a callable registered with register_target"""
        return self.targets.pop(target_name)

    def register_comm(self, comm):
        """Register a new comm"""
        comm_id = comm.comm_id
        comm.kernel_client = self.kernel_client
        self.comms[comm_id] = comm
        comm.sig_is_closing.connect(self.unregister_comm)
        return comm_id

    @QtCore.Slot(object)
    def unregister_comm(self, comm):
        """Unregister a comm, and close its counterpart."""
        # unlike get_comm, this should raise a KeyError
        comm.sig_is_closing.disconnect(self.unregister_comm)
        self.comms.pop(comm.comm_id)

    def get_comm(self, comm_id, closing=False):
        """Get a comm with a particular id

        Returns the comm if found, otherwise None.

        This will not raise an error,
        it will log messages if the comm cannot be found.
        If the comm is closing, it might already have closed,
        so this is ignored.
        """
        try:
            return self.comms[comm_id]
        except KeyError:
            if closing:
                return
            self.log.warning("No such comm: %s", comm_id)
            # don't create the list of keys if debug messages aren't enabled
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug("Current comms: %s", list(self.comms.keys()))

    # comm message handlers
    def comm_open(self, msg):
        """Handler for comm_open messages"""
        content = msg['content']
        comm_id = content['comm_id']
        target_name = content['target_name']
        f = self.targets.get(target_name, None)

        comm = Comm(target_name, self.kernel_client, comm_id)
        self.register_comm(comm)

        if f is None:
            self.log.error("No such comm target registered: %s", target_name)
        else:
            try:
                f(comm, msg)
                return
            except Exception:
                self.log.error("Exception opening comm with target: %s",
                               target_name, exc_info=True)

        # Failure.
        try:
            comm.close()
        except Exception:
            self.log.error(
                "Could not close comm during `comm_open` failure "
                "clean-up.  The comm may not have been opened yet.""",
                exc_info=True)

    def comm_close(self, msg):
        """Handler for comm_close messages"""
        content = msg['content']
        comm_id = content['comm_id']
        comm = self.get_comm(comm_id, closing=True)
        if comm is None:
            return

        self.unregister_comm(comm)

        try:
            comm.handle_close(msg)
        except Exception:
            self.log.error('Exception in comm_close for %s', comm_id,
                           exc_info=True)

    def comm_msg(self, msg):
        """Handler for comm_msg messages"""
        content = msg['content']
        comm_id = content['comm_id']
        comm = self.get_comm(comm_id)
        if comm is None:
            return
        try:
            comm.handle_msg(msg)
        except Exception:
            self.log.error('Exception in comm_msg for %s', comm_id,
                           exc_info=True)


class Comm(MetaQObjectHasTraits(
        'NewBase', (LoggingConfigurable, SuperQObject), {})):
    """
    Comm base class
    """
    sig_is_closing = QtCore.Signal(object)

    def __init__(self, target_name, kernel_client, comm_id=None,
                 msg_callback=None, close_callback=None):
        """
        Create a new comm. Must call open to use.
        """
        super().__init__(target_name=target_name)
        self.target_name = target_name
        self.kernel_client = kernel_client
        if comm_id is None:
            comm_id = uuid.uuid1().hex
        self.comm_id = comm_id
        self._msg_callback = msg_callback
        self._close_callback = close_callback
        self._send_channel = self.kernel_client.shell_channel

    def _send_msg(self, msg_type, content, data, metadata, buffers):
        """
        Send a message on the shell channel.
        """
        if data is None:
            data = {}
        if content is None:
            content = {}
        content['comm_id'] = self.comm_id
        content['data'] = data

        msg = self.kernel_client.session.msg(
            msg_type, content, metadata=metadata)
        if buffers:
            msg['buffers'] = buffers
        return self._send_channel.send(msg)

    # methods for sending messages
    def open(self, data=None, metadata=None, buffers=None):
        """Open the kernel-side version of this comm"""
        return self._send_msg(
            'comm_open', {'target_name': self.target_name},
            data, metadata, buffers)

    def send(self, data=None, metadata=None, buffers=None):
        """Send a message to the kernel-side version of this comm"""
        return self._send_msg(
            'comm_msg', {}, data, metadata, buffers)

    def close(self, data=None, metadata=None, buffers=None):
        """Close the kernel-side version of this comm"""
        self.sig_is_closing.emit(self)
        return self._send_msg(
            'comm_close', {}, data, metadata, buffers)

    # methods for registering callbacks for incoming messages

    def on_msg(self, callback):
        """Register a callback for comm_msg

        Will be called with the `data` of any comm_msg messages.

        Call `on_msg(None)` to disable an existing callback.
        """
        self._msg_callback = callback

    def on_close(self, callback):
        """Register a callback for comm_close

        Will be called with the `data` of the close message.

        Call `on_close(None)` to disable an existing callback.
        """
        self._close_callback = callback

    # methods for handling incoming messages
    def handle_msg(self, msg):
        """Handle a comm_msg message"""
        self.log.debug("handle_msg[%s](%s)", self.comm_id, msg)
        if self._msg_callback:
            return self._msg_callback(msg)

    def handle_close(self, msg):
        """Handle a comm_close message"""
        self.log.debug("handle_close[%s](%s)", self.comm_id, msg)
        if self._close_callback:
            return self._close_callback(msg)


__all__ = ['CommManager']
