"""Declarative specifications for pgModeler ``.dbm`` exercises.

A spec describes *what* the student's model must contain, not *how* they
build it. Relationships are declared as semantic facts ("loan is many-to-one
with book") rather than implementation details ("there is a column
loan.book_id referencing book.book_id with a UNIQUE constraint"). This lets
students use either pgModeler workflow — the explicit *Foreign Keys* tab or
the interactive *Relationship* tool — without changing the spec.

These dataclasses are pure data. Matching logic lives in
:mod:`rel_db_learning.dbm_validator.checks`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


Cardinality = Literal["1:1", "1:N"]


@dataclass
class ColumnSpec:
    """A required column inside a :class:`TableSpec`.

    Only declare columns the student types explicitly. FK columns generated
    by pgModeler's *Relationship* tool live conceptually with the
    relationship, not the table — leave them out of the spec.

    Parameters
    ----------
    name : str
        Expected column name. Matching is case-insensitive.
    expected_type : str, optional
        Type family the column should belong to (``"varchar"``,
        ``"integer"``, ``"text"``, ``"date"``, ...). Lenient match —
        ``character varying(120)`` satisfies an ``"varchar"`` expectation.
        Mismatches produce an info note, not a failure.
    primary_key : bool, optional
        When ``True`` the column must participate in the table's PRIMARY
        KEY constraint. Strict check.
    """

    name: str
    expected_type: Optional[str] = None
    primary_key: bool = False


@dataclass
class RelationshipSpec:
    """A semantic relationship between two tables.

    Does **not** specify FK column names — pgModeler may auto-generate
    them via the *Relationship* tool. Use this to declare that a
    relationship of a given cardinality must exist.

    Parameters
    ----------
    from_table : str
        The table on the "many" side (or, for 1:1, the side that *owns*
        the FK column). Case-insensitive.
    to_table : str
        The table on the "one" side (the referenced PK side).
        Case-insensitive.
    cardinality : "1:1" | "1:N"
        Required cardinality. 1:1 means the FK column is also UNIQUE.
    description : str, optional
        Human-readable label used in feedback (e.g. ``"loan → book"``).
    """

    from_table: str
    to_table: str
    cardinality: Cardinality
    description: Optional[str] = None


@dataclass
class TableSpec:
    """A required table with its required columns."""

    name: str
    required_columns: list[ColumnSpec]
    description: Optional[str] = None


@dataclass
class ExerciseSpec:
    """The full specification for one project stage.

    Parameters
    ----------
    title, description : str
        Shown in the feedback heading.
    required_tables : list[TableSpec]
        Tables (with their required columns) the model must contain.
    required_relationships : list[RelationshipSpec], optional
        Semantic relationships the model must contain.
    required_views : list[str], optional
        Names of views the model must contain. Matched case-insensitively,
        like tables. Empty for the early stages; the mechanism exists so
        later stages (CREATE VIEW) can require views.
    inherits_from : ExerciseSpec, optional
        When set, this spec only declares its *additions*; the parent's
        requirements are merged in by :meth:`resolve`. Chains may be
        several levels deep (Stage 4 inherits Stage 3 inherits Stage 2).
    """

    title: str
    description: str
    required_tables: list[TableSpec] = field(default_factory=list)
    required_relationships: list[RelationshipSpec] = field(default_factory=list)
    required_views: list[str] = field(default_factory=list)
    inherits_from: Optional["ExerciseSpec"] = None

    def resolve(self) -> "ExerciseSpec":
        """Return a fully-resolved, inheritance-free copy of this spec.

        Walks the :attr:`inherits_from` chain and merges every parent's
        requirements with this spec's additions. The returned spec keeps
        *this* spec's ``title`` and ``description`` but has
        ``inherits_from`` set to ``None`` and self-contained requirement
        lists, so the comparison logic never has to know about
        inheritance.

        Merge rules (parent first, child added on top):

        * **Tables** — union by name (case-insensitive). A table declared
          in both parent and child is merged; their columns are unioned.
        * **Columns** of a shared table — union by name; a child column
          redeclaring a parent column replaces it.
        * **Relationships / views** — union, de-duplicated.

        The method is idempotent: resolving an already-resolved spec
        returns an equivalent spec.
        """
        if self.inherits_from is None:
            return ExerciseSpec(
                title=self.title,
                description=self.description,
                required_tables=_merge_tables([], self.required_tables),
                required_relationships=_merge_relationships(
                    [], self.required_relationships
                ),
                required_views=_merge_views([], self.required_views),
                inherits_from=None,
            )

        parent = self.inherits_from.resolve()
        return ExerciseSpec(
            title=self.title,
            description=self.description,
            required_tables=_merge_tables(
                parent.required_tables, self.required_tables
            ),
            required_relationships=_merge_relationships(
                parent.required_relationships, self.required_relationships
            ),
            required_views=_merge_views(
                parent.required_views, self.required_views
            ),
            inherits_from=None,
        )


# ── Merge helpers for spec inheritance ───────────────────────────────────────


def _merge_columns(
    parent_cols: list[ColumnSpec],
    child_cols: list[ColumnSpec],
) -> list[ColumnSpec]:
    """Union two column lists by name; a child column overrides its parent."""
    merged: list[ColumnSpec] = list(parent_cols)
    position: dict[str, int] = {c.name.lower(): i for i, c in enumerate(merged)}
    for col in child_cols:
        key = col.name.lower()
        if key in position:
            merged[position[key]] = col
        else:
            position[key] = len(merged)
            merged.append(col)
    return merged


def _merge_tables(
    parent_tables: list[TableSpec],
    child_tables: list[TableSpec],
) -> list[TableSpec]:
    """Union two table lists by name, merging columns of shared tables."""
    merged: list[TableSpec] = []
    position: dict[str, int] = {}
    for table in parent_tables:
        position[table.name.lower()] = len(merged)
        merged.append(
            TableSpec(
                name=table.name,
                required_columns=list(table.required_columns),
                description=table.description,
            )
        )
    for table in child_tables:
        key = table.name.lower()
        if key in position:
            existing = merged[position[key]]
            existing.required_columns = _merge_columns(
                existing.required_columns, table.required_columns
            )
            if table.description:
                existing.description = table.description
        else:
            position[key] = len(merged)
            merged.append(
                TableSpec(
                    name=table.name,
                    required_columns=list(table.required_columns),
                    description=table.description,
                )
            )
    return merged


def _merge_relationships(
    parent_rels: list[RelationshipSpec],
    child_rels: list[RelationshipSpec],
) -> list[RelationshipSpec]:
    """Union two relationship lists, de-duplicating by tables + cardinality."""
    merged: list[RelationshipSpec] = []
    seen: set[tuple[str, str, str]] = set()
    for rel in list(parent_rels) + list(child_rels):
        signature = (
            rel.from_table.lower(),
            rel.to_table.lower(),
            rel.cardinality,
        )
        if signature in seen:
            continue
        seen.add(signature)
        merged.append(rel)
    return merged


def _merge_views(parent_views: list[str], child_views: list[str]) -> list[str]:
    """Union two view-name lists, de-duplicating case-insensitively."""
    merged: list[str] = []
    seen: set[str] = set()
    for name in list(parent_views) + list(child_views):
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(name)
    return merged
