"""SQL query self-assessment widget for REL_DB_LEARNING modules 04 and 05.

``sql_query_check`` is called directly in a notebook cell — it runs once on
execution and displays immediate feedback. On failure it reveals the correct
SQL query and the expected result, which is pedagogically appropriate for a
module that teaches SQL.

To keep the correct answer out of the notebook the student is working in, the
correct SQL and expected rows live in :mod:`exercise_answers`. A notebook cell
passes only an exercise key (e.g. ``"m04_nb_05_exercise_3"``) as ``correct_sql``
and the widget resolves the answer from ``EXERCISE_ANSWERS``. Passing literal
SQL together with ``expected_rows`` is still supported for backward
compatibility.

Used only in modules 04 and 05. Not used in modules 01-03.
"""

from __future__ import annotations

import html as _html
import re
from typing import List, Optional, Tuple

import pandas as pd
import psycopg2.errors
import sqlalchemy.exc
import ipywidgets as widgets
from IPython.display import display
from sqlalchemy import text

from ._helpers import _rows_match
from .exercise_answers import EXERCISE_ANSWERS

# A bare identifier (no whitespace) that could be an exercise key.
_KEY_PATTERN = re.compile(r"^\w+$")


def _sql_error_message(exc: sqlalchemy.exc.SQLAlchemyError) -> str:
    """Translate a SQLAlchemy database error to a short English message."""
    if isinstance(exc, sqlalchemy.exc.ResourceClosedError):
        return (
            "Your query did not return a result set. "
            "Make sure you are writing a SELECT statement."
        )
    original = getattr(exc, "orig", None)
    if original is None:
        return str(exc)
    if isinstance(original, psycopg2.errors.UndefinedColumn):
        try:
            col = original.diag.column_name
        except Exception:
            col = None
        return (
            f"Column '{col}' does not exist in the table."
            if col
            else "A column does not exist in the table."
        )
    if isinstance(original, psycopg2.errors.UndefinedTable):
        try:
            tbl = original.diag.table_name
        except Exception:
            tbl = None
        return (
            f"Table '{tbl}' does not exist in the database."
            if tbl
            else "A table does not exist in the database."
        )
    if isinstance(original, psycopg2.errors.SyntaxError):
        return "Syntax error in your SQL query."
    return str(original)


def _resolve_answer(
    correct_sql: str,
    expected_rows: Optional[List[Tuple]],
) -> Tuple[str, List[Tuple]]:
    """Resolve ``correct_sql``/``expected_rows`` from an exercise key or literals.

    If ``correct_sql`` is a key present in :data:`EXERCISE_ANSWERS`, the correct
    SQL and expected rows are taken from the answer key and any passed
    ``expected_rows`` is ignored. If ``correct_sql`` is literal SQL,
    ``expected_rows`` is required. A bare identifier that is not a known key is
    treated as a missing-key error.

    Parameters
    ----------
    correct_sql : str
        Either an exercise key or literal correct SQL.
    expected_rows : list of tuple or None
        Expected rows when ``correct_sql`` is literal SQL.

    Returns
    -------
    tuple of (str, list of tuple)
        The resolved correct SQL and expected rows.

    Raises
    ------
    ValueError
        If ``correct_sql`` looks like a key but is not registered, or if literal
        SQL is given without ``expected_rows``.
    """
    if correct_sql in EXERCISE_ANSWERS:
        answer = EXERCISE_ANSWERS[correct_sql]
        return answer["correct_sql"], list(answer["expected_rows"])

    if _KEY_PATTERN.match(correct_sql):
        raise ValueError(
            f"Exercise key '{correct_sql}' is not present in EXERCISE_ANSWERS. "
            "Add it to exercise_answers.py or pass literal SQL with expected_rows."
        )

    if expected_rows is None:
        raise ValueError(
            "expected_rows is required when correct_sql is literal SQL "
            "(it is only optional when correct_sql is a registered exercise key)."
        )
    return correct_sql, list(expected_rows)


def sql_query_check(
    student_sql: str,
    correct_sql: str,
    expected_rows: Optional[List[Tuple]] = None,
    connection=None,
) -> None:
    """Check a student's SQL query against expected result rows.

    Runs ``student_sql`` on the given connection, compares the resulting
    rows to the expected rows (order-insensitive, string-coerced). On
    success shows a green confirmation. On failure shows a red message,
    the correct SQL in a monospace box, and the expected result.

    The correct SQL and expected rows are normally resolved from
    :data:`EXERCISE_ANSWERS` by passing an exercise key as ``correct_sql`` (so
    the answer is not visible in the notebook). Passing literal SQL together
    with ``expected_rows`` is also supported.

    Parameters
    ----------
    student_sql : str
        The SQL query the student wrote.
    correct_sql : str
        An exercise key registered in :data:`EXERCISE_ANSWERS`, or literal
        correct SQL (shown on failure — modules 04 and 05 teach SQL, so
        revealing it is intended).
    expected_rows : list of tuple, optional
        Expected result rows for order-insensitive comparison. Required when
        ``correct_sql`` is literal SQL; ignored when ``correct_sql`` is a key.
    connection :
        SQLAlchemy engine to run the query on.
    """
    correct_sql, expected_rows = _resolve_answer(correct_sql, expected_rows)

    # ── Execute student query ────────────────────────────────────────────────
    try:
        student_df = pd.read_sql(text(student_sql), connection)
    except sqlalchemy.exc.SQLAlchemyError as exc:
        msg = _sql_error_message(exc)
        display(widgets.HTML(
            value=(
                "<div style='color:#c62828; font-weight:bold;'>"
                f"✗ {_html.escape(msg)}"
                "</div>"
            )
        ))
        return

    # ── Always show the student's result ────────────────────────────────────
    display(widgets.HTML(
        value="<div style='font-weight:bold; margin-bottom:4px;'>Your result:</div>"
    ))
    display(student_df)

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

    # ── Wrong answer — reveal correct SQL and expected result ─────────────────
    try:
        correct_df = pd.read_sql(text(correct_sql), connection)
    except sqlalchemy.exc.SQLAlchemyError:
        correct_df = pd.DataFrame(expected_rows)

    display(widgets.HTML(
        value=(
            "<div style='color:#c62828; font-weight:bold; margin-bottom:6px;'>"
            "✗ Not correct.</div>"
            "<div style='font-weight:bold; margin-bottom:4px;'>Correct SQL:</div>"
            "<div style='font-family:monospace; background:#f5f5f5; "
            "border:1px solid #ddd; padding:6px 10px; margin-bottom:8px; "
            "border-radius:4px; white-space:pre;'>"
            f"{_html.escape(correct_sql)}"
            "</div>"
        )
    ))
    if not correct_df.empty:
        display(widgets.HTML(
            value="<div style='font-weight:bold; margin-bottom:4px;'>Expected result:</div>"
        ))
        display(correct_df)
