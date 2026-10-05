"""Interactive lossless-join decomposition explorer for REL_DB_LEARNING module 05.

``decomposition_explorer`` is a static, in-memory teaching widget. It does
not touch the database, specs, seed data, or schema, it works over a small
hardcoded ``address`` table (matching the notebook's zip/city example) and
lets a student pick a predefined way to split it in two, then watches
whether joining the two pieces back together rebuilds the original table
(lossless) or produces spurious rows (lossy).

Used in module 05, notebook 05 (BCNF, lossless-join decomposition).
"""

from __future__ import annotations

import html as _html
from typing import Dict, List, Optional, Sequence, Set, Tuple

import ipywidgets as widgets
from IPython.display import display

_RED = "#c62828"
_GREEN = "#2e7d32"
_SPURIOUS_BACKGROUND = "#ffebee"

_ADDRESS_COLUMNS = ["street", "city", "zip_code"]
_ADDRESS_ROWS: List[List[str]] = [
    ["Kissamou St", "Chania", "73100"],
    ["Apokoronou St", "Chania", "73100"],
    ["Chalepas St", "Chania", "73134"],
    ["Skalidi St", "Kissamos", "73400"],
    ["Irron Pol St", "Kissamos", "73400"],
    ["Omogenon St", "Kissamos", "73400"],
]

_OPTIONS: Dict[str, Dict] = {
    "A": {
        "label": "Split on zip_code (R1: city, zip_code | R2: street, zip_code)",
        "r1_columns": ["city", "zip_code"],
        "r2_columns": ["street", "zip_code"],
        "common_column": "zip_code",
    },
    "B": {
        "label": "Split on city (R1: street, city | R2: city, zip_code)",
        "r1_columns": ["street", "city"],
        "r2_columns": ["city", "zip_code"],
        "common_column": "city",
    },
}


def _project(rows: Sequence[Sequence], all_columns: Sequence[str], keep_columns: Sequence[str]) -> List[Tuple]:
    """Project rows onto a subset of columns, deduplicated.

    Parameters
    ----------
    rows : sequence of sequence
        Rows aligned to ``all_columns``.
    all_columns : sequence of str
        The full column list that ``rows`` is aligned to.
    keep_columns : sequence of str
        The columns to keep, in the order they should appear in the result.

    Returns
    -------
    list of tuple
        The distinct projected rows, in first-seen order, with column order
        matching ``keep_columns``.

    Raises
    ------
    ValueError
        If any column in ``keep_columns`` is not present in ``all_columns``.
    """
    for column in keep_columns:
        if column not in all_columns:
            raise ValueError(
                f"column {column!r} is not in all_columns {list(all_columns)!r}."
            )
    indices = [all_columns.index(column) for column in keep_columns]
    result: List[Tuple] = []
    for row in rows:
        projected = tuple(row[i] for i in indices)
        if projected not in result:
            result.append(projected)
    return result


def _natural_join(
    left_rows: Sequence[Sequence],
    left_cols: Sequence[str],
    right_rows: Sequence[Sequence],
    right_cols: Sequence[str],
) -> Tuple[List[str], List[Tuple]]:
    """Natural join two relations on their common columns.

    Parameters
    ----------
    left_rows : sequence of sequence
        Rows of the left relation, aligned to ``left_cols``.
    left_cols : sequence of str
        Column names of the left relation.
    right_rows : sequence of sequence
        Rows of the right relation, aligned to ``right_cols``.
    right_cols : sequence of str
        Column names of the right relation.

    Returns
    -------
    tuple of (list of str, list of tuple)
        ``result_columns`` is the common columns (in left order), followed
        by the right-only columns. ``result_rows`` is every combination of a
        left row and a right row whose common-column values match.

    Raises
    ------
    ValueError
        If ``left_cols`` and ``right_cols`` share no common column.
    """
    common = [column for column in left_cols if column in right_cols]
    if not common:
        raise ValueError(
            f"no common columns between {list(left_cols)!r} and {list(right_cols)!r}."
        )
    right_only = [column for column in right_cols if column not in common]
    result_columns = list(left_cols) + right_only

    left_index = {column: i for i, column in enumerate(left_cols)}
    right_index = {column: i for i, column in enumerate(right_cols)}

    result_rows: List[Tuple] = []
    for left_row in left_rows:
        left_key = tuple(left_row[left_index[column]] for column in common)
        for right_row in right_rows:
            right_key = tuple(right_row[right_index[column]] for column in common)
            if left_key == right_key:
                extra = tuple(right_row[right_index[column]] for column in right_only)
                result_rows.append(tuple(left_row) + extra)
    return result_columns, result_rows


def _reorder_to(row: Sequence, from_columns: Sequence[str], to_columns: Sequence[str]) -> Tuple:
    """Reorder a row's values from ``from_columns`` order to ``to_columns`` order."""
    index_map = [from_columns.index(column) for column in to_columns]
    return tuple(row[i] for i in index_map)


