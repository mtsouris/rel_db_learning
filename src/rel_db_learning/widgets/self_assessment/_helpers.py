"""Shared helpers for self-assessment widgets."""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd


def _rows_match(df: pd.DataFrame, expected_rows: List[Tuple]) -> bool:
    """Return True when ``df`` rows match ``expected_rows`` (order-insensitive).

    Values are compared as strings to avoid int/numpy.int64 mismatches.
    """
    if len(df) != len(expected_rows):
        return False
    actual = sorted(tuple(str(v) for v in row) for row in df.itertuples(index=False))
    expected = sorted(tuple(str(v) for v in row) for row in expected_rows)
    return actual == expected
