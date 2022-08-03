from typing import Set, Optional, Literal, TypeAlias, MutableSequence

from pydantic import Field
from pydantic.dataclasses import dataclass

from cegarpy import formula
from cegarpy.formula import Clause, BoxChain, Implication, Valuation, MutableValuation, ConjunctiveClause, models, Box, \
    Dia

Inconclusive: Literal['Inconclusive'] = 'Inconclusive'
Satisfiable: Literal['Satisfiable'] = 'Satisfiable'
Unsatisfiable: Literal['Unsatisfiable'] = 'Unsatisfiable'
Open: Literal['Open'] = 'Open'
Closed: Literal['Closed'] = 'Closed'

_LocalNode: TypeAlias = 'LocalNode'


class __ValuationConfig:
    arbitrary_types_allowed = True


@dataclass(config=__ValuationConfig)
class JumpRestartNode:
    assumptions: Valuation = Field(default_factory=MutableValuation)
    valuation: Valuation = Field(default_factory=MutableValuation)
    clauses: ConjunctiveClause = Field(default_factory=ConjunctiveClause)
    box_implications: Set[Implication] = Field(default_factory=set)
    dia_implications: Set[Implication] = Field(default_factory=set)
    modal_box_chain: BoxChain = Field(default_factory=BoxChain)
    jump_nodes: Optional[MutableSequence[_LocalNode]] = Field(default=None)
    restart_node: Optional[_LocalNode] = Field(default=None)
    status: Optional[Literal['Open', 'Closed']] = Field(default=None)
    expanded_dia_implications: MutableSequence[Implication] = Field(default_factory=list)

    def jump(self) -> None:
        dia_implication = next((d for d in self.dia_implications if
                                d not in self.expanded_dia_implications and d.left.evaluate(self.valuation)), None)
        if dia_implication is None and not self.modal_box_chain.formula_sequence:
            self.status = Open  # TODO: Is this right?
            return
        self.expanded_dia_implications.append(dia_implication)
        assumptions_: MutableValuation = MutableValuation()
        assumptions_.mapping = {atom: self.assumptions.assignment(atom) for atom in self.assumptions.alphabet}
        assert isinstance(dia_implication.right, Dia)
        assert isinstance(dia_implication.right.formula, formula.Literal)
        assumptions_.mapping[dia_implication.right.formula.atom] = dia_implication.right.formula.sign
        clauses_set = set()
        for box_implication in self.box_implications:
            assert isinstance(box_implication.left, formula.Literal)
            assert isinstance(box_implication.right, Box)
            if box_implication.left.evaluate(self.valuation):
                clauses_set.add(box_implication.right.formula)
        if self.modal_box_chain.formula_sequence:

            box_implications_: Set[Implication] = set()
            dia_implications_: Set[Implication] = set()
            for isf in self.modal_box_chain.formula_sequence[0].immediate_subformulae:
                assert isinstance(isf, Implication)
                if isinstance(isf.right, Box):
                    box_implications_.add(isf)
                elif isinstance(isf.right, Dia):
                    dia_implications_.add(isf)
                else:
                    clauses_set.add(isf)

        else:
            box_implications_ = set()
            dia_implications_ = set()
        clauses_ = ConjunctiveClause(frozenset(clauses_set))
        modal_box_chain_ = self.modal_box_chain.pull_up()

        jump = LocalNode(

            assumptions=assumptions_,
            clauses=clauses_,
            box_implications=box_implications_,
            dia_implications=dia_implications_,
            modal_box_chain=modal_box_chain_
        )
        self.jump_nodes.append(jump)

    def restart(self, dia_implication: Implication) -> None:
        assert isinstance(dia_implication.right, Dia)
        assert isinstance(dia_implication.left, formula.Literal)
        c: formula.Literal = dia_implication.left
        as_ = {box_implication.left for box_implication in self.box_implications if
               isinstance(box_implication.left, formula.Literal) and box_implication.left.evaluate(self.valuation)}
        clauses_ = ConjunctiveClause(
            self.clauses.formulae | {Clause(frozenset({-lit for lit in as_} | {-c}))})
        box_implications_ = set(self.box_implications)
        dia_implications_ = set(self.dia_implications)
        restart = LocalNode(
            assumptions=self.assumptions,
            clauses=clauses_,
            box_implications=box_implications_,
            dia_implications=dia_implications_
        )

        self.restart_node = restart

    def expand(self) -> None:
        if self.status is not None:
            return
        if self.jump_nodes is None:
            self.jump_nodes = []
        if self.restart_node is not None:
            if self.restart_node.status is None:
                self.restart_node.expand()
            else:
                self.status = self.restart_node.status
        elif self.jump_nodes:
            if self.jump_nodes[-1].status is not None:
                if self.jump_nodes[-1].status == 'Closed':
                    self.restart(self.expanded_dia_implications[-1])
                else:
                    self.jump()
            else:
                self.jump_nodes[-1].expand()
        else:
            self.jump()


@dataclass(config=__ValuationConfig)
class LocalNode:
    assumptions: Valuation = Field(default=MutableValuation)
    clauses: ConjunctiveClause = Field(default_factory=ConjunctiveClause)
    box_implications: Set[Implication] = Field(default_factory=set)
    dia_implications: Set[Implication] = Field(default_factory=set)
    modal_box_chain: BoxChain = Field(default_factory=BoxChain)
    model: Optional[Valuation] = Field(default=None)
    child: Optional[JumpRestartNode] = Field(default=None)
    status: Optional[Literal['Open', 'Closed']] = Field(default=None)

    def local(self) -> None:
        self.model = next(models(self.clauses, valuation=self.assumptions), None)
        if self.model is None:
            self.status = Closed

    def __create_child(self) -> None:
        self.child = JumpRestartNode(
            assumptions=self.assumptions,
            valuation=self.model,
            clauses=self.clauses,
            box_implications=self.box_implications,
            dia_implications=self.dia_implications,
            modal_box_chain=self.modal_box_chain
        )
        assert self.child is not None

    def expand(self) -> None:
        if self.child is None:
            self.local()
            if self.status != Closed:
                self.__create_child()
        elif self.status is None:
            self.child.expand()
            if self.child.status is not None:
                self.status = self.child.status
        assert self.status == Closed or self.child is not None


@dataclass(config=__ValuationConfig)
class ModalTableau:
    classic_formulae: ConjunctiveClause = Field(default_factory=ConjunctiveClause)
    modal_formulae: BoxChain = Field(default_factory=BoxChain)
    assumptions: Valuation = Field(default_factory=MutableValuation)
    tableau_root: Optional[LocalNode] = Field(default=None)

    def initialize(self) -> None:

        if self.modal_formulae.formula_sequence:
            box_implications: Set[Implication] = set()
            dia_implications: Set[Implication] = set()
            for modal_implication in self.modal_formulae.formula_sequence[0].immediate_subformulae:
                assert isinstance(modal_implication, Implication), ""
                if isinstance(modal_implication.right, Box):
                    box_implications.add(modal_implication)
                else:
                    assert isinstance(modal_implication.right, Dia)
                    dia_implications.add(modal_implication)
            self.tableau_root = LocalNode(
                assumptions=self.assumptions,
                clauses=self.classic_formulae,
                box_implications=box_implications,
                dia_implications=dia_implications,
                modal_box_chain=self.modal_formulae.pull_up()
            )
        else:
            self.tableau_root = LocalNode(
                assumptions=self.assumptions,
                clauses=self.classic_formulae)

    def solve(self) -> bool:
        while self.tableau_root.status is None:
            self.tableau_root.expand()
        return self.tableau_root.status == Open
