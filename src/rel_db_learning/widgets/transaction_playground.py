"""Interactive transaction playground for REL_DB_LEARNING module 04.

``transaction_playground`` is a static, in-memory teaching widget. It does
not touch the database, specs, seed data, or schema, it is a concept-first
walkthrough of a fixed lending transaction, meant to run before the SQL
syntax for transactions is introduced. It makes three otherwise invisible
properties visible: atomicity (all-or-nothing rollback), isolation
(uncommitted changes are invisible to other sessions), and durability and
visibility (a commit makes changes permanent and visible everywhere).

Used in module 04, notebook 13 (transactions), placed before the SQL is
taught.
"""

from __future__ import annotations

import html as _html
from typing import Callable, Dict, List, Optional, Sequence

import ipywidgets as widgets
from IPython.display import display

_ACTIVE_BACKGROUND = "#1565c0"
_ACTIVE_TEXT = "#ffffff"
_DONE_BACKGROUND = "#90caf9"
_DONE_TEXT = "#0d47a1"
_UPCOMING_BACKGROUND = "#eeeeee"
_UPCOMING_TEXT = "#424242"
_CHANGED_BACKGROUND = "#e8f5e9"
_NO_CHANGES_COLOR = "#9e9e9e"
_COMMIT_COLOR = "#2e7d32"
_ROLLBACK_COLOR = "#c62828"

_BOOK_COLUMNS = ["book_id", "title", "is_available"]
_LOAN_COLUMNS = ["loan_id", "book_id", "member_id"]

_INITIAL_BOOK_ROWS: List[Dict] = [
    {"book_id": 1, "title": "The Silmarillion", "is_available": True},
    {"book_id": 2, "title": "Neuromancer", "is_available": True},
]
_INITIAL_LOAN_ROWS: List[Dict] = [
    {"loan_id": 400, "book_id": 2, "member_id": 3},
]
_NEW_LOAN_ROW: Dict = {"loan_id": 500, "book_id": 1, "member_id": 1}

_STEP_LABELS = [
    "Start",
    "Open transaction",
    "Record the loan",
    "Mark book unavailable",
    "Commit / Roll back",
]

_STEP_SQL = {
    1: "BEGIN;",
    2: "INSERT INTO loan (loan_id, book_id, member_id) VALUES (500, 1, 1);",
    3: "UPDATE book SET is_available = false WHERE book_id = 1;",
}
_TERMINAL_SQL = {"commit": "COMMIT;", "rollback": "ROLLBACK;"}

_INTRO_NOTE = (
    "Follow the steps below to see what a transaction actually does behind "
    "the scenes, before we look at the SQL that drives it."
)


def _copy_rows(rows: Sequence[Dict]) -> List[Dict]:
    """Return a fresh list of shallow copies of ``rows``."""
    return [dict(row) for row in rows]


def _initial_state() -> Dict[str, List[Dict]]:
    """The shared data before any transaction runs."""
    return {"book": _copy_rows(_INITIAL_BOOK_ROWS), "loan": _copy_rows(_INITIAL_LOAN_ROWS)}


def _changed_state() -> Dict[str, List[Dict]]:
    """The shared data after both transaction statements have taken effect."""
    book = _copy_rows(_INITIAL_BOOK_ROWS)
    for row in book:
        if row["book_id"] == 1:
            row["is_available"] = False
    loan = _copy_rows(_INITIAL_LOAN_ROWS) + [dict(_NEW_LOAN_ROW)]
    return {"book": book, "loan": loan}


def _your_session_state(step: int) -> Dict[str, List[Dict]]:
    """The transaction's own view of the data at steps 0-3."""
    if step in (0, 1):
        return _initial_state()
    if step == 2:
        return {
            "book": _copy_rows(_INITIAL_BOOK_ROWS),
            "loan": _copy_rows(_INITIAL_LOAN_ROWS) + [dict(_NEW_LOAN_ROW)],
        }
    return _changed_state()  # step == 3


