"""A dropdown completer widget for the qtconsole."""

import os
import sys

from qtpy import QT6
from qtpy import QtCore, QtGui, QtWidgets


class CompletionWidget(QtWidgets.QListWidget):
    """ A widget for GUI tab completion.
    """

    #--------------------------------------------------------------------------
    # 'QObject' interface
    #--------------------------------------------------------------------------

    def __init__(self, console_widget, height=0):
        """ Create a completion widget that is attached to the specified Qt
            text edit widget.
        """
        text_edit = console_widget._control
        assert isinstance(text_edit, (QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit))
        super().__init__(parent=console_widget)

        self._text_edit = text_edit
        self._height_max = height if height > 0 else self.sizeHint().height()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # We need Popup style to ensure correct mouse interaction
        # (dialog would dissappear on mouse click with ToolTip style)
        self.setWindowFlags(QtCore.Qt.Popup)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        original_policy = text_edit.focusPolicy()

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        text_edit.setFocusPolicy(original_policy)

        # Ensure that the text edit keeps focus when widget is displayed.
        self.setFocusProxy(self._text_edit)

        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.itemActivated.connect(self._complete_current)

    def eventFilter(self, obj, event):
        """ Reimplemented to handle mouse input and to auto-hide when the
            text edit loses focus.
        """
        if obj is self:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                pos = self.mapToGlobal(event.pos())
                target = QtWidgets.QApplication.widgetAt(pos)
                if (target and self.isAncestorOf(target) or target is self):
                    return False
                else:
                    self.cancel_completion()

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter,
                   QtCore.Qt.Key_Tab):
            self._complete_current()
        elif key == QtCore.Qt.Key_Escape:
            self.hide()
        elif key in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down,
                     QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown,
                     QtCore.Qt.Key_Home, QtCore.Qt.Key_End):
            return super().keyPressEvent(event)
        else:
            QtWidgets.QApplication.sendEvent(self._text_edit, event)

    #--------------------------------------------------------------------------
    # 'QWidget' interface
    #--------------------------------------------------------------------------

    def hideEvent(self, event):
        """ Reimplemented to disconnect signal handlers and event filter.
        """
        super().hideEvent(event)
        try:
            self._text_edit.cursorPositionChanged.disconnect(self._update_current)
        except TypeError:
            pass
        self.removeEventFilter(self)

    def showEvent(self, event):
        """ Reimplemented to connect signal handlers and event filter.
        """
        super().showEvent(event)
        self._text_edit.cursorPositionChanged.connect(self._update_current)
        self.installEventFilter(self)

    #--------------------------------------------------------------------------
    # 'CompletionWidget' interface
    #--------------------------------------------------------------------------

    def show_items(self, cursor, items, prefix_length=0):
        """ Shows the completion widget with 'items' at the position specified
            by 'cursor'.
        """
        point = self._get_top_left_position(cursor)
        self.clear()
        path_items = []
        for item in items:
            # Check if the item could refer to a file or dir. The replacing
            # of '"' is needed for items on Windows
            if (os.path.isfile(os.path.abspath(item.replace("\"", ""))) or
                    os.path.isdir(os.path.abspath(item.replace("\"", "")))):
                path_items.append(item.replace("\"", ""))
            else:
                list_item = QtWidgets.QListWidgetItem()
                list_item.setData(QtCore.Qt.UserRole, item)
                # Need to split to only show last element of a dot completion
                list_item.setText(item.split(".")[-1])
                self.addItem(list_item)

        common_prefix = os.path.dirname(os.path.commonprefix(path_items))
        for path_item in path_items:
            list_item = QtWidgets.QListWidgetItem()
            list_item.setData(QtCore.Qt.UserRole, path_item)
            if common_prefix:
                text = path_item.split(common_prefix)[-1]
            else:
                text = path_item
            list_item.setText(text)
            self.addItem(list_item)

        if QT6:
            screen_rect = self.screen().availableGeometry()
        else:
            screen_rect = QtWidgets.QApplication.desktop().availableGeometry(self)
        screen_height = screen_rect.height()
        height = int(min(self._height_max, screen_height - 50)) # -50px
        if ((screen_height - point.y() - height) < 0):
            point = self._text_edit.mapToGlobal(self._text_edit.cursorRect().topRight())
            py = point.y()
            point.setY(int(py - min(height, py - 10))) # -10px
        w = (self.sizeHintForColumn(0) +
             self.verticalScrollBar().sizeHint().width() +
             2 * self.frameWidth())
        self.setGeometry(point.x(), point.y(), w, height)

        # Move cursor to start of the prefix to replace it
        # when a item is selected
        cursor.movePosition(QtGui.QTextCursor.Left, n=prefix_length)
        self._start_position = cursor.position()
        self.setCurrentRow(0)
        self.raise_()
        self.show()

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _get_top_left_position(self, cursor):
        """ Get top left position for this widget.
        """
        return self._text_edit.mapToGlobal(self._text_edit.cursorRect().bottomRight())

    def _complete_current(self):
        """ Perform the completion with the currently selected item.
        """
        text = self.currentItem().data(QtCore.Qt.UserRole)
        self._current_text_cursor().insertText(text)
        self.hide()

    def _current_text_cursor(self):
        """ Returns a cursor with text between the start position and the
            current position selected.
        """
        cursor = self._text_edit.textCursor()
        if cursor.position() >= self._start_position:
            cursor.setPosition(self._start_position,
                               QtGui.QTextCursor.KeepAnchor)
        return cursor

    def _update_current(self):
        """ Updates the current item based on the current text and the
            position of the widget.
        """
        # Update widget position
        cursor = self._text_edit.textCursor()
        point = self._get_top_left_position(cursor)
        point.setY(self.y())
        self.move(point)

        # Update current item
        prefix = self._current_text_cursor().selection().toPlainText()
        if prefix:
            items = self.findItems(prefix, (QtCore.Qt.MatchStartsWith |
                                            QtCore.Qt.MatchCaseSensitive))
            if items:
                self.setCurrentItem(items[0])
            else:
                self.hide()
        else:
            self.hide()

    def cancel_completion(self):
        self.hide()
