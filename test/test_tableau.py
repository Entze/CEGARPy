# noinspection DuplicatedCode
import unittest

from cegarpy.atom import Atom
from cegarpy.formula import Literal, ConjunctiveClause, BoxChain, Implication, Box, Dia, Disjunction
from cegarpy.tableau import ModalTableau


class TestInitialize(unittest.TestCase):

    def test_example(self):
        p_ = Atom('p')
        p = Literal(p_)
        q_ = Atom('q')
        q = Literal(q_)

        a1_ = Atom('a1')
        a1 = Literal(a1_)
        b1_ = Atom('b1')
        b1 = Literal(b1_)
        a2_ = Atom('a2')
        a2 = Literal(a2_)
        c1_ = Atom('c1')
        c1 = Literal(c1_)

        classical_formulae = ConjunctiveClause(frozenset({
            a1, a2, c1
        }))
        modal_formuluae = BoxChain(
            (
                ConjunctiveClause(
                    frozenset({Implication(a1, Box(b1)), Implication(a2, Box(p)), Implication(c1, Dia(-q))})),
                ConjunctiveClause(frozenset({Implication(b1, Disjunction(-p, q))}))
            )
        )

        m = ModalTableau(classical_formulae, modal_formuluae)

        m.initialize()


class TestSolve(unittest.TestCase):

    def test_example(self):
        p_ = Atom('p')
        p = Literal(p_)
        q_ = Atom('q')
        q = Literal(q_)

        a1_ = Atom('a1')
        a1 = Literal(a1_)
        b1_ = Atom('b1')
        b1 = Literal(b1_)
        a2_ = Atom('a2')
        a2 = Literal(a2_)
        c1_ = Atom('c1')
        c1 = Literal(c1_)

        classical_formulae = ConjunctiveClause(frozenset({
            a1, a2, c1
        }))
        modal_formuluae = BoxChain(
            (
                ConjunctiveClause(
                    frozenset({Implication(a1, Box(b1)), Implication(a2, Box(p)), Implication(c1, Dia(-q))})),
                ConjunctiveClause(frozenset({Implication(b1, Disjunction(-p, q))}))
            )
        )

        m = ModalTableau(classical_formulae, modal_formuluae)

        m.initialize()
        expected = False
        actual = m.solve()

        self.assertEqual(expected, actual)
