"""Ejercicios y casos límite de los temas complementarios del temario."""

from fractions import Fraction as Q
from itertools import permutations
import random
import sys
import unittest
from unittest.mock import patch

import numpy as np

from matematicas_ia.catalog import LESSONS
from matematicas_ia.core import InputError, calculate, determinant, identity, matrix, multiply, rref
from matematicas_ia.spectral import characteristic_coefficients


def raw(a):
    return "\n".join(" ".join(str(x) for x in row) for row in a)


class SpaceTests(unittest.TestCase):
    def test_rank_rectangular_and_zero(self):
        for a, expected in [("1 2 3\n2 4 6", 1), ("0 0\n0 0", 0), ("1 0 0\n0 1 0", 2), ("0\n2", 1)]:
            with self.subTest(a=a):
                self.assertEqual(calculate("rank", {"a": a}).value, expected)

    def test_rank_uses_exact_fractions(self):
        result = calculate("rank", {"a": "1 1\n1 1.000000000001"})
        self.assertEqual(result.value, 2)

    def test_basis_uses_original_columns(self):
        result = calculate("span_basis", {"a": "2 4 0\n0 0 3"})
        self.assertEqual(result.value, [[2, 0], [0, 3]])
        self.assertIn("dependientes", result.interpretation)
        self.assertIn("todo ℝ^2", result.interpretation)

    def test_independent_proper_subspace(self):
        result = calculate("span_basis", {"a": "1\n2\n3"})
        self.assertEqual(result.value, [[1, 2, 3]])
        self.assertIn("independientes", result.interpretation)
        self.assertIn("subespacio propio", result.interpretation)

    def test_zero_span_has_empty_basis(self):
        result = calculate("span_basis", {"a": "0 0\n0 0"})
        self.assertEqual(result.value, [])
        self.assertIn("{0}", result.interpretation)

    def test_nullspace_general_solution(self):
        result = calculate("nullspace", {"a": "1 2 3\n2 4 6"})
        self.assertEqual(result.value, [[-2, 1, 0], [-3, 0, 1]])
        self.assertIn("t1·v1 + t2·v2", result.steps[-1])

    def test_nullspace_zero_and_injective(self):
        self.assertEqual(calculate("nullspace", {"a": "0 0\n0 0"}).value, identity(2))
        result = calculate("nullspace", {"a": "1 0\n0 1\n1 1"})
        self.assertEqual(result.value, [])
        self.assertIn("dimensión cero", result.interpretation)

    def test_free_column_before_pivot(self):
        self.assertEqual(calculate("nullspace", {"a": "0 2 4"}).value, [[1, 0, 0], [0, -2, 1]])

    def test_rank_nullity_and_basis_invariants(self):
        rng = random.Random(42)
        for m in range(1, 6):
            for n in range(1, 6):
                a = [[Q(rng.randrange(-2, 3)) for _ in range(n)] for _ in range(m)]
                data = {"a": raw(a)}
                rank = calculate("rank", data).value
                kernel = calculate("nullspace", data).value
                image_basis = calculate("span_basis", data).value
                self.assertEqual(rank + len(kernel), n)
                self.assertEqual(len(image_basis), rank)
                if kernel:
                    self.assertEqual(len(rref(kernel, n)[1]), len(kernel))
                for v in kernel:
                    self.assertEqual(multiply(a, [[x] for x in v]), [[0]] * m)
                # Las columnas originales elegidas realmente generan todo Im(A).
                if image_basis:
                    basis_matrix = [list(row) for row in zip(*image_basis)]
                    for col in zip(*a):
                        membership = calculate("span_membership", {"a": raw(basis_matrix), "b": " ".join(str(x) for x in col)})
                        self.assertEqual(multiply(basis_matrix, [[x] for x in membership.value]), [[x] for x in col])

    def test_membership_unique(self):
        result = calculate("span_membership", {"a": "1 0\n0 1\n1 1", "b": "2 3 5"})
        self.assertEqual(result.value, [2, 3])
        self.assertIn("es única", result.interpretation)

    def test_membership_nonunique(self):
        result = calculate("span_membership", {"a": "1 2\n2 4", "b": "3 6"})
        self.assertEqual(result.value, [3, 0])
        self.assertIn("no es única", result.interpretation)
        self.assertIn("c₀ + Σ", result.steps[-1])

    def test_membership_incompatible(self):
        result = calculate("span_membership", {"a": "1 0\n0 1\n1 1", "b": "2 3 6"})
        self.assertEqual(result.value, "No pertenece al espacio generado")

    def test_membership_zero_space(self):
        self.assertEqual(calculate("span_membership", {"a": "0 0", "b": "0"}).value, [0, 0])
        self.assertEqual(calculate("span_membership", {"a": "0 0", "b": "1"}).value, "No pertenece al espacio generado")


