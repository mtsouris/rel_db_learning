"""Functional-dependency self-assessment widget for REL_DB_LEARNING module 05.

``fd_check`` is called directly in a notebook cell: it runs once on execution
and displays immediate feedback. It checks a student's attribute-closure or
candidate-keys answer against the correct result computed by the
:class:`~rel_db_learning.normalization.relation.Relation` wrapper.

Like the other self-assessment widgets it is argument-based (not interactive):
it always shows the student's own normalized answer, then a verdict, and
reveals the correct answer on failure. Colors match ``sql_query_check``:
green ``#2e7d32`` for success, red ``#c62828`` for failure.

Used in module 05. Not used in modules 01-04.
"""

from __future__ import annotations

import html as _html
from typing import Iterable, List, Set

from IPython.display import display
import ipywidgets as widgets

from rel_db_learning.normalization import Relation

_GREEN = "#2e7d32"
_RED = "#c62828"
_VALID_KINDS = ("closure", "candidate_keys")


def _red(message: str) -> None:
    """Display a red, bold message (used for both failures and bad input)."""
    display(widgets.HTML(
        value=(
            f"<div style='color:{_RED}; font-weight:bold;'>"
            f"{message}"
            "</div>"
        )
    ))


def _order_key(relation: Relation, name: str) -> int:
    """Sort key placing attributes in the relation's declared order."""
    try:
        return relation.attributes.index(name)
    except ValueError:
        return len(relation.attributes)


def _format_set(relation: Relation, names: Iterable[str]) -> str:
    """Render a set of attribute names as ``{a, b, c}`` in declared order."""
    ordered = sorted(set(names), key=lambda n: (_order_key(relation, n), n))
    inner = ", ".join(_html.escape(n) for n in ordered)
    return "{" + inner + "}"


def _format_keys(relation: Relation, keys: Iterable[frozenset]) -> str:
    """Render a collection of candidate keys as ``{a}, {b, c}``.

    Keys are ordered by size and then by their attributes' declared order so
    the display is deterministic.
    """
    keys = list(keys)
    if not keys:
        return "(none)"
    ordered_keys = sorted(
        keys,
        key=lambda k: (
            len(k),
            tuple(sorted(_order_key(relation, n) for n in k)),
        ),
    )
    return ", ".join(_format_set(relation, k) for k in ordered_keys)


def _normalize_names(answer: Iterable[str]) -> List[str]:
    """Normalize an iterable of names to a list, tolerating a bare string."""
    if isinstance(answer, str):
        return [answer]
    return list(answer)


def _unknown_names(relation: Relation, names: Iterable[str]) -> List[str]:
    """Return, in first-seen order, the names that are not in the relation."""
    valid = set(relation.attributes)
    unknown: List[str] = []
    for name in names:
        if name not in valid and name not in unknown:
            unknown.append(name)
    return unknown


def _report_unknown(relation: Relation, unknown: List[str]) -> None:
    """Display a clear red message naming the unknown attribute(s)."""
    if len(unknown) == 1:
        label = f"Unknown attribute {unknown[0]!r}."
    else:
        names = ", ".join(repr(n) for n in unknown)
        label = f"Unknown attributes: {names}."
    known = ", ".join(relation.attributes)
    # Text content (not an attribute value), so apostrophes need not be escaped.
    _red(
        f"✗ {_html.escape(label, quote=False)} "
        f"Known attributes are: {_html.escape(known, quote=False)}."
    )


