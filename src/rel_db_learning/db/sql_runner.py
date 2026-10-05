"""SQL execution helpers for REL_DB_LEARNING notebooks.

Two functions cover the two main use cases:

* :func:`run_sql` — SELECT queries. Wraps :func:`pandas.read_sql` with
  auto-LIMIT protection and friendly error messages.
* :func:`run_ddl` — DDL and other non-SELECT SQL (CREATE TABLE, ALTER TABLE,
  DROP, GRANT, full pgModeler exports). Uses the DBAPI driver directly so
  multi-statement scripts work in a single call.
"""

from __future__ import annotations

import pandas as pd
import psycopg2
import psycopg2.errors
import sqlalchemy.exc
from sqlalchemy import text


def _diag_field(exc: psycopg2.Error, field: str) -> str | None:
    """Return a diagnostics field from a psycopg2 exception, or None."""
    try:
        return getattr(exc.diag, field, None)
    except Exception:
        return None


def run_sql(query: str, conn, limit: int = 50) -> pd.DataFrame:
    """Execute a SQL SELECT query and return the result as a DataFrame.

    For SELECT queries that do not already carry a LIMIT clause, a
    ``LIMIT {limit}`` is appended automatically.  If the result hits
    exactly ``limit`` rows an informational message is printed.

    For DDL (CREATE TABLE, ALTER TABLE, DROP, GRANT) or other statements
    that do not return rows, use :func:`run_ddl` instead.

    Parameters
    ----------
    query : str
        SQL statement to execute.
    conn :
        A SQLAlchemy engine (e.g. from ``get_project_connection()``).
    limit : int, optional
        Row cap applied to bare SELECT queries. Defaults to 50.

    Returns
    -------
    pandas.DataFrame
        Query result.

    Raises
    ------
    psycopg2.errors.UndefinedColumn
        With an English message when a referenced column does not exist.
    psycopg2.errors.UndefinedTable
        With an English message when a referenced table does not exist.
    psycopg2.errors.SyntaxError
        With an English message on SQL syntax errors.
    psycopg2.errors.DuplicateTable
        With an English message when the table already exists.
    psycopg2.errors.ForeignKeyViolation
        With an English message on FK constraint violations.
    """
    q_lower = query.lower()
    is_select = "select" in q_lower
    has_limit = "limit" in q_lower
    is_explain = query.strip().upper().startswith("EXPLAIN")
    auto_limit_applied = is_select and not has_limit and not is_explain

    if auto_limit_applied:
        base = query.rstrip().rstrip(";").rstrip()
        effective_query = f"{base} LIMIT {limit}"
    else:
        effective_query = query

    try:
        # Wrap in text() so SQLAlchemy doesn't interpret '%' as a parameter
        # placeholder — needed for LIKE patterns such as "name LIKE 'A%'".
        df = pd.read_sql(text(effective_query), conn)
    except sqlalchemy.exc.ResourceClosedError:
        # Raised when the statement returned no result set (e.g. DDL executed
        # via pd.read_sql). Print a helpful hint rather than crashing.
        print(
            "This SQL statement does not return rows. "
            "Use run_ddl() for CREATE TABLE, ALTER TABLE, DROP, and other "
            "statements that do not produce a result set."
        )
        return pd.DataFrame()
    except sqlalchemy.exc.SQLAlchemyError as exc:
        original = getattr(exc, "orig", None)  # None if exc is not a DBAPIError
        if original is None:
            raise
        if isinstance(original, psycopg2.errors.UndefinedColumn):
            col = _diag_field(original, "column_name")
            msg = (
                f"Column '{col}' does not exist in the table."
                if col else
                "A column does not exist in the table."
            )
            raise psycopg2.errors.UndefinedColumn(msg) from exc
        if isinstance(original, psycopg2.errors.UndefinedTable):
            tbl = _diag_field(original, "table_name")
            msg = (
                f"Table '{tbl}' does not exist in the database."
                if tbl else
                "A table does not exist in the database."
            )
            raise psycopg2.errors.UndefinedTable(msg) from exc
        if isinstance(original, psycopg2.errors.SyntaxError):
            raise psycopg2.errors.SyntaxError(
                "Syntax error in your SQL query."
            ) from exc
        if isinstance(original, psycopg2.errors.DuplicateTable):
            tbl = _diag_field(original, "table_name")
            msg = (
                f"Table '{tbl}' already exists."
                if tbl else
                "Table already exists."
            )
            raise psycopg2.errors.DuplicateTable(msg) from exc
        if isinstance(original, psycopg2.errors.ForeignKeyViolation):
            raise psycopg2.errors.ForeignKeyViolation(
                "Foreign key constraint violation."
            ) from exc
        raise  # unrecognized orig reraise SQLAlchemyError unchanged

    if auto_limit_applied and len(df) == limit:
        print(
            f"Showing the first {limit} rows. "
            "Add LIMIT N to your query to set a different limit."
        )

    return df


def run_ddl(sql: str, conn) -> None:
    """Execute DDL or other non-SELECT SQL on a SQLAlchemy engine.

    Handles multi-statement scripts, such as a full pgModeler SQL export
    containing CREATE TABLE, ALTER TABLE ADD CONSTRAINT, GRANT, and SQL
    comments. All statements are passed to the DBAPI driver (psycopg2) in
    a single call and executed inside an explicit transaction that is
    committed on success.

    On success, prints a short confirmation. On error, prints a clean
    English message without a raw traceback.

    Parameters
    ----------
    sql : str
        One or more SQL statements separated by semicolons.
    conn :
        A SQLAlchemy engine (e.g. from ``get_project_connection()``).
    """
    try:
        # exec_driver_sql sends the SQL straight to the DBAPI cursor
        # (psycopg2), which accepts multiple semicolon-separated statements
        # in a single call. conn.begin() wraps the call in a transaction and
        # commits automatically on a clean exit.
        with conn.begin() as connection:
            connection.exec_driver_sql(sql)
        print("SQL executed successfully.")
    except sqlalchemy.exc.SQLAlchemyError as exc:
        original = getattr(exc, "orig", None)
        if isinstance(original, psycopg2.errors.DuplicateTable):
            tbl = _diag_field(original, "table_name")
            msg = (
                f"Table '{tbl}' already exists. "
                "Drop it first or skip this step."
                if tbl else
                "A table already exists. Drop it first or skip this step."
            )
            print(f"Error: {msg}")
        elif isinstance(original, psycopg2.errors.SyntaxError):
            print(
                "Error: Syntax error in your SQL. "
                "Check the statement and try again."
            )
        elif original is not None:
            print(f"Error: {original}")
        else:
            print(f"Error: {exc}")
