"""Regresi kebocoran kosakata, perangkat, dan vektor B4."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.absa_schema import ASPECTS, NONE
from src.model_bilstm import build_vocab, encode, train_one


class VocabularyTests(unittest.TestCase):
    def test_unseen_word_uses_unk_even_if_pretrained(self):
        vocab = build_vocab(["login berhasil"])
        index = {word: i for i, word in enumerate(vocab)}
        self.assertEqual(encode("kata_baru", index, set(vocab[2:])), [1, 1, 1])
        self.assertNotIn("baru", vocab)


@unittest.skipUnless(importlib.util.find_spec("torch"), "torch belum terpasang")
class TrainingTests(unittest.TestCase):
    def dataset(self, heldout):
        texts = {"t1": "login berhasil", "t2": "login gagal", "t3": "login berhasil",
                 "t4": "login gagal", "v": heldout, "u": heldout}
        labels = {rid: dict.fromkeys(ASPECTS, NONE) for rid in texts}
        for rid in texts:
            labels[rid]["akun_login"] = "positif" if rid in ("t1", "t3") else "negatif"
        return SimpleNamespace(train_ids=["t1", "t2", "t3", "t4"], val_ids=["v"],
                               labels=labels, labels_path="synthetic", text=texts.__getitem__)

    def test_heldout_text_does_not_expand_vocabulary_and_training_is_finite(self):
        import torch
        torch.set_num_threads(1)
        with tempfile.TemporaryDirectory() as tmp:
            vectors = Path(tmp) / "tiny.vec"
            vectors.write_text("3 300\n" + "\n".join(
                w + " " + " ".join([str(v)] * 300)
                for w, v in [("login", .1), ("berhasil", .2), ("gagal", -.1)]), encoding="utf-8")
            configs = []
            for heldout in ["unikvalidasi", "kata ujiyangberbeda"]:
                pred, config, val, _ = train_one(self.dataset(heldout), 42, ["u"], vectors,
                                                max_epochs=2, log=lambda *_: None)
                configs.append(config)
                self.assertEqual(set(pred), {"u"})
                self.assertEqual(config["kosakata"], 3)
                self.assertEqual(config["vocab_source"], "train_only")
                self.assertEqual(config["cakupan_fasttext"], 1)
                self.assertEqual(config["device"], "cpu")
                self.assertTrue(0 <= val["f1_pasangan"] <= 1)
            self.assertEqual(configs[0]["vocab_sha256"], configs[1]["vocab_sha256"])

    def test_missing_cuda_fails_without_cpu_fallback(self):
        with patch("torch.cuda.is_available", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "CUDA tidak tersedia"):
                train_one(self.dataset("uji"), 42, ["u"], None, device="cuda")

    def test_wrong_vectors_fail_instead_of_zero_embeddings(self):
        with tempfile.TemporaryDirectory() as tmp:
            vectors = Path(tmp) / "wrong.vec"
            vectors.write_text("1 300\nasingle " + " ".join(["0.1"] * 300), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Tidak ada vektor"):
                train_one(self.dataset("uji"), 42, ["u"], vectors)
