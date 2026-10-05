"""Read a live PostgreSQL schema into the same :class:`ParsedModel` the
``.dbm`` parser produces.

From Stage 2 onward the student's project lives in the ``my_project``
database rather than in a ``.dbm`` file, so the validator has to inspect
the real schema. This module queries ``information_schema`` and assembles
exactly the same :class:`~rel_db_learning.dbm_validator.parser.ParsedModel`
shape that
:func:`~rel_db_learning.dbm_validator.parser.parse_dbm` returns. Because
the shapes are identical, the comparison logic in
:mod:`rel_db_learning.dbm_validator.checks` and the rendering in
:mod:`rel_db_learning.dbm_validator.feedback` work unchanged regardless of
which source produced the model.

Conventions that keep the two producers aligned:

* **Type names.** ``information_schema.columns.data_type`` returns the same
  long-form names pgModeler writes into a ``.dbm`` (``"integer"``,
  ``"character varying"``, ``"text"``, ``"date"``, ``"boolean"``,
  ``"numeric"`` …), so the lenient type-family matching in ``checks.py``
  treats both identically. The few verbose spellings PostgreSQL adds for
  temporal types (``"timestamp without time zone"`` …) are normalised to
  pgModeler's short form by :func:`_normalize_type`.
* **Cardinality.** A foreign key whose column set is also covered by a
  UNIQUE constraint is a 1:1 relationship; any other foreign key is 1:N.
  This mirrors the parser's Pattern A inference exactly.

All queries use :func:`sqlalchemy.text` and pass identifiers as bound
parameters.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from .parser import ParsedColumn, ParsedModel, ParsedRelationship, ParsedTable


# ── Type normalisation ───────────────────────────────────────────────────────

# PostgreSQL reports temporal types with a verbose "with/without time zone"
# suffix in ``information_schema``. pgModeler stores the short form in a
# ``.dbm``, so we collapse to the short form here to keep the two producers
# byte-identical for these types. Every other type the project uses
# (integer, character varying, text, date, boolean, numeric, …) already
# matches verbatim, so it falls through unchanged.
_TYPE_NORMALIZATION: dict[str, str] = {
    "timestamp without time zone": "timestamp",
    "timestamp with time zone": "timestamptz",
    "time without time zone": "time",
    "time with time zone": "timetz",
}


def _normalize_type(data_type: str) -> str:
    """Map an ``information_schema`` ``data_type`` to the parser's convention.

    Lower-cases and trims the value, then collapses the verbose temporal
    spellings to pgModeler's short form. For the data types used in the
    project this returns exactly what the ``.dbm`` parser stores in
    :attr:`ParsedColumn.type_name`.
    """
    if not data_type:
        return ""
    normalized = data_type.strip().lower()
    return _TYPE_NORMALIZATION.get(normalized, normalized)


# ── Internal value object for foreign keys ───────────────────────────────────


@dataclass
class _ForeignKey:
    """One foreign-key constraint read from ``information_schema``."""

    from_table: str
    from_columns: list[str]
    to_table: str
    to_columns: list[str]


# ── Query runner ─────────────────────────────────────────────────────────────


def _run_query(engine, query: str, params: dict | None = None) -> list[dict]:
    """Execute a read-only query and return rows as a list of plain dicts.

    Centralising the connection handling keeps each reader below focused on
    one query and gives tests a single, small surface to fake.
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return [dict(row) for row in result.mappings().all()]


def _columns_match_unique(
    unique_constraints: list[list[str]],
    columns: list[str],
) -> bool:
    """Return ``True`` when ``columns`` exactly matches a UNIQUE constraint.

    Case- and order-insensitive set comparison, mirroring the ``.dbm``
    parser so a partially overlapping multi-column UNIQUE never upgrades a
    1:N to 1:1.
    """
    if not columns:
        return False
    needle = {c.lower() for c in columns}
    return any(
        {c.lower() for c in cols} == needle for cols in unique_constraints
    )


# ── Per-object readers (one query each) ──────────────────────────────────────


def _read_tables(engine) -> list[str]:
    """Return the names of base tables in the ``public`` schema."""
    rows = _run_query(
        engine,
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
    )
    return [row["table_name"] for row in rows]


def _read_columns(engine, table_name: str) -> list[ParsedColumn]:
    """Return the columns of ``table_name`` as :class:`ParsedColumn` objects.

    When a column's type is a PostgreSQL DOMAIN, ``information_schema``
    reports ``data_type`` as ``'USER-DEFINED'``. To make validation work the
    same way for both plain columns and domain-backed columns, we LEFT JOIN
    ``information_schema.domains`` and use the domain's underlying base type
    (e.g. ``'character varying'``) in place of ``'USER-DEFINED'``.
    """
    rows = _run_query(
        engine,
        """
        SELECT
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.character_maximum_length,
            d.data_type AS domain_data_type
        FROM information_schema.columns c
        LEFT JOIN information_schema.domains d
          ON d.domain_schema = c.domain_schema
         AND d.domain_name = c.domain_name
        WHERE c.table_schema = 'public'
          AND c.table_name = :table_name
        ORDER BY c.ordinal_position
        """,
        {"table_name": table_name},
    )
    columns: list[ParsedColumn] = []
    for row in rows:
        # Prefer the domain's base type when the column is USER-DEFINED.
        # For plain columns domain_data_type is None, so we fall back to
        # the column's own data_type unchanged.
        effective_type = row.get("domain_data_type") or row["data_type"]
        columns.append(
            ParsedColumn(
                name=row["column_name"],
                type_name=_normalize_type(effective_type),
                type_length=row["character_maximum_length"],
                not_null=(str(row["is_nullable"]).upper() == "NO"),
            )
        )
    return columns


