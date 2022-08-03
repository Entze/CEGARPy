from typing import TypeAlias, Set, Any, FrozenSet, Sequence, Optional, Mapping, MutableMapping, Iterator, Iterable

import more_itertools
from frozendict import frozendict  # type: ignore
from pydantic import Field
from pydantic.dataclasses import dataclass

from cegarpy.atom import Atom

_Valuation: TypeAlias = 'Valuation'


class Valuation:

    @property
    def alphabet(self) -> Iterator[Atom]:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if not isinstance(other, Valuation):
            return False
        return set(self.alphabet) == set(other.alphabet) and all(
            self.assignment(atom) == other.assignment(atom) for atom in self.alphabet)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Valuation):
            return False
        return set(self.alphabet) < set(other.alphabet) and all(
            self.assignment(atom) == other.assignment(atom) for atom in self.alphabet)

    def __le__(self, other) -> bool:
        if not isinstance(other, Valuation):
            return False
        return set(self.alphabet) <= set(other.alphabet) and all(
            self.assignment(atom) == other.assignment(atom) for atom in self.alphabet)

    def __gt__(self, other) -> bool:
        if not isinstance(other, Valuation):
            return False
        return set(self.alphabet) > set(other.alphabet) and all(
            self.assignment(atom) == other.assignment(atom) for atom in other.alphabet)

    def __ge__(self, other) -> bool:
        if not isinstance(other, Valuation):
            return False
        return set(self.alphabet) >= set(other.alphabet) and all(
            self.assignment(atom) == other.assignment(atom) for atom in other.alphabet)

    def assignment(self, atom: Atom) -> bool:
        raise NotImplementedError

    @classmethod
    def from_atoms(cls, atoms: Iterable[Atom]) -> _Valuation:
        raise NotImplementedError


_FrozenValuation: TypeAlias = 'FrozenValuation'


@dataclass(frozen=True)
class FrozenValuation(Valuation):
    mapping: Mapping[Atom, bool] = Field(default_factory=frozendict)

    @property
    def alphabet(self) -> Iterator[Atom]:
        return iter(self.mapping.keys())

    def assignment(self, atom: Atom) -> bool:
        return self.mapping.get(atom, False)

    @classmethod
    def from_atoms(cls, atoms: Iterable[Atom]) -> _FrozenValuation:
        return FrozenValuation(frozendict({atom: True for atom in atoms}))


_MutableValuation: TypeAlias = 'MutableValuation'


@dataclass
class MutableValuation(Valuation):
    mapping: MutableMapping[Atom, bool] = Field(default_factory=dict)

    @property
    def alphabet(self) -> Iterator[Atom]:
        return iter(self.mapping.keys())

    def assignment(self, atom: Atom) -> bool:
        return self.mapping.get(atom, False)

    @classmethod
    def from_atoms(cls, atoms: Iterable[Atom]) -> _MutableValuation:
        return MutableValuation({atom: True for atom in atoms})


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

    @property
    def atoms(self) -> Set[Atom]:
        return {atom for isf in self.immediate_subformulae for atom in isf.atoms}

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Formula):
            raise TypeError(f"Cannot compare Formula to type {type(other).__name__}")
        return self.precedence < other.precedence

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Formula):
            raise TypeError(f"Cannot compare Formula to type {type(other).__name__}")
        return self.precedence > other.precedence

    def __call__(self, *args: Any, valuation: Optional[Valuation] = None, **kwargs: Any) -> bool:
        return self.evaluate(valuation)

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


def all_valuations(formula: Formula,
                   alphabet: Optional[Set[Atom]] = None,
                   valuation: Optional[Valuation] = None) -> Iterator[Valuation]:
    if alphabet is None:
        alphabet = formula.atoms
    if valuation is None:
        free_atoms = alphabet
    else:
        free_atoms = alphabet - set(valuation.alphabet)
    for true_atoms in more_itertools.powerset(free_atoms):
        yield FrozenValuation.from_atoms(true_atoms)


def models(formula: Formula,
           alphabet: Optional[Set[Atom]] = None,
           valuation: Optional[Valuation] = None) -> Iterator[Valuation]:
    return (val for val in all_valuations(formula, alphabet, valuation) if formula.evaluate(val))


