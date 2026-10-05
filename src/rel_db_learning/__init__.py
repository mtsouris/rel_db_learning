import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "REL_DB_LEARNING"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .db.chinook_loader import install_chinook
from .db.connection import (
    get_chinook_connection,
    get_project_connection,
    setup_connection,
)
from .db.ibis_helpers import get_ibis_chinook, get_ibis_project
from .db.my_project_loader import (
    install_my_project,
    rebuild_messy_library,
    reset_my_project_data,
    reset_my_project_data_full,
)
from .db.sql_runner import run_ddl, run_sql
from .dbm_validator import validate_exercise
from .normalization import Relation
from .setup.environment import check_environment
from .setup.verify import verify_setup
from .widgets.self_assessment import fd_check

__all__ = [
    "setup_connection",
    "get_chinook_connection",
    "get_project_connection",
    "run_sql",
    "run_ddl",
    "install_chinook",
    "install_my_project",
    "reset_my_project_data",
    "reset_my_project_data_full",
    "rebuild_messy_library",
    "get_ibis_chinook",
    "get_ibis_project",
    "check_environment",
    "verify_setup",
    "validate_exercise",
    "Relation",
    "fd_check",
]
