"""Interactive view-staleness explorer for REL_DB_LEARNING module 04.

``view_staleness`` is a static, in-memory teaching widget. It does not touch
the database, specs, seed data, or schema — it works over a small hardcoded
loan table, so students can see the difference between an ordinary view
(recomputed on every read, so always current) and a materialized view
(stores its last computed result, so it can go stale until REFRESH is run).

Used in module 04, notebook 10 (views).
"""

from __future__ import annotations

import html as _html
from typing import Dict, List, Sequence, Tuple

import ipywidgets as widgets
from IPython.display import display

_STALE_COLOR = "#e65100"
_UP_TO_DATE_COLOR = "#2e7d32"
_STALE_BACKGROUND = "#fff3e0"

_BASE_COLUMNS = ["loan_id", "member_name"]
_VIEW_COLUMNS = ["member_name", "loan_count"]

_MEMBERS = ["Alice Green", "Bob Stone", "Carla Reyes"]

_ORIGINAL_BASE_ROWS: List[Dict] = [
    {"loan_id": 101, "member_name": "Alice Green"},
    {"loan_id": 102, "member_name": "Alice Green"},
    {"loan_id": 103, "member_name": "Bob Stone"},
    {"loan_id": 104, "member_name": "Carla Reyes"},
]

_INTRO_NOTE = (
    "An ordinary view recomputes its query every time you read it, so it is "
    "always current. A materialized view stores its last computed result "
    "and only updates when you run REFRESH, so it can become stale once the "
    "base table changes underneath it."
)


def _loans_per_member(rows: Sequence[Dict]) -> List[Tuple[str, int]]:
    """Compute loans per member from base rows.

    Parameters
    ----------
    rows : sequence of dict
        Base loan rows, each with at least a ``member_name`` key.

    Returns
    -------
    list of tuple of (str, int)
        ``(member_name, loan_count)`` pairs, sorted by ``member_name``.
    """
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["member_name"]] = counts.get(row["member_name"], 0) + 1
    return sorted(counts.items())


def _is_stale(snapshot: Sequence[Tuple[str, int]], base_rows: Sequence[Dict]) -> bool:
    """Return True if ``snapshot`` differs from a fresh computation over ``base_rows``.

    Parameters
    ----------
    snapshot : sequence of tuple of (str, int)
        The materialized view's stored ``(member_name, loan_count)`` rows.
    base_rows : sequence of dict
        The current base loan rows.

    Returns
    -------
    bool
        True if the stored snapshot no longer matches what a fresh
        recomputation over ``base_rows`` would produce.
    """
    return list(snapshot) != _loans_per_member(base_rows)


def _next_loan_id(rows: Sequence[Dict]) -> int:
    """Return one more than the largest existing ``loan_id`` in ``rows``."""
    return max(row["loan_id"] for row in rows) + 1


def _build_new_loan_row(rows: Sequence[Dict], member_name: str) -> Dict:
    """Build a new loan row for ``member_name``.

    Parameters
    ----------
    rows : sequence of dict
        The current base loan rows, used to pick the next ``loan_id``.
    member_name : str
        The member to create a loan for. Must be one of :data:`_MEMBERS`.

    Returns
    -------
    dict
        A new row with a fresh ``loan_id`` and the given ``member_name``.

    Raises
    ------
    ValueError
        If ``member_name`` is not one of the allowed sample members.
    """
    if member_name not in _MEMBERS:
        raise ValueError(
            f"member_name {member_name!r} is not one of the sample members "
            f"{_MEMBERS!r}."
        )
    return {"loan_id": _next_loan_id(rows), "member_name": member_name}


