"""Test QtPrintSupport."""

import sys

import pytest

from qtpy import QtPrintSupport


def test_qtprintsupport():
    """Test the qtpy.QtPrintSupport namespace"""
    assert QtPrintSupport.QAbstractPrintDialog is not None
    assert QtPrintSupport.QPageSetupDialog is not None
    assert QtPrintSupport.QPrintDialog is not None
    assert QtPrintSupport.QPrintPreviewDialog is not None
    assert QtPrintSupport.QPrintEngine is not None
    assert QtPrintSupport.QPrinter is not None
    assert QtPrintSupport.QPrinterInfo is not None
    assert QtPrintSupport.QPrintPreviewWidget is not None


def test_qpagesetupdialog_exec_():
    """Test qtpy.QtPrintSupport.QPageSetupDialog exec_"""
    assert QtPrintSupport.QPageSetupDialog.exec_ is not None


def test_qprintdialog_exec_():
    """Test qtpy.QtPrintSupport.QPrintDialog exec_"""
    assert QtPrintSupport.QPrintDialog.exec_ is not None


def test_qprintpreviewwidget_print_(qtbot):
    """Test qtpy.QtPrintSupport.QPrintPreviewWidget print_"""
    assert QtPrintSupport.QPrintPreviewWidget.print_ is not None
    preview_widget = QtPrintSupport.QPrintPreviewWidget()
    preview_widget.print_()
