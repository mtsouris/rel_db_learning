"""Persistent configuration for REL_DB_LEARNING.

The config file lives at ``~/.rel_db_learning/config.json`` — outside the
project directory so that personal database credentials are never tracked
by git.

The password is stored in plaintext. This is an intentional tradeoff for
the educational setting; students should not have to manage a secrets
manager just to follow along.
"""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Dict


CONFIG_DIR: Path = Path.home() / ".rel_db_learning"
CONFIG_FILE: Path = CONFIG_DIR / "config.json"


def config_exists() -> bool:
    """Return ``True`` if the config file is present on disk."""
    return CONFIG_FILE.exists()


def get_config() -> Dict[str, Any]:
    """Read and return the saved configuration.

    Returns
    -------
    dict
        Parsed JSON content of the config file.

    Raises
    ------
    FileNotFoundError
        If no config file exists yet. The message suggests running
        ``setup_connection()`` first.
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "No connection has been configured. "
            "Run setup_connection() first."
        )
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_config(
    host: str,
    port: int,
    user: str,
    password: str,
    chinook_db: str = "chinook",
    project_db: str = "my_project",
) -> None:
    """Persist PostgreSQL connection settings to the config file.

    The parent directory is created if missing. On Unix-like systems the
    file permissions are restricted to owner read/write (``0o600``). On
    Windows the permission step is skipped silently because ``chmod``
    does not map cleanly to NTFS ACLs.

    Parameters
    ----------
    host : str
        PostgreSQL server hostname.
    port : int
        PostgreSQL server port.
    user : str
        Database user with privileges to create databases.
    password : str
        Plaintext password for ``user``.
    chinook_db : str, optional
        Name of the chinook database. Defaults to ``"chinook"``.
    project_db : str, optional
        Name of the student's project database. Defaults to
        ``"my_project"``.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "chinook_db": chinook_db,
        "project_db": project_db,
    }
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    if sys.platform != "win32":
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)


def reset_config() -> None:
    """Delete the config file if it exists; no-op when already missing."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
