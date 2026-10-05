"""Vendored subset of the ``dbis-functional-dependencies`` package (v1.0.4).

Only the two modules required for functional-dependency analysis are vendored
here (``BCNF`` and ``fdsbase``). The upstream distribution declares heavy and
broken runtime dependencies (sphinx, build, networkx, graphviz, and a hard
``numpy~=1.26`` pin that fails to build on Python 3.14), none of which the FD
logic actually imports at runtime. Vendoring keeps this educational library
self-contained for ZIP-based installation while honoring the upstream
Apache-2.0 license (see the ``LICENSE`` and ``NOTICE`` files in this directory).

Only stdlib and ``numpy`` (already a core dependency via pandas) are used at
runtime. This is an internal package; nothing here is part of the public API.
Public code should import from :mod:`rel_db_learning.normalization.relation`.
"""

from .BCNF import FunctionalDependencySet

__all__ = ["FunctionalDependencySet"]
