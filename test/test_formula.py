# noinspection DuplicatedCode
import unittest

from cegarpy.atom import Atom
from cegarpy.formula import Literal, AtomicFormula, Negation, Implication, Conjunction, Equivalence, Bot, Top, Box, Dia, \
    Disjunction


class TestIsNNF(unittest.TestCase):

    def test_literal(self):
        a = Atom('a')
        l = Literal(a)

        expected = True
        actual = l.is_nnf

        self.assertEqual(expected, actual)

    def test_negation(self):
        a = Atom('a')
        f = AtomicFormula(a)
        n = Negation(f)

        expected = False
        actual = n.is_nnf

        self.assertEqual(expected, actual)

    def test_dia(self):
        a = Atom('a')
        f = AtomicFormula(a)
        d = Dia(f)

        expected = True
        actual = d.is_nnf

        self.assertEqual(expected, actual)

    def test_conjunction(self):
        a = Atom('a')
        b = Atom('b')
        l = Literal(a)
        m = Literal(b)

        c = Conjunction(l, m)

        expected = True
        actual = c.is_nnf

        self.assertEqual(expected, actual)

    def test_implication(self):
        a = Atom('a')
        b = Atom('b')
        l = Literal(a)
        m = Literal(b)

        i = Implication(l, m)

        expected = False
        actual = i.is_nnf

        self.assertEqual(expected, actual)

    def test_equivalence(self):
        a = Atom('a')
        b = Atom('b')
        l = Literal(a)
        m = Literal(b)

        e = Equivalence(l, m)

        expected = False
        actual = e.is_nnf

        self.assertEqual(expected, actual)


class TestStr(unittest.TestCase):

    def test_atomic_formula(self):
        p = Atom('p')
        a = AtomicFormula(p)

        expected = 'p'
        actual = str(a)

        self.assertEqual(expected, actual)

    def test_compound(self):
        bot = Bot()
        top = Top()

        p_ = Atom('p')
        q_ = Atom('q')

        p = Literal(p_)
        q = Literal(q_)

        sf1 = Implication(Box(p), Box(Box(p)))
        sf2 = Equivalence(Dia(q), Negation(Box(Negation(q))))
        sf3 = Equivalence(Negation(top), bot)
        sf4 = Equivalence(Equivalence(p, q), Conjunction(Implication(p, q), Implication(q, p)))
        sf5 = Equivalence(top, Negation(bot))
        sf6 = Implication(Conjunction(-p, -q), Disjunction(-p, -q))

        f = Conjunction(sf1, Conjunction(sf2, Conjunction(sf3, Conjunction(sf4, Conjunction(sf5, sf6)))))

        expected = '(□p → □□p) ⋀ (⋄q ≡ ¬□¬q) ⋀ (¬⊤ ≡ ⊥) ⋀ (p ≡ q ≡ (p → q) ⋀ (q → p)) ⋀ (⊤ ≡ ¬⊥) ⋀ (¬p ⋀ ¬q → ¬p ⋁ ¬q)'
        actual = str(f)

        self.assertEqual(expected, actual)
