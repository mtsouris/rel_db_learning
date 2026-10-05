"""Parser for pgModeler ``.dbm`` files.

A ``.dbm`` is a small XML document describing a database model. This
module extracts tables, columns, primary keys, and **relationships**
into a uniform internal representation.

pgModeler offers two distinct ways to express a relationship in a
``.dbm`` file:

* **Pattern A — explicit Foreign Keys tab.** The user adds an FK column
  and a ``<constraint type="fk-constr">`` constraint. The constraint
  carries the source/destination tables and column names directly.
  Cardinality 1:1 is signalled by a sibling UNIQUE constraint on the
  same source columns; otherwise it's 1:N.

* **Pattern B — interactive Relationship tool.** The user draws a line
  between two tables. pgModeler stores this as a top-level
  ``<relationship type="rel11" | "rel1n" | "reln1" ...>`` element and
  auto-generates the FK column / constraint / (for 1:1) UNIQUE at SQL
  export time. None of those auto-generated artefacts appear in the
  ``.dbm`` XML.

A third element type, ``<relationship type="relfk">``, is just a visual
label decorating an already-existing explicit FK (Pattern A). It carries
a ``reference-fk`` attribute pointing to the real constraint. We skip
these to avoid double-counting relationships.

The parser normalises both real patterns into the same
:class:`ParsedRelationship` shape so callers don't have to care which
workflow the student used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
from xml.etree import ElementTree as ET


Cardinality = Literal["1:1", "1:N"]
RelationshipSource = Literal["explicit", "implicit"]


# ── Parsed-model dataclasses ─────────────────────────────────────────────────


@dataclass
class ParsedColumn:
    """One column as found in a parsed ``.dbm`` file."""

    name: str
    type_name: str = ""
    type_length: Optional[int] = None
    not_null: bool = False


@dataclass
class ParsedTable:
    """One table with its columns and intrinsic constraints.

    ``unique_constraint_columns`` is kept on the parsed model because
    the parser itself needs it to classify Pattern A FKs as 1:1 vs 1:N.
    It is *not* surfaced through the public spec API.
    """

    name: str
    columns: list[ParsedColumn] = field(default_factory=list)
    primary_key_columns: list[str] = field(default_factory=list)
    unique_constraint_columns: list[list[str]] = field(default_factory=list)


@dataclass
class ParsedRelationship:
    """A normalised semantic relationship between two tables.

    Both pgModeler patterns collapse into this shape.

    Attributes
    ----------
    from_table : str
        The "many" side for 1:N, or the FK-owning side for 1:1.
    to_table : str
        The "one" / referenced side.
    cardinality : "1:1" | "1:N"
    source : "explicit" | "implicit"
        ``"explicit"`` means the relationship came from an explicit
        ``fk-constr`` constraint. ``"implicit"`` means it came from a
        ``<relationship type="rel11|rel1n|reln1">`` element. Kept for
        debugging — the checker treats both equally.
    """

    from_table: str
    to_table: str
    cardinality: Cardinality
    source: RelationshipSource


@dataclass
class ParsedModel:
    """Top-level container returned by :func:`parse_dbm`.

    ``views`` holds the names of any views in the model. The ``.dbm``
    parser leaves it empty (pgModeler view parsing is not needed for the
    student workflow), but the live-database reader in
    :mod:`rel_db_learning.dbm_validator.schema_reader` populates it. The
    field defaults to an empty list so every existing producer and
    consumer of :class:`ParsedModel` keeps working unchanged.
    """

    tables: list[ParsedTable] = field(default_factory=list)
    relationships: list[ParsedRelationship] = field(default_factory=list)
    views: list[str] = field(default_factory=list)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _strip_schema(qualified_name: str) -> str:
    """Drop a leading ``schema.`` prefix from a qualified name."""
    if "." in qualified_name:
        return qualified_name.split(".", 1)[1]
    return qualified_name


def _split_columns_attr(value: str) -> list[str]:
    """Split a comma-separated ``names="a,b,c"`` attribute into a list."""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Parse a length string into ``int``; return ``None`` on failure."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ── Element-level extractors ─────────────────────────────────────────────────


def _parse_column(elem: ET.Element) -> ParsedColumn:
    """Build a :class:`ParsedColumn` from a ``<column>`` element."""
    name = elem.get("name", "")
    not_null = elem.get("not-null", "false").lower() == "true"
    type_elem = elem.find("type")
    type_name = ""
    type_length: Optional[int] = None
    if type_elem is not None:
        type_name = type_elem.get("name", "")
        type_length = _parse_int(type_elem.get("length"))
    return ParsedColumn(
        name=name,
        type_name=type_name,
        type_length=type_length,
        not_null=not_null,
    )


def _extract_constraint_columns(
    constraint: ET.Element,
    ref_type: str,
) -> list[str]:
    """Return the column names listed under ``<columns ref-type="...">``."""
    for cols in constraint.findall("columns"):
        if cols.get("ref-type") == ref_type:
            return _split_columns_attr(cols.get("names", ""))
    return []


def _parse_table(elem: ET.Element) -> ParsedTable:
    """Build a :class:`ParsedTable` from a ``<table>`` element.

    Picks up nested PK and UNIQUE constraints. FK constraints nested
    inside a table are *not* collected here — the top-level walker
    handles them uniformly.
    """
    table = ParsedTable(name=elem.get("name", ""))
    for col in elem.findall("column"):
        table.columns.append(_parse_column(col))
    for constraint in elem.findall("constraint"):
        ctype = constraint.get("type", "")
        if ctype == "pk-constr":
            table.primary_key_columns = _extract_constraint_columns(
                constraint, "src-columns"
            )
        elif ctype == "uq-constr":
            cols = _extract_constraint_columns(constraint, "src-columns")
            if cols:
                table.unique_constraint_columns.append(cols)
    return table


def _find_table(model: ParsedModel, name: str) -> Optional[ParsedTable]:
    lower = name.lower()
    for t in model.tables:
        if t.name.lower() == lower:
            return t
    return None


def _columns_match_unique(
    table: Optional[ParsedTable],
    columns: list[str],
) -> bool:
    """Return ``True`` when ``columns`` exactly matches a UNIQUE constraint.

    Comparison is case-insensitive and order-insensitive. An exact set
    match is required so a multi-column UNIQUE that only partially
    overlaps the FK doesn't accidentally upgrade a 1:N to 1:1.
    """
    if table is None or not columns:
        return False
    needle = {c.lower() for c in columns}
    for cols in table.unique_constraint_columns:
        if {c.lower() for c in cols} == needle:
            return True
    return False


def _parse_explicit_fk(
    constraint: ET.Element,
    model: ParsedModel,
    fallback_from_table: Optional[str] = None,
) -> Optional[ParsedRelationship]:
    """Build a :class:`ParsedRelationship` from an ``fk-constr`` constraint.

    Cardinality is decided by looking at the source table's UNIQUE
    constraints: an exact column-set match means 1:1; anything else
    (including no UNIQUE at all) means 1:N.
    """
    from_qual = constraint.get("table") or fallback_from_table or ""
    to_qual = constraint.get("ref-table", "")
    if not from_qual or not to_qual:
        return None

    src_cols = _extract_constraint_columns(constraint, "src-columns")
    if not src_cols:
        return None

    from_table = _strip_schema(from_qual)
    to_table = _strip_schema(to_qual)

    source_table = _find_table(model, from_table)
    cardinality: Cardinality = (
        "1:1" if _columns_match_unique(source_table, src_cols) else "1:N"
    )

    return ParsedRelationship(
        from_table=from_table,
        to_table=to_table,
        cardinality=cardinality,
        source="explicit",
    )


def _parse_implicit_relationship(
    elem: ET.Element,
) -> Optional[ParsedRelationship]:
    """Build a :class:`ParsedRelationship` from a top-level ``<relationship>``.

    Returns ``None`` for ``relfk`` types (visual labels) or for any
    element missing the required ``src-table`` / ``dst-table``.

    Direction convention (matches the task spec):

    * ``rel11`` → cardinality 1:1; FK side is ``src-table``.
    * ``rel1n`` / ``reln1`` → cardinality 1:N; we map ``src-table`` to
      the "many" side. This convention reflects how pgModeler emits the
      auto-generated FK column on the source table.
    """
    rel_type = elem.get("type", "")
    if rel_type == "relfk" or elem.get("reference-fk") is not None:
        return None

    if rel_type == "rel11":
        cardinality: Cardinality = "1:1"
    elif rel_type in {"rel1n", "reln1"}:
        cardinality = "1:N"
    else:
        # Unknown / unsupported relationship type (rel_nn etc.) — skip.
        return None

    src = elem.get("src-table", "")
    dst = elem.get("dst-table", "")
    if not src or not dst:
        return None

    return ParsedRelationship(
        from_table=_strip_schema(src),
        to_table=_strip_schema(dst),
        cardinality=cardinality,
        source="implicit",
    )


# ── Public entry point ───────────────────────────────────────────────────────


def parse_dbm(filepath: str) -> ParsedModel:
    """Parse a pgModeler ``.dbm`` file into a :class:`ParsedModel`.

    Parameters
    ----------
    filepath : str
        Path to the ``.dbm`` file to parse.

    Returns
    -------
    ParsedModel
        Tables, columns, primary keys, and the union of explicit
        (Pattern A) and implicit (Pattern B) relationships. An empty
        model is valid — not an error.

    Raises
    ------
    FileNotFoundError
        With an English message if ``filepath`` does not exist.
    ValueError
        With an English message if the file is not parseable XML or does
        not look like a pgModeler model.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        raise ValueError(
            "The file is not a valid pgModeler .dbm file."
        ) from exc

    root = tree.getroot()
    if root.tag != "dbmodel":
        raise ValueError(
            "The file is not a valid pgModeler .dbm file."
        )

    model = ParsedModel()

    # 1. Tables (with their nested PK / UNIQUE constraints).
    for table_elem in root.findall("table"):
        model.tables.append(_parse_table(table_elem))

    # 2. Explicit FKs — top-level <constraint type="fk-constr"> (the
    #    placement pgModeler uses by default).
    for constraint in root.findall("constraint"):
        if constraint.get("type") == "fk-constr":
            rel = _parse_explicit_fk(constraint, model)
            if rel is not None:
                model.relationships.append(rel)

    # 3. Explicit FKs — fallback: <constraint type="fk-constr"> nested
    #    inside a <table>. Rare, but legal.
    for table_elem in root.findall("table"):
        table_name = table_elem.get("name", "")
        for constraint in table_elem.findall("constraint"):
            if constraint.get("type") != "fk-constr":
                continue
            rel = _parse_explicit_fk(
                constraint, model, fallback_from_table=table_name
            )
            if rel is not None:
                model.relationships.append(rel)

    # 4. Implicit relationships — top-level <relationship>. relfk
    #    visual labels are filtered inside _parse_implicit_relationship,
    #    so they never produce a duplicate of an explicit FK.
    for rel_elem in root.findall("relationship"):
        rel = _parse_implicit_relationship(rel_elem)
        if rel is not None:
            model.relationships.append(rel)

    return model
