"""Database connection helpers for REL_DB_LEARNING.

Exposes:

* :func:`setup_connection` — interactive ipywidgets form for the initial
  configuration. Persists settings via :mod:`rel_db_learning.config`.
* :func:`get_chinook_connection` — connection to the read-only ``chinook``
  database used for examples and theory.
* :func:`get_project_connection` — connection to the student's
  ``my_project`` database used for practice.
* :func:`_get_admin_connection` — private helper returning a connection to
  the default ``postgres`` database (used by loaders for
  ``CREATE DATABASE``).
"""

from __future__ import annotations

import ipywidgets as widgets
import psycopg2
import sqlalchemy.exc
from IPython.display import display
from psycopg2.extensions import connection as PgConnection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from rel_db_learning import config


def setup_connection() -> None:
    """Display an interactive form to configure the PostgreSQL connection.

    Renders six input fields (host, port, user, password, chinook DB
    name, project DB name) and a "Save & Test" button. Clicking the
    button:

    1. Connects to the default ``postgres`` database to verify
       credentials and host reachability.
    2. On success, persists the settings via
       :func:`rel_db_learning.config.save_config` and prints a
       confirmation message.
    3. On failure, prints an error message including the underlying
       exception text.

    Intended to be called from a Jupyter notebook cell.
    """
    host_w = widgets.Text(value="localhost", description="Host:")
    port_w = widgets.IntText(value=5432, description="Port:")
    user_w = widgets.Text(value="postgres", description="User:")
    pass_w = widgets.Password(description="Password:")
    chinook_w = widgets.Text(value="chinook", description="Chinook DB:")
    project_w = widgets.Text(value="my_project", description="Project DB:")
    button = widgets.Button(description="Save & Test", button_style="primary")
    output = widgets.Output()

    def on_click(_button: widgets.Button) -> None:
        with output:
            output.clear_output()
            host = host_w.value
            port = int(port_w.value)
            user = user_w.value
            password = pass_w.value
            chinook_db = chinook_w.value
            project_db = project_w.value
            try:
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    dbname="postgres",
                )
            except Exception as exc:
                print(
                    "Connection failed. Check your settings and "
                    "try again."
                )
                print(f"Error: {exc}")
                return
            conn.close()
            config.save_config(
                host=host,
                port=port,
                user=user,
                password=password,
                chinook_db=chinook_db,
                project_db=project_db,
            )
            print("Connection successful! Settings have been saved.")

    button.on_click(on_click)
    form = widgets.VBox(
        [host_w, port_w, user_w, pass_w, chinook_w, project_w, button, output]
    )
    display(form)


def _get_admin_connection() -> PgConnection:
    """Return a connection to the default ``postgres`` database.

    Used by loaders that need to issue ``CREATE DATABASE``.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet.
    """
    cfg = config.get_config()
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname="postgres",
    )


def get_chinook_connection() -> Engine:
    """Return a SQLAlchemy engine connected to the ``chinook`` database.

    The engine uses psycopg2 as its driver.  It is suitable as the
    ``conn`` argument to :func:`rel_db_learning.db.sql_runner.run_sql`
    and to ``pandas.read_sql``.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. The message suggests running
        :func:`setup_connection` first.
    psycopg2.OperationalError
        If the chinook database does not exist. The message suggests
        running ``install_chinook()``.
    """
    cfg = config.get_config()
    dbname = cfg["chinook_db"]
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{dbname}"
    )
    engine = create_engine(url)
    try:
        with engine.connect():
            pass
    except sqlalchemy.exc.OperationalError as exc:
        if "does not exist" in str(exc).lower():
            raise psycopg2.OperationalError(
                f"Database '{dbname}' does not exist. "
                "Run install_chinook() to create it."
            ) from exc
        raise
    return engine


def get_project_connection() -> Engine:
    """Return a SQLAlchemy engine connected to the student's ``my_project`` database.

    The engine uses psycopg2 as its driver.  It is suitable as the
    ``conn`` argument to :func:`rel_db_learning.db.sql_runner.run_sql`
    and to ``pandas.read_sql``.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. The message suggests running
        :func:`setup_connection` first.
    psycopg2.OperationalError
        If the project database does not exist. The message suggests
        running ``install_my_project()``.
    """
    cfg = config.get_config()
    dbname = cfg["project_db"]
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{dbname}"
    )
    engine = create_engine(url)
    try:
        with engine.connect():
            pass
    except sqlalchemy.exc.OperationalError as exc:
        if "does not exist" in str(exc).lower():
            raise psycopg2.OperationalError(
                f"Database '{dbname}' does not exist. "
                "Run install_my_project() to create it."
            ) from exc
        raise
    return engine
