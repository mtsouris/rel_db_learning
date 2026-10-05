"""Translate a simple relational algebra expression into tuple calculus.

This is the inverse of :func:`calculus_to_algebra` and is used in
notebook 03_2 to *show* students that the two notations describe the
same queries.

It handles only the simple shapes — bare relation, ``σ`` over a single
relation, ``π`` over a single relation, ``π`` over ``σ`` over a single
relation. Joins and set operations are explicitly rejected because
expressing them in tuple calculus requires multiple tuple variables
(out of scope for the course).

Supported translations (with ``t`` as the tuple variable):

* ``R``                       → ``{ t | t ∈ R }``
* ``σ(cond)(R)``              → ``{ t | t ∈ R ∧ <cond with t. prefix> }``
* ``π(cols)(R)``              → ``{ t.col1, t.col2 | t ∈ R }``
* ``π(cols)(σ(cond)(R))``     → ``{ t.col1 | t ∈ R ∧ <cond with t. prefix> }``

Errors raise :class:`CalculusParseError` with an English message.
"""

from __future__ import annotations

from typing import List

from .algebra_to_sql import (
    AlgebraParseError,
    Difference,
    Intersect,
    Join,
    Projection,
    Relation,
    Selection,
    Union,
    _Parser as _AlgebraParser,
    _tokenize as _algebra_tokenize,
)
from .calculus_to_algebra import CalculusParseError


_UNSUPPORTED_MSG = (
    "Conversion to calculus is only supported for simple expressions "
    "(σ and π over a single relation)."
)


def algebra_to_calculus(expression: str) -> str:
    """Translate a simple algebra expression into tuple calculus notation.

    Parameters
    ----------
    expression : str
        A relational algebra expression. Only the four simple shapes
        described in the module docstring are supported.

    Returns
    -------
    str
        Equivalent tuple calculus expression, e.g.
        ``"{ t.name | t ∈ artist ∧ t.artist_id < 10 }"``.

    Raises
    ------
    CalculusParseError
        With an English message when the input cannot be parsed or uses a
        construct that this translator does not support (join, union,
        intersection, difference, nested projections, etc.).
    """
    if expression is None or expression.strip() == "":
        raise CalculusParseError("Expression is empty.")

    try:
        tokens = _algebra_tokenize(expression)
        if not tokens:
            raise CalculusParseError("Expression is empty.")
        ast = _AlgebraParser(tokens).parse()
    except AlgebraParseError as exc:
        raise CalculusParseError(str(exc)) from exc

    return _to_calculus(ast, tuple_var="t")


def _to_calculus(node, tuple_var: str) -> str:
    if isinstance(node, Relation):
        return f"{{ {tuple_var} | {tuple_var} ∈ {node.name} }}"

    if isinstance(node, Selection):
        if not isinstance(node.child, Relation):
            raise CalculusParseError(_UNSUPPORTED_MSG)
        relation = node.child.name
        cond = _prefix_condition(node.condition, tuple_var)
        return f"{{ {tuple_var} | {tuple_var} ∈ {relation} ∧ {cond} }}"

    if isinstance(node, Projection):
        cols_joined = ", ".join(f"{tuple_var}.{c}" for c in node.columns)
        child = node.child

        if isinstance(child, Relation):
            return f"{{ {cols_joined} | {tuple_var} ∈ {child.name} }}"

        if isinstance(child, Selection) and isinstance(child.child, Relation):
            relation = child.child.name
            cond = _prefix_condition(child.condition, tuple_var)
            return (
                f"{{ {cols_joined} | {tuple_var} ∈ {relation} ∧ {cond} }}"
            )

        raise CalculusParseError(_UNSUPPORTED_MSG)

    # Join / Union / Intersect / Difference all land here.
    if isinstance(node, (Join, Union, Intersect, Difference)):
        raise CalculusParseError(_UNSUPPORTED_MSG)

    raise CalculusParseError(_UNSUPPORTED_MSG)


def _prefix_condition(sql_cond: str, tuple_var: str) -> str:
    """Convert a Selection.condition (SQL form) back to calculus notation.

    The algebra parser stores conditions as SQL strings (``AND``/``OR``/
    ``NOT``). This helper:

    * Replaces ``AND`` / ``OR`` / ``NOT`` keywords with ``∧`` / ``∨`` / ``¬``.
    * Prefixes every column-name identifier with ``tuple_var.``.
    * Preserves numbers, string literals, comparison operators, and
      parentheses verbatim.
    """
    parts: List[str] = []
    i = 0
    n = len(sql_cond)

    while i < n:
        c = sql_cond[i]

        if c.isspace():
            i += 1
            continue

        if c == "(" or c == ")":
            parts.append(c)
            i += 1
            continue

        if c == "'":
            j = i + 1
            while j < n:
                if sql_cond[j] == "'":
                    # Handle SQL-escaped '' inside the literal.
                    if j + 1 < n and sql_cond[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            if j >= n:
                # Should not happen — the algebra parser balances literals.
                parts.append(sql_cond[i:])
                break
            parts.append(sql_cond[i : j + 1])
            i = j + 1
            continue

        if c.isdigit():
            j = i
            while j < n and (sql_cond[j].isdigit() or sql_cond[j] == "."):
                j += 1
            parts.append(sql_cond[i:j])
            i = j
            continue

        if c.isalpha() or c == "_":
            j = i
            while j < n and (sql_cond[j].isalnum() or sql_cond[j] == "_"):
                j += 1
            word = sql_cond[i:j]
            upper = word.upper()
            if upper == "AND":
                parts.append("∧")
            elif upper == "OR":
                parts.append("∨")
            elif upper == "NOT":
                parts.append("¬")
            elif upper == "LIKE":
                parts.append("LIKE")
            else:
                parts.append(f"{tuple_var}.{word}")
            i = j
            continue

        if c in "=<>!":
            if i + 1 < n and sql_cond[i + 1] == "=":
                parts.append(c + "=")
                i += 2
            else:
                parts.append(c)
                i += 1
            continue

        # Anything else passes through unchanged so we never silently drop chars.
        parts.append(c)
        i += 1

    return " ".join(parts)
