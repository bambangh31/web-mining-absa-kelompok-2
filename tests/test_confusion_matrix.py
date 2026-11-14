"""Matriks diuji dengan data buatan, termasuk aspek terlewat dan tambahan."""
import unittest

from src.absa_schema import ASPECTS, LABELS, empty_labels
from src.evaluate import confusion_matrix, evaluate


class ConfusionMatrixTests(unittest.TestCase):
    def test_rows_are_gold_and_columns_predictions(self):
        matrix = confusion_matrix(
            ["negatif", "negatif", "tidak_disebut", "positif"],
            ["negatif", "tidak_disebut", "netral", "negatif"],
        )
        self.assertEqual(matrix, [[0, 0, 0, 1], [0, 0, 1, 0], [1, 0, 1, 0], [0, 0, 0, 0]])
        with self.assertRaises(ValueError):
            confusion_matrix(["negatif"], [])

    def test_pooled_matrix_and_subset(self):
        gold = {"a": {**empty_labels(), "performa": "negatif"}, "b": empty_labels()}
        pred = {"a": empty_labels()}
        result = evaluate(gold, pred, ["a"])
        self.assertEqual(result["confusion_matrix_labels"], list(LABELS))
        self.assertEqual(result["confusion_matrix_gabungan"][2][0], 1)
        self.assertEqual(sum(map(sum, result["confusion_matrix_gabungan"])), len(ASPECTS))
        for aspect in ASPECTS:
            self.assertEqual(sum(map(sum, result["per_aspek"][aspect]["confusion_matrix"])), 1)
        self.assertEqual(result["recall_pasangan"], 0)
        with self.assertRaisesRegex(ValueError, "kosong"):
            evaluate(gold, pred, [])
