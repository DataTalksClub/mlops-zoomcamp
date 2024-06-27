"""A FrontendWidget that emulates a repl for a Jupyter kernel.

This supports the additional functionality provided by Jupyter kernel.
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from collections import namedtuple
from subprocess import Popen
import sys
import time
from warnings import warn

from qtpy import QtCore, QtGui

from IPython.lib.lexers import IPythonLexer, IPython3Lexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from qtconsole import __version__
from traitlets import Bool, Unicode, observe, default
from .frontend_widget import FrontendWidget
from . import styles

#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------

# Default strings to build and display input and output prompts (and separators
# in between)
default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '
default_out_prompt = 'Out[<span class="out-prompt-number">%i</span>]: '
default_input_sep = '\n'
default_output_sep = ''
default_output_sep2 = ''

# Base path for most payload sources.
zmq_shell_source = 'ipykernel.zmqshell.ZMQInteractiveShell'

if sys.platform.startswith('win'):
    default_editor = 'notepad'
else:
    default_editor = ''

#-----------------------------------------------------------------------------
# JupyterWidget class
#-----------------------------------------------------------------------------

class IPythonWidget(FrontendWidget):
    """Dummy class for config inheritance. Destroyed below."""


class JupyterWidget(IPythonWidget):
    """A FrontendWidget for a Jupyter kernel."""

    # If set, the 'custom_edit_requested(str, int)' signal will be emitted when
    # an editor is needed for a file. This overrides 'editor' and 'editor_line'
    # settings.
    custom_edit = Bool(False)
    custom_edit_requested = QtCore.Signal(object, object)

    editor = Unicode(default_editor, config=True,
        help="""
        A command for invoking a GUI text editor. If the string contains a
        {filename} format specifier, it will be used. Otherwise, the filename
        will be appended to the end the command. To use a terminal text editor,
        the command should launch a new terminal, e.g.
        ``"gnome-terminal -- vim"``.
        """)

    editor_line = Unicode(config=True,
        help="""
        The editor command to use when a specific line number is requested. The
        string should contain two format specifiers: {line} and {filename}. If
        this parameter is not specified, the line number option to the %edit
        magic will be ignored.
        """)

    style_sheet = Unicode(config=True,
        help="""
        A CSS stylesheet. The stylesheet can contain classes for:
            1. Qt: QPlainTextEdit, QFrame, QWidget, etc
            2. Pygments: .c, .k, .o, etc. (see PygmentsHighlighter)
            3. QtConsole: .error, .in-prompt, .out-prompt, etc
        """)

    syntax_style = Unicode(config=True,
        help="""
        If not empty, use this Pygments style for syntax highlighting.
        Otherwise, the style sheet is queried for Pygments style
        information.
        """)

    # Prompts.
    in_prompt = Unicode(default_in_prompt, config=True)
    out_prompt = Unicode(default_out_prompt, config=True)
    input_sep = Unicode(default_input_sep, config=True)
    output_sep = Unicode(default_output_sep, config=True)
    output_sep2 = Unicode(default_output_sep2, config=True)

    # JupyterWidget protected class variables.
    _PromptBlock = namedtuple('_PromptBlock', ['block', 'length', 'number'])
    _payload_source_edit = 'edit_magic'
    _payload_source_exit = 'ask_exit'
    _payload_source_next_input = 'set_next_input'
    _payload_source_page = 'page'
    _retrying_history_request = False
    _starting = False

    #---------------------------------------------------------------------------
    # 'object' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        # JupyterWidget protected variables.
        self._payload_handlers = {
            self._payload_source_edit : self._handle_payload_edit,
            self._payload_source_exit : self._handle_payload_exit,
            self._payload_source_page : self._handle_payload_page,
            self._payload_source_next_input : self._handle_payload_next_input }
        self._previous_prompt_obj = None
        self._keep_kernel_on_exit = None

        # Initialize widget styling.
        if self.style_sheet:
            self._style_sheet_changed()
            self._syntax_style_changed()
        else:
            self.set_default_style()

        # Initialize language name.
        self.language_name = None
        self._prompt_requested = False

    #---------------------------------------------------------------------------
    # 'BaseFrontendMixin' abstract interface
    #
    # For JupyterWidget,  override FrontendWidget methods which implement the
    # BaseFrontend Mixin abstract interface
    #---------------------------------------------------------------------------

    def _handle_complete_reply(self, rep):
        """Support Jupyter's improved completion machinery.
        """
        self.log.debug("complete: %s", rep.get('content', ''))
        cursor = self._get_cursor()
        info = self._request_info.get('complete')
        if (info and info.id == rep['parent_header']['msg_id']
                and info.pos == self._get_input_buffer_cursor_pos()
                and info.code == self.input_buffer):
            content = rep['content']
            matches = content['matches']
            start = content['cursor_start']
            end = content['cursor_end']

            start = max(start, 0)
            end = max(end, start)

            # Move the control's cursor to the desired end point
            cursor_pos = self._get_input_buffer_cursor_pos()
            if end < cursor_pos:
                cursor.movePosition(QtGui.QTextCursor.Left,
                                    n=(cursor_pos - end))
            elif end > cursor_pos:
                cursor.movePosition(QtGui.QTextCursor.Right,
                                    n=(end - cursor_pos))
            # This line actually applies the move to control's cursor
            self._control.setTextCursor(cursor)

            offset = end - start
            # Move the local cursor object to the start of the match and
            # complete.
            cursor.movePosition(QtGui.QTextCursor.Left, n=offset)
            self._complete_with_items(cursor, matches)

    def _handle_execute_reply(self, msg):
        """Support prompt requests.
        """
        msg_id = msg['parent_header'].get('msg_id')
        info = self._request_info['execute'].get(msg_id)
        if info and info.kind == 'prompt':
            self._prompt_requested = False
            content = msg['content']
            if content['status'] == 'aborted':
                self._show_interpreter_prompt()
            else:
                number = content['execution_count'] + 1
                self._show_interpreter_prompt(number)
            self._request_info['execute'].pop(msg_id)
        else:
            super()._handle_execute_reply(msg)

    def _handle_history_reply(self, msg):
        """ Handle history tail replies, which are only supported
            by Jupyter kernels.
        """
        content = msg['content']
        if 'history' not in content:
            self.log.error("History request failed: %r"%content)
            if content.get('status', '') == 'aborted' and \
                                            not self._retrying_history_request:
                # a *different* action caused this request to be aborted, so
                # we should try again.
                self.log.error("Retrying aborted history request")
                # prevent multiple retries of aborted requests:
                self._retrying_history_request = True
                # wait out the kernel's queue flush, which is currently timed at 0.1s
                time.sleep(0.25)
                self.kernel_client.history(hist_access_type='tail',n=1000)
            else:
                self._retrying_history_request = False
            return
        # reset retry flag
        self._retrying_history_request = False
        history_items = content['history']
        self.log.debug("Received history reply with %i entries", len(history_items))
        items = []
        last_cell = ""
        for _, _, cell in history_items:
            cell = cell.rstrip()
            if cell != last_cell:
                items.append(cell)
                last_cell = cell
        self._set_history(items)

    def _insert_other_input(self, cursor, content, remote=True):
        """Insert function for input from other frontends"""
        n = content.get('execution_count', 0)
        prompt = self._make_in_prompt(n, remote=remote)
        cont_prompt = self._make_continuation_prompt(self._prompt, remote=remote)
        cursor.insertText('\n')
        for i, line in enumerate(content['code'].strip().split('\n')):
            if i == 0:
                self._insert_html(cursor, prompt)
            else:
                self._insert_html(cursor, cont_prompt)
            self._insert_plain_text(cursor, line + '\n')

        # Update current prompt number
        self._update_prompt(n + 1)

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        self.log.debug("execute_input: %s", msg.get('content', ''))
        if self.include_output(msg):
            self._append_custom(
                self._insert_other_input, msg['content'], before_prompt=True)
        elif not self._prompt:
            self._append_custom(
                self._insert_other_input, msg['content'],
                before_prompt=True, remote=False)

    def _handle_execute_result(self, msg):
        """Handle an execute_result message"""
        self.log.debug("execute_result: %s", msg.get('content', ''))
        if self.include_output(msg):
            self.flush_clearoutput()
            content = msg['content']
            prompt_number = content.get('execution_count', 0)
            data = content['data']
            if 'text/plain' in data:
                self._append_plain_text(self.output_sep, before_prompt=True)
                self._append_html(
                    self._make_out_prompt(prompt_number, remote=not self.from_here(msg)),
                    before_prompt=True
                )
                text = data['text/plain']
                # If the repr is multiline, make sure we start on a new line,
                # so that its lines are aligned.
                if "\n" in text and not self.output_sep.endswith("\n"):
                    self._append_plain_text('\n', before_prompt=True)
                self._append_plain_text(text + self.output_sep2, before_prompt=True)

                if not self.from_here(msg):
                    self._append_plain_text('\n', before_prompt=True)

    def _handle_display_data(self, msg):
        """The base handler for the ``display_data`` message."""
        # For now, we don't display data from other frontends, but we
        # eventually will as this allows all frontends to monitor the display
        # data. But we need to figure out how to handle this in the GUI.
        if self.include_output(msg):
            self.flush_clearoutput()
            data = msg['content']['data']
            # In the regular JupyterWidget, we simply print the plain text
            # representation.
            if 'text/plain' in data:
                text = data['text/plain']
                self._append_plain_text(text, True)
            # This newline seems to be needed for text and html output.
            self._append_plain_text('\n', True)

    def _handle_kernel_info_reply(self, rep):
        """Handle kernel info replies."""
        content = rep['content']
        self.language_name = content['language_info']['name']
        pygments_lexer = content['language_info'].get('pygments_lexer', '')

        try:
            # Other kernels with pygments_lexer info will have to be
            # added here by hand.
            if pygments_lexer == 'ipython3':
                lexer = IPython3Lexer()
            elif pygments_lexer == 'ipython2':
                lexer = IPythonLexer()
            else:
                lexer = get_lexer_by_name(self.language_name)
            self._highlighter._lexer = lexer
        except ClassNotFound:
            pass

        self.kernel_banner = content.get('banner', '')
        if self._starting:
            # finish handling started channels
            self._starting = False
            super()._started_channels()

    def _started_channels(self):
        """Make a history request"""
        self._starting = True
        self.kernel_client.kernel_info()
        self.kernel_client.history(hist_access_type='tail', n=1000)


    #---------------------------------------------------------------------------
    # 'FrontendWidget' protected interface
    #---------------------------------------------------------------------------

    def _process_execute_error(self, msg):
        """Handle an execute_error message"""
        self.log.debug("execute_error: %s", msg.get('content', ''))

        content = msg['content']

        traceback = '\n'.join(content['traceback']) + '\n'
        if False:
            # FIXME: For now, tracebacks come as plain text, so we can't
            # use the html renderer yet.  Once we refactor ultratb to
            # produce properly styled tracebacks, this branch should be the
            # default
            traceback = traceback.replace(' ', '&nbsp;')
            traceback = traceback.replace('\n', '<br/>')

            ename = content['ename']
            ename_styled = '<span class="error">%s</span>' % ename
            traceback = traceback.replace(ename, ename_styled)

            self._append_html(traceback)
        else:
            # This is the fallback for now, using plain text with ansi
            # escapes
            self._append_plain_text(traceback, before_prompt=not self.from_here(msg))

    def _process_execute_payload(self, item):
        """ Reimplemented to dispatch payloads to handler methods.
        """
        handler = self._payload_handlers.get(item['source'])
        if handler is None:
            # We have no handler for this type of payload, simply ignore it
            return False
        else:
            handler(item)
            return True

    def _show_interpreter_prompt(self, number=None):
        """ Reimplemented for IPython-style prompts.
        """
        # If a number was not specified, make a prompt number request.
        if number is None:
            if self._prompt_requested:
                # Already asked for prompt, avoid multiple prompts.
                return
            self._prompt_requested = True
            msg_id = self.kernel_client.execute('', silent=True)
            info = self._ExecutionRequest(msg_id, 'prompt', False)
            self._request_info['execute'][msg_id] = info
            return

        # Show a new prompt and save information about it so that it can be
        # updated later if the prompt number turns out to be wrong.
        self._prompt_sep = self.input_sep
        self._show_prompt(self._make_in_prompt(number), html=True)
        block = self._control.document().lastBlock()
        length = len(self._prompt)
        self._previous_prompt_obj = self._PromptBlock(block, length, number)

        # Update continuation prompt to reflect (possibly) new prompt length.
        self._set_continuation_prompt(
            self._make_continuation_prompt(self._prompt), html=True)

    def _update_prompt(self, new_prompt_number):
        """Replace the last displayed prompt with a new one."""
        if self._previous_prompt_obj is None:
            return

        block = self._previous_prompt_obj.block

        # Make sure the prompt block has not been erased.
        if block.isValid() and block.text():

            # Remove the old prompt and insert a new prompt.
            cursor = QtGui.QTextCursor(block)
            cursor.movePosition(QtGui.QTextCursor.Right,
                                QtGui.QTextCursor.KeepAnchor,
                                self._previous_prompt_obj.length)
            prompt = self._make_in_prompt(new_prompt_number)
            self._prompt = self._insert_html_fetching_plain_text(
                cursor, prompt)

            # When the HTML is inserted, Qt blows away the syntax
            # highlighting for the line, so we need to rehighlight it.
            self._highlighter.rehighlightBlock(cursor.block())

            # Update the prompt cursor
            self._prompt_cursor.setPosition(cursor.position() - 1)

            # Store the updated prompt.
            block = self._control.document().lastBlock()
            length = len(self._prompt)
            self._previous_prompt_obj = self._PromptBlock(block, length, new_prompt_number)

    def _show_interpreter_prompt_for_reply(self, msg):
        """ Reimplemented for IPython-style prompts.
        """
        # Update the old prompt number if necessary.
        content = msg['content']
        # abort replies do not have any keys:
        if content['status'] == 'aborted':
            if self._previous_prompt_obj:
                previous_prompt_number = self._previous_prompt_obj.number
            else:
                previous_prompt_number = 0
        else:
            previous_prompt_number = content['execution_count']
        if self._previous_prompt_obj and \
                self._previous_prompt_obj.number != previous_prompt_number:
            self._update_prompt(previous_prompt_number)
            self._previous_prompt_obj = None

        # Show a new prompt with the kernel's estimated prompt number.
        self._show_interpreter_prompt(previous_prompt_number + 1)

    #---------------------------------------------------------------------------
    # 'JupyterWidget' interface
    #---------------------------------------------------------------------------

    def set_default_style(self, colors='lightbg'):
        """ Sets the widget style to the class defaults.

        Parameters
        ----------
        colors : str, optional (default lightbg)
            Whether to use the default light background or dark
            background or B&W style.
        """
        colors = colors.lower()
        if colors=='lightbg':
            self.style_sheet = styles.default_light_style_sheet
            self.syntax_style = styles.default_light_syntax_style
        elif colors=='linux':
            self.style_sheet = styles.default_dark_style_sheet
            self.syntax_style = styles.default_dark_syntax_style
        elif colors=='nocolor':
            self.style_sheet = styles.default_bw_style_sheet
            self.syntax_style = styles.default_bw_syntax_style
        else:
            raise KeyError("No such color scheme: %s"%colors)

    #---------------------------------------------------------------------------
    # 'JupyterWidget' protected interface
    #---------------------------------------------------------------------------

    def _edit(self, filename, line=None):
        """ Opens a Python script for editing.

        Parameters
        ----------
        filename : str
            A path to a local system file.

        line : int, optional
            A line of interest in the file.
        """
        if self.custom_edit:
            self.custom_edit_requested.emit(filename, line)
        elif not self.editor:
            self._append_plain_text('No default editor available.\n'
            'Specify a GUI text editor in the `JupyterWidget.editor` '
            'configurable to enable the %edit magic')
        else:
            try:
                filename = '"%s"' % filename
                if line and self.editor_line:
                    command = self.editor_line.format(filename=filename,
                                                      line=line)
                else:
                    try:
                        command = self.editor.format()
                    except KeyError:
                        command = self.editor.format(filename=filename)
                    else:
                        command += ' ' + filename
            except KeyError:
                self._append_plain_text('Invalid editor command.\n')
            else:
                try:
                    Popen(command, shell=True)
                except OSError:
                    msg = 'Opening editor with command "%s" failed.\n'
                    self._append_plain_text(msg % command)

    def _make_in_prompt(self, number, remote=False):
        """ Given a prompt number, returns an HTML In prompt.
        """
        try:
            body = self.in_prompt % number
        except TypeError:
            # allow in_prompt to leave out number, e.g. '>>> '
            from xml.sax.saxutils import escape
            body = escape(self.in_prompt)
        if remote:
            body = self.other_output_prefix + body
        return '<span class="in-prompt">%s</span>' % body

    def _make_continuation_prompt(self, prompt, remote=False):
        """ Given a plain text version of an In prompt, returns an HTML
            continuation prompt.
        """
        end_chars = '...: '
        space_count = len(prompt.lstrip('\n')) - len(end_chars)
        if remote:
            space_count += len(self.other_output_prefix.rsplit('\n')[-1])
        body = '&nbsp;' * space_count + end_chars
        return '<span class="in-prompt">%s</span>' % body

    def _make_out_prompt(self, number, remote=False):
        """ Given a prompt number, returns an HTML Out prompt.
        """
        try:
            body = self.out_prompt % number
        except TypeError:
            # allow out_prompt to leave out number, e.g. '<<< '
            from xml.sax.saxutils import escape
            body = escape(self.out_prompt)
        if remote:
            body = self.other_output_prefix + body
        return '<span class="out-prompt">%s</span>' % body

    #------ Payload handlers --------------------------------------------------

    # Payload handlers with a generic interface: each takes the opaque payload
    # dict, unpacks it and calls the underlying functions with the necessary
    # arguments.

    def _handle_payload_edit(self, item):
        self._edit(item['filename'], item['line_number'])

    def _handle_payload_exit(self, item):
        self._keep_kernel_on_exit = item['keepkernel']
        self.exit_requested.emit(self)

    def _handle_payload_next_input(self, item):
        self.input_buffer = item['text']

    def _handle_payload_page(self, item):
        # Since the plain text widget supports only a very small subset of HTML
        # and we have no control over the HTML source, we only page HTML
        # payloads in the rich text widget.
        data = item['data']
        if 'text/html' in data and self.kind == 'rich':
            self._page(data['text/html'], html=True)
        else:
            self._page(data['text/plain'], html=False)

    #------ Trait change handlers --------------------------------------------

    @observe('style_sheet')
    def _style_sheet_changed(self, changed=None):
        """ Set the style sheets of the underlying widgets.
        """
        self.setStyleSheet(self.style_sheet)
        if self._control is not None:
            self._control.document().setDefaultStyleSheet(self.style_sheet)

        if self._page_control is not None:
            self._page_control.document().setDefaultStyleSheet(self.style_sheet)

    @observe('syntax_style')
    def _syntax_style_changed(self, changed=None):
        """ Set the style for the syntax highlighter.
        """
        if self._highlighter is None:
            # ignore premature calls
            return
        if self.syntax_style:
            self._highlighter.set_style(self.syntax_style)
            self._ansi_processor.set_background_color(self.syntax_style)
        else:
            self._highlighter.set_style_sheet(self.style_sheet)

    #------ Trait default initializers -----------------------------------------

    @default('banner')
    def _banner_default(self):
        return "Jupyter QtConsole {version}\n".format(version=__version__)


# Clobber IPythonWidget above:

class IPythonWidget(JupyterWidget):
    """Deprecated class; use JupyterWidget."""
    def __init__(self, *a, **kw):
        warn("IPythonWidget is deprecated; use JupyterWidget",
             DeprecationWarning)
        super().__init__(*a, **kw)