def _find_spurious(
    original_rows: Sequence[Sequence],
    original_cols: Sequence[str],
    join_cols: Sequence[str],
    join_rows: Sequence[Sequence],
) -> List[Tuple]:
    """Find the join rows that are not present in the original relation.

    Parameters
    ----------
    original_rows : sequence of sequence
        The original relation's rows, aligned to ``original_cols``.
    original_cols : sequence of str
        The original relation's column names.
    join_cols : sequence of str
        The join result's column names. Must be a permutation of
        ``original_cols``.
    join_rows : sequence of sequence
        The join result's rows, aligned to ``join_cols``.

    Returns
    -------
    list of tuple
        The subset of ``join_rows``, reordered to ``original_cols`` order,
        that do not appear in ``original_rows``. These are the spurious
        tuples introduced by a lossy decomposition.

    Raises
    ------
    ValueError
        If ``join_cols`` is not a permutation of ``original_cols``.
    """
    if set(join_cols) != set(original_cols) or len(join_cols) != len(original_cols):
        raise ValueError(
            f"join_cols {list(join_cols)!r} is not a permutation of "
            f"original_cols {list(original_cols)!r}."
        )
    original_set = {tuple(row) for row in original_rows}
    spurious: List[Tuple] = []
    for row in join_rows:
        reordered = _reorder_to(row, join_cols, original_cols)
        if reordered not in original_set:
            spurious.append(reordered)
    return spurious


def _render_table(
    columns: Sequence[str],
    rows: Sequence[Sequence],
    highlighted_indices: Optional[Set[int]] = None,
) -> str:
    """Render rows as an HTML table, shading spurious rows light red."""
    highlighted_indices = highlighted_indices or set()
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(col)}</th>"
        for col in columns
    )
    body = ""
    for i, row in enumerate(rows):
        style_attr = (
            f" style='background:{_SPURIOUS_BACKGROUND};'" if i in highlighted_indices else ""
        )
        cells = "".join(
            f"<td style='border:1px solid #ddd; padding:4px 8px;'>"
            f"{_html.escape(str(value))}</td>"
            for value in row
        )
        body += f"<tr{style_attr}>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse; margin-bottom:4px;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def _render_block(
    title: str,
    columns: Sequence[str],
    rows: Sequence[Sequence],
    highlighted_indices: Optional[Set[int]] = None,
) -> str:
    """Render one labeled table block for the side-by-side layout."""
    return (
        "<div>"
        f"<div style='font-weight:bold; margin-bottom:4px;'>{_html.escape(title)}</div>"
        + _render_table(columns, rows, highlighted_indices)
        + "</div>"
    )


def _render_explanation(title: str, body_html: str, color: str) -> str:
    """Render a colored explanation with a bold title."""
    return (
        f"<div style='color:{color}; font-weight:bold; margin-top:6px; "
        f"margin-bottom:4px;'>{_html.escape(title)}</div>"
        f"<div style='color:{color};'>{body_html}</div>"
    )


def decomposition_explorer() -> None:
    """Display an interactive explorer for lossless vs. lossy decomposition.

    Lets a student choose one of two predefined ways to split the sample
    ``address`` table into R1 and R2, then computes the natural join of R1
    and R2 back together and compares it to the original table. If the join
    reproduces the original rows exactly, the decomposition is lossless. If
    it produces spurious rows that were never in the original table, the
    decomposition is lossy.

    This widget is static and in-memory: it never touches the database,
    specs, seed data, or schema.
    """
    option_dropdown = widgets.Dropdown(
        options=[(_OPTIONS[key]["label"], key) for key in ("A", "B")],
        value="A",
        description="Decomposition:",
    )
    output = widgets.Output()

    def _render(option_key: str) -> None:
        option = _OPTIONS[option_key]
        r1_columns = option["r1_columns"]
        r2_columns = option["r2_columns"]

        r1_rows = _project(_ADDRESS_ROWS, _ADDRESS_COLUMNS, r1_columns)
        r2_rows = _project(_ADDRESS_ROWS, _ADDRESS_COLUMNS, r2_columns)
        join_columns, join_rows = _natural_join(r1_rows, r1_columns, r2_rows, r2_columns)
        spurious_rows = _find_spurious(_ADDRESS_ROWS, _ADDRESS_COLUMNS, join_columns, join_rows)

        original_set = {tuple(row) for row in _ADDRESS_ROWS}
        highlighted_indices = {
            i for i, row in enumerate(join_rows)
            if _reorder_to(row, join_columns, _ADDRESS_COLUMNS) not in original_set
        }

        html = (
            "<div style=\"display:flex; flex-wrap:wrap; gap:24px; align-items:flex-start;\">"
            + _render_block("Original: address", _ADDRESS_COLUMNS, _ADDRESS_ROWS)
            + _render_block("R1", r1_columns, r1_rows)
            + _render_block("R2", r2_columns, r2_rows)
            + _render_block("Join result: R1 natural join R2", join_columns, join_rows, highlighted_indices)
            + "</div>"
        )

        if spurious_rows:
            html += _render_explanation(
                "Lossy decomposition",
                f"Joining R1 and R2 back together produced {len(spurious_rows)} spurious "
                "row(s) that were never in the original table (highlighted above). The "
                f"common column, {_html.escape(option['common_column'])}, does not uniquely "
                "determine the other columns, so the join recombines values that never "
                "belonged together.",
                _RED,
            )
        else:
            html += _render_explanation(
                "Lossless decomposition",
                "Joining R1 and R2 back together rebuilds the original table exactly, "
                "so no information was lost.",
                _GREEN,
            )

        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _on_change(change: Dict) -> None:
        if change["name"] == "value":
            _render(change["new"])

    option_dropdown.observe(_on_change, names="value")

    display(option_dropdown)
    display(output)
    _render(option_dropdown.value)
