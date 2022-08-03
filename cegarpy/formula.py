from typing import TypeAlias, Set, Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from cegarpy.atom import Atom

_Formula: TypeAlias = 'Formula'


@dataclass(frozen=True, eq=True)
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
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Formula):
            raise TypeError(f"Cannot compare Formula to type {type(other).__name__}")
        return self.precedence < other.precedence

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Formula):
            raise TypeError(f"Cannot compare Formula to type {type(other).__name__}")
        return self.precedence > other.precedence


@dataclass(frozen=True, eq=True)
class NonaryFormula(Formula):

    @property
    def precedence(self) -> float:
        return 30


@dataclass(frozen=True, eq=True)
class AtomicFormula(NonaryFormula):
    atom: Atom

    def __str__(self) -> str:
        return str(self.atom)


_Literal: TypeAlias = 'Literal'


@dataclass(frozen=True, eq=True)
class Literal(NonaryFormula):
    atom: Atom
    sign: bool = Field(default=True)

    def __str__(self) -> str:
        if self.sign is False:
            return f"¬{self.atom}"
        return str(self.atom)

    def __neg__(self) -> _Literal:
        return Literal(self.atom, not self.sign)


@dataclass(frozen=True, eq=True)
class Bot(NonaryFormula):

    @property
    def precedence(self) -> float:
        return float('inf')

    def __str__(self) -> str:
        return '⊥'


@dataclass(frozen=True, eq=True)
class Top(Formula):

    @property
    def precedence(self) -> float:
        return float('inf')

    def __str__(self) -> str:
        return '⊤'


@dataclass(frozen=True, eq=True)
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
            return f"{self.connective_symbol}({self.formula})"
        return f"{self.connective_symbol}{self.formula}"


@dataclass(frozen=True, eq=True)
class Negation(UnaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super().precedence

    @property
    def connective_symbol(self) -> str:
        return '¬'


@dataclass(frozen=True, eq=True)
class Box(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence

    @property
    def connective_symbol(self) -> str:
        return '□'


@dataclass(frozen=True, eq=True)
class Dia(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence

    @property
    def connective_symbol(self) -> str:
        return '⋄'


@dataclass(frozen=True, eq=True)
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
            left: str = f"({self.left})"
        else:
            left = str(self.left)
        if self.precedence > self.right.precedence:
            right: str = f"({self.right})"
        else:
            right = str(self.right)

        return f"{left} {self.connective_symbol} {right}"


@dataclass(frozen=True, eq=True)
class Conjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence + 4

    @property
    def connective_symbol(self) -> str:
        return '⋀'


@dataclass(frozen=True, eq=True)
class Disjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence + 3

    @property
    def connective_symbol(self) -> str:
        return '⋁'


@dataclass(frozen=True, eq=True)
class Implication(BinaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super().precedence + 2

    @property
    def connective_symbol(self) -> str:
        return '→'


@dataclass(frozen=True, eq=True)
class Equivalence(BinaryFormula):

    @property
    def is_nnf(self) -> bool:
        return False

    @property
    def precedence(self) -> float:
        return super().precedence + 1

    @property
    def connective_symbol(self) -> str:
        return '≡'