def fd_check(
    relation: Relation,
    kind: str,
    student_answer: Iterable,
    given: Iterable[str] | None = None,
) -> None:
    """Check a student's functional-dependency answer.

    Parameters
    ----------
    relation : Relation
        The relation whose closures and candidate keys define the correct
        answers.
    kind : str
        Either ``"closure"`` or ``"candidate_keys"``.
    student_answer : iterable
        For ``"closure"``: an iterable of attribute names (the claimed
        closure). For ``"candidate_keys"``: an iterable of iterables of
        attribute names (the claimed candidate keys, for example
        ``[{"book_id"}]`` or ``[["a", "b"], ["a", "c"]]``).
    given : iterable of str, optional
        For ``"closure"`` only: the attribute set whose closure is asked.
        Required when ``kind == "closure"``.

    Raises
    ------
    ValueError
        If ``kind`` is not one of ``"closure"`` / ``"candidate_keys"``, or if
        ``kind == "closure"`` and ``given`` is not provided.

    Notes
    -----
    Unknown attribute names supplied by the student (or in ``given``) are
    reported as a red message rather than raising, so a typo does not crash
    the notebook cell.
    """
    if kind not in _VALID_KINDS:
        raise ValueError(
            f"kind must be one of {_VALID_KINDS}, got {kind!r}."
        )
    if kind == "closure" and given is None:
        raise ValueError(
            "given is required when kind == 'closure': pass the attribute set "
            "whose closure is asked."
        )

    if kind == "closure":
        _check_closure(relation, student_answer, given)
    else:
        _check_candidate_keys(relation, student_answer)


def _check_closure(
    relation: Relation,
    student_answer: Iterable[str],
    given: Iterable[str],
) -> None:
    given_names = _normalize_names(given)
    student_names = _normalize_names(student_answer)

    # Validate names before computing anything, so a typo is handled cleanly.
    unknown = _unknown_names(relation, list(given_names) + list(student_names))
    if unknown:
        _report_unknown(relation, unknown)
        return

    student_set: Set[str] = set(student_names)
    correct_set: Set[str] = relation.closure(given_names)

    # Always restate what was asked and show the student's own answer.
    display(widgets.HTML(
        value=(
            "<div style='margin-bottom:4px;'>Closure of "
            f"<b>{_format_set(relation, given_names)}</b></div>"
            "<div style='font-weight:bold; margin-bottom:4px;'>Your answer:</div>"
            f"<div style='font-family:monospace; margin-bottom:6px;'>"
            f"{_format_set(relation, student_set)}</div>"
        )
    ))

    if student_set == correct_set:
        display(widgets.HTML(
            value=(
                f"<div style='color:{_GREEN}; font-weight:bold;'>"
                "✓ Correct</div>"
            )
        ))
        return

    display(widgets.HTML(
        value=(
            f"<div style='color:{_RED}; font-weight:bold; margin-bottom:6px;'>"
            "✗ Not correct.</div>"
            "<div style='font-weight:bold; margin-bottom:4px;'>"
            "Correct closure:</div>"
            f"<div style='font-family:monospace;'>"
            f"{_format_set(relation, correct_set)}</div>"
        )
    ))


def _check_candidate_keys(
    relation: Relation,
    student_answer: Iterable[Iterable[str]],
) -> None:
    # Normalize the student's nested answer to a set of frozensets, tolerating
    # a bare string for a single-attribute key.
    student_keys: Set[frozenset] = set()
    all_names: List[str] = []
    for key in student_answer:
        key_names = _normalize_names(key)
        all_names.extend(key_names)
        student_keys.add(frozenset(key_names))

    unknown = _unknown_names(relation, all_names)
    if unknown:
        _report_unknown(relation, unknown)
        return

    correct_keys: Set[frozenset] = {frozenset(k) for k in relation.candidate_keys()}

    # Always show the student's own answer.
    display(widgets.HTML(
        value=(
            "<div style='font-weight:bold; margin-bottom:4px;'>Your answer:</div>"
            f"<div style='font-family:monospace; margin-bottom:6px;'>"
            f"{_format_keys(relation, student_keys)}</div>"
        )
    ))

    if student_keys == correct_keys:
        display(widgets.HTML(
            value=(
                f"<div style='color:{_GREEN}; font-weight:bold;'>"
                "✓ Correct</div>"
            )
        ))
        return

    display(widgets.HTML(
        value=(
            f"<div style='color:{_RED}; font-weight:bold; margin-bottom:6px;'>"
            "✗ Not correct.</div>"
            "<div style='font-weight:bold; margin-bottom:4px;'>"
            "Correct candidate keys:</div>"
            f"<div style='font-family:monospace;'>"
            f"{_format_keys(relation, correct_keys)}</div>"
        )
    ))
