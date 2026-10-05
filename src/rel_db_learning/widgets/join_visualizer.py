"""Interactive join visualizer for REL_DB_LEARNING module 04.

``join_visualizer`` is a static, in-memory teaching widget. It does not touch
the database, specs, seed data, or schema — it computes joins in pure Python
over small hardcoded sample tables, so students can flip between INNER, LEFT,
RIGHT, and FULL joins and immediately see how the result set changes.

Used in module 04, notebook 07 (joins).
"""

from __future__ import annotations

import html as _html
from typing import Dict, List, Optional, Sequence, Tuple

import ipywidgets as widgets
from IPython.display import display

_JOIN_TYPES = ("INNER", "LEFT", "RIGHT", "FULL")

_JOIN_WORDS = {
    "INNER": "INNER JOIN",
    "LEFT": "LEFT JOIN",
    "RIGHT": "RIGHT JOIN",
    "FULL": "FULL JOIN",
}

_MEMBER_COLUMNS = ["member_id", "full_name"]
_MEMBER_ROWS = [
    [1, "Alice Green"],
    [2, "Bob Stone"],
    [3, "Carla Reyes"],
]

_LOAN_COLUMNS = ["loan_id", "member_id", "loan_date"]
_LOAN_ROWS = [
    [101, 1, "2024-01-10"],
    [102, 1, "2024-02-05"],
    [103, 2, "2024-01-22"],
    [104, 99, "2024-03-01"],
]

_ORPHAN_NOTE = (
    "Note: in the real Library database, foreign key constraints prevent a "
    "loan from referencing a member who does not exist, so you would not see "
    "right-side NULLs there. This small example includes one such row on "
    "purpose, so you can see how RIGHT and FULL joins behave when a match is "
    "missing."
)


def _compute_join(
    left_name: str,
    left_cols: Sequence[str],
    left_rows: Sequence[Sequence],
    right_name: str,
    right_cols: Sequence[str],
    right_rows: Sequence[Sequence],
    join_key: str,
    join_type: str,
) -> Tuple[List[str], List[Dict]]:
    """Compute a join between two in-memory tables.

    Parameters
    ----------
    left_name : str
        Name used to qualify left-hand column names in the result.
    left_cols : sequence of str
        Column names of the left table.
    left_rows : sequence of sequence
        Row values of the left table, aligned to ``left_cols``.
    right_name : str
        Name used to qualify right-hand column names in the result.
    right_cols : sequence of str
        Column names of the right table.
    right_rows : sequence of sequence
        Row values of the right table, aligned to ``right_cols``.
    join_key : str
        Column name to join on. Must be present in both ``left_cols`` and
        ``right_cols``.
    join_type : str
        One of ``"INNER"``, ``"LEFT"``, ``"RIGHT"``, ``"FULL"``.

    Returns
    -------
    tuple of (list of str, list of dict)
        ``result_columns`` is the qualified column names, left columns first
        then right columns. ``result_rows`` is a list of
        ``{"cells": list, "origin": str}`` dicts, where ``cells`` aligns to
        ``result_columns`` (``None`` marks a NULL from a missing side) and
        ``origin`` is one of ``"matched"``, ``"left_only"``, ``"right_only"``.

    Raises
    ------
    ValueError
        If ``join_key`` is missing from either side, or ``join_type`` is not
        one of the four supported values.
    """
    if join_type not in _JOIN_TYPES:
        raise ValueError(
            f"join_type must be one of {_JOIN_TYPES}, got {join_type!r}."
        )
    if join_key not in left_cols:
        raise ValueError(
            f"join_key {join_key!r} is not a column of the left table "
            f"({list(left_cols)!r})."
        )
    if join_key not in right_cols:
        raise ValueError(
            f"join_key {join_key!r} is not a column of the right table "
            f"({list(right_cols)!r})."
        )

    left_idx = left_cols.index(join_key)
    right_idx = right_cols.index(join_key)

    result_columns = [f"{left_name}.{c}" for c in left_cols] + [
        f"{right_name}.{c}" for c in right_cols
    ]

    left_nulls = [None] * len(left_cols)
    right_nulls = [None] * len(right_cols)

    result_rows: List[Dict] = []
    matched_right_indices = set()

    for left_row in left_rows:
        key_value = left_row[left_idx]
        matches = [
            (i, right_row)
            for i, right_row in enumerate(right_rows)
            if right_row[right_idx] == key_value
        ]
        if matches:
            for i, right_row in matches:
                matched_right_indices.add(i)
                result_rows.append({
                    "cells": list(left_row) + list(right_row),
                    "origin": "matched",
                })
        elif join_type in ("LEFT", "FULL"):
            result_rows.append({
                "cells": list(left_row) + right_nulls,
                "origin": "left_only",
            })

    if join_type in ("RIGHT", "FULL"):
        for i, right_row in enumerate(right_rows):
            if i not in matched_right_indices:
                result_rows.append({
                    "cells": left_nulls + list(right_row),
                    "origin": "right_only",
                })

    return result_columns, result_rows