def _read_primary_key(engine, table_name: str) -> list[str]:
    """Return the column names that make up ``table_name``'s primary key."""
    rows = _run_query(
        engine,
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = :table_name
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """,
        {"table_name": table_name},
    )
    return [row["column_name"] for row in rows]


def _read_unique_constraints(engine, table_name: str) -> list[list[str]]:
    """Return one column list per UNIQUE constraint on ``table_name``.

    Used to classify a foreign key as 1:1 (FK columns are also UNIQUE) vs
    1:N. PRIMARY KEY constraints are deliberately excluded, matching the
    ``.dbm`` parser which only inspects ``uq-constr`` constraints.
    """
    rows = _run_query(
        engine,
        """
        SELECT tc.constraint_name, kcu.column_name, kcu.ordinal_position
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = :table_name
          AND tc.constraint_type = 'UNIQUE'
        ORDER BY tc.constraint_name, kcu.ordinal_position
        """,
        {"table_name": table_name},
    )
    grouped: dict[str, list[str]] = {}
    for row in rows:
        grouped.setdefault(row["constraint_name"], []).append(
            row["column_name"]
        )
    return list(grouped.values())


def _read_foreign_keys(engine, table_name: str) -> list[_ForeignKey]:
    """Return the foreign keys declared on ``table_name``.

    Each result carries the source columns (on ``table_name``) and the
    referenced table/columns, grouped by constraint so multi-column keys
    stay together.
    """
    rows = _run_query(
        engine,
        """
        SELECT
            tc.constraint_name      AS constraint_name,
            kcu.table_name          AS from_table,
            kcu.column_name         AS from_column,
            kcu.ordinal_position    AS ordinal_position,
            ccu.table_name          AS to_table,
            ccu.column_name         AS to_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints AS rc
          ON tc.constraint_name = rc.constraint_name
         AND tc.constraint_schema = rc.constraint_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON rc.unique_constraint_name = ccu.constraint_name
         AND rc.unique_constraint_schema = ccu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = :table_name
          AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.constraint_name, kcu.ordinal_position
        """,
        {"table_name": table_name},
    )

    grouped: dict[str, _ForeignKey] = {}
    for row in rows:
        name = row["constraint_name"]
        fk = grouped.get(name)
        if fk is None:
            fk = _ForeignKey(
                from_table=row["from_table"],
                from_columns=[],
                to_table=row["to_table"],
                to_columns=[],
            )
            grouped[name] = fk
        fk.from_columns.append(row["from_column"])
        fk.to_columns.append(row["to_column"])
    return list(grouped.values())


def _read_views(engine) -> list[str]:
    """Return the names of views in the ``public`` schema."""
    rows = _run_query(
        engine,
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name
        """,
    )
    return [row["table_name"] for row in rows]


# ── Public entry point ───────────────────────────────────────────────────────


def read_schema(engine) -> ParsedModel:
    """Read the live PostgreSQL schema and build a :class:`ParsedModel`.

    Inspects tables, columns (name, type, nullability), primary keys,
    foreign keys, unique constraints, and views from ``information_schema``
    and returns the same model shape produced by
    :func:`rel_db_learning.dbm_validator.parser.parse_dbm`, so the existing
    comparison and feedback logic apply without modification.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        A SQLAlchemy engine connected to the database to inspect (for
        example the result of ``get_project_connection()``).

    Returns
    -------
    ParsedModel
        Tables with columns / primary keys / unique constraints, the
        relationships inferred from foreign keys (1:1 when the FK column is
        also UNIQUE, otherwise 1:N), and the list of view names. An empty
        schema yields an empty model — not an error.
    """
    model = ParsedModel()

    table_names = _read_tables(engine)
    unique_by_table: dict[str, list[list[str]]] = {}
    foreign_keys: list[_ForeignKey] = []

    for name in table_names:
        uniques = _read_unique_constraints(engine, name)
        unique_by_table[name.lower()] = uniques
        model.tables.append(
            ParsedTable(
                name=name,
                columns=_read_columns(engine, name),
                primary_key_columns=_read_primary_key(engine, name),
                unique_constraint_columns=uniques,
            )
        )
        foreign_keys.extend(_read_foreign_keys(engine, name))

    for fk in foreign_keys:
        uniques = unique_by_table.get(fk.from_table.lower(), [])
        cardinality = (
            "1:1" if _columns_match_unique(uniques, fk.from_columns) else "1:N"
        )
        model.relationships.append(
            ParsedRelationship(
                from_table=fk.from_table,
                to_table=fk.to_table,
                cardinality=cardinality,
                # Live foreign keys are explicit constraints, the same
                # category the parser assigns to Pattern A relationships.
                source="explicit",
            )
        )

    model.views = _read_views(engine)
    return model
