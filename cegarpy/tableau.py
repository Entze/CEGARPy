from typing import Set, Optional, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

from cegarpy.formula import Clause, BoxChain, Implication, Valuation, MutableValuation

Inconclusive: Literal['Inconclusive'] = 'Inconclusive'
Satisfiable: Literal['Satisfiable'] = 'Satisfiable'
Unsatisfiable: Literal['Unsatisfiable'] = 'Unsatisfiable'


@dataclass
class JumpRestartNode:

    def expand(self) -> None:
        raise NotImplementedError


@dataclass
class LocalNode:
    valuation: Valuation = Field(default=MutableValuation)
    clauses: Set[Clause] = Field(default_factory=set)
    box_implications: Set[Implication] = Field(default_factory=set)
    dia_implications: Set[Implication] = Field(default_factory=set)
    modal_box_chain: BoxChain = Field(default_factory=BoxChain)
    child: Optional[JumpRestartNode] = Field(default=None)
    status: Literal['Satisfiable', 'Unsatisfiable', 'Inconclusive'] = Field(default=Inconclusive)

    def __direct_expand(self) -> None:
        assert self.child is None

        assert self.child is not None

    def expand(self) -> None:
        if self.child is None:
            self.__direct_expand()
        else:
            self.child.expand()


@dataclass
class ModalTableau:
    classic_formulae: Clause = Field(default_factory=Clause)
    modal_formulae: BoxChain = Field(default_factory=BoxChain)
    assumptions: Valuation = Field(default_factory=MutableValuation)
    tableau_root: Optional[LocalNode] = Field(default=None)
