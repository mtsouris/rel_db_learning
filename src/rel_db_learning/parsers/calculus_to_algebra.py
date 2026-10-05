"""Translate tuple relational calculus into relational algebra.

The pipeline used by module 03_2 notebooks is::

    student calculus expression
       → calculus_to_algebra (THIS module)   ─┐
       → algebra_to_sql                       ├─ ultimately reaches run_sql
       → execute on chinook                  ─┘

Supported expression shapes — single relation, no tuple-variable joins:

* ``{ t | t ∈ R }``                              — all rows of R
* ``{ t | t ∈ R ∧ cond }``                       — σ(cond)(R)
* ``{ t.c1, t.c2 | t ∈ R }``                     — π(c1, c2)(R)
* ``{ t.c1 | t ∈ R ∧ cond }``                    — π(c1)(σ(cond)(R))

Inside the predicate:

* Comparisons: ``=``, ``!=``, ``<``, ``>``, ``<=``, ``>=``, ``LIKE``
* Logical: ``∧`` (AND), ``∨`` (OR), ``¬`` (NOT)
* Column references **must** be prefixed with the tuple variable, e.g.
  ``t.artist_id``. The prefix is stripped during translation because
  algebra has no notion of tuple variables.

The existential quantifier ``∃`` is recognised by the tokenizer so that
"unknown symbol" errors don't fire on valid notation. Translating it
fully would require multi-relation tuple-variable joins which are out
of scope for the course — any actual ``∃`` use raises a clear English
error explaining the limitation.

All error messages are in English.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


# ── Errors ───────────────────────────────────────────────────────────────────


class CalculusParseError(Exception):
    """Raised when a tuple relational calculus expression cannot be parsed."""


# ── Tokens ───────────────────────────────────────────────────────────────────


class TokenType(Enum):
    LBRACE = auto()
    RBRACE = auto()
    PIPE = auto()
    DOT = auto()
    COMMA = auto()
    IN = auto()        # ∈
    AND = auto()       # ∧
    OR = auto()        # ∨
    NOT = auto()       # ¬
    EXISTS = auto()    # ∃
    LPAREN = auto()
    RPAREN = auto()
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
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "|": TokenType.PIPE,
    ".": TokenType.DOT,
    ",": TokenType.COMMA,
    "∈": TokenType.IN,
    "∧": TokenType.AND,
    "∨": TokenType.OR,
    "¬": TokenType.NOT,
    "∃": TokenType.EXISTS,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
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
            raise CalculusParseError("Unknown symbol: '!'")

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
                raise CalculusParseError(
                    "Syntax error in calculus expression: "
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

        raise CalculusParseError(f"Unknown symbol: '{c}'")

    return tokens


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

    def _expect(self, ttype: TokenType, error_msg: str) -> Token:
        tok = self._peek()
        if tok is None or tok.type != ttype:
            raise CalculusParseError(error_msg)
        return self._advance()

    # ─ Entry ─

    def parse(self) -> str:
        # { output_spec | t ∈ R [∧ cond] }
        self._expect(
            TokenType.LBRACE,
            "Expression must start with '{'.",
        )

        output_var, projection_cols = self._parse_output_spec()

        self._expect(
            TokenType.PIPE,
            "Missing '|' symbol (such that).",
        )

        membership_var, relation = self._parse_membership()

        if output_var != membership_var:
            raise CalculusParseError(
                f"Variable '{output_var}' does not match the membership "
                f"variable '{membership_var}'."
            )

        condition_str: Optional[str] = None
        if self._peek_type() == TokenType.AND:
            self._advance()
            condition_str = self._parse_condition(membership_var)

        self._expect(
            TokenType.RBRACE,
            "Expression must end with '}'.",
        )

        if self._peek() is not None:
            extra = self._peek()
            raise CalculusParseError(
                "Syntax error in calculus expression: "
                f"unexpected content after expression near '{extra.value}'."
            )

        return _build_algebra(relation, projection_cols, condition_str)

    # ─ Output spec: t  |  t.c1, t.c2, ... ─

    def _parse_output_spec(self) -> tuple[str, Optional[List[str]]]:
        tok = self._peek()
        if tok is None or tok.type != TokenType.IDENT:
            raise CalculusParseError(
                "Syntax error in calculus expression: expected a tuple "
                "variable (e.g. t) after '{'."
            )
        self._advance()
        tuple_var = tok.value

        # Bare tuple variable → no projection.
        if self._peek_type() != TokenType.DOT:
            return tuple_var, None

        # t.col [, t.col]*
        cols: List[str] = []
        cols.append(self._consume_column_after_dot(tuple_var))
        while self._peek_type() == TokenType.COMMA:
            self._advance()
            var_tok = self._peek()
            if var_tok is None or var_tok.type != TokenType.IDENT:
                raise CalculusParseError(
                    "Syntax error in calculus expression: expected a tuple "
                    "variable after ','."
                )
            self._advance()
            if var_tok.value != tuple_var:
                raise CalculusParseError(
                    f"Variable '{var_tok.value}' does not match variable "
                    f"'{tuple_var}'."
                )
            self._expect(
                TokenType.DOT,
                "Syntax error in calculus expression: expected '.' after "
                "the tuple variable.",
            )
            cols.append(self._consume_column_name())

        return tuple_var, cols

    def _consume_column_after_dot(self, tuple_var: str) -> str:
        # caller has consumed the tuple variable, we now consume DOT then IDENT.
        self._expect(
            TokenType.DOT,
            "Syntax error in calculus expression: expected '.' after "
            "the tuple variable.",
        )
        return self._consume_column_name()

    def _consume_column_name(self) -> str:
        col_tok = self._peek()
        if col_tok is None or col_tok.type != TokenType.IDENT:
            raise CalculusParseError(
                "Syntax error in calculus expression: expected a column "
                "name after '.'."
            )
        self._advance()
        return col_tok.value

    # ─ Membership: t ∈ R ─

    def _parse_membership(self) -> tuple[str, str]:
        tok = self._peek()
        if tok is None or tok.type != TokenType.IDENT:
            raise CalculusParseError(
                "Missing membership declaration (e.g. t ∈ artist)."
            )
        self._advance()
        tuple_var = tok.value

        if self._peek_type() != TokenType.IN:
            raise CalculusParseError(
                "Missing membership declaration (e.g. t ∈ artist)."
            )
        self._advance()

        rel_tok = self._peek()
        if rel_tok is None or rel_tok.type != TokenType.IDENT:
            raise CalculusParseError(
                "Missing membership declaration (e.g. t ∈ artist)."
            )
        self._advance()
        return tuple_var, rel_tok.value

    # ─ Condition grammar (NOT > AND > OR; emitted using calculus symbols) ─

    def _parse_condition(self, tuple_var: str) -> str:
        return self._parse_cond_or(tuple_var)

    def _parse_cond_or(self, tuple_var: str) -> str:
        left = self._parse_cond_and(tuple_var)
        while self._peek_type() == TokenType.OR:
            self._advance()
            right = self._parse_cond_and(tuple_var)
            left = f"{left} ∨ {right}"
        return left

    def _parse_cond_and(self, tuple_var: str) -> str:
        left = self._parse_cond_not(tuple_var)
        while self._peek_type() == TokenType.AND:
            self._advance()
            right = self._parse_cond_not(tuple_var)
            left = f"{left} ∧ {right}"
        return left

    def _parse_cond_not(self, tuple_var: str) -> str:
        if self._peek_type() == TokenType.NOT:
            self._advance()
            inner = self._parse_cond_not(tuple_var)
            return f"¬{inner}"
        return self._parse_cond_atom(tuple_var)

    def _parse_cond_atom(self, tuple_var: str) -> str:
        if self._peek_type() == TokenType.EXISTS:
            raise CalculusParseError(
                "The existential quantifier ∃ is recognized, but this "
                "expression form is too complex for this library — "
                "exercises do not use it."
            )
        if self._peek_type() == TokenType.LPAREN:
            self._advance()
            inner = self._parse_cond_or(tuple_var)
            self._expect(
                TokenType.RPAREN,
                "Missing parenthesis in condition expression.",
            )
            return f"({inner})"
        return self._parse_predicate(tuple_var)

    def _parse_predicate(self, tuple_var: str) -> str:
        left = self._parse_operand(tuple_var)
        nxt = self._peek()
        if nxt is None:
            raise CalculusParseError(
                "Syntax error in calculus expression: the condition has no "
                "comparison operator."
            )
        if nxt.type == TokenType.IDENT and nxt.value.upper() == "LIKE":
            self._advance()
            right = self._parse_operand(tuple_var)
            return f"{left} LIKE {right}"
        if nxt.type != TokenType.COMP_OP:
            raise CalculusParseError(
                "Syntax error in calculus expression: expected a comparison "
                f"operator, found '{nxt.value}'."
            )
        op = self._advance().value
        right = self._parse_operand(tuple_var)
        return f"{left} {op} {right}"

    def _parse_operand(self, tuple_var: str) -> str:
        tok = self._peek()
        if tok is None:
            raise CalculusParseError(
                "Syntax error in calculus expression: expected a value or column."
            )
        if tok.type == TokenType.IDENT:
            self._advance()
            # In tuple calculus, column refs must be ``var.column``.
            if self._peek_type() != TokenType.DOT:
                raise CalculusParseError(
                    "Column references must have a tuple variable prefix "
                    f"(e.g. '{tuple_var}.{tok.value}'), found "
                    f"'{tok.value}' without a prefix."
                )
            if tok.value != tuple_var:
                raise CalculusParseError(
                    f"Variable '{tok.value}' does not match variable "
                    f"'{tuple_var}'."
                )
            self._advance()  # consume DOT
            return self._consume_column_name()
        if tok.type == TokenType.NUMBER:
            self._advance()
            return tok.value
        if tok.type == TokenType.STRING:
            self._advance()
            escaped = tok.value.replace("'", "''")
            return f"'{escaped}'"
        raise CalculusParseError(
            "Syntax error in calculus expression: expected a value or column, "
            f"found '{tok.value}'."
        )


def _build_algebra(
    relation: str,
    projection_cols: Optional[List[str]],
    condition_str: Optional[str],
) -> str:
    if condition_str is not None:
        base = f"σ({condition_str})({relation})"
    else:
        base = relation
    if projection_cols:
        cols_joined = ", ".join(projection_cols)
        return f"π({cols_joined})({base})"
    return base


# ── Public entry point ───────────────────────────────────────────────────────


def calculus_to_algebra(expression: str) -> str:
    """Translate a tuple relational calculus expression into algebra.

    Parameters
    ----------
    expression : str
        A tuple calculus expression in Unicode notation, e.g.
        ``"{ t.name | t ∈ artist ∧ t.artist_id < 10 }"``.

    Returns
    -------
    str
        Equivalent relational algebra expression (Unicode notation),
        suitable as input to
        :func:`rel_db_learning.parsers.algebra_to_sql.algebra_to_sql`.

    Raises
    ------
    CalculusParseError
        With an English message on invalid input (empty string, missing
        ``{``/``}``/``|``/``∈``, tuple-variable mismatch, malformed
        condition, ``∃`` usage, etc.).
    """
    if expression is None or expression.strip() == "":
        raise CalculusParseError("Expression is empty.")

    tokens = _tokenize(expression)
    if not tokens:
        raise CalculusParseError("Expression is empty.")

    return _Parser(tokens).parse()