@dataclass(frozen=True, eq=True)
class NonaryFormula(Formula):

    @property
    def precedence(self) -> float:
        return 30

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, eq=True)
class AtomicFormula(NonaryFormula):
    atom: Atom

    @property
    def atoms(self) -> Set[Atom]:
        return {self.atom}

    def __str__(self) -> str:
        return str(self.atom)

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        if valuation is None:
            return False
        return valuation.assignment(self.atom)


_Literal: TypeAlias = 'Literal'


@dataclass(frozen=True, eq=True)
class Literal(NonaryFormula):
    atom: Atom
    sign: bool = Field(default=True)

    @property
    def atoms(self) -> Set[Atom]:
        return {self.atom}

    def __str__(self) -> str:
        if self.sign is False:
            return f"¬{self.atom}"
        return str(self.atom)

    def __neg__(self) -> _Literal:
        return Literal(self.atom, not self.sign)

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        if valuation is None:
            return not self.sign
        return bool(valuation.assignment(self.atom) ^ (not self.sign))


@dataclass(frozen=True, eq=True)
class Bot(NonaryFormula):

    @property
    def precedence(self) -> float:
        return float('inf')

    def __str__(self) -> str:
        return '⊥'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return False


@dataclass(frozen=True, eq=True)
class Top(Formula):

    @property
    def precedence(self) -> float:
        return float('inf')

    def __str__(self) -> str:
        return '⊤'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return False


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

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


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

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return not self.formula.evaluate(valuation)


@dataclass(frozen=True, eq=True)
class Box(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence

    @property
    def connective_symbol(self) -> str:
        return '□'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise TypeError("Box Formulae cannot be evaluated")


@dataclass(frozen=True, eq=True)
class Dia(UnaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence

    @property
    def connective_symbol(self) -> str:
        return '⋄'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise TypeError("Dia Formulae cannot be evaluated")


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

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, eq=True)
class Conjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence + 4

    @property
    def connective_symbol(self) -> str:
        return '⋀'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return self.left.evaluate(valuation) and self.right.evaluate(valuation)


@dataclass(frozen=True, eq=True)
class Disjunction(BinaryFormula):

    @property
    def precedence(self) -> float:
        return super().precedence + 3

    @property
    def connective_symbol(self) -> str:
        return '⋁'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return self.left.evaluate(valuation) or self.right.evaluate(valuation)


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

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return (not self.left.evaluate(valuation)) or self.right.evaluate(valuation)


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

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return self.left.evaluate(valuation) == self.right.evaluate(valuation)


@dataclass(frozen=True, eq=True)
class NAryFormula(Formula):
    formulae: FrozenSet[Formula] = Field(default_factory=frozenset)

    @property
    def immediate_subformulae(self) -> Set[_Formula]:
        return set(self.formulae)

    @property
    def precedence(self) -> float:
        return 50

    def __str__(self) -> str:
        return f"{self.connective_symbol}{'{'}{','.join(str(formula) for formula in self.formulae)}{'}'}"

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, eq=True)
class Clause(NAryFormula):

    @property
    def connective_symbol(self) -> str:
        return '⋁'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return any(formula.evaluate(valuation) for formula in self.formulae)


@dataclass(frozen=True, eq=True)
class ConjunctiveClause(NAryFormula):

    @property
    def connective_symbol(self) -> str:
        return '⋀'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        return all(formula.evaluate(valuation) for formula in self.formulae)


@dataclass(frozen=True, eq=True)
class SeqFormula(Formula):
    formula_sequence: Sequence[Formula] = Field(default_factory=tuple)

    @property
    def precedence(self) -> float:
        return 60

    def __str__(self) -> str:
        if not self.formula_sequence:
            return "[]"
        res = f"[{self.formula_sequence[0]}]"
        for formula in self.formula_sequence[1:]:
            res += f" {self.connective_symbol} [{formula}]"
        return res

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, eq=True)
class BoxChain(SeqFormula):

    @property
    def connective_symbol(self) -> str:
        return '□'

    def evaluate(self, valuation: Optional[Valuation] = None) -> bool:
        raise TypeError("BoxChain Formulae cannot be evaluated")
