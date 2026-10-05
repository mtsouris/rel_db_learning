"""Normalization tools for Module 05.

This package provides real-name wrappers around a vendored functional-dependency
engine. The first component is :class:`Relation`, which supports attribute
closure and candidate-key computation using real column names. Normal-form
tests and decomposition will be added here later.
"""

from .relation import Relation

__all__ = ["Relation"]
