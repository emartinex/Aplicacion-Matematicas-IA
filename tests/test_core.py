"""Casos de los apuntes, propiedades algebraicas y entradas inválidas."""

from fractions import Fraction as Q
from math import sqrt
import random
import unittest

from matematicas_ia.catalog import LESSONS
from matematicas_ia.core import InputError, calculate, identity, matrix, multiply, number, vector


class NotesTests(unittest.TestCase):
    def test_all_examples_have_explanations(self):
        for lesson in LESSONS:
            with self.subTest(operation=lesson.id):
                result = calculate(lesson.id, {f.key: f.example for f in lesson.fields})
                self.assertTrue(result.steps)
                self.assertTrue(result.interpretation)
                self.assertTrue(lesson.scenario)

    def test_vector_exercise(self):
        values = {"a": "3 -2 4", "b": "1 5 -2", "k": "2"}
        for op, expected in [("v_add", [4, 3, 2]), ("v_sub", [2, -7, 6]), ("v_scale", [6, -4, 8]), ("v_dot", -15)]:
            with self.subTest(op=op):
                self.assertEqual(calculate(op, values).value, expected)

    def test_norm(self):
        self.assertEqual(calculate("v_norm", {"a": "3 4"}).value, 5)
        self.assertEqual(calculate("v_norm", {"a": "0 0"}).value, 0)
        self.assertEqual(calculate("v_norm", {"a": "3/5 4/5"}).value, 1)
        result = calculate("v_norm", {"a": "1 1"})
        self.assertAlmostEqual(result.value, sqrt(2))
        self.assertIn("aproximada", result.summary)

    def test_matrix_exercise(self):
        values = {"a": "3 -2\n4 5", "b": "-1 6\n2 -3", "k": "2", "alpha": "3", "beta": "-2"}
        for op, expected in [("m_add", [[2, 4], [6, 2]]), ("m_sub", [[4, -8], [2, 8]]), ("m_scale", [[6, -4], [8, 10]]), ("m_combo", [[11, -18], [8, 21]])]:
            with self.subTest(op=op):
                self.assertEqual(calculate(op, values).value, expected)

    def test_product(self):
        self.assertEqual(calculate("m_product", {"a": "2 1 0\n1 3 2", "b": "1 0\n2 1\n0 3"}).value, [[4, 1], [7, 9]])

    def test_transpose(self):
        result = calculate("m_transpose", {"a": "1 8 4\n2 9 5\n5 21 6\n6 32 2"})
        self.assertEqual(result.value, [[1, 2, 5, 6], [8, 9, 21, 32], [4, 5, 6, 2]])

    def test_identity_and_dimensions(self):
        self.assertEqual(calculate("m_identity", {"n": "2"}).value, [[1, 0], [0, 1]])
        self.assertEqual(calculate("m_dimensions", {"a": "1 2 3\n4 5 6"}).value, "2 × 3")

    def test_prediction(self):
        self.assertEqual(calculate("prediction", {"x": "8 7 9", "w": "0.5 0.3 0.2", "bias": "0"}).value, Q(79, 10))
        self.assertEqual(calculate("prediction", {"x": "8 7 9", "w": "0.5 0.3 0.2", "bias": "-1"}).value, Q(69, 10))


