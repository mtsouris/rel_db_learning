"""Public API for the pgModeler project validator.

The validator compares a student's database model against an
:class:`ExerciseSpec` and renders English HTML feedback inside a Jupyter
notebook. The model can come from either source:

* a student-edited ``.dbm`` file (Stage 1, before the database exists), or
* the live ``my_project`` PostgreSQL database (Stage 2 onward).

For ``.dbm`` files both pgModeler workflows for declaring relationships
are accepted:

* explicit foreign keys (``<constraint type="fk-constr">``), and
* the interactive Relationship tool (``<relationship type="rel11"…>``).

Typical use from a notebook::

    from rel_db_learning import validate_exercise, get_project_connection
    from rel_db_learning.dbm_validator.exercises import (
        PROJECT_STAGE_1_INITIAL_DESIGN,
        PROJECT_STAGE_2_INITIAL_DEPLOYED,
    )

    # Stage 1 — validate the .dbm file.
    validate_exercise(
        student_dbm="student_work/my_project/stage_1_initial_design.dbm",
        spec=PROJECT_STAGE_1_INITIAL_DESIGN,
    )

    # Stage 2 onward — validate the live database.
    validate_exercise(
        project_db=get_project_connection(),
        spec=PROJECT_STAGE_2_INITIAL_DEPLOYED,
    )
"""

from __future__ import annotations

from typing import Optional

from .checks import CheckItem, CheckResult, check_exercise
from .feedback import render_error, render_feedback
from .parser import (
    ParsedColumn,
    ParsedModel,
    ParsedRelationship,
    ParsedTable,
    parse_dbm,
)
from .schema_reader import read_schema
from .specs import ColumnSpec, ExerciseSpec, RelationshipSpec, TableSpec


def validate_exercise(
    student_dbm: Optional[str] = None,
    spec: Optional[ExerciseSpec] = None,
    project_db=None,
) -> None:
    """Validate a student's model against ``spec`` and render feedback.

    The model is obtained from exactly one of two sources:

    * ``student_dbm`` — a path to a ``.dbm`` file, parsed with
      :func:`~rel_db_learning.dbm_validator.parser.parse_dbm` (the Stage 1
      workflow, kept fully backward compatible).
    * ``project_db`` — a SQLAlchemy engine for the live database (for
      example ``get_project_connection()``), read with
      :func:`~rel_db_learning.dbm_validator.schema_reader.read_schema`
      (the Stage 2-onward workflow).

    Whichever source is used, the spec is resolved (so any
    :attr:`ExerciseSpec.inherits_from` chain is merged in) before the
    comparison runs, and the result is displayed via
    :func:`IPython.display.display`. Problems reading the source (a missing
    file, invalid XML, or a database error) are shown as a friendly error
    box instead of raising.

    Parameters
    ----------
    student_dbm : str, optional
        Path to the student's ``.dbm`` file. Mutually exclusive with
        ``project_db``.
    spec : ExerciseSpec
        The exercise specification to validate against.
    project_db : sqlalchemy.engine.Engine, optional
        Engine connected to the live database. Mutually exclusive with
        ``student_dbm``.

    Raises
    ------
    ValueError
        If ``spec`` is missing, or if neither / both of ``student_dbm``
        and ``project_db`` are supplied.
    """
    if spec is None:
        raise ValueError("validate_exercise requires a 'spec' argument.")

    if (student_dbm is None) == (project_db is None):
        raise ValueError(
            "Provide exactly one source to validate: either "
            "student_dbm=\"path/to/file.dbm\" (for a .dbm file) or "
            "project_db=connection (for the live database) — not both and "
            "not neither."
        )

    if student_dbm is not None:
        try:
            parsed = parse_dbm(student_dbm)
        except (FileNotFoundError, ValueError) as exc:
            render_error(str(exc))
            return
    else:
        try:
            parsed = read_schema(project_db)
        except Exception as exc:  # noqa: BLE001 - shown as feedback, not raised
            render_error(
                "Could not read the schema from the database. Make sure the "
                "connection is valid and the database is reachable. "
                f"Details: {exc}"
            )
            return

    resolved = spec.resolve()
    result = check_exercise(parsed, resolved)
    render_feedback(result, resolved)


__all__ = [
    "validate_exercise",
    "ExerciseSpec",
    "TableSpec",
    "ColumnSpec",
    "RelationshipSpec",
    "CheckResult",
    "CheckItem",
    "ParsedModel",
    "ParsedTable",
    "ParsedColumn",
    "ParsedRelationship",
    "parse_dbm",
    "read_schema",
    "check_exercise",
    "render_feedback",
    "render_error",
]
