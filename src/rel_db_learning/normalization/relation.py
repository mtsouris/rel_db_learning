"""A thin, real-name wrapper around the vendored functional-dependency engine.

The vendored :class:`FunctionalDependencySet` works with single-character
attribute symbols (``A``, ``B``, ``C``, ...). That is convenient for the
underlying algorithms but unreadable for students, who think in terms of real
column names such as ``book_id`` or ``publisher_name``.

:class:`Relation` keeps the symbol bookkeeping fully internal: every public
method accepts and returns real attribute names, while the mapping to and from
single-character symbols happens behind the scenes. The wrapped engine and the
name/symbol maps are kept accessible so that later normalization features
(normal-form tests, decomposition) can be layered on without refactoring.
"""

from __future__ import annotations

from itertools import combinations

from ._vendor import FunctionalDependencySet

# Single-character symbols are allocated from this alphabet, in order. The
# underlying engine identifies each attribute by exactly one character, which
# caps a relation at 26 attributes. Our teaching relations are far smaller, so
# this is a guard rail rather than a real limit.
_SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_MAX_ATTRIBUTES = len(_SYMBOLS)


class Relation:
    """A relation schema with functional dependencies, keyed by real names.

    Attributes are supplied as real names (for example
    ``["publisher_name", "publisher_address"]``). Internally each name is
    assigned a unique single-character symbol in the order the names are given
    (the first attribute becomes ``A``, the second ``B``, and so on), which
    makes the symbol assignment deterministic and reproducible.

    All public methods speak real names. Single-character symbols never appear
    in any public argument or return value.

    Args:
        attributes: The real attribute names of the relation. Must be a
            non-empty list of unique, non-empty strings, with at most 26
            entries.
        name: An optional human-readable name for the relation, used only for
            display.

    Raises:
        ValueError: If ``attributes`` is empty, contains duplicates or
            non-string/empty entries, or has more than 26 elements.

    Example:
        >>> r = Relation(["publisher_name", "publisher_address",
        ...               "publisher_city"], name="publisher")
        >>> r.add_fd("publisher_name", ["publisher_address", "publisher_city"])
        >>> sorted(r.closure("publisher_name"))
        ['publisher_address', 'publisher_city', 'publisher_name']
        >>> r.candidate_keys()
        [frozenset({'publisher_name'})]
    """

    def __init__(self, attributes: list[str], name: str | None = None) -> None:
        if not isinstance(attributes, (list, tuple)):
            raise ValueError(
                "attributes must be a list of attribute names, got "
                f"{type(attributes).__name__}."
            )
        attributes = list(attributes)
        if len(attributes) == 0:
            raise ValueError("A relation must have at least one attribute.")
        for attr in attributes:
            if not isinstance(attr, str) or attr == "":
                raise ValueError(
                    "Every attribute name must be a non-empty string, got "
                    f"{attr!r}."
                )
        if len(set(attributes)) != len(attributes):
            duplicates = sorted(
                {a for a in attributes if attributes.count(a) > 1}
            )
            raise ValueError(
                "Attribute names must be unique. Duplicated: "
                f"{', '.join(duplicates)}."
            )
        if len(attributes) > _MAX_ATTRIBUTES:
            raise ValueError(
                f"A relation may have at most {_MAX_ATTRIBUTES} attributes, "
                f"but {len(attributes)} were given. Our teaching relations are "
                "small; if you really need more, this wrapper is the wrong tool."
            )

        self.name = name
        self._attributes: list[str] = attributes
        # Deterministic, order-based symbol assignment: first name -> "A", etc.
        self._name_to_symbol: dict[str, str] = {
            attr: _SYMBOLS[i] for i, attr in enumerate(attributes)
        }
        self._symbol_to_name: dict[str, str] = {
            symbol: attr for attr, symbol in self._name_to_symbol.items()
        }
        # The wrapped engine, kept accessible for future normalization features.
        self._fdset = FunctionalDependencySet("".join(self._name_to_symbol.values()))
        # Recorded FDs in real names, for rendering and future reuse.
        self._fds: list[tuple[list[str], list[str]]] = []

    # -- internal helpers ----------------------------------------------------

    @staticmethod
    def _as_list(attrs: list[str] | str) -> list[str]:
        """Normalize a single name or a list of names to a list of names."""
        if isinstance(attrs, str):
            return [attrs]
        if isinstance(attrs, (list, tuple)):
            return list(attrs)
        raise ValueError(
            "Expected an attribute name or a list of attribute names, got "
            f"{type(attrs).__name__}."
        )

    def _to_symbols(self, names: list[str] | str) -> str:
        """Translate real names to the engine's symbol string, validating them."""
        names = self._as_list(names)
        if len(names) == 0:
            raise ValueError("At least one attribute name is required.")
        symbols = []
        for real_name in names:
            try:
                symbols.append(self._name_to_symbol[real_name])
            except KeyError:
                raise ValueError(
                    f"Unknown attribute {real_name!r}. Known attributes are: "
                    f"{', '.join(self._attributes)}."
                ) from None
        return "".join(symbols)

    def _to_names(self, symbols: object) -> set[str]:
        """Translate an iterable of engine symbols back to a set of real names."""
        return {self._symbol_to_name[symbol] for symbol in symbols}

    # -- public API ----------------------------------------------------------

    @property
    def attributes(self) -> list[str]:
        """The relation's attribute names, in their original declared order."""
        return list(self._attributes)

    def add_fd(self, lhs: list[str] | str, rhs: list[str] | str) -> None:
        """Add a functional dependency ``lhs -> rhs`` using real attribute names.

        Args:
            lhs: The determinant: a single attribute name or a list of names.
            rhs: The dependent: a single attribute name or a list of names.

        Raises:
            ValueError: If either side is empty or names an attribute that does
                not belong to this relation.
        """
        lhs_names = self._as_list(lhs)
        rhs_names = self._as_list(rhs)
        lhs_symbols = self._to_symbols(lhs_names)
        rhs_symbols = self._to_symbols(rhs_names)
        self._fdset.add_dependency(lhs_symbols, rhs_symbols)
        self._fds.append((lhs_names, rhs_names))

    def closure(self, attrs: list[str] | str) -> set[str]:
        """Return the attribute closure of ``attrs`` as a set of real names.

        The closure is the set of all attributes functionally determined by
        ``attrs`` under the relation's functional dependencies (it always
        includes ``attrs`` itself).

        Args:
            attrs: A single attribute name or a list of names.

        Returns:
            The closure as a set of real attribute names.

        Raises:
            ValueError: If ``attrs`` is empty or names an unknown attribute.
        """
        symbols = self._to_symbols(attrs)
        return self._to_names(self._fdset.get_attr_closure(symbols))

    def candidate_keys(self) -> list[frozenset[str]]:
        """Return the relation's candidate keys as real attribute names.

        Returns:
            A list of candidate keys, each a ``frozenset`` of real attribute
            names. A candidate key is a minimal attribute set whose closure is
            the whole relation.
        """
        return [
            frozenset(self._to_names(key)) for key in self._fdset.find_candidate_keys()
        ]

    def is_2nf(self) -> bool:
        """Return whether the relation is in second normal form (2NF).

        A relation is in 2NF when it is in 1NF and every non-prime attribute
        (one that is not part of any candidate key) is fully functionally
        dependent on every candidate key, that is, there are no partial
        dependencies on part of a key.

        Returns:
            ``True`` if the relation satisfies 2NF, ``False`` otherwise.
        """
        return self._fdset.is2NF()

    def is_3nf(self) -> bool:
        """Return whether the relation is in third normal form (3NF).

        A relation is in 3NF when, for every non-trivial dependency
        ``X -> A``, either ``X`` is a superkey or ``A`` is a prime attribute
        (part of some candidate key). This rules out transitive dependencies
        of non-prime attributes on a key.

        Returns:
            ``True`` if the relation satisfies 3NF, ``False`` otherwise.
        """
        return self._fdset.is3NF()

    def is_bcnf(self) -> bool:
        """Return whether the relation is in Boyce-Codd normal form (BCNF).

        A relation is in BCNF when the left-hand side of every non-trivial
        functional dependency is a superkey. BCNF is strictly stronger than
        3NF.

        Returns:
            ``True`` if the relation satisfies BCNF, ``False`` otherwise.
        """
        return self._fdset.isBCNF()

    def normal_form(self) -> str:
        """Return the highest normal form the relation satisfies.

        The check respects the containment hierarchy
        (BCNF implies 3NF implies 2NF) and stops at the strongest form that
        holds. Because :class:`Relation` models atomic attributes, the result
        is always at least 1NF.

        Returns:
            One of ``"BCNF"``, ``"3NF"``, ``"2NF"``, or ``"1NF"`` (the default
            when 2NF is violated).
        """
        if self.is_bcnf():
            return "BCNF"
        if self.is_3nf():
            return "3NF"
        if self.is_2nf():
            return "2NF"
        return "1NF"

    def decompose(self) -> list["Relation"]:
        """Return the BCNF decomposition of this relation.

        Uses the vendored DBIS decomposition algorithm to split the relation
        into sub-relations that are each in BCNF and whose natural join is
        lossless. The vendored algorithm yields attribute sets only, so the
        functional dependencies of each sub-relation are computed here by
        projecting the original dependencies onto the sub-relation's
        attributes: for every non-empty subset ``X`` of a sub-relation, the
        closure of ``X`` under the original dependencies, intersected with the
        sub-relation's attributes, gives the attributes ``X`` determines there.

        A relation that is already in BCNF decomposes to a single relation with
        the same attributes as this one.

        Returns:
            A list of new :class:`Relation` objects, with real attribute names,
            each carrying the projection of the original functional
            dependencies onto its own attributes. Calling :meth:`is_bcnf` on
            any returned relation reports ``True``.
        """
        # Work on a copy so the live engine's state (its isdecomposed/tables
        # flags) is left untouched; defaults keep the algorithm silent.
        symbol_tables = self._fdset.copy().decompose2()

        parts: list[Relation] = []
        for symbol_set in symbol_tables:
            sub_names = self._to_names(symbol_set)
            # Preserve the relation's original declaration order for the part.
            ordered = [a for a in self._attributes if a in sub_names]
            part = Relation(ordered, name=self.name)
            for lhs, rhs in self._projected_fds(ordered):
                part.add_fd(lhs, rhs)
            parts.append(part)
        return parts

    def _projected_fds(
        self, sub_attributes: list[str]
    ) -> list[tuple[list[str], list[str]]]:
        """Project this relation's dependencies onto a subset of its attributes.

        For each non-empty subset ``X`` of ``sub_attributes``, the closure of
        ``X`` under the original dependencies, intersected with
        ``sub_attributes`` and with ``X`` itself removed, gives the attributes
        that ``X`` determines within the sub-relation. Trivial dependencies
        (empty right-hand sides) are skipped.

        Args:
            sub_attributes: The sub-relation's attribute names, a subset of this
                relation's attributes.

        Returns:
            A list of ``(lhs, rhs)`` pairs of real attribute names describing
            the projected dependencies.
        """
        sub_set = set(sub_attributes)
        projected: list[tuple[list[str], list[str]]] = []
        for size in range(1, len(sub_attributes) + 1):
            for combo in combinations(sub_attributes, size):
                lhs = list(combo)
                determined = (self.closure(lhs) & sub_set) - set(lhs)
                if determined:
                    rhs = [a for a in sub_attributes if a in determined]
                    projected.append((lhs, rhs))
        return projected

    def is_lossless(self, decomposition: list["Relation"]) -> bool:
        """Return whether a decomposition reconstructs this relation losslessly.

        Implements the standard CHASE algorithm. A tableau is built with one row
        per sub-relation: a cell is the column's distinguished symbol when the
        attribute belongs to that sub-relation, and a unique non-distinguished
        symbol otherwise. Each functional dependency ``X -> Y`` is applied
        repeatedly: among rows that agree on all of ``X``, their ``Y`` values are
        equated (a distinguished value wins if present). The decomposition is
        lossless if and only if some row becomes fully distinguished once no
        further change is possible.

        Args:
            decomposition: A list of :class:`Relation` objects whose attribute
                sets are subsets of this relation's attributes.

        Returns:
            ``True`` if joining the sub-relations reconstructs this relation
            without loss, ``False`` otherwise.
        """
        attributes = self._attributes

        def distinguished(attr: str) -> tuple[str, str]:
            return ("d", attr)

        # One tableau row per sub-relation; distinguished where the attribute is
        # present, a row-unique non-distinguished symbol otherwise.
        rows: list[dict[str, tuple]] = []
        for index, sub in enumerate(decomposition):
            present = set(sub.attributes)
            rows.append(
                {
                    attr: distinguished(attr)
                    if attr in present
                    else ("b", index, attr)
                    for attr in attributes
                }
            )

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self._fds:
                groups: dict[tuple, list[dict[str, tuple]]] = {}
                for row in rows:
                    key = tuple(row[a] for a in lhs)
                    groups.setdefault(key, []).append(row)
                for group in groups.values():
                    if len(group) < 2:
                        continue
                    for attr in rhs:
                        symbols = {row[attr] for row in group}
                        if len(symbols) == 1:
                            continue
                        target = distinguished(attr)
                        winner = target if target in symbols else min(symbols)
                        for loser in symbols - {winner}:
                            for row in rows:
                                if row[attr] == loser:
                                    row[attr] = winner
                            changed = True

        return any(
            all(row[attr] == distinguished(attr) for attr in attributes)
            for row in rows
        )

    def render_fds(self) -> str:
        """Render the functional dependencies in readable, real-name form.

        Returns:
            One dependency per line, for example
            ``"publisher_name -> publisher_address, publisher_city"``. Returns
            a placeholder line if no dependencies have been added yet.
        """
        if not self._fds:
            return "(no functional dependencies)"
        lines = []
        for lhs_names, rhs_names in self._fds:
            lines.append(f"{', '.join(lhs_names)} -> {', '.join(rhs_names)}")
        return "\n".join(lines)

    def __str__(self) -> str:
        header = self.name if self.name else "Relation"
        return (
            f"{header}({', '.join(self._attributes)})\n"
            f"{self.render_fds()}"
        )

    def __repr__(self) -> str:
        name_part = f", name={self.name!r}" if self.name else ""
        return f"Relation({self._attributes!r}{name_part})"
