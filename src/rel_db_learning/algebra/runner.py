"""Algebra and calculus runner helpers used by module 03 notebooks.

Module 03 notebooks hide SQL from students. Four helpers are exposed:

* :func:`algebra_run` — executes a *pre-defined* SQL constant. Used for
  teacher examples and for revealing the correct answer on a failed
  exercise in 03_1. The student does not see the SQL.
* :func:`student_algebra` — takes a student's algebra expression,
  translates it to SQL internally via
  :func:`rel_db_learning.parsers.algebra_to_sql.algebra_to_sql`, and
  executes it on chinook. The student writes algebra, sees results, and
  never sees SQL.
* :func:`calculus_run` — executes a *pre-defined* SQL constant. Used for
  teacher examples and for revealing correct answers in 03_2.
* :func:`student_calculus` — takes a student's tuple calculus expression,
  translates it calculus → algebra → SQL via
  :func:`rel_db_learning.parsers.calculus_to_algebra.calculus_to_algebra`
  and :func:`rel_db_learning.parsers.algebra_to_sql.algebra_to_sql`, and
  executes it on chinook. The student writes calculus, sees results, and
  never sees SQL or the intermediate algebra form.

Parse errors raised by either translator surface as a clean English
message (``print``-ed) rather than a Python traceback, keeping the
notebook output friendly for beginners.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from rel_db_learning.db.connection import get_chinook_connection
from rel_db_learning.db.sql_runner import run_sql
from rel_db_learning.parsers.algebra_to_sql import (
    AlgebraParseError,
    algebra_to_sql,
)
from rel_db_learning.parsers.calculus_to_algebra import (
    CalculusParseError,
    calculus_to_algebra,
)


def algebra_run(sql_constant: str) -> pd.DataFrame:
    """Execute a pre-defined SQL constant on the chinook database.

    Used by module 03_1 for teacher examples and for revealing correct
    answers on failed exercises. The SQL string is supplied by the
    library (from ``examples/module_03.py``); students never see it.

    Parameters
    ----------
    sql_constant : str
        SQL query to execute (typically an ``EXAMPLE_XX_YY`` constant).

    Returns
    -------
    pandas.DataFrame
        Query result, rendered nicely by Jupyter.
    """
    conn = get_chinook_connection()
    return run_sql(sql_constant, conn)


def student_algebra(expression: str) -> Optional[pd.DataFrame]:
    """Translate a student's algebra expression and execute it.

    Parameters
    ----------
    expression : str
        A relational algebra expression in Unicode notation.

    Returns
    -------
    pandas.DataFrame or None
        Query result on success. On a parse error, the English error
        message is printed and ``None`` is returned — no traceback
        bubbles up to the student.
    """
    try:
        sql = algebra_to_sql(expression)
    except AlgebraParseError as exc:
        print(str(exc))
        return None

    conn = get_chinook_connection()
    return run_sql(sql, conn)


def calculus_run(sql_constant: str) -> pd.DataFrame:
    """Execute a pre-defined SQL constant on the chinook database.

    Used by module 03_2 for teacher examples and for revealing correct
    answers on failed exercises. Identical to :func:`algebra_run` in
    behaviour — kept as a separate name so notebook code reads naturally
    next to calculus expressions.

    Parameters
    ----------
    sql_constant : str
        SQL query to execute.

    Returns
    -------
    pandas.DataFrame
        Query result.
    """
    conn = get_chinook_connection()
    return run_sql(sql_constant, conn)


def student_calculus(expression: str) -> Optional[pd.DataFrame]:
    """Translate a student's tuple calculus expression and execute it.

    Pipeline: calculus → algebra → SQL → chinook. The student only ever
    sees the input they wrote and the resulting DataFrame.

    Parameters
    ----------
    expression : str
        A tuple relational calculus expression in Unicode notation, e.g.
        ``"{ t.name | t ∈ artist ∧ t.artist_id < 10 }"``.

    Returns
    -------
    pandas.DataFrame or None
        Query result on success. On a parse error in *either* translation
        stage, the English error message is printed and ``None`` is
        returned — no traceback bubbles up to the student.
    """
    try:
        algebra = calculus_to_algebra(expression)
        sql = algebra_to_sql(algebra)
    except (CalculusParseError, AlgebraParseError) as exc:
        print(str(exc))
        return None

    conn = get_chinook_connection()
    return run_sql(sql, conn)
