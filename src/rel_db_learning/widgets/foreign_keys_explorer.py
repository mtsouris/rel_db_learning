"""Interactive foreign key explorer for REL_DB_LEARNING module 02.

``foreign_keys_explorer`` is a static, in-memory teaching widget. It does
not touch the database, specs, seed data, or schema, and it never shows
SQL: module 02 is pgModeler-first, SQL is not introduced until module 04.
It speaks entirely in actions ("delete this member", "add a loan"), so a
foreign key's protective behavior can be seen before any syntax is
involved.

Used in module 02, notebook 03_foreign_keys.
"""

from __future__ import annotations

import html as _html
from typing import Dict, List, Optional, Sequence, Set, Tuple

import ipywidgets as widgets
from IPython.display import display

_RED = "#c62828"
_GREEN = "#2e7d32"
_AMBER = "#e65100"
_BLOCKING_BACKGROUND = "#ffebee"

_MEMBER_COLUMNS = ["member_id", "full_name"]
_BOOK_COLUMNS = ["book_id", "title"]
_LOAN_COLUMNS = ["loan_id", "member_id", "book_id"]

_INITIAL_MEMBER_ROWS: List[Dict] = [
    {"member_id": 1, "full_name": "Alice Green"},
    {"member_id": 2, "full_name": "Bob Stone"},
    {"member_id": 3, "full_name": "Carla Reyes"},
]
_INITIAL_BOOK_ROWS: List[Dict] = [
    {"book_id": 10, "title": "The Silmarillion"},
    {"book_id": 11, "title": "Neuromancer"},
    {"book_id": 12, "title": "Snow Crash"},
]
_INITIAL_LOAN_ROWS: List[Dict] = [
    {"loan_id": 100, "member_id": 1, "book_id": 10},
    {"loan_id": 101, "member_id": 1, "book_id": 11},
    {"loan_id": 102, "member_id": 2, "book_id": 10},
]

_MISSING_MEMBER_ID = 999
_MISSING_BOOK_ID = 888

_MODE_CAPTIONS = {
    "RESTRICT": (
        "RESTRICT: deleting a member or book that still has loans is blocked, "
        "so no loan is ever left referencing a parent that no longer exists."
    ),
    "CASCADE": (
        "CASCADE: deleting a member or book also deletes every loan that "
        "references it, so no loan is left behind, but those loans disappear "
        "along with their parent."
    ),
}


def _loans_referencing(loan_rows: Sequence[Dict], parent_kind: str, parent_id: int) -> List[Dict]:
    """Return the loan rows that reference the given parent.

    Parameters
    ----------
    loan_rows : sequence of dict
        The current loan rows, each with ``member_id`` and ``book_id`` keys.
    parent_kind : str
        Either ``"member"`` or ``"book"``.
    parent_id : int
        The id of the parent row to check references for.

    Returns
    -------
    list of dict
        The loan rows whose ``{parent_kind}_id`` matches ``parent_id``, in
        their original order.

    Raises
    ------
    ValueError
        If ``parent_kind`` is not ``"member"`` or ``"book"``.
    """
    if parent_kind not in ("member", "book"):
        raise ValueError(f"parent_kind must be 'member' or 'book', got {parent_kind!r}.")
    key = f"{parent_kind}_id"
    return [row for row in loan_rows if row[key] == parent_id]