class LinearAlgebraTests(unittest.TestCase):
    def test_exact_decimal(self):
        self.assertEqual(calculate("v_add", {"a": "0.1", "b": "0.2"}).value, [Q(3, 10)])

    def test_inverse_pivot_swap_and_singular(self):
        self.assertEqual(calculate("m_inverse", {"a": "0 1\n2 3"}).value, [[Q(-3, 2), Q(1, 2)], [1, 0]])
        self.assertIn("singular", calculate("m_inverse", {"a": "1 2\n2 4"}).summary)
        self.assertEqual(calculate("m_inverse", {"a": "4"}).value, [[Q(1, 4)]])

    def test_inverse_property_on_generated_matrices(self):
        generator = random.Random(2026)
        for n in range(2, 6):
            for _ in range(6):
                a = [[Q(generator.randint(-3, 3)) for j in range(n)] for i in range(n)]
                for i in range(n):
                    a[i][i] = sum(abs(a[i][j]) for j in range(n) if j != i) + 1
                raw = "\n".join(" ".join(str(x) for x in row) for row in a)
                inverse = calculate("m_inverse", {"a": raw}).value
                self.assertEqual(multiply(a, inverse), identity(n))
                self.assertEqual(multiply(inverse, a), identity(n))

    def test_unique_system(self):
        self.assertEqual(calculate("system", {"a": "1 2\n4 5", "b": "3 6"}).value, [-1, 2])

    def test_overdetermined_system(self):
        result = calculate("system", {"a": "1 0\n0 1\n1 1", "b": "2 3 5"})
        self.assertEqual(result.value, [2, 3])

    def test_inconsistent_system(self):
        result = calculate("system", {"a": "1 2\n2 4", "b": "3 7"})
        self.assertEqual(result.value, "No existe solución")

    def test_infinite_solutions(self):
        result = calculate("system", {"a": "1 2\n2 4", "b": "3 6"})
        self.assertEqual(result.summary, "Infinitas soluciones")
        self.assertIn("x2 = t1", result.value)
        self.assertIn("x1 = 3 + (-2)·t1", result.value)

    def test_free_variables_before_pivot(self):
        result = calculate("system", {"a": "0 1 2", "b": "3"})
        self.assertIn("x1 = t1", result.value)
        self.assertIn("x3 = t2", result.value)
        self.assertIn("x2 = 3 + (-2)·t2", result.value)

    def test_zero_system(self):
        self.assertEqual(calculate("system", {"a": "0 0", "b": "0"}).summary, "Infinitas soluciones")
        self.assertEqual(calculate("system", {"a": "0 0", "b": "1"}).summary, "Sistema incompatible")

    def test_regression_learns_known_line(self):
        result = calculate("regression", {"x": "0 1 2 3", "y": "1 3 5 7"})
        self.assertEqual(result.value, "ŷ = (2)·x + (1)")
        self.assertIn("= 0.", result.steps[-1])

    def test_regression_noisy_data(self):
        result = calculate("regression", {"x": "1 2 3 4", "y": "2 3 5 4"})
        self.assertEqual(result.value, "ŷ = (4/5)·x + (3/2)")
        self.assertIn("9/20", result.steps[-1])


class ValidationTests(unittest.TestCase):
    def test_invalid_numbers(self):
        for value in ["", "nan", "inf", "1/0", "2+3", "__import__('os')", "0,5", "1e99", "1e-99", "-", "9"*33]:
            with self.subTest(value=value), self.assertRaises(InputError):
                number(value)

    def test_supported_number_formats(self):
        for raw, expected in [("-2", -2), (".5", Q(1, 2)), ("1/3", Q(1, 3)), ("-1/3", Q(-1, 3)), ("2e-3", Q(1, 500))]:
            self.assertEqual(number(raw), expected)

    def test_invalid_shapes(self):
        cases = [
            ("v_add", {"a": "1 2", "b": "1"}),
            ("m_add", {"a": "1 2", "b": "1\n2"}),
            ("m_product", {"a": "1 2", "b": "1 2"}),
            ("m_inverse", {"a": "1 2"}),
            ("m_identity", {"n": "2.5"}),
            ("m_identity", {"n": "0"}),
            ("m_identity", {"n": "9"}),
            ("system", {"a": "1 2", "b": "1 2"}),
            ("prediction", {"x": "1", "w": "1 2", "bias": "0"}),
            ("regression", {"x": "1 1", "y": "2 3"}),
            ("regression", {"x": "1", "y": "2"}),
        ]
        for op, values in cases:
            with self.subTest(op=op), self.assertRaises(InputError):
                calculate(op, values)

    def test_invalid_collections(self):
        for raw in ["", "1 2\n3", "1\n\n2", "\n".join(["1"]*9)]:
            with self.subTest(raw=raw), self.assertRaises(InputError):
                matrix(raw)
        with self.assertRaises(InputError):
            vector(" ".join(["1"]*9))

    def test_semicolon_rows(self):
        self.assertEqual(matrix("1 2;3 4"), [[1, 2], [3, 4]])


if __name__ == "__main__":
    unittest.main()
