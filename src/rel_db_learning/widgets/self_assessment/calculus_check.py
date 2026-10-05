"""Tuple calculus self-assessment widget for REL_DB_LEARNING module 03.

``calculus_check`` is called directly in a notebook cell — it runs once on
execution and displays immediate feedback. It never shows SQL or the
intermediate algebra form; on failure it reveals the correct calculus
expression and its result.

Used in module 03_2 (exercises where the student writes tuple calculus).
Not used in other modules.
"""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd
from IPython.display import display
import ipywidgets as widgets

from rel_db_learning.db.connection import get_chinook_connection
from rel_db_learning.db.sql_runner import run_sql
from rel_db_learning.parsers.algebra_to_sql import AlgebraParseError, algebra_to_sql
from rel_db_learning.parsers.calculus_to_algebra import (
    CalculusParseError,
    calculus_to_algebra,
)

from ._helpers import _rows_match


def _run_calculus(expression: str) -> pd.DataFrame:
    algebra = calculus_to_algebra(expression)
    sql = algebra_to_sql(algebra)
    conn = get_chinook_connection()
    return run_sql(sql, conn)


def calculus_check(
    student_expression: str,
    correct_expression: str,
    expected_rows: List[Tuple],
) -> None:
    """Verify a student's tuple calculus expression produces the expected result.

    Parameters
    ----------
    student_expression : str
        The tuple calculus expression the student wrote.
    correct_expression : str
        The reference calculus expression (shown on failure — SQL and the
        intermediate algebra form are never shown).
    expected_rows : list of tuple
        Expected result rows for order-insensitive comparison.
    """
    # ── Execute student expression ───────────────────────────────────────────
    try:
        student_df = _run_calculus(student_expression)
    except (CalculusParseError, AlgebraParseError) as exc:
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

    # ── Wrong answer — reveal correct calculus expression and its result ──────
    try:
        correct_df = _run_calculus(correct_expression)
    except (CalculusParseError, AlgebraParseError):
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
