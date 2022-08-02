# noinspection DuplicatedCode
import unittest

from cegarpy.atom import Atom
from cegarpy.formula import Literal, AtomicFormula, Negation


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

    def test_conjunction(self):

        a = Atom('a')
        b = Atom('b')
