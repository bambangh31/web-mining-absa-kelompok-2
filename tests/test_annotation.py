"""Uji kontrak anotasi dengan 850 ulasan BUATAN, bukan dataset atau gold."""

import csv
import itertools
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from src import annotation as tool


def overwrite_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class AnnotationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reviews = self.root / "reviews.csv"
        self.split = self.root / "split.csv"
        self.workspace = self.root / "workspace"
        reviews, splits = [], []
        for group, count in tool.COUNTS.items():
            for i in range(count):
                key = f"BUATAN-{group}-{i:03}"
                reviews.append({"reviewId": key, "text_llm": "Teks buatan untuk pengujian", "score": "1"})
                splits.append({"reviewId": key, "split": group})
        overwrite_csv(self.reviews, ["reviewId", "text_llm", "score"], reviews)
        overwrite_csv(self.split, ["reviewId", "split"], splits)
        self.manifest = tool.prepare(self.reviews, self.split, self.workspace)

    def fill_phase(self, phase):
        for member in tool.MEMBERS:
            path = self.workspace / f"{phase}_{member}.csv"
            rows = tool.read_csv(path, tool.SHEET_FIELDS)
            for row in rows:
                row.update({a: "tidak_disebut" for a in tool.ASPECTS})
                row["akun_login"] = "negatif"
            overwrite_csv(path, tool.SHEET_FIELDS, rows)

    def change_row(self, phase, member, key, **changes):
        path = self.workspace / f"{phase}_{member}.csv"
        rows = tool.read_csv(path, tool.SHEET_FIELDS)
        for row in rows:
            if row["reviewId"] == key:
                row.update(changes)
        overwrite_csv(path, tool.SHEET_FIELDS, rows)

    def test_assignments_balanced_disjoint_and_blinded(self):
        assignments = self.manifest["assignments"]
        calibration = set(assignments["kalibrasi"]["bambang"])
        self.assertEqual(len(calibration), 50)
        for member in tool.MEMBERS:
            self.assertEqual(set(assignments["kalibrasi"][member]), calibration)
            self.assertEqual(len(assignments["gold"][member]), 275)
            self.assertFalse(calibration & set(assignments["gold"][member]))
        owners = Counter(key for ids in assignments["gold"].values() for key in ids)
        self.assertEqual(Counter(owners.values()), {1: 500, 2: 300})
        for a, b in itertools.combinations(tool.MEMBERS, 2):
            self.assertEqual(len(set(assignments["gold"][a]) & set(assignments["gold"][b])), 50)
        for path in self.workspace.glob("*.csv"):
            rows = tool.read_csv(path, tool.SHEET_FIELDS)
            self.assertNotIn("score", rows[0])
            self.assertNotIn("split", rows[0])
            self.assertTrue(all(row[a] == "" for row in rows for a in tool.ASPECTS))

    def test_preparation_is_reproducible_and_refuses_overwrite(self):
        before = tool.digest(self.reviews)
        other = self.root / "other"
        tool.prepare(self.reviews, self.split, other)
        for path in self.workspace.glob("*.csv"):
            self.assertEqual(path.read_bytes(), (other / path.name).read_bytes())
        self.assertEqual(before, tool.digest(self.reviews))
        with self.assertRaises(FileExistsError):
            tool.prepare(self.reviews, self.split, self.workspace)

    def test_reject_wrong_split_sizes_unknown_ids_and_duplicates(self):
        rows = tool.read_csv(self.split, ["reviewId", "split"])
        rows[0]["split"] = "gold_train"
        overwrite_csv(self.split, ["reviewId", "split"], rows)
        with self.assertRaisesRegex(ValueError, "perlu 50"):
            tool.prepare(self.reviews, self.split, self.root / "wrong")
        rows[0]["split"] = "kalibrasi"
        rows[0]["reviewId"] = "TIDAK-ADA"
        overwrite_csv(self.split, ["reviewId", "split"], rows)
        with self.assertRaisesRegex(ValueError, "tidak ditemukan"):
            tool.prepare(self.reviews, self.split, self.root / "unknown")
        rows[0] = dict(rows[1])
        overwrite_csv(self.split, ["reviewId", "split"], rows)
        with self.assertRaisesRegex(ValueError, "duplikat"):
            tool.prepare(self.reviews, self.split, self.root / "duplicate")

    def test_blank_labels_never_become_gold(self):
        with self.assertRaisesRegex(ValueError, "label kosong"):
            tool.audit(self.workspace, "kalibrasi", self.root / "audit")
        self.assertFalse((self.root / "audit").exists())
        with self.assertRaisesRegex(ValueError, "label kosong"):
            tool.finalize(self.workspace, "gold", None, self.root / "final")
        self.assertFalse((self.root / "final").exists())

    def test_detects_missing_id_bad_annotator_text_mismatch_and_invalid_labels(self):
        self.fill_phase("kalibrasi")
        member = "bambang"
        key = self.manifest["assignments"]["kalibrasi"][member][0]
        self.change_row("kalibrasi", member, key, annotator="efraim")
        with self.assertRaisesRegex(ValueError, "nama anotator"):
            tool.load_phase(self.workspace, "kalibrasi")
        self.change_row("kalibrasi", member, key, annotator=member, text_llm="Teks tertukar")
        with self.assertRaisesRegex(ValueError, "teks/ID berubah"):
            tool.load_phase(self.workspace, "kalibrasi")
        self.change_row("kalibrasi", member, key, text_llm="Teks buatan untuk pengujian", akun_login="positve")
        with self.assertRaisesRegex(ValueError, "tidak valid"):
            tool.load_phase(self.workspace, "kalibrasi")
        self.change_row("kalibrasi", member, key, akun_login="negatif", umum="positif")
        with self.assertRaisesRegex(ValueError, "umum"):
            tool.load_phase(self.workspace, "kalibrasi")
        path = self.workspace / "kalibrasi_bambang.csv"
        rows = tool.read_csv(path, tool.SHEET_FIELDS)
        overwrite_csv(path, tool.SHEET_FIELDS, rows[1:])
        with self.assertRaisesRegex(ValueError, "ID hilang"):
            tool.load_phase(self.workspace, "kalibrasi")

    def test_gold_conflict_needs_third_annotator_and_export_has_no_text(self):
        self.fill_phase("gold")
        a, b = "bambang", "efraim"
        key = sorted(set(self.manifest["assignments"]["gold"][a]) & set(self.manifest["assignments"]["gold"][b]))[0]
        self.change_row("gold", a, key, akun_login="positif")
        report = tool.audit(self.workspace, "gold", self.root / "audit")
        self.assertEqual(report["conflict_cells"], 1)
        self.assertEqual(len(report["agreement"]), 6 * len(tool.ASPECTS))  # 6 pasangan anotator
        with self.assertRaisesRegex(ValueError, "belum diselesaikan"):
            tool.finalize(self.workspace, "gold", None, self.root / "final")
        decisions = self.root / "audit/resolutions.csv"
        rows = tool.read_csv(decisions, tool.RESOLUTION_FIELDS)
        rows[0].update(final_label="negatif", adjudicator=a, catatan="Alasan pengujian buatan")
        overwrite_csv(decisions, tool.RESOLUTION_FIELDS, rows)
        with self.assertRaisesRegex(ValueError, "anotator ketiga"):
            tool.finalize(self.workspace, "gold", decisions, self.root / "final")
        rows[0]["adjudicator"] = "jap"
        overwrite_csv(decisions, tool.RESOLUTION_FIELDS, rows)
        result = tool.finalize(self.workspace, "gold", decisions, self.root / "final")
        self.assertEqual(result["review_count"], 800)
        exported = tool.read_csv(self.root / "final/gold.csv", ["reviewId", *tool.ASPECTS])
        self.assertEqual(len(exported), 800)
        self.assertEqual(set(exported[0]), {"reviewId", *tool.ASPECTS})
        self.assertNotIn("Teks buatan", (self.root / "final/gold.csv").read_text(encoding="utf-8-sig"))
        self.assertEqual(result["kappa_stage"], "sebelum_adjudikasi")
        with self.assertRaises(FileExistsError):
            tool.finalize(self.workspace, "gold", decisions, self.root / "final")

    def test_stale_or_unexpected_resolution_is_rejected(self):
        self.fill_phase("kalibrasi")
        key = self.manifest["assignments"]["kalibrasi"]["bambang"][0]
        self.change_row("kalibrasi", "bambang", key, akun_login="positif")
        tool.audit(self.workspace, "kalibrasi", self.root / "audit")
        decisions = self.root / "audit/resolutions.csv"
        rows = tool.read_csv(decisions, tool.RESOLUTION_FIELDS)
        rows[0].update(final_label="negatif", adjudicator="jap", catatan="Kesepakatan buatan")
        overwrite_csv(decisions, tool.RESOLUTION_FIELDS, rows)
        self.change_row("kalibrasi", "efraim", key, akun_login="netral")
        with self.assertRaisesRegex(ValueError, "Label awal berubah"):
            tool.finalize(self.workspace, "kalibrasi", decisions, self.root / "final")
        rows[0]["reviewId"] = "ID-ASING"
        overwrite_csv(decisions, tool.RESOLUTION_FIELDS, rows)
        with self.assertRaisesRegex(ValueError, "tidak cocok"):
            tool.finalize(self.workspace, "kalibrasi", decisions, self.root / "final")

    def test_kappa_against_manually_computed_cases(self):
        self.assertAlmostEqual(tool.cohen_kappa(["a", "a", "b", "b"], ["a", "a", "a", "b"]), .5)
        self.assertEqual(tool.cohen_kappa(["a", "b"], ["a", "b"]), 1.)
        self.assertEqual(tool.cohen_kappa(["a", "b"], ["b", "a"]), -1.)
        self.assertEqual(tool.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]), 0.)
        self.assertIsNone(tool.cohen_kappa(["a", "a"], ["a", "a"]))
        with self.assertRaises(ValueError):
            tool.cohen_kappa([], [])


if __name__ == "__main__":
    unittest.main()
