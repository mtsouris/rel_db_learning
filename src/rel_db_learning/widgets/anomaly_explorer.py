"""Interactive anomaly explorer for REL_DB_LEARNING module 05.

``anomaly_explorer`` is a static, in-memory teaching widget. It does not touch
the database, specs, seed data, or schema — it works over a small hardcoded,
deliberately un-normalized book table (publisher address repeated per book),
so students can trigger update, delete, and insert anomalies and see exactly
what goes wrong.

Used in module 05, notebook 01 (anomalies and functional dependencies).
"""

from __future__ import annotations

import html as _html
from typing import Dict, List, Optional, Sequence, Set, Tuple

import ipywidgets as widgets
from IPython.display import display

_RED = "#c62828"

_COLUMNS = ["book_id", "title", "publisher_name", "publisher_address"]

_ORIGINAL_ROWS: List[Dict] = [
    {"book_id": 1, "title": "The Silmarillion", "publisher_name": "Gollancz", "publisher_address": "Orion House, London"},
    {"book_id": 2, "title": "Ringworld", "publisher_name": "Gollancz", "publisher_address": "Orion House, London"},
    {"book_id": 3, "title": "Gateway", "publisher_name": "Gollancz", "publisher_address": "Orion House, London"},
    {"book_id": 4, "title": "Neuromancer", "publisher_name": "Ace", "publisher_address": "1745 Broadway, New York"},
    {"book_id": 5, "title": "Snow Crash", "publisher_name": "Ace", "publisher_address": "1745 Broadway, New York"},
]


def _find_update_inconsistencies(rows: Sequence[Dict]) -> Dict[str, Set[str]]:
    """Find publishers whose rows disagree on ``publisher_address``.

    Parameters
    ----------
    rows : sequence of dict
        Rows of the working table, each with at least ``publisher_name`` and
        ``publisher_address`` keys.

    Returns
    -------
    dict of str to set of str
        Maps ``publisher_name`` to the set of distinct addresses found for
        it, restricted to publishers with more than one distinct address.
    """
    by_publisher: Dict[str, Set[str]] = {}
    for row in rows:
        by_publisher.setdefault(row["publisher_name"], set()).add(row["publisher_address"])
    return {
        publisher: addresses
        for publisher, addresses in by_publisher.items()
        if len(addresses) > 1
    }


def _is_last_row_for_publisher(rows_before: Sequence[Dict], book_id: int) -> bool:
    """Return True if ``book_id`` is the only row for its publisher in ``rows_before``.

    Parameters
    ----------
    rows_before : sequence of dict
        Rows of the table as they were before the row is removed.
    book_id : int
        The ``book_id`` of the row being deleted.

    Returns
    -------
    bool
        True if no other row in ``rows_before`` shares this row's
        ``publisher_name``.

    Raises
    ------
    ValueError
        If ``book_id`` is not present in ``rows_before``.
    """
    target = next((row for row in rows_before if row["book_id"] == book_id), None)
    if target is None:
        raise ValueError(f"book_id {book_id!r} not found in rows.")
    publisher = target["publisher_name"]
    matches = sum(1 for row in rows_before if row["publisher_name"] == publisher)
    return matches == 1


def _apply_update(rows: List[Dict], book_id: int, new_address: str) -> None:
    """Set ``publisher_address`` for the row with ``book_id``, mutating ``rows`` in place.

    Raises
    ------
    ValueError
        If ``book_id`` is not present in ``rows``.
    """
    for row in rows:
        if row["book_id"] == book_id:
            row["publisher_address"] = new_address
            return
    raise ValueError(f"book_id {book_id!r} not found in rows.")


def _apply_delete(rows: List[Dict], book_id: int) -> Dict:
    """Remove the row with ``book_id`` from ``rows`` in place and return it.

    Raises
    ------
    ValueError
        If ``book_id`` is not present in ``rows``.
    """
    for i, row in enumerate(rows):
        if row["book_id"] == book_id:
            return rows.pop(i)
    raise ValueError(f"book_id {book_id!r} not found in rows.")


