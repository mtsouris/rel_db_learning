"""Render a :class:`CheckResult` as styled HTML for Jupyter notebooks.

Output is grouped into five sections — Tables, Columns, Primary Keys,
Relationships, Views — and each item gets a colour-coded row with an icon
``✓`` (pass), ``✗`` (fail), or ``ⓘ`` (info). All messages are in English.
Empty sections are omitted, so the Views section only appears once a spec
requires views. The UNIQUE constraint section was removed: 1:1 cardinality
is now declared and checked at the relationship level.

CSS is inlined: no external assets, and the output works in JupyterLab,
classic Jupyter, and nbviewer alike.
"""

from __future__ import annotations

from html import escape
from typing import Iterable

from IPython.display import HTML, display

from .checks import CheckItem, CheckResult
from .specs import ExerciseSpec


# ── Section ordering and English titles ──────────────────────────────────────

_SECTIONS: list[tuple[str, str]] = [
    ("table", "Tables"),
    ("column", "Columns"),
    ("primary_key", "Primary Keys"),
    ("relationship", "Relationships"),
    ("view", "Views"),
]

_ICONS: dict[str, str] = {
    "pass": "✓",
    "fail": "✗",
    "info": "ⓘ",
}

_ROW_COLORS: dict[str, tuple[str, str]] = {
    # (background, border-left)
    "pass": ("#e8f5e9", "#2e7d32"),
    "fail": ("#fdecea", "#c62828"),
    "info": ("#f4f4f4", "#757575"),
}

_TEXT_COLORS: dict[str, str] = {
    "pass": "#1b5e20",
    "fail": "#b71c1c",
    "info": "#424242",
}


def _items_by_category(items: list[CheckItem]) -> dict[str, list[CheckItem]]:
    """Group items by category, preserving original order within each group."""
    grouped: dict[str, list[CheckItem]] = {}
    for item in items:
        grouped.setdefault(item.category, []).append(item)
    return grouped


def _render_item(item: CheckItem) -> str:
    """Return the HTML for one check row."""
    bg, border = _ROW_COLORS[item.status]
    color = _TEXT_COLORS[item.status]
    icon = _ICONS[item.status]
    msg = escape(item.message)
    details_html = ""
    if item.details:
        details_html = (
            f'<div style="margin-top:4px;font-size:0.9em;color:#555;">'
            f"{escape(item.details)}</div>"
        )
    return (
        f'<div style="background:{bg};border-left:4px solid {border};'
        f'padding:8px 12px;margin:4px 0;border-radius:4px;color:{color};'
        f'font-family:system-ui,-apple-system,sans-serif;">'
        f'<span style="font-weight:bold;margin-right:8px;">{icon}</span>'
        f"{msg}{details_html}"
        f"</div>"
    )


def _render_section(title: str, items: Iterable[CheckItem]) -> str:
    rendered = "".join(_render_item(item) for item in items)
    if not rendered:
        return ""
    return (
        f'<div style="margin-top:18px;">'
        f'<h4 style="margin:0 0 8px 0;color:#333;'
        f'font-family:system-ui,-apple-system,sans-serif;">{escape(title)}</h4>'
        f"{rendered}</div>"
    )


def _render_header(result: CheckResult, spec: ExerciseSpec) -> str:
    if result.success:
        bg, border, color = "#e8f5e9", "#2e7d32", "#1b5e20"
        summary = "All checks passed."
    else:
        n_fail = sum(1 for c in result.checks if c.status == "fail")
        bg, border, color = "#fdecea", "#c62828", "#b71c1c"
        summary = f"Found {n_fail} issues that need fixing."

    return (
        f'<div style="background:{bg};border-left:5px solid {border};'
        f'padding:14px 18px;border-radius:6px;color:{color};'
        f'font-family:system-ui,-apple-system,sans-serif;">'
        f'<div style="font-size:1.15em;font-weight:bold;">'
        f"{escape(spec.title)}</div>"
        f'<div style="margin-top:4px;">{escape(spec.description)}</div>'
        f'<div style="margin-top:10px;font-weight:bold;">{escape(summary)}</div>'
        f"</div>"
    )


def _render_closing(success: bool) -> str:
    if success:
        text = "Congratulations! Your stage is complete."
        bg, color = "#e8f5e9", "#1b5e20"
    else:
        text = "Fix the issues above and re-run the cell to verify."
        bg, color = "#fff3e0", "#e65100"
    return (
        f'<div style="margin-top:18px;background:{bg};padding:12px 16px;'
        f'border-radius:6px;color:{color};font-weight:bold;'
        f'font-family:system-ui,-apple-system,sans-serif;">{escape(text)}</div>'
    )


def render_feedback(result: CheckResult, spec: ExerciseSpec) -> None:
    """Display the check result in the notebook as styled HTML.

    Parameters
    ----------
    result : CheckResult
        Output of :func:`rel_db_learning.dbm_validator.checks.check_exercise`.
    spec : ExerciseSpec
        The spec the result was produced against — used for the heading.
    """
    grouped = _items_by_category(result.checks)
    sections_html = "".join(
        _render_section(title, grouped.get(category, []))
        for category, title in _SECTIONS
    )

    html = (
        '<div style="max-width:780px;padding:6px;">'
        f"{_render_header(result, spec)}"
        f"{sections_html}"
        f"{_render_closing(result.success)}"
        "</div>"
    )
    display(HTML(html))


def render_error(message: str) -> None:
    """Display a parsing / setup error in the notebook as styled HTML."""
    html = (
        '<div style="max-width:780px;background:#fdecea;border-left:5px solid '
        "#c62828;padding:14px 18px;border-radius:6px;color:#b71c1c;"
        'font-family:system-ui,-apple-system,sans-serif;">'
        '<div style="font-size:1.1em;font-weight:bold;">Error during '
        "verification</div>"
        f'<div style="margin-top:6px;">{escape(message)}</div>'
        "</div>"
    )
    display(HTML(html))
