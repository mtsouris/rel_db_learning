"""Optional Ibis connection helpers for REL_DB_LEARNING.

Ibis is an optional dependency used only in the bonus sections of Module 04
query notebooks. Install it with::

    pip install rel_db_learning[ibis]

Both helpers use the same persistent config as
:func:`~rel_db_learning.db.connection.get_chinook_connection` and
:func:`~rel_db_learning.db.connection.get_project_connection`.
"""

from __future__ import annotations

from rel_db_learning import config

_IBIS_INSTALL_HINT = (
    "Ibis is not installed. The Ibis sections of Module 04 are optional. "
    "To use them, run: pip install rel_db_learning[ibis]"
)


def get_ibis_chinook():
    """Return an Ibis PostgreSQL backend connected to the chinook database.

    Uses the same stored config as :func:`get_chinook_connection`.

    Returns
    -------
    ibis.backends.postgres.Backend
        Connected Ibis backend for the chinook database.

    Raises
    ------
    ImportError
        If ibis-framework is not installed.
    FileNotFoundError
        If no connection has been configured yet.
    """
    try:
        import ibis
    except ImportError as exc:
        raise ImportError(_IBIS_INSTALL_HINT) from exc

    cfg = config.get_config()
    return ibis.postgres.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["chinook_db"],
    )


def get_ibis_project():
    """Return an Ibis PostgreSQL backend connected to the my_project database.

    Uses the same stored config as :func:`get_project_connection`.

    Returns
    -------
    ibis.backends.postgres.Backend
        Connected Ibis backend for the my_project database.

    Raises
    ------
    ImportError
        If ibis-framework is not installed.
    FileNotFoundError
        If no connection has been configured yet.
    """
    try:
        import ibis
    except ImportError as exc:
        raise ImportError(_IBIS_INSTALL_HINT) from exc

    cfg = config.get_config()
    return ibis.postgres.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["project_db"],
    )
