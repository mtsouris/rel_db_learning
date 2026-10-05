"""Final setup verification for REL_DB_LEARNING.

:func:`verify_setup` is the last cell a student runs in the setup notebook.
It confirms that the config exists and that both databases are reachable.
All output is in English.
"""

from __future__ import annotations

from sqlalchemy import text

from rel_db_learning import config
from rel_db_learning.db.connection import get_chinook_connection, get_project_connection


def verify_setup() -> None:
    """Verify that configuration and both database connections are working.

    Checks in order:

    1. Config file exists.
    2. Can connect to the chinook database and run ``SELECT 1``.
    3. Can connect to the my_project database and run ``SELECT 1``.

    Prints an English status line for each step. Prints a final success
    message when all checks pass. Does not raise exceptions — every
    failure is reported as a printed message with a hint.
    """
    if not config.config_exists():
        print(
            "✗ No saved connection settings were found. "
            "Run setup_connection() and press Save & Test first."
        )
        return

    chinook_ok = _check_db(
        label="chinook",
        connect_fn=get_chinook_connection,
        install_hint="Run install_chinook() to create the database.",
    )
    project_ok = _check_db(
        label="my_project",
        connect_fn=get_project_connection,
        install_hint="Run install_my_project() to create the database.",
    )

    if chinook_ok and project_ok:
        print("All set! You can start from module 01_introduction.")


def _check_db(label: str, connect_fn, install_hint: str) -> bool:
    try:
        engine = connect_fn()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ Connection to database '{label}' OK.")
        return True
    except Exception as exc:
        msg = str(exc)
        if "does not exist" in msg.lower():
            print(
                f"✗ Database '{label}' does not exist yet. {install_hint}"
            )
        elif "setup_connection" in msg or "No connection has been configured" in msg:
            print(
                f"✗ No connection settings were found. "
                "Run setup_connection() first."
            )
        else:
            print(
                f"✗ Failed to connect to database '{label}': {exc}\n"
                "   Check that the PostgreSQL server is running and that "
                "the connection settings are correct (setup_connection())."
            )
        return False
