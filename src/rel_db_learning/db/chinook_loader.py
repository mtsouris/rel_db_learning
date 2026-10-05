"""Installer for the bundled Chinook PostgreSQL database.

Students call :func:`install_chinook` once from the setup notebook to
create and populate the ``chinook`` database on their local PostgreSQL
server.
"""

from __future__ import annotations

import importlib.resources

import psycopg2
from psycopg2 import sql

from rel_db_learning import config
from rel_db_learning.db.connection import _get_admin_connection


def install_chinook(force: bool = False) -> None:
    """Create and populate the ``chinook`` database.

    Reads the target database name from the saved config. Connects to the
    default ``postgres`` database (via :func:`_get_admin_connection`) to
    issue DDL, then connects to the new database to run the bundled SQL
    script.

    Parameters
    ----------
    force : bool, optional
        When ``True``, drop and re-create the database if it already exists.
        Defaults to ``False``.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet.
    psycopg2.Error
        On any database error during creation or population; an English
        message is printed before re-raising.
    """
    cfg = config.get_config()
    dbname = cfg["chinook_db"]

    admin_conn = _get_admin_connection()
    admin_conn.autocommit = True
    try:
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
            )
            exists = cur.fetchone() is not None

        if exists and not force:
            print(
                f"Database '{dbname}' already exists. "
                "Use install_chinook(force=True) to reinstall."
            )
            return

        if exists:
            with admin_conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = %s AND pid <> pg_backend_pid()",
                    (dbname,),
                )
            with admin_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(dbname))
                )

        print("Creating database...")
        with admin_conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname))
            )
    finally:
        admin_conn.close()

    sql_text = (
        importlib.resources.files("rel_db_learning.data.chinook")
        .joinpath("chinook_postgres.sql")
        .read_text(encoding="utf-8")
    )

    print("Loading data...")
    db_conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=dbname,
    )
    try:
        with db_conn.cursor() as cur:
            cur.execute(sql_text)
        db_conn.commit()
    except Exception:
        db_conn.rollback()
        db_conn.close()
        print(f"Error while loading database '{dbname}'.")
        raise

    # Count tables and rows after a successful load.
    try:
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
            tables = [row[0] for row in cur.fetchall()]

        n_tables = len(tables)
        n_rows = 0
        for tbl in tables:
            with db_conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(tbl)
                    )
                )
                n_rows += cur.fetchone()[0]
    finally:
        db_conn.close()

    print(
        f"✓ Database '{dbname}' installed. "
        f"({n_tables} tables, {n_rows} rows of data)"
    )
