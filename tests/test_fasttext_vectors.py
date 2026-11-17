import gzip
import tempfile
import unittest
from pathlib import Path

from src.fasttext_vectors import extract_subset


class FastTextTests(unittest.TestCase):
    def test_extracts_only_requested_words_and_records_source_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp)/"tiny.gz", Path(tmp)/"subset.vec"
            with gzip.open(source, "wt", encoding="utf-8") as f:
                f.write("3 2\nlogin 0.1 0.2\nuji 0.5 0.6\nberhasil 0.3 0.4\n")
            meta = extract_subset(source, target, {"login", "berhasil", "hilang"}, dim=2)
            self.assertEqual(meta["n_matched"], 2)
            self.assertAlmostEqual(meta["coverage"], 2/3)
            self.assertEqual(len(meta["archive_sha256"]), 64)
            self.assertNotIn("uji", target.read_text())
            self.assertTrue(target.read_text().startswith("2 2\n"))

    def test_truncated_source_does_not_replace_existing_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp)/"tiny.gz", Path(tmp)/"subset.vec"
            target.write_text("existing")
            with gzip.open(source, "wt", encoding="utf-8") as f:
                f.write("3 2\nlogin 0.1 0.2\n")
            with self.assertRaisesRegex(ValueError, "tidak lengkap"):
                extract_subset(source, target, {"login"}, dim=2)
            self.assertEqual(target.read_text(), "existing")

    def test_nonfinite_vector_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp)/"tiny.gz", Path(tmp)/"subset.vec"
            with gzip.open(source, "wt", encoding="utf-8") as f:
                f.write("1 2\nlogin nan 0.2\n")
            with self.assertRaisesRegex(ValueError, "tidak valid"):
                extract_subset(source, target, {"login"}, dim=2)
            self.assertFalse(target.exists())