def _can_delete_parent(
    loan_rows: Sequence[Dict],
    parent_kind: str,
    parent_id: int,
    on_delete: str,
) -> Dict:
    """Determine the outcome of deleting a parent row under a given ON DELETE mode.

    Parameters
    ----------
    loan_rows : sequence of dict
        The current loan rows.
    parent_kind : str
        Either ``"member"`` or ``"book"``.
    parent_id : int
        The id of the parent row to delete.
    on_delete : str
        Either ``"RESTRICT"`` or ``"CASCADE"``.

    Returns
    -------
    dict
        ``{"allowed": bool, "cascaded_loans": list of dict, "blocking_loans": list of dict}``.
        Under RESTRICT, the delete is blocked (``allowed=False``) whenever any
        loan references the parent, and those loans are returned as
        ``blocking_loans``. Under CASCADE, the delete is always allowed, and
        any referencing loans are returned as ``cascaded_loans``.

    Raises
    ------
    ValueError
        If ``parent_kind`` is not ``"member"`` or ``"book"``, or ``on_delete``
        is not ``"RESTRICT"`` or ``"CASCADE"``.
    """
    if on_delete not in ("RESTRICT", "CASCADE"):
        raise ValueError(f"on_delete must be 'RESTRICT' or 'CASCADE', got {on_delete!r}.")

    referencing = _loans_referencing(loan_rows, parent_kind, parent_id)

    if on_delete == "RESTRICT":
        if referencing:
            return {"allowed": False, "cascaded_loans": [], "blocking_loans": referencing}
        return {"allowed": True, "cascaded_loans": [], "blocking_loans": []}

    return {"allowed": True, "cascaded_loans": referencing, "blocking_loans": []}


def _can_add_loan(
    member_rows: Sequence[Dict],
    book_rows: Sequence[Dict],
    member_id: int,
    book_id: int,
) -> Dict:
    """Determine whether a new loan can reference the given member and book.

    Parameters
    ----------
    member_rows : sequence of dict
        The current member rows.
    book_rows : sequence of dict
        The current book rows.
    member_id : int
        The member id the new loan would reference.
    book_id : int
        The book id the new loan would reference.

    Returns
    -------
    dict
        ``{"allowed": bool, "missing": list of str}``. ``missing`` lists which
        referenced parents are absent, as strings like ``"member 999"`` or
        ``"book 888"``; it is empty when both parents exist.
    """
    missing: List[str] = []
    if not any(row["member_id"] == member_id for row in member_rows):
        missing.append(f"member {member_id}")
    if not any(row["book_id"] == book_id for row in book_rows):
        missing.append(f"book {book_id}")
    return {"allowed": not missing, "missing": missing}


def _render_table(columns: Sequence[str], rows: Sequence[Dict], highlighted_loan_ids: Optional[Set[int]] = None) -> str:
    """Render ``rows`` as an HTML table, shading blocking loan rows light red."""
    highlighted_loan_ids = highlighted_loan_ids or set()
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(col)}</th>"
        for col in columns
    )
    body = ""
    for row in rows:
        highlighted = row.get("loan_id") in highlighted_loan_ids
        style_attr = f" style='background:{_BLOCKING_BACKGROUND};'" if highlighted else ""
        cells = "".join(
            f"<td style='border:1px solid #ddd; padding:4px 8px;'>"
            f"{_html.escape(str(row[col]))}</td>"
            for col in columns
        )
        body += f"<tr{style_attr}>{cells}</tr>"
    return (
        f"<table style='border-collapse:collapse; margin-bottom:8px;'>"
        f"<tr>{header}</tr>{body}</table>"
    )


def _render_explanation(title: str, body_html: str, color: str) -> str:
    """Render a colored explanation with a bold title."""
    return (
        f"<div style='color:{color}; font-weight:bold; margin-top:6px; "
        f"margin-bottom:4px;'>{_html.escape(title)}</div>"
        f"<div style='color:{color};'>{body_html}</div>"
    )


def _mode_caption_html(on_delete: str) -> str:
    """Render the plain-language caption for the current ON DELETE mode."""
    return f"<div style='margin-bottom:8px;'>{_html.escape(_MODE_CAPTIONS[on_delete])}</div>"


