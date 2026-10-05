"""Check a parsed pgModeler model against an :class:`ExerciseSpec`.

The matching philosophy is hybrid:

* **Table / column names** — case-insensitive.
* **Primary keys** — strict: every column flagged ``primary_key=True``
  must be part of the table's PK.
* **Relationships** — strict on existence and cardinality, but
  implementation-agnostic. A required ``RelationshipSpec`` is satisfied
  by *either* an explicit FK + (matching UNIQUE for 1:1) *or* a Pattern
  B ``<relationship>`` element. The student picks the workflow.
* **Data types** — lenient; only the type *family* is checked. Mismatches
  surface as info notes, never as failures.
* **Extras** — tables, columns, or relationships beyond the spec are
  allowed silently.

Public API: :func:`check_exercise` and the dataclasses
:class:`CheckResult` / :class:`CheckItem`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from .parser import ParsedColumn, ParsedModel, ParsedRelationship, ParsedTable
from .specs import ColumnSpec, ExerciseSpec, RelationshipSpec, TableSpec


CheckStatus = Literal["pass", "fail", "info"]
CheckCategory = Literal[
    "table", "column", "primary_key", "relationship", "view"
]


@dataclass
class CheckItem:
    """One row of feedback inside a :class:`CheckResult`."""

    status: CheckStatus
    category: CheckCategory
    message: str
    details: Optional[str] = None


@dataclass
class CheckResult:
    """Aggregate result of running an :class:`ExerciseSpec` against a model."""

    success: bool
    checks: list[CheckItem] = field(default_factory=list)


# ── Type-family matching (lenient) ───────────────────────────────────────────

_TYPE_FAMILIES: dict[str, set[str]] = {
    "varchar": {"varchar", "character varying"},
    "char": {"char", "character"},
    "integer": {"integer", "int", "int4", "int2", "smallint", "int8", "bigint"},
    "bigint": {"bigint", "int8"},
    "smallint": {"smallint", "int2"},
    "text": {"text"},
    "date": {"date"},
    "timestamp": {"timestamp", "timestamptz", "timestamp with time zone",
                  "timestamp without time zone"},
    "time": {"time", "time with time zone", "time without time zone"},
    "numeric": {"numeric", "decimal"},
    "real": {"real", "float4"},
    "double precision": {"double precision", "float8"},
    "boolean": {"boolean", "bool"},
}


def _type_matches(expected: str, actual: str) -> bool:
    """Return ``True`` when ``actual`` belongs to the family of ``expected``."""
    if not expected:
        return True
    e = expected.strip().lower()
    a = (actual or "").strip().lower()
    family = _TYPE_FAMILIES.get(e)
    if family is None:
        return e == a
    return a in family


# ── Lookup helpers (case-insensitive) ────────────────────────────────────────


def _find_table(parsed: ParsedModel, name: str) -> Optional[ParsedTable]:
    lower = name.lower()
    for table in parsed.tables:
        if table.name.lower() == lower:
            return table
    return None


def _find_column(table: ParsedTable, name: str) -> Optional[ParsedColumn]:
    lower = name.lower()
    for col in table.columns:
        if col.name.lower() == lower:
            return col
    return None


def _is_pk_column(table: ParsedTable, column_name: str) -> bool:
    lower = column_name.lower()
    return any(c.lower() == lower for c in table.primary_key_columns)


def _relationship_matches(
    rel: ParsedRelationship,
    spec: RelationshipSpec,
) -> bool:
    """Return ``True`` when a parsed relationship satisfies the spec."""
    return (
        rel.from_table.lower() == spec.from_table.lower()
        and rel.to_table.lower() == spec.to_table.lower()
        and rel.cardinality == spec.cardinality
    )


# ── Per-table checks ─────────────────────────────────────────────────────────


def _check_column(
    parsed_table: ParsedTable,
    table_spec: TableSpec,
    col_spec: ColumnSpec,
    items: list[CheckItem],
) -> None:
    """Append CheckItems for one required column of a present table."""
    parsed_col = _find_column(parsed_table, col_spec.name)
    label = f"{table_spec.name}.{col_spec.name}"

    if parsed_col is None:
        items.append(CheckItem(
            status="fail",
            category="column",
            message=f"Column {label} is missing.",
            details=(
                f"Add a column named '{col_spec.name}' to table "
                f"'{table_spec.name}'."
            ),
        ))
        return

    items.append(CheckItem(
        status="pass",
        category="column",
        message=f"Column {label} exists.",
    ))

    # Type family (lenient — info only).
    if col_spec.expected_type:
        if not _type_matches(col_spec.expected_type, parsed_col.type_name):
            items.append(CheckItem(
                status="info",
                category="column",
                message=(
                    f"The type of {label} is "
                    f"'{parsed_col.type_name or '—'}', but "
                    f"'{col_spec.expected_type}' was expected."
                ),
                details=(
                    "This is not an error — you can change it to match "
                    "the exercise specification if you wish."
                ),
            ))

    # Primary key membership (strict).
    if col_spec.primary_key:
        if _is_pk_column(parsed_table, col_spec.name):
            items.append(CheckItem(
                status="pass",
                category="primary_key",
                message=f"{label} is a primary key.",
            ))
        else:
            items.append(CheckItem(
                status="fail",
                category="primary_key",
                message=f"Column {label} is not a primary key.",
                details=(
                    f"Set '{col_spec.name}' as the Primary Key in table "
                    f"'{table_spec.name}'."
                ),
            ))


def _check_table(
    parsed: ParsedModel,
    table_spec: TableSpec,
    items: list[CheckItem],
) -> None:
    """Append CheckItems for one required table."""
    parsed_table = _find_table(parsed, table_spec.name)
    if parsed_table is None:
        items.append(CheckItem(
            status="fail",
            category="table",
            message=f"Table '{table_spec.name}' is missing.",
            details=(
                f"Create a table named '{table_spec.name}' in "
                "pgModeler."
            ),
        ))
        return

    items.append(CheckItem(
        status="pass",
        category="table",
        message=f"Table '{table_spec.name}' exists.",
    ))

    for col_spec in table_spec.required_columns:
        _check_column(parsed_table, table_spec, col_spec, items)


def _check_relationship(
    parsed: ParsedModel,
    rel_spec: RelationshipSpec,
    items: list[CheckItem],
) -> None:
    """Append a CheckItem for one required relationship."""
    label = rel_spec.description or (
        f"{rel_spec.from_table} → {rel_spec.to_table}"
    )
    if any(_relationship_matches(r, rel_spec) for r in parsed.relationships):
        items.append(CheckItem(
            status="pass",
            category="relationship",
            message=(
                f"{rel_spec.cardinality} relationship between "
                f"'{rel_spec.from_table}' and '{rel_spec.to_table}' exists ({label})."
            ),
        ))
        return

    # Distinguish "right tables, wrong cardinality" from "no relationship at all".
    same_tables = [
        r for r in parsed.relationships
        if r.from_table.lower() == rel_spec.from_table.lower()
        and r.to_table.lower() == rel_spec.to_table.lower()
    ]
    if same_tables:
        actual = same_tables[0].cardinality
        details = (
            f"Found a {actual} relationship, but "
            f"{rel_spec.cardinality} is required. "
            + (
                "For 1:1, the FK side needs a UNIQUE constraint "
                "(or use the Relationship tool with type One-to-One)."
                if rel_spec.cardinality == "1:1"
                else "Remove any UNIQUE constraint on the FK column."
            )
        )
    else:
        details = (
            f"Connect tables '{rel_spec.from_table}' and "
            f"'{rel_spec.to_table}' in pgModeler — either with a Foreign Key "
            "in the table's tab or with the Relationship tool."
        )

    items.append(CheckItem(
        status="fail",
        category="relationship",
        message=(
            f"Missing {rel_spec.cardinality} relationship between "
            f"'{rel_spec.from_table}' and '{rel_spec.to_table}' ({label})."
        ),
        details=details,
    ))


def _check_view(
    parsed: ParsedModel,
    view_name: str,
    items: list[CheckItem],
) -> None:
    """Append a CheckItem for one required view (case-insensitive match)."""
    lower = view_name.lower()
    if any(v.lower() == lower for v in parsed.views):
        items.append(CheckItem(
            status="pass",
            category="view",
            message=f"View '{view_name}' exists.",
        ))
        return

    items.append(CheckItem(
        status="fail",
        category="view",
        message=f"View '{view_name}' is missing.",
        details=(
            f"Create a view named '{view_name}' (CREATE VIEW) and re-run "
            "the export so it reaches the database."
        ),
    ))


# ── Public entry point ───────────────────────────────────────────────────────


def check_exercise(parsed: ParsedModel, spec: ExerciseSpec) -> CheckResult:
    """Compare a parsed ``.dbm`` against an :class:`ExerciseSpec`.

    Parameters
    ----------
    parsed : ParsedModel
        The model returned by
        :func:`rel_db_learning.dbm_validator.parser.parse_dbm`.
    spec : ExerciseSpec
        The exercise specification to check against.

    Returns
    -------
    CheckResult
        ``success`` is ``True`` when no ``fail`` items were produced
        (``info`` items are allowed). ``checks`` lists every individual
        verification in the order it was performed.
    """
    items: list[CheckItem] = []

    for table_spec in spec.required_tables:
        _check_table(parsed, table_spec, items)

    for rel_spec in spec.required_relationships:
        _check_relationship(parsed, rel_spec, items)

    for view_name in spec.required_views:
        _check_view(parsed, view_name, items)

    success = not any(item.status == "fail" for item in items)
    return CheckResult(success=success, checks=items)
