"""System environment checks for REL_DB_LEARNING setup.

Checks whether PostgreSQL and pgModeler are available on the current
machine. All output is printed in English; no exceptions are raised so
the student always sees a human-readable summary.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess


def check_environment() -> None:
    """Check that PostgreSQL and pgModeler are available, and report Ibis status.

    Tries to run ``psql --version`` and ``pgmodeler-cli --version`` via
    subprocess. Prints an English status line for each tool — a missing
    pgModeler prints a warning rather than an error because the GUI app
    is sufficient for the course.

    Also checks whether the optional ``ibis-framework`` package is installed
    and prints an informational message either way. A missing Ibis does not
    fail the check; it is only needed for the bonus sections of Module 04.

    Does not raise exceptions; all outcomes are communicated via printed
    messages so students can see exactly what is missing.
    """
    _check_tool(
        name="PostgreSQL",
        executable="psql",
        args=["--version"],
        missing_msg=(
            "✗ PostgreSQL not found in PATH. "
            "Make sure it is installed."
        ),
        is_optional=False,
    )
    _check_tool(
        name="pgModeler",
        executable="pgmodeler-cli",
        args=["--version"],
        missing_msg=(
            "⚠ pgModeler CLI not found in PATH. "
            "If you have pgModeler GUI installed, this is fine — "
            "we just cannot verify the version from here."
        ),
        is_optional=True,
    )
    _check_ibis()


def _check_tool(
    name: str,
    executable: str,
    args: list[str],
    missing_msg: str,
    is_optional: bool,
) -> None:
    if shutil.which(executable) is None and not _try_subprocess(executable, args):
        print(missing_msg)
        return

    try:
        result = subprocess.run(
            [executable, *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        version_line = (result.stdout or result.stderr).strip().splitlines()[0]
        print(f"✓ {name} found ({version_line})")
    except FileNotFoundError:
        print(missing_msg)
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or exc.stderr or "").strip()
        if output:
            print(f"✓ {name} found ({output.splitlines()[0]})")
        else:
            print(missing_msg)
    except subprocess.TimeoutExpired:
        print(
            f"⚠ Check for {name} was interrupted (timeout). "
            "Try running manually: "
            f"`{executable} {' '.join(args)}`"
        )


def _try_subprocess(executable: str, args: list[str]) -> bool:
    """Return True if the executable can be found via a quick probe."""
    try:
        subprocess.run(
            [executable, *args],
            capture_output=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, OSError):
        return False
    except subprocess.TimeoutExpired:
        return True


def _check_ibis() -> None:
    """Print an informational line about whether ibis-framework is installed."""
    spec = importlib.util.find_spec("ibis")
    if spec is not None:
        try:
            import ibis  # noqa: PLC0415
            version_str = getattr(ibis, "__version__", "unknown version")
            print(f"✓ Ibis found ({version_str}) (optional)")
        except Exception:
            print("✓ Ibis found (optional)")
    else:
        print(
            "⚠ Ibis not installed (optional, needed only for the Python data API "
            "sections in Module 04). Install with: pip install rel_db_learning[ibis]"
        )