def _render_table(columns: Sequence[str], rows: Sequence[Sequence], amber: bool = False) -> str:
    """Render ``rows`` as an HTML table, optionally shading cells light amber."""
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(col)}</th>"
        for col in columns
    )
    cell_style = "border:1px solid #ddd; padding:4px 8px;"
    if amber:
        cell_style += f" background:{_STALE_BACKGROUND};"
    body = ""
    for row in rows:
        cells = "".join(
            f"<td style='{cell_style}'>{_html.escape(str(value))}</td>"
            for value in row
        )
        body += f"<tr>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse; margin-bottom:4px;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def view_staleness() -> None:
    """Display an interactive comparison of an ordinary view and a materialized view.

    Shows a small base ``loan`` table alongside two derived views over it
    (loans grouped by member): an ordinary view, which is recomputed from
    the base table on every render, and a materialized view, which shows a
    stored snapshot that only updates when REFRESH is pressed. Adding a
    loan makes the materialized view stale until it is refreshed; Reset
    restores the original base rows and re-syncs the snapshot.

    This widget is static and in-memory: it never touches the database,
    specs, seed data, or schema.
    """
    base_rows: List[Dict] = [dict(row) for row in _ORIGINAL_BASE_ROWS]
    materialized_snapshot: List[Tuple[str, int]] = _loans_per_member(base_rows)

    member_dropdown = widgets.Dropdown(options=_MEMBERS, description="Member:")
    add_button = widgets.Button(description="Add loan")
    refresh_button = widgets.Button(description="REFRESH materialized view")
    reset_button = widgets.Button(description="Reset")
    output = widgets.Output()

    def _render(status_text: str = "") -> None:
        ordinary_counts = _loans_per_member(base_rows)
        stale = _is_stale(materialized_snapshot, base_rows)
        caption_color = _STALE_COLOR if stale else _UP_TO_DATE_COLOR
        caption_text = (
            "Stale: this does not reflect the latest base table. Press REFRESH."
            if stale else "Up to date."
        )

        html = (
            "<div style='font-weight:bold; margin-bottom:4px;'>Base table: loan</div>"
            + _render_table(
                _BASE_COLUMNS,
                [(row["loan_id"], row["member_name"]) for row in base_rows],
            )
            + "<div style='font-weight:bold; margin:8px 0 4px 0;'>"
            "Ordinary view: loans_per_member (always current)</div>"
            + _render_table(_VIEW_COLUMNS, ordinary_counts)
            + "<div style='font-weight:bold; margin:8px 0 4px 0;'>"
            "Materialized view: loans_per_member (refreshed on demand)</div>"
            + _render_table(_VIEW_COLUMNS, materialized_snapshot, amber=stale)
            + f"<div style='color:{caption_color}; margin-bottom:4px;'>"
            f"{_html.escape(caption_text)}</div>"
        )
        if status_text:
            html += f"<div style='margin-top:4px;'>{_html.escape(status_text)}</div>"

        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _on_add_clicked(_button: widgets.Button) -> None:
        member_name = member_dropdown.value
        new_row = _build_new_loan_row(base_rows, member_name)
        base_rows.append(new_row)
        _render(
            status_text=(
                f"Added loan {new_row['loan_id']} for {member_name}. "
                "The materialized view is now stale; press REFRESH to update it."
            )
        )

    def _on_refresh_clicked(_button: widgets.Button) -> None:
        nonlocal materialized_snapshot
        materialized_snapshot = _loans_per_member(base_rows)
        _render(status_text="Materialized view refreshed: it now matches the ordinary view.")

    def _on_reset_clicked(_button: widgets.Button) -> None:
        nonlocal materialized_snapshot
        base_rows.clear()
        base_rows.extend(dict(row) for row in _ORIGINAL_BASE_ROWS)
        materialized_snapshot = _loans_per_member(base_rows)
        _render(status_text="")

    add_button.on_click(_on_add_clicked)
    refresh_button.on_click(_on_refresh_clicked)
    reset_button.on_click(_on_reset_clicked)

    display(widgets.HTML(value=f"<p>{_html.escape(_INTRO_NOTE)}</p>"))
    display(widgets.HBox([member_dropdown, add_button, refresh_button, reset_button]))
    display(output)
    _render()
