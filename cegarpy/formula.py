from typing import TypeAlias, Set

from pydantic import Field
from pydantic.dataclasses import dataclass

from cegarpy.atom import Atom

_Formula: TypeAlias = "Formula"


@dataclass(frozen=True)
class Formula:

    @property
    def is_nnf(self) -> bool:
        return all(isf.is_nnf for isf in self.immediate_subformulae)

    @property
    def immediate_subformulae(self) -> Set[_Formula]:
        return set()

    @property
    def precedence(self) -> float:
        return float('-inf')

    @property
    def connective_symbol(self) -> str:
        return ""


@dataclass(frozen=True)
class NonaryFormula(Formula):

    def precedence(self) -> float:
        return float('inf')


@dataclass(frozen=True, order=True)
class AtomicFormula(NonaryFormula):
    atom: Atom

    def __str__(self) -> str:
        return str(self.atom)


@dataclass(frozen=True)
class Literal(NonaryFormula):
    atom: Atom
    sign: bool = Field(default=True)

    def __str__(self) -> str:
        if self.sign is False:
            return "¬{}".format(self.atom)
        return str(self.atom)


@dataclass(frozen=True)
class Bot(NonaryFormula):

    def __str__(self) -> str:
        return '⊥'


@dataclass(frozen=True)
class Top(Formula):

    def __str__(self) -> str:
        return '⊤'


@dataclass(frozen=True)
class UnaryFormula(Formula):
    formula: Formula

    @property
    def immediate_subformulae(self) -> Set[_Formula]:
        return {self.formula}

    @property
    def precedence(self) -> float:
        return 20

    def __str__(self) -> str:
        if self.precedence > self.formula.precedence:
            return "{}({})".format(self.connective_symbol, self.formula)
        return "{}{}".format(self.connective_symbol, self.formula)


@dataclass(frozen=True)
class Negation(UnaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super(Negation, self).precedence + 3

    @property
    def connective_symbol(self) -> str:
        return '¬'


@dataclass(frozen=True)
class Box(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super(Box, self).precedence + 2

    @property
    def connective_symbol(self) -> str:
        return '□'


@dataclass(frozen=True)
class Dia(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super(Dia, self).precedence + 1

    @property
    def connective_symbol(self) -> str:
        return '⋄'


@dataclass(frozen=True, order=True)
class BinaryFormula(Formula):
    left: Formula
    right: Formula

    @property
    def immediate_subformulae(self) -> Set[_Formula]:
        return {self.left, self.right}

    @property
    def precedence(self) -> float:
        return 10

    def __str__(self) -> str:
        if self.precedence > self.left.precedence:
            left: str = "({})".format(self.left)
        else:
            left = str(self.left)
        if self.precedence > self.right.precedence:
            right: str = "({})".format(self.right)
        else:
            right = str(self.right)

        return "{} {} {}".format(left, self.connective_symbol, right)


@dataclass(frozen=True, order=True)
class Conjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super(Conjunction, self).precedence + 4

    @property
    def connective_symbol(self) -> str:
        return '⋀'


@dataclass(frozen=True, order=True)
class Disjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super(Disjunction, self).precedence + 3

    @property
    def connective_symbol(self) -> str:
        return '⋁'


@dataclass(frozen=True, order=True)
class Implication(BinaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super(Implication, self).precedence + 2

    @property
    def connective_symbol(self) -> str:
        return '→'


@dataclass(frozen=True, order=True)
class Equivalence(BinaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super(Equivalence, self).precedence + 1

    @property
    def connective_symbol(self) -> str:
        return '≡'