def _state_at_step(step: int, choice: Optional[str] = None) -> Dict[str, Dict[str, List[Dict]]]:
    """Compute what each session sees at a given step of the lending transaction.

    Parameters
    ----------
    step : int
        The current step, 0 through 4:
        0 Start, 1 Open transaction, 2 Record the loan, 3 Mark book
        unavailable, 4 the terminal Commit/Roll back step.
    choice : str, optional
        Required and must be ``"commit"`` or ``"rollback"`` when
        ``step == 4``. Must be omitted (None) for steps 0-3.

    Returns
    -------
    dict
        ``{"your_session": {"book": [...], "loan": [...]}, "other_session": {...}}``.
        Each table is a fresh list of row dicts, so callers may mutate the
        result freely.

    Raises
    ------
    ValueError
        If ``step`` is not one of 0, 1, 2, 3, 4; if ``choice`` is given for
        steps 0-3; or if ``step == 4`` and ``choice`` is not ``"commit"`` or
        ``"rollback"``.
    """
    if step not in range(5):
        raise ValueError(f"step must be 0-4, got {step!r}.")

    if step != 4:
        if choice is not None:
            raise ValueError(
                f"choice must be None for step {step!r}; only step 4 has a choice."
            )
        return {
            "your_session": _your_session_state(step),
            "other_session": _initial_state(),
        }

    if choice not in ("commit", "rollback"):
        raise ValueError(
            f"choice must be 'commit' or 'rollback' at step 4, got {choice!r}."
        )
    build_state = _changed_state if choice == "commit" else _initial_state
    return {"your_session": build_state(), "other_session": build_state()}


def _is_book_row_changed(row: Dict) -> bool:
    """True if ``row`` differs from the initial book table's matching row."""
    for initial_row in _INITIAL_BOOK_ROWS:
        if initial_row["book_id"] == row["book_id"]:
            return initial_row["is_available"] != row["is_available"]
    return True


def _is_loan_row_changed(row: Dict) -> bool:
    """True if ``row`` is not one of the initial loan table's rows."""
    return not any(initial_row["loan_id"] == row["loan_id"] for initial_row in _INITIAL_LOAN_ROWS)


def _render_table(
    columns: Sequence[str],
    rows: Sequence[Dict],
    changed_predicate: Callable[[Dict], bool],
) -> str:
    """Render ``rows`` as an HTML table, shading changed rows light green."""
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(col)}</th>"
        for col in columns
    )
    body = ""
    for row in rows:
        style_attr = (
            f" style='background:{_CHANGED_BACKGROUND};'"
            if changed_predicate(row) else ""
        )
        cells = "".join(
            f"<td style='border:1px solid #ddd; padding:4px 8px;'>"
            f"{_html.escape(str(row[col]))}</td>"
            for col in columns
        )
        body += f"<tr{style_attr}>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse; margin-bottom:6px;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def _render_panel(title: str, state: Dict[str, List[Dict]], show_no_changes_caption: bool) -> str:
    """Render one session's panel: a title, the book table, and the loan table."""
    html = f"<div style='font-weight:bold; margin-bottom:4px;'>{_html.escape(title)}</div>"
    html += "<div style='font-size:0.85em; color:#555; margin-bottom:2px;'>book</div>"
    html += _render_table(_BOOK_COLUMNS, state["book"], _is_book_row_changed)
    html += "<div style='font-size:0.85em; color:#555; margin-bottom:2px;'>loan</div>"
    html += _render_table(_LOAN_COLUMNS, state["loan"], _is_loan_row_changed)
    if show_no_changes_caption:
        html += (
            f"<div style='color:{_NO_CHANGES_COLOR}; font-size:0.9em; "
            "margin-top:2px;'>Sees no changes yet</div>"
        )
    return html


def _render_roadmap(step: int, choice: Optional[str]) -> str:
    """Render the five-stage roadmap strip, highlighting the current stage."""
    labels = list(_STEP_LABELS)
    if step == 4 and choice is not None:
        labels[4] = "Committed" if choice == "commit" else "Rolled back"

    segments = []
    for i, label in enumerate(labels):
        if i < step:
            background, text_color = _DONE_BACKGROUND, _DONE_TEXT
        elif i == step:
            background, text_color = _ACTIVE_BACKGROUND, _ACTIVE_TEXT
        else:
            background, text_color = _UPCOMING_BACKGROUND, _UPCOMING_TEXT
        segments.append(
            "<span style='display:inline-block; padding:6px 10px; margin-right:4px; "
            f"margin-bottom:4px; border-radius:4px; background:{background}; "
            f"color:{text_color};'>{_html.escape(label)}</span>"
        )
    return "<div style='margin-bottom:8px;'>" + "".join(segments) + "</div>"


