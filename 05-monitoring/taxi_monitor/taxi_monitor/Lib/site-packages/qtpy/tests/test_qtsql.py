"""Test QtSql."""

import sys

import pytest

from qtpy import PYSIDE2, PYSIDE_VERSION, QtSql


@pytest.fixture
def database_connection():
    """Create a database connection"""
    connection = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    yield connection
    connection.close()


def test_qtsql():
    """Test the qtpy.QtSql namespace"""
    assert QtSql.QSqlDatabase is not None
    assert QtSql.QSqlDriverCreatorBase is not None
    assert QtSql.QSqlDriver is not None
    assert QtSql.QSqlError is not None
    assert QtSql.QSqlField is not None
    assert QtSql.QSqlIndex is not None
    assert QtSql.QSqlQuery is not None
    assert QtSql.QSqlRecord is not None
    assert QtSql.QSqlResult is not None
    assert QtSql.QSqlQueryModel is not None
    assert QtSql.QSqlRelationalDelegate is not None
    assert QtSql.QSqlRelation is not None
    assert QtSql.QSqlRelationalTableModel is not None
    assert QtSql.QSqlTableModel is not None

    # Following modules are not (yet) part of any wrapper:
    # QSqlDriverCreator, QSqlDriverPlugin


@pytest.mark.skipif(
    sys.platform == "win32" and PYSIDE2 and PYSIDE_VERSION.startswith("5.13"),
    reason="SQLite driver unavailable on PySide 5.13.2 with Windows",
)
def test_qtsql_members_aliases(database_connection):
    """
    Test aliased methods over qtpy.QtSql members including:

    * qtpy.QtSql.QSqlDatabase.exec_
    * qtpy.QtSql.QSqlQuery.exec_
    * qtpy.QtSql.QSqlResult.exec_
    """
    assert QtSql.QSqlDatabase.exec_ is not None
    assert QtSql.QSqlQuery.exec_ is not None
    assert QtSql.QSqlResult.exec_ is not None

    assert database_connection.open()
    database_connection.setDatabaseName("test.sqlite")
    QtSql.QSqlDatabase.exec_(
        database_connection,
        """
        CREATE TABLE test (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            name VARCHAR(40) NOT NULL
        )
        """,
    )

    # Created table 'test' and 'sqlite_sequence'
    assert len(database_connection.tables()) == 2

    insert_table_query = QtSql.QSqlQuery()
    assert insert_table_query.exec_(
        """
        INSERT INTO test (name) VALUES (
            "TESTING"
        )
        """,
    )

    select_table_query = QtSql.QSqlQuery()
    select_table_query.prepare(
        """
        SELECT * FROM test
        """,
    )
    select_table_query.exec_()
    record = select_table_query.record()
    assert not record.isEmpty()