def _render_source_table(columns: Sequence[str], rows: Sequence[Sequence]) -> str:
    """Render a source table as a plain HTML table (no caption)."""
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(str(c))}</th>"
        for c in columns
    )
    body = ""
    for row in rows:
        cells = "".join(
            f"<td style='border:1px solid #ddd; padding:4px 8px;'>"
            f"{_html.escape(str(v))}</td>"
            for v in row
        )
        body += f"<tr>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse; margin-bottom:8px;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def _render_cell(value: object) -> str:
    """Render a single result cell, showing NULL for missing values."""
    if value is None:
        return "<span style='color:#9e9e9e; font-style:italic;'>NULL</span>"
    return _html.escape(str(value))


def _render_result_table(columns: Sequence[str], rows: Sequence[Dict]) -> str:
    """Render the joined result as an HTML table with origin-based row shading."""
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(c)}</th>"
        for c in columns
    )
    body = ""
    for row in rows:
        bg = "#e8f5e9" if row["origin"] == "matched" else "#f5f5f5"
        cells = "".join(
            f"<td style='border:1px solid #ddd; padding:4px 8px;'>"
            f"{_render_cell(v)}</td>"
            for v in row["cells"]
        )
        body += f"<tr style='background:{bg};'>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def _render_sql(left_name: str, right_name: str, join_key: str, join_type: str) -> str:
    """Render the SQL equivalent of the selected join as a monospace box."""
    sql = (
        f"SELECT *\n"
        f"FROM {left_name}\n"
        f"{_JOIN_WORDS[join_type]} {right_name} ON "
        f"{left_name}.{join_key} = {right_name}.{join_key};"
    )
    return (
        "<div style='font-family:monospace; background:#f5f5f5; "
        "border:1px solid #ddd; padding:6px 10px; margin-top:8px; "
        "border-radius:4px; white-space:pre;'>"
        f"{_html.escape(sql)}"
        "</div>"
    )


def join_visualizer(
    left_table: Optional[Tuple[List[str], List[List]]] = None,
    right_table: Optional[Tuple[List[str], List[List]]] = None,
    left_name: str = "member",
    right_name: str = "loan",
    join_key: str = "member_id",
    show_sql: bool = True,
) -> None:
    """Display an interactive join visualizer over two small in-memory tables.

    Renders the two source tables, a control to pick the join type, and a
    result area that recomputes the joined result (and, optionally, the
    equivalent SQL) whenever the join type changes. Nothing here touches the
    database, specs, seed data, or schema — it is a static teaching aid.

    Parameters
    ----------
    left_table : tuple of (list of str, list of list), optional
        ``(columns, rows)`` for the left table. Defaults to a small sample
        ``member`` table when omitted.
    right_table : tuple of (list of str, list of list), optional
        ``(columns, rows)`` for the right table. Defaults to a small sample
        ``loan`` table when omitted.
    left_name : str, optional
        Display name and SQL alias for the left table. Defaults to
        ``"member"``.
    right_name : str, optional
        Display name and SQL alias for the right table. Defaults to
        ``"loan"``.
    join_key : str, optional
        Column to join on; must exist in both tables. Defaults to
        ``"member_id"``.
    show_sql : bool, optional
        When True (the default), show the equivalent SQL below the result
        table.

    Raises
    ------
    ValueError
        If ``join_key`` is not present in both tables.
    """
    left_cols, left_rows = left_table if left_table is not None else (
        _MEMBER_COLUMNS, _MEMBER_ROWS,
    )
    right_cols, right_rows = right_table if right_table is not None else (
        _LOAN_COLUMNS, _LOAN_ROWS,
    )

    if join_key not in left_cols:
        raise ValueError(
            f"join_key {join_key!r} is not a column of the left table "
            f"({list(left_cols)!r})."
        )
    if join_key not in right_cols:
        raise ValueError(
            f"join_key {join_key!r} is not a column of the right table "
            f"({list(right_cols)!r})."
        )

    source_html = (
        f"<div style='font-weight:bold; margin-bottom:4px;'>"
        f"Left table: {_html.escape(left_name)}</div>"
        + _render_source_table(left_cols, left_rows)
        + f"<div style='font-weight:bold; margin:8px 0 4px 0;'>"
        f"Right table: {_html.escape(right_name)}</div>"
        + _render_source_table(right_cols, right_rows)
        + f"<p style='margin-top:10px;'>{_html.escape(_ORPHAN_NOTE)}</p>"
    )
    display(widgets.HTML(value=source_html))

    join_type_control = widgets.RadioButtons(
        options=list(_JOIN_TYPES),
        value="INNER",
        description="Join type:",
    )
    output = widgets.Output()

    def _render(join_type: str) -> None:
        result_columns, result_rows = _compute_join(
            left_name, left_cols, left_rows,
            right_name, right_cols, right_rows,
            join_key, join_type,
        )
        html = (
            f"<div style='font-weight:bold; margin-bottom:4px;'>Result:</div>"
            + _render_result_table(result_columns, result_rows)
        )
        if show_sql:
            html += _render_sql(left_name, right_name, join_key, join_type)
        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _on_change(change: Dict) -> None:
        if change["name"] == "value":
            _render(change["new"])

    join_type_control.observe(_on_change, names="value")

    display(join_type_control)
    display(output)
    _render(join_type_control.value)