def foreign_keys_explorer() -> None:
    """Display an interactive explorer for foreign key protective behavior.

    Shows a member table and a book table (parents) and a loan table
    (child, with a foreign key to each parent). Lets a student attempt to
    delete a member or book, or add a loan, and see whether the action
    succeeds, is blocked, or cascades, depending on the chosen ON DELETE
    mode (RESTRICT or CASCADE).

    This widget speaks only in actions, never in SQL: module 02 is
    pgModeler-first and SQL is introduced later, in module 04. It is
    static and in-memory: it never touches the database, specs, seed
    data, or schema.
    """
    member_rows: List[Dict] = [dict(row) for row in _INITIAL_MEMBER_ROWS]
    book_rows: List[Dict] = [dict(row) for row in _INITIAL_BOOK_ROWS]
    loan_rows: List[Dict] = [dict(row) for row in _INITIAL_LOAN_ROWS]
    current_inputs: Dict[str, widgets.Widget] = {}

    on_delete_toggle = widgets.ToggleButtons(
        options=["RESTRICT", "CASCADE"], value="RESTRICT", description="ON DELETE:"
    )
    mode_caption_widget = widgets.HTML(value=_mode_caption_html(on_delete_toggle.value))

    action_toggle = widgets.ToggleButtons(
        options=["Delete a member", "Delete a book", "Add a loan"],
        value="Delete a member",
        description="Action:",
    )
    controls_box = widgets.VBox()
    apply_button = widgets.Button(description="Apply")
    reset_button = widgets.Button(description="Reset")
    output = widgets.Output()

    def _member_options() -> List[Tuple[str, int]]:
        return [(f"{row['member_id']}: {row['full_name']}", row["member_id"]) for row in member_rows]

    def _book_options() -> List[Tuple[str, int]]:
        return [(f"{row['book_id']}: {row['title']}", row["book_id"]) for row in book_rows]

    def _build_controls() -> None:
        action = action_toggle.value
        current_inputs.clear()
        if action == "Delete a member":
            dropdown = widgets.Dropdown(options=_member_options(), description="Member:")
            current_inputs["member_dropdown"] = dropdown
            controls_box.children = [dropdown]
        elif action == "Delete a book":
            dropdown = widgets.Dropdown(options=_book_options(), description="Book:")
            current_inputs["book_dropdown"] = dropdown
            controls_box.children = [dropdown]
        else:  # Add a loan
            member_options = _member_options() + [
                ("a member who does not exist (id 999)", _MISSING_MEMBER_ID)
            ]
            book_options = _book_options() + [
                ("a book that does not exist (id 888)", _MISSING_BOOK_ID)
            ]
            member_dropdown = widgets.Dropdown(options=member_options, description="Member:")
            book_dropdown = widgets.Dropdown(options=book_options, description="Book:")
            current_inputs["member_dropdown"] = member_dropdown
            current_inputs["book_dropdown"] = book_dropdown
            controls_box.children = [member_dropdown, book_dropdown]

    def _render(explanation_html: str = "", highlighted_loan_ids: Optional[Set[int]] = None) -> None:
        html = (
            "<div style=\"display:flex; flex-wrap:wrap; gap:24px; align-items:flex-start;\">"
            + "<div>"
            + "<div style='font-weight:bold; margin-bottom:4px;'>member</div>"
            + _render_table(_MEMBER_COLUMNS, member_rows)
            + "</div>"
            + "<div>"
            + "<div style='font-weight:bold; margin-bottom:4px;'>book</div>"
            + _render_table(_BOOK_COLUMNS, book_rows)
            + "</div>"
            + "<div>"
            + "<div style='font-weight:bold; margin-bottom:4px;'>loan</div>"
            + _render_table(_LOAN_COLUMNS, loan_rows, highlighted_loan_ids)
            + "</div>"
            + "</div>"
        )
        if explanation_html:
            html += explanation_html
        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _handle_delete(parent_kind: str) -> None:
        dropdown = current_inputs.get(f"{parent_kind}_dropdown")
        if dropdown is None or dropdown.value is None:
            _render(_render_explanation(
                "Nothing to delete", "There are no rows left to choose from.", _RED,
            ))
            return
        parent_id = dropdown.value
        on_delete = on_delete_toggle.value
        result = _can_delete_parent(loan_rows, parent_kind, parent_id, on_delete)

        parent_rows = member_rows if parent_kind == "member" else book_rows
        id_key = f"{parent_kind}_id"
        label_key = "full_name" if parent_kind == "member" else "title"
        parent_row = next(row for row in parent_rows if row[id_key] == parent_id)
        label = parent_row[label_key]

        if not result["allowed"]:
            blocking_ids = {row["loan_id"] for row in result["blocking_loans"]}
            count = len(result["blocking_loans"])
            explanation = _render_explanation(
                "Delete blocked",
                f"Deleting {parent_kind} <b>{_html.escape(str(label))}</b> (id {parent_id}) "
                f"is blocked: {count} loan{'s' if count != 1 else ''} still reference it. "
                f"Removing this {parent_kind} would leave those loans pointing at a "
                f"{parent_kind} that no longer exists. This is exactly what the foreign "
                "key prevents.",
                _RED,
            )
            _render(explanation, highlighted_loan_ids=blocking_ids)
            return

        if on_delete == "CASCADE" and result["cascaded_loans"]:
            cascaded_ids = {row["loan_id"] for row in result["cascaded_loans"]}
            id_list = ", ".join(str(loan_id) for loan_id in sorted(cascaded_ids))
            parent_rows.remove(parent_row)
            loan_rows[:] = [row for row in loan_rows if row["loan_id"] not in cascaded_ids]
            explanation = _render_explanation(
                "Cascade delete",
                f"Deleting {parent_kind} <b>{_html.escape(str(label))}</b> (id {parent_id}) "
                f"also deleted the loan(s) that referenced it (loan id(s) {id_list}), "
                "because CASCADE propagates the delete to the children.",
                _AMBER,
            )
            _render(explanation)
            _build_controls()
            return

        parent_rows.remove(parent_row)
        explanation = _render_explanation(
            "Delete succeeded",
            f"Deleted {parent_kind} <b>{_html.escape(str(label))}</b> (id {parent_id}) "
            f"safely: no loan referenced it.",
            _GREEN,
        )
        _render(explanation)
        _build_controls()

    def _handle_add_loan() -> None:
        member_id = current_inputs["member_dropdown"].value
        book_id = current_inputs["book_dropdown"].value
        result = _can_add_loan(member_rows, book_rows, member_id, book_id)

        if not result["allowed"]:
            if len(result["missing"]) == 1:
                missing_text = f"{result['missing'][0]} does not exist"
            else:
                missing_text = f"{' and '.join(result['missing'])} do not exist"
            explanation = _render_explanation(
                "Insert blocked",
                f"This loan cannot be added: {_html.escape(missing_text)}. A foreign key "
                "does not allow a loan to reference a parent that does not exist.",
                _RED,
            )
            _render(explanation)
            return

        new_loan_id = max((row["loan_id"] for row in loan_rows), default=0) + 1
        loan_rows.append({"loan_id": new_loan_id, "member_id": member_id, "book_id": book_id})
        explanation = _render_explanation(
            "Add succeeded",
            f"Added loan {new_loan_id}: member {member_id} borrowed book {book_id}.",
            _GREEN,
        )
        _render(explanation)

    def _on_apply_clicked(_button: widgets.Button) -> None:
        action = action_toggle.value
        if action == "Delete a member":
            _handle_delete("member")
        elif action == "Delete a book":
            _handle_delete("book")
        else:
            _handle_add_loan()

    def _on_reset_clicked(_button: widgets.Button) -> None:
        member_rows[:] = [dict(row) for row in _INITIAL_MEMBER_ROWS]
        book_rows[:] = [dict(row) for row in _INITIAL_BOOK_ROWS]
        loan_rows[:] = [dict(row) for row in _INITIAL_LOAN_ROWS]
        _build_controls()
        _render()

    def _on_action_change(change: Dict) -> None:
        if change["name"] == "value":
            _build_controls()

    def _on_mode_change(change: Dict) -> None:
        if change["name"] == "value":
            mode_caption_widget.value = _mode_caption_html(change["new"])

    action_toggle.observe(_on_action_change, names="value")
    on_delete_toggle.observe(_on_mode_change, names="value")
    apply_button.on_click(_on_apply_clicked)
    reset_button.on_click(_on_reset_clicked)

    _build_controls()

    display(on_delete_toggle)
    display(mode_caption_widget)
    display(action_toggle)
    display(controls_box)
    display(widgets.HBox([apply_button, reset_button]))
    display(output)
    _render()
