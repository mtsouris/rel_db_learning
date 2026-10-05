"""Algebra expression self-assessment for REL_DB_LEARNING module 03.

``algebra_check`` is called directly in a notebook cell — it runs once on
execution and displays immediate feedback. It never shows SQL; on failure it
reveals the correct algebra expression and its result.

Used in modules 03_1 and 03_2 (Type B exercises where the student writes
algebra). Not used in other modules.
"""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd
from IPython.display import display
import ipywidgets as widgets

from rel_db_learning.db.connection import get_chinook_connection
from rel_db_learning.db.sql_runner import run_sql
from rel_db_learning.parsers.algebra_to_sql import AlgebraParseError, algebra_to_sql

from ._helpers import _rows_match  # noqa: F401  (re-exported; tests import from here)


def _run_algebra(expression: str) -> pd.DataFrame:
    sql = algebra_to_sql(expression)
    conn = get_chinook_connection()
    return run_sql(sql, conn)


def algebra_check(
    student_expression: str,
    correct_expression: str,
    expected_rows: List[Tuple],
) -> None:
    """Verify a student's algebra expression produces the expected result.

    Parameters
    ----------
    student_expression : str
        The algebra expression the student wrote.
    correct_expression : str
        The reference algebra expression (shown on failure — SQL is never
        shown).
    expected_rows : list of tuple
        Expected result rows for order-insensitive comparison.
    """
    # ── Execute student expression ───────────────────────────────────────────
    try:
        student_df = _run_algebra(student_expression)
    except AlgebraParseError as exc:
        display(widgets.HTML(
            value=(
                "<div style='color:#c62828; font-weight:bold;'>"
                f"✗ {exc}"
                "</div>"
            )
        ))
        return

    # ── Compare result ───────────────────────────────────────────────────────
    if _rows_match(student_df, expected_rows):
        display(widgets.HTML(
            value=(
                "<div style='color:#2e7d32; font-weight:bold;'>"
                "✓ Correct"
                "</div>"
            )
        ))
        return

    # ── Wrong answer — reveal correct algebra and its result ─────────────────
    try:
        correct_df = _run_algebra(correct_expression)
    except AlgebraParseError:
        correct_df = pd.DataFrame()

    error_html = widgets.HTML(
        value=(
            "<div style='color:#c62828; font-weight:bold; margin-bottom:6px;'>"
            "✗ Not correct. The correct expression is:</div>"
            "<div style='font-family:monospace; background:#f5f5f5; "
            "border:1px solid #ddd; padding:6px 10px; margin-bottom:8px; "
            "border-radius:4px;'>"
            f"{correct_expression}"
            "</div>"
        )
    )
    display(error_html)
    if not correct_df.empty:
        display(correct_df)