class DeterminantTests(unittest.TestCase):
    def test_known_determinants(self):
        for a, expected in [("5", 5), ("0 1\n2 3", -2), ("1 2\n2 4", 0), ("2 1 0\n1 3 2\n0 1 4", 16), ("1/2 1/3\n0 -2", -1)]:
            with self.subTest(a=a):
                self.assertEqual(calculate("determinant", {"a": a}).value, expected)

    def test_matches_leibniz_formula(self):
        rng = random.Random(2026)
        for n in range(1, 5):
            for _ in range(12):
                a = [[Q(rng.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
                reference = Q(0)
                for p in permutations(range(n)):
                    inversions = sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
                    term = Q((-1)**inversions)
                    for i, j in enumerate(p):
                        term *= a[i][j]
                    reference += term
                self.assertEqual(determinant(a)[0], reference)

    def test_maximum_size(self):
        a = identity(8)
        a[0][0] = Q(1, 3)
        a[7][7] = -9
        self.assertEqual(determinant(a)[0], -3)


class OrthogonalityTests(unittest.TestCase):
    def test_yes_no_and_fractions(self):
        for a, b, expected in [("1 2 -1", "2 -1 0", True), ("1 1", "1 0", False), ("1/3 1/2", "3 -2", True), ("1 0", "1e-12 1", False)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(calculate("orthogonality", {"a": a, "b": b}).value.startswith("Sí"), expected)

    def test_zero_is_orthogonal_without_angle(self):
        result = calculate("orthogonality", {"a": "0 0", "b": "1 2"})
        self.assertTrue(result.value.startswith("Sí"))
        self.assertIn("no define una dirección ni un ángulo", result.interpretation)


class EigenTests(unittest.TestCase):
    def assert_pairs(self, a, result):
        array = np.array(matrix(a), dtype=float)
        solution = result.value
        for value, v, residual in zip(solution.eigenvalues, solution.vectors, solution.residuals):
            np.testing.assert_allclose(array @ v, value * np.array(v), atol=1e-10, rtol=1e-10)
            self.assertAlmostEqual(float(np.linalg.norm(v)), 1)
            self.assertLess(residual, 1e-10)

    def test_symmetric_pairs_and_orthonormality(self):
        a = "2 1\n1 2"
        result = calculate("eigen", {"a": a})
        np.testing.assert_allclose(result.value.eigenvalues, [1, 3])
        vectors = np.array(result.value.vectors).T
        np.testing.assert_allclose(vectors.conj().T @ vectors, np.eye(2), atol=1e-12)
        self.assert_pairs(a, result)

    def test_complex_conjugate_pairs(self):
        a = "0 -1\n1 0"
        result = calculate("eigen", {"a": a})
        np.testing.assert_allclose(result.value.eigenvalues, [-1j, 1j])
        self.assert_pairs(a, result)
        self.assertIn("i", str(result.value))

    def test_irrational_values(self):
        a = "1 1\n1 -1"
        result = calculate("eigen", {"a": a})
        np.testing.assert_allclose(result.value.eigenvalues, [-np.sqrt(2), np.sqrt(2)])
        self.assert_pairs(a, result)

    def test_repeated_values_identity_and_zero(self):
        for a, expected in [("1 0\n0 1", [1, 1]), ("0 0\n0 0", [0, 0]), ("3/2", [1.5])]:
            result = calculate("eigen", {"a": a})
            np.testing.assert_allclose(result.value.eigenvalues, expected)
            self.assert_pairs(a, result)

    def test_defective_matrix_does_not_claim_basis(self):
        a = "2 1\n0 2"
        result = calculate("eigen", {"a": a})
        np.testing.assert_allclose(result.value.eigenvalues, [2, 2])
        self.assertIn("casi dependientes", result.interpretation)
        self.assertIn("no certifica una base", result.interpretation)
        self.assert_pairs(a, result)

    def test_larger_matrix(self):
        a = raw([[Q(i+1) if i == j else Q(0) for j in range(8)] for i in range(8)])
        result = calculate("eigen", {"a": a})
        np.testing.assert_allclose(result.value.eigenvalues, range(1, 9))
        self.assert_pairs(a, result)

    def test_scale_and_small_imaginary_parts_are_preserved(self):
        result = calculate("eigen", {"a": "0 -1e-12\n1e-12 0"})
        np.testing.assert_allclose(result.value.eigenvalues, [-1e-12j, 1e-12j], rtol=1e-14, atol=0)
        self.assertIn("1e-12i", str(result.value))
        result = calculate("eigen", {"a": "1e12 0\n0 1e-12"})
        np.testing.assert_allclose(result.value.eigenvalues, [1e-12, 1e12], rtol=1e-14, atol=0)

    def test_characteristic_polynomial(self):
        self.assertEqual(characteristic_coefficients(matrix("2 1\n1 2")), [1, -4, 3])
        self.assertEqual(characteristic_coefficients(matrix("0 -1\n1 0")), [1, 0, 1])
        # Cayley–Hamilton valida los coeficientes sin depender del algoritmo numérico.
        a = matrix("1 2 3\n0 -1 4\n5 2 0")
        p = characteristic_coefficients(a)
        accumulated = [[Q(0)] * 3 for _ in range(3)]
        for coefficient in p:
            accumulated = multiply(accumulated, a)
            for i in range(3):
                accumulated[i][i] += coefficient
        self.assertEqual(accumulated, [[0]*3 for _ in range(3)])
        self.assertEqual(p[-1], -determinant(a)[0])

    def test_missing_numpy_has_actionable_message(self):
        with patch.dict(sys.modules, {"numpy": None}):
            with self.assertRaisesRegex(InputError, "requirements.txt"):
                calculate("eigen", {"a": "1"})
            self.assertEqual(calculate("determinant", {"a": "2"}).value, 2)

    def test_numerical_failure_is_user_error(self):
        with patch("numpy.linalg.eigh", side_effect=np.linalg.LinAlgError):
            with self.assertRaisesRegex(InputError, "no convergió"):
                calculate("eigen", {"a": "1"})


class NewValidationTests(unittest.TestCase):
    def test_invalid_dimensions(self):
        for operation, data in [("eigen", {"a": "1 2"}), ("determinant", {"a": "1\n2"}), ("span_membership", {"a": "1 0\n0 1", "b": "1"}), ("orthogonality", {"a": "1 2", "b": "1"})]:
            with self.subTest(operation=operation), self.assertRaises(InputError):
                calculate(operation, data)

    def test_catalog_has_unique_identifiers(self):
        self.assertEqual(len(LESSONS), len({lesson.id for lesson in LESSONS}))


if __name__ == "__main__":
    unittest.main()
