"""Translate relational algebra (Unicode notation) into SQL.

The translator is used internally by
:mod:`rel_db_learning.algebra.runner` so that students in module 03 can
write algebra expressions and see results without ever encountering SQL.

Supported operations (six total):

* ``σ(condition)(relation)``      — selection
* ``π(col1, col2, ...)(relation)`` — projection
* ``relation1 ⋈ relation2``        — natural join
* ``relation1 ∪ relation2``        — union
* ``relation1 ∩ relation2``        — intersection
* ``relation1 − relation2``        — difference (U+2212)

Condition operators inside σ():

* Comparisons: ``=``, ``!=``, ``<``, ``>``, ``<=``, ``>=``, ``LIKE``
* Logical: ``∧`` (AND), ``∨`` (OR), ``¬`` (NOT)
* Parentheses for grouping.

The implementation is a textbook recursive-descent parser:

1. A tokenizer turns the input into a flat token stream.
2. The parser builds a small AST of dataclasses.
3. An SQL generator walks the AST emitting PostgreSQL-compatible SQL,
   wrapping subqueries in parentheses with unique aliases as required
   by ``FROM`` clauses.

All error messages are in English so students see actionable feedback.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union as TypingUnion


# ── Errors ───────────────────────────────────────────────────────────────────


class AlgebraParseError(Exception):
    """Raised when a relational algebra expression cannot be parsed."""


# ── Tokens ───────────────────────────────────────────────────────────────────


class TokenType(Enum):
    SIGMA = auto()
    PI = auto()
    JOIN = auto()
    UNION = auto()
    INTERSECT = auto()
    DIFFERENCE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COMP_OP = auto()
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    position: int


_SINGLE_CHAR_TOKENS = {
    "σ": TokenType.SIGMA,
    "π": TokenType.PI,
    "⋈": TokenType.JOIN,
    "∪": TokenType.UNION,
    "∩": TokenType.INTERSECT,
    "−": TokenType.DIFFERENCE,  # U+2212
    "∧": TokenType.AND,
    "∨": TokenType.OR,
    "¬": TokenType.NOT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ",": TokenType.COMMA,
}


def _tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]

        if c.isspace():
            i += 1
            continue

        if c in _SINGLE_CHAR_TOKENS:
            tokens.append(Token(_SINGLE_CHAR_TOKENS[c], c, i))
            i += 1
            continue

        if c == "=":
            tokens.append(Token(TokenType.COMP_OP, "=", i))
            i += 1
            continue

        if c == "!":
            if i + 1 < n and text[i + 1] == "=":
                tokens.append(Token(TokenType.COMP_OP, "!=", i))
                i += 2
                continue
            raise AlgebraParseError(f"Unknown symbol: '!'")

        if c == "<":
            if i + 1 < n and text[i + 1] == "=":
                tokens.append(Token(TokenType.COMP_OP, "<=", i))
                i += 2
            else:
                tokens.append(Token(TokenType.COMP_OP, "<", i))
                i += 1
            continue

        if c == ">":
            if i + 1 < n and text[i + 1] == "=":
                tokens.append(Token(TokenType.COMP_OP, ">=", i))
                i += 2
            else:
                tokens.append(Token(TokenType.COMP_OP, ">", i))
                i += 1
            continue

        if c == "'":
            j = i + 1
            while j < n and text[j] != "'":
                j += 1
            if j >= n:
                raise AlgebraParseError(
                    "Syntax error in expression: "
                    "missing closing quote on string literal."
                )
            tokens.append(Token(TokenType.STRING, text[i + 1 : j], i))
            i = j + 1
            continue

        if c.isdigit() or (c == "." and i + 1 < n and text[i + 1].isdigit()):
            j = i
            seen_dot = c == "."
            while j < n and (text[j].isdigit() or (text[j] == "." and not seen_dot)):
                if text[j] == ".":
                    seen_dot = True
                j += 1
            tokens.append(Token(TokenType.NUMBER, text[i:j], i))
            i = j
            continue

        # ASCII identifiers only — chinook uses lowercase snake_case English.
        if c.isascii() and (c.isalpha() or c == "_"):
            j = i
            while j < n and text[j].isascii() and (text[j].isalnum() or text[j] == "_"):
                j += 1
            tokens.append(Token(TokenType.IDENT, text[i:j], i))
            i = j
            continue

        raise AlgebraParseError(f"Unknown symbol: '{c}'")

    return tokens


# ── AST ──────────────────────────────────────────────────────────────────────


@dataclass
class Relation:
    name: str


@dataclass
class Selection:
    condition: str  # already translated to SQL
    child: "Node"


@dataclass
class Projection:
    columns: List[str]
    child: "Node"


@dataclass
class Join:
    left: "Node"
    right: "Node"


@dataclass
class Union:
    left: "Node"
    right: "Node"


@dataclass
class Intersect:
    left: "Node"
    right: "Node"


@dataclass
class Difference:
    left: "Node"
    right: "Node"


Node = TypingUnion[
    Relation, Selection, Projection, Join, Union, Intersect, Difference
]


# ── Parser ───────────────────────────────────────────────────────────────────


class _Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # ─ Utilities ─

    def _peek(self) -> Optional[Token]:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _peek_type(self) -> Optional[TokenType]:
        tok = self._peek()
        return tok.type if tok else None

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, ttype: TokenType, context: str = "") -> Token:
        tok = self._peek()
        if tok is None:
            raise AlgebraParseError(
                "Expression ends abruptly — check the syntax."
            )
        if tok.type != ttype:
            if ttype == TokenType.RPAREN:
                raise AlgebraParseError("Missing parenthesis in expression.")
            if ttype == TokenType.LPAREN:
                raise AlgebraParseError("Missing parenthesis in expression.")
            detail = context or f"expected '{ttype.name}'"
            raise AlgebraParseError(
                f"Syntax error in expression: {detail}."
            )
        return self._advance()

    # ─ Algebra grammar ─

    def parse(self) -> Node:
        if not self._tokens:
            raise AlgebraParseError("Expression is empty.")
        node = self._parse_set_expr()
        if self._peek() is not None:
            extra = self._peek()
            raise AlgebraParseError(
                "Syntax error in expression: "
                f"unexpected content after expression near '{extra.value}'."
            )
        return node

    def _parse_set_expr(self) -> Node:
        left = self._parse_join_expr()
        while self._peek_type() in (
            TokenType.UNION,
            TokenType.INTERSECT,
            TokenType.DIFFERENCE,
        ):
            op = self._advance()
            right = self._parse_join_expr()
            if op.type == TokenType.UNION:
                left = Union(left, right)
            elif op.type == TokenType.INTERSECT:
                left = Intersect(left, right)
            else:
                left = Difference(left, right)
        return left

    def _parse_join_expr(self) -> Node:
        left = self._parse_atom()
        while self._peek_type() == TokenType.JOIN:
            self._advance()
            right = self._parse_atom()
            left = Join(left, right)
        return left

    def _parse_atom(self) -> Node:
        tok = self._peek()
        if tok is None:
            raise AlgebraParseError(
                "Expression ends abruptly — check the syntax."
            )
        if tok.type == TokenType.SIGMA:
            return self._parse_selection()
        if tok.type == TokenType.PI:
            return self._parse_projection()
        if tok.type == TokenType.LPAREN:
            self._advance()
            inner = self._parse_set_expr()
            self._expect(TokenType.RPAREN)
            return inner
        if tok.type == TokenType.IDENT:
            self._advance()
            return Relation(tok.value)
        raise AlgebraParseError(
            "Syntax error in expression: "
            f"unexpected symbol '{tok.value}'."
        )

    def _parse_selection(self) -> Node:
        self._expect(TokenType.SIGMA)
        self._expect(TokenType.LPAREN)
        condition = self._parse_condition()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.LPAREN)
        child = self._parse_set_expr()
        self._expect(TokenType.RPAREN)
        return Selection(condition, child)

    def _parse_projection(self) -> Node:
        self._expect(TokenType.PI)
        self._expect(TokenType.LPAREN)
        columns = self._parse_column_list()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.LPAREN)
        child = self._parse_set_expr()
        self._expect(TokenType.RPAREN)
        return Projection(columns, child)

    def _parse_column_list(self) -> List[str]:
        cols = [self._parse_column_ref()]
        while self._peek_type() == TokenType.COMMA:
            self._advance()
            cols.append(self._parse_column_ref())
        return cols

    def _parse_column_ref(self) -> str:
        tok = self._peek()
        if tok is None or tok.type != TokenType.IDENT:
            raise AlgebraParseError(
                "Syntax error in expression: expected a column name."
            )
        self._advance()
        return tok.value

    # ─ Condition grammar (translated to SQL on the fly) ─

    def _parse_condition(self) -> str:
        return self._parse_cond_or()

    def _parse_cond_or(self) -> str:
        left = self._parse_cond_and()
        while self._peek_type() == TokenType.OR:
            self._advance()
            right = self._parse_cond_and()
            left = f"{left} OR {right}"
        return left

    def _parse_cond_and(self) -> str:
        left = self._parse_cond_not()
        while self._peek_type() == TokenType.AND:
            self._advance()
            right = self._parse_cond_not()
            left = f"{left} AND {right}"
        return left

    def _parse_cond_not(self) -> str:
        if self._peek_type() == TokenType.NOT:
            self._advance()
            inner = self._parse_cond_not()
            return f"NOT {inner}"
        return self._parse_cond_atom()

    def _parse_cond_atom(self) -> str:
        tok = self._peek()
        if tok is None:
            raise AlgebraParseError(
                "Expression does not end correctly — check the syntax."
            )
        if tok.type == TokenType.LPAREN:
            self._advance()
            inner = self._parse_cond_or()
            self._expect(TokenType.RPAREN)
            return f"({inner})"
        return self._parse_predicate()

    def _parse_predicate(self) -> str:
        left = self._parse_operand()
        nxt = self._peek()
        if nxt is None:
            raise AlgebraParseError(
                "Expression does not end correctly — check the syntax."
            )
        if nxt.type == TokenType.IDENT and nxt.value.upper() == "LIKE":
            self._advance()
            right = self._parse_operand()
            return f"{left} LIKE {right}"
        if nxt.type != TokenType.COMP_OP:
            if nxt.type == TokenType.RPAREN:
                raise AlgebraParseError(
                    "Inside σ(...), expected a condition (e.g. artist_id = 5 or "
                    "name LIKE 'A%'). If you wanted to select columns, "
                    "use π instead of σ."
                )
            raise AlgebraParseError(
                "Syntax error in expression: "
                f"expected a comparison operator, found '{nxt.value}'."
            )
        op = self._advance().value
        right = self._parse_operand()
        return f"{left} {op} {right}"

    def _parse_operand(self) -> str:
        tok = self._peek()
        if tok is None:
            raise AlgebraParseError(
                "Expression does not end correctly — check the syntax."
            )
        if tok.type == TokenType.IDENT:
            self._advance()
            return tok.value
        if tok.type == TokenType.NUMBER:
            self._advance()
            return tok.value
        if tok.type == TokenType.STRING:
            self._advance()
            escaped = tok.value.replace("'", "''")
            return f"'{escaped}'"
        raise AlgebraParseError(
            "Syntax error in expression: "
            f"expected a value or column name, found '{tok.value}'."
        )


# ── SQL generator ────────────────────────────────────────────────────────────


class _SQLGenerator:
    """Walk the AST and emit a PostgreSQL-compatible query string.

    Subqueries that appear in a ``FROM`` clause are wrapped in
    parentheses with a unique alias (``sub1``, ``sub2``, …) because
    PostgreSQL requires aliases for subqueries used as table sources.
    """

    def __init__(self) -> None:
        self._counter = 0

    def to_sql(self, node: Node) -> str:
        if isinstance(node, Relation):
            return f"SELECT * FROM {node.name}"
        if isinstance(node, Selection):
            return (
                f"SELECT * FROM {self._from_clause(node.child)} "
                f"WHERE {node.condition}"
            )
        if isinstance(node, Projection):
            cols = ", ".join(node.columns)
            return f"SELECT {cols} FROM {self._from_clause(node.child)}"
        if isinstance(node, Join):
            return (
                f"SELECT * FROM {self._from_clause(node.left)} "
                f"NATURAL JOIN {self._from_clause(node.right)}"
            )
        if isinstance(node, Union):
            return f"({self.to_sql(node.left)}) UNION ({self.to_sql(node.right)})"
        if isinstance(node, Intersect):
            return (
                f"({self.to_sql(node.left)}) INTERSECT "
                f"({self.to_sql(node.right)})"
            )
        if isinstance(node, Difference):
            return (
                f"({self.to_sql(node.left)}) EXCEPT "
                f"({self.to_sql(node.right)})"
            )
        raise AlgebraParseError(
            "Syntax error in expression: unknown AST node type."
        )

    def _next_alias(self) -> str:
        self._counter += 1
        return f"sub{self._counter}"

    def _from_clause(self, node: Node) -> str:
        if isinstance(node, Relation):
            return node.name
        inner = self.to_sql(node)
        return f"({inner}) AS {self._next_alias()}"


# ── Public entry point ───────────────────────────────────────────────────────


def algebra_to_sql(expression: str) -> str:
    """Translate a relational algebra expression into a SQL query.

    Parameters
    ----------
    expression : str
        A relational algebra expression in Unicode notation.

    Returns
    -------
    str
        A PostgreSQL-compatible SQL query equivalent to ``expression``.

    Raises
    ------
    AlgebraParseError
        With an English message on invalid input (empty string, unknown
        symbol, unbalanced parentheses, malformed condition, etc.).
    """
    if expression is None or expression.strip() == "":
        raise AlgebraParseError("Expression is empty.")

    tokens = _tokenize(expression)
    if not tokens:
        raise AlgebraParseError("Expression is empty.")

    parser = _Parser(tokens)
    ast = parser.parse()
    return _SQLGenerator().to_sql(ast)