def _render_sql_box(step: int, choice: Optional[str]) -> str:
    """Render the small secondary SQL box for the current step, if any."""
    sql = _STEP_SQL.get(step)
    if sql is None and step == 4 and choice is not None:
        sql = _TERMINAL_SQL[choice]
    if sql is None:
        return ""
    return (
        "<div style='margin-bottom:8px;'>"
        "<div style='font-size:0.9em; color:#555; margin-bottom:2px;'>"
        "The SQL you will learn next:</div>"
        "<div style='font-family:monospace; background:#f5f5f5; border:1px solid #ddd; "
        "padding:6px 10px; border-radius:4px; white-space:pre; display:inline-block;'>"
        f"{_html.escape(sql)}</div></div>"
    )


def transaction_playground() -> None:
    """Display an interactive, concept-first walkthrough of a database transaction.

    Walks through a fixed lending transaction (open, record a loan, mark a
    book unavailable, then commit or roll back) one step at a time, showing
    the shared data as seen by two side-by-side sessions: the transaction's
    own session and another librarian's session on a different connection.

    This makes three properties visible without any SQL: isolation
    (uncommitted changes are invisible to the other session through Steps
    1-3), atomicity (rolling back undoes every change, all or nothing), and
    durability and visibility (committing makes the changes permanent and
    immediately visible to the other session too).

    This widget is static and in-memory: it never touches the database,
    specs, seed data, or schema.
    """
    step = 0
    choice: Optional[str] = None

    forward_button = widgets.Button(description="Step forward")
    commit_button = widgets.Button(description="Commit")
    rollback_button = widgets.Button(description="Roll back")
    reset_button = widgets.Button(description="Reset")
    controls_box = widgets.HBox([forward_button, reset_button])
    output = widgets.Output()

    def _update_controls() -> None:
        if step == 3:
            controls_box.children = [commit_button, rollback_button, reset_button]
        elif step == 4:
            controls_box.children = [reset_button]
        else:
            controls_box.children = [forward_button, reset_button]

    def _render() -> None:
        state_now = _state_at_step(step, choice)

        html = _render_roadmap(step, choice)
        html += _render_sql_box(step, choice)

        show_other_caption = step in (1, 2, 3)
        html += "<div style='display:flex; gap:24px; flex-wrap:wrap;'>"
        html += (
            "<div style='flex:1; min-width:260px;'>"
            + _render_panel("Your session", state_now["your_session"], False)
            + "</div>"
        )
        html += (
            "<div style='flex:1; min-width:260px;'>"
            + _render_panel(
                "Another librarian's session",
                state_now["other_session"],
                show_other_caption,
            )
            + "</div>"
        )
        html += "</div>"

        if step == 4:
            if choice == "commit":
                html += (
                    f"<div style='color:{_COMMIT_COLOR}; font-weight:bold; "
                    "margin-top:8px;'>Committed: the changes are now permanent "
                    "and visible to every session.</div>"
                )
            else:
                html += (
                    f"<div style='color:{_ROLLBACK_COLOR}; font-weight:bold; "
                    "margin-top:8px;'>Rolled back: all changes were undone. The "
                    "database is exactly as it was before BEGIN.</div>"
                )

        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _on_forward_clicked(_button: widgets.Button) -> None:
        nonlocal step
        if step < 3:
            step += 1
        _update_controls()
        _render()

    def _on_commit_clicked(_button: widgets.Button) -> None:
        nonlocal step, choice
        step, choice = 4, "commit"
        _update_controls()
        _render()

    def _on_rollback_clicked(_button: widgets.Button) -> None:
        nonlocal step, choice
        step, choice = 4, "rollback"
        _update_controls()
        _render()

    def _on_reset_clicked(_button: widgets.Button) -> None:
        nonlocal step, choice
        step, choice = 0, None
        _update_controls()
        _render()

    forward_button.on_click(_on_forward_clicked)
    commit_button.on_click(_on_commit_clicked)
    rollback_button.on_click(_on_rollback_clicked)
    reset_button.on_click(_on_reset_clicked)

    _update_controls()
    display(widgets.HTML(value=f"<p>{_html.escape(_INTRO_NOTE)}</p>"))
    display(controls_box)
    display(output)
    _render()