def _render_table(
    rows: Sequence[Dict],
    columns: Sequence[str] = _COLUMNS,
    highlighted_publishers: Optional[Set[str]] = None,
) -> str:
    """Render the working table as an HTML table, highlighting given publishers' rows."""
    highlighted_publishers = highlighted_publishers or set()
    header = "".join(
        f"<th style='border:1px solid #ddd; background:#eeeeee; padding:4px 8px;'>"
        f"{_html.escape(col)}</th>"
        for col in columns
    )
    body = ""
    for row in rows:
        highlighted = row["publisher_name"] in highlighted_publishers
        style_attr = " style='background:#ffebee;'" if highlighted else ""
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


def _render_explanation(title: str, body_html: str) -> str:
    """Render a red-highlighted anomaly explanation with a bold title."""
    return (
        f"<div style='color:{_RED}; font-weight:bold; margin-top:8px; "
        f"margin-bottom:4px;'>{_html.escape(title)}</div>"
        f"<div style='color:{_RED};'>{body_html}</div>"
    )


def _render_note(body_html: str) -> str:
    """Render a neutral (non-anomaly) note below the table."""
    return f"<div style='margin-top:8px;'>{body_html}</div>"


def anomaly_explorer() -> None:
    """Display an interactive explorer for update, delete, and insert anomalies.

    Shows a small, deliberately un-normalized book table where each row
    repeats its publisher's address. A toggle picks which anomaly to
    demonstrate (Update, Delete, or Insert); the controls below it adapt to
    the selected anomaly. Applying an action mutates a working copy of the
    table (so repeated actions accumulate) and shows the resulting table
    together with an explanation of what, if anything, went wrong. Reset
    restores the original five rows and clears the explanation.

    This widget is static and in-memory: it never touches the database,
    specs, seed data, or schema.
    """
    working_rows: List[Dict] = [dict(row) for row in _ORIGINAL_ROWS]
    current_inputs: Dict[str, widgets.Widget] = {}

    anomaly_type_control = widgets.ToggleButtons(
        options=["Update", "Delete", "Insert"],
        value="Update",
        description="Anomaly:",
    )
    controls_box = widgets.VBox()
    apply_button = widgets.Button(description="Apply")
    reset_button = widgets.Button(description="Reset")
    output = widgets.Output()

    def _book_options() -> List[Tuple[str, int]]:
        return [(f"{row['book_id']}: {row['title']}", row["book_id"]) for row in working_rows]

    def _build_controls() -> None:
        anomaly_type = anomaly_type_control.value
        current_inputs.clear()
        if anomaly_type == "Update":
            book_dropdown = widgets.Dropdown(options=_book_options(), description="Book:")
            address_text = widgets.Text(description="New address:")
            current_inputs["book_dropdown"] = book_dropdown
            current_inputs["address_text"] = address_text
            controls_box.children = [book_dropdown, address_text]
        elif anomaly_type == "Delete":
            book_dropdown = widgets.Dropdown(options=_book_options(), description="Book:")
            current_inputs["book_dropdown"] = book_dropdown
            controls_box.children = [book_dropdown]
        else:  # Insert
            publisher_name_text = widgets.Text(description="Publisher:")
            publisher_address_text = widgets.Text(description="Address:")
            current_inputs["publisher_name_text"] = publisher_name_text
            current_inputs["publisher_address_text"] = publisher_address_text
            controls_box.children = [publisher_name_text, publisher_address_text]

    def _show(html: str) -> None:
        output.clear_output(wait=True)
        with output:
            display(widgets.HTML(value=html))

    def _handle_update() -> None:
        book_dropdown = current_inputs["book_dropdown"]
        if book_dropdown.value is None:
            _show(_render_table(working_rows) + _render_note(
                "No books remain in the table. Press Reset to restore the sample data."
            ))
            return
        book_id = book_dropdown.value
        new_address = current_inputs["address_text"].value
        _apply_update(working_rows, book_id, new_address)

        changed_row = next(row for row in working_rows if row["book_id"] == book_id)
        publisher = changed_row["publisher_name"]
        inconsistencies = _find_update_inconsistencies(working_rows)

        if publisher in inconsistencies:
            addresses = sorted(inconsistencies[publisher])
            addr_list = ", ".join(f"'{_html.escape(a)}'" for a in addresses)
            html = _render_table(working_rows, highlighted_publishers={publisher})
            html += _render_explanation(
                "Update anomaly",
                f"Publisher <b>{_html.escape(publisher)}</b> now has disagreeing "
                f"addresses: {addr_list}. The same fact, this publisher's address, "
                "is stored in many rows, so updating only one row leaves the "
                "database inconsistent.",
            )
        else:
            html = _render_table(working_rows)
            html += _render_note(
                f"No inconsistency yet: every row for "
                f"{_html.escape(publisher)} still agrees on the address. Try "
                "changing a different book for the same publisher to see the "
                "update anomaly."
            )
        _show(html)

    def _handle_delete() -> None:
        book_dropdown = current_inputs["book_dropdown"]
        if book_dropdown.value is None:
            _show(_render_table(working_rows) + _render_note(
                "No books remain in the table. Press Reset to restore the sample data."
            ))
            return
        book_id = book_dropdown.value
        rows_before = [dict(row) for row in working_rows]
        was_last = _is_last_row_for_publisher(rows_before, book_id)
        removed = _apply_delete(working_rows, book_id)

        html = _render_table(working_rows)
        if was_last:
            html += _render_explanation(
                "Delete anomaly",
                f"Deleting the last book for <b>{_html.escape(removed['publisher_name'])}</b> "
                "also erased that publisher's address, which we did not intend to "
                "lose. Deleting one fact (a book) unintentionally removed another "
                "fact (a publisher's address).",
            )
        else:
            html += _render_note(
                "No information was lost this time: other books by "
                f"{_html.escape(removed['publisher_name'])} still remember its "
                "address. Try deleting all books of one publisher to see the "
                "delete anomaly."
            )
        _show(html)
        _build_controls()

    def _handle_insert() -> None:
        publisher_name = current_inputs["publisher_name_text"].value or "(unnamed)"
        publisher_address = current_inputs["publisher_address_text"].value or "(no address)"
        html = _render_table(working_rows)
        html += _render_explanation(
            "Insert anomaly",
            f"We cannot record publisher <b>{_html.escape(publisher_name)}</b> at "
            f"address <b>{_html.escape(publisher_address)}</b> yet: book_id is the "
            "primary key of this table, and every row requires a book. We cannot "
            "store a publisher's address until at least one book by that publisher "
            "exists. Nothing was inserted.",
        )
        _show(html)

    _HANDLERS = {
        "Update": _handle_update,
        "Delete": _handle_delete,
        "Insert": _handle_insert,
    }

    def _on_apply_clicked(_change: widgets.Button) -> None:
        _HANDLERS[anomaly_type_control.value]()

    def _on_reset_clicked(_change: widgets.Button) -> None:
        working_rows.clear()
        working_rows.extend(dict(row) for row in _ORIGINAL_ROWS)
        _build_controls()
        _show(_render_table(working_rows))

    def _on_type_change(change: Dict) -> None:
        if change["name"] == "value":
            _build_controls()

    anomaly_type_control.observe(_on_type_change, names="value")
    apply_button.on_click(_on_apply_clicked)
    reset_button.on_click(_on_reset_clicked)

    _build_controls()

    display(widgets.HTML(
        value="<div style='font-weight:bold; margin-bottom:4px;'>"
        "Sample book table (publisher address repeated per book)</div>"
    ))
    display(anomaly_type_control)
    display(controls_box)
    display(widgets.HBox([apply_button, reset_button]))
    display(output)
    _show(_render_table(working_rows))
