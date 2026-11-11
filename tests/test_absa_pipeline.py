"""Uji pipeline ABSA dengan data BUATAN: skema, Excel, LLM (tiruan), metrik, model."""

import csv
import json
import os
import random
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import absa_schema as schema
from src import evaluate as ev
from src import label_excel
from src import llm_label
from src import text_features as tf

NONE = schema.NONE


def labels(**given):
    row = schema.empty_labels()
    row.update(given)
    return row


class SchemaTests(unittest.TestCase):
    def test_eight_aspects_umum_last(self):
        self.assertEqual(len(schema.ASPECTS), 8)
        self.assertEqual(schema.ASPECTS[-1], "umum")
        self.assertIn("pembaruan_aplikasi", schema.SPECIFIC)
        self.assertIn("layanan_pelanggan", schema.SPECIFIC)
        self.assertTrue(all("_" not in n for n in schema.ASPECT_NAMES.values()))

    def test_aggregate_rules(self):
        row = schema.aggregate_mentions([
            ("akun login", "negatif"), ("akun_login", "negatif"),
            ("performa", "positif"), ("performa", "negatif"),       # seri -> negatif
            ("fitur kesehatan", "positif"), ("fitur kesehatan", "netral"),
            ("kemudahan penggunaan", "netral"),
            ("umum", "positif")])                                  # ada aspek khusus -> umum kosong
        self.assertEqual(row["akun_login"], "negatif")
        self.assertEqual(row["performa"], "negatif")
        self.assertEqual(row["fitur_kesehatan"], "positif")
        self.assertEqual(row["kemudahan_penggunaan"], "netral")
        self.assertEqual(row["umum"], NONE)
        self.assertEqual(schema.aggregate_mentions([("umum", "positif")])["umum"], "positif")
        self.assertEqual(schema.aggregate_mentions([]), schema.empty_labels())

    def test_names_and_validation(self):
        self.assertEqual(schema.aspect_from_name("Pembaruan Aplikasi"), "pembaruan_aplikasi")
        self.assertEqual(schema.label_from_name("tidak disebut"), NONE)
        with self.assertRaises(ValueError):
            schema.aspect_from_name("harga")
        with self.assertRaisesRegex(ValueError, "umum"):
            schema.validate_labels({"reviewId": "x", **labels(performa="negatif", umum="negatif")})


class TextFeatureTests(unittest.TestCase):
    def test_tokenize_and_slang(self):
        self.assertEqual(tf.tokenize("gak bisa login!! [nik] ok"), ["gak", "bisa", "login", "!", "!", "[nik]", "ok"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lex.csv"
            path.write_text("slang,formal\nyg,yang\ngak,enggak\nudh,sudah\nudh,udah\nudh,sudah\n", encoding="utf-8")
            lexicon = tf.load_lexicon(path)
        self.assertEqual(lexicon["gak"], "tidak")          # negasi disatukan
        self.assertEqual(lexicon["udh"], "sudah")          # bentuk paling sering
        self.assertEqual(tf.b1_text("udh login yg gak bisa", lexicon), "sudah login yang tidak bisa")
        self.assertEqual(tf.normalize_slang("terdaftar tidak", lexicon), "terdaftar tidak")  # tanpa stemming

    def test_missing_lexicon_has_instructions(self):
        with self.assertRaisesRegex(FileNotFoundError, "curl"):
            tf.load_lexicon(Path("tidak/ada.csv"))


class ExcelTests(unittest.TestCase):
    def test_roundtrip_and_raw_check(self):
        reviews = {
            "id-1": {"No": 1, "reviewId": "id-1", "Tanggal": "2024-01-01 10:00:00", "Versi Aplikasi": "5.0.0",
                     "Rating": 1, "Komentar": "Setelah update gak bisa login, ANJ"},
            "id-2": {"No": 2, "reviewId": "id-2", "Tanggal": "2024-01-02 10:00:00", "Versi Aplikasi": "",
                     "Rating": 5, "Komentar": "aplikasi bagus"},
        }
        mentions = [
            {"reviewId": "id-1", "kata": "login", "seragam": "login", "aspek": "akun_login", "label": "negatif",
             "bukti": "gak bisa login"},
            {"reviewId": "id-1", "kata": "update", "seragam": "update", "aspek": "pembaruan_aplikasi",
             "label": "negatif", "bukti": "Setelah update"},
            {"reviewId": "id-2", "kata": "aplikasi", "seragam": "aplikasi", "aspek": "umum", "label": "positif",
             "bukti": "aplikasi bagus"},
        ]
        raw = {rid: {"content": r["Komentar"], "reviewCreatedVersion": r["Versi Aplikasi"],
                     "score": str(r["Rating"]), "at": r["Tanggal"]} for rid, r in reviews.items()}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lembar.xlsx"
            label_excel.write_mentions(path, reviews, mentions)
            got_reviews, got_mentions = label_excel.read_mentions(path)
            import openpyxl
            headers = [c.value for ws in openpyxl.load_workbook(path) for c in ws[1]]
        self.assertTrue(all("_" not in str(h) for h in headers))
        self.assertEqual(got_reviews["id-1"]["Komentar"], reviews["id-1"]["Komentar"])  # kata kasar tetap
        self.assertEqual(label_excel.check_against_raw(got_reviews, got_mentions, raw), [])
        lab = label_excel.review_labels(got_reviews, got_mentions)
        self.assertEqual(lab["id-1"], labels(akun_login="negatif", pembaruan_aplikasi="negatif"))
        self.assertEqual(lab["id-2"], labels(umum="positif"))
        raw["id-2"]["content"] = "aplikasi bagus!"
        self.assertTrue(label_excel.check_against_raw(got_reviews, got_mentions, raw))


class LlmTests(unittest.TestCase):
    def test_few_shot_examples_are_exact(self):
        for text, mentions in llm_label.FEW_SHOT:
            for kata, _, kategori, label, bukti in mentions:
                self.assertIn(kata, text)
                self.assertIn(bukti, text)
                self.assertIn(kategori, llm_label.CATEGORY_NAMES)
        self.assertIn("pembaruan aplikasi", llm_label.system_prompt())

    def test_locate_and_clean(self):
        original = "Udah   di update\ntapi GAK bisa dibuka"
        self.assertEqual(llm_label.locate("di update tapi", original), "di update\ntapi")
        self.assertEqual(llm_label.locate("gak bisa", original), "GAK bisa")
        mentions, issues = llm_label.clean_mentions("x", [
            {"kata": "update", "seragam": "update", "kategori": "pembaruan aplikasi", "label": "negatif",
             "bukti": "Udah di update; tidak ada"},
            {"kata": "harga", "seragam": "harga", "kategori": "harga", "label": "negatif", "bukti": ""}], original)
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["bukti"], "Udah   di update")
        self.assertEqual(len(issues), 2)

    def test_batches_resume_and_retry(self):
        calls = []

        def fake(model, system, user, temperature, api_key, timeout=300):
            calls.append(user)
            if len(calls) == 1:
                return "{bukan json", {}
            ids = [line.split(":")[0] for line in user.splitlines() if line.startswith("r")]
            out = [{"id": i, "aspek": [{"kata": "login", "seragam": "login", "kategori": "akun login",
                                        "label": "negatif", "bukti": "gak bisa login"}]} for i in ids]
            return json.dumps({"hasil": out}), {"usage": None}

        items = [(f"id-{i}", "gak bisa login") for i in range(5)]
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(llm_label, "call_gemini", fake), \
                mock.patch.dict(os.environ, {"GEMINI_API_KEY": "uji"}), mock.patch.object(llm_label.time, "sleep"):
            result = llm_label.label_reviews(items, None, "gemini", "m", Path(tmp), batch_size=2, log=lambda *_: 0)
            self.assertEqual(len(result), 5)
            before = len(calls)
            llm_label.label_reviews(items, None, "gemini", "m", Path(tmp), batch_size=2, log=lambda *_: 0)
            self.assertEqual(len(calls), before)     # dilanjutkan dari raw.jsonl, tidak dikirim ulang
        self.assertEqual(before, 4)                  # 3 batch + 1 percobaan ulang


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.gold = {"a": labels(akun_login="negatif", performa="negatif"),
                     "b": labels(umum="positif"),
                     "c": labels(fitur_kesehatan="positif")}
        self.pred = {"a": labels(akun_login="negatif", performa="positif"),
                     "b": labels(umum="positif"),
                     "c": labels(fitur_kesehatan="positif", pembaruan_aplikasi="negatif")}

    def test_pair_f1_by_hand(self):
        result = ev.evaluate(self.gold, self.pred)
        # gold 4 pasangan, pred 5, benar 3 -> P 0,6, R 0,75, F1 0,6667
        self.assertAlmostEqual(result["f1_pasangan"], 2 * 0.6 * 0.75 / 1.35)
        # deteksi: gold 4, pred 5, benar 4 -> F1 0,8889
        self.assertAlmostEqual(result["f1_deteksi_micro"], 2 * 0.8 * 1.0 / 1.8)
        self.assertEqual(result["per_aspek"]["performa"]["macro_f1_sentimen"], 0.0)
        self.assertEqual(result["per_aspek"]["akun_login"]["macro_f1_sentimen"], 1.0)
        self.assertAlmostEqual(result["ulasan_persis_sama"], 1 / 3)

    def test_kappa_and_bootstrap(self):
        self.assertIsNone(ev.cohen_kappa(["a", "a"], ["a", "a"]))
        self.assertAlmostEqual(ev.cohen_kappa(["a", "b", "a", "b"], ["a", "b", "b", "b"]), 0.5)
        boot = ev.paired_bootstrap(self.gold, {"baik": self.gold, "kurang": self.pred}, list(self.gold), n=200)
        self.assertEqual(boot["model_teratas"], "baik")
        self.assertEqual(boot, ev.paired_bootstrap(self.gold, {"baik": self.gold, "kurang": self.pred},
                                                   list(self.gold), n=200))


def synthetic_project(root, n_reviews=850):
    """Data buatan dengan pola kata kunci yang bisa dipelajari model."""
    rng = random.Random(7)
    templates = [
        ("gak bisa login terus", labels(akun_login="negatif")),
        ("setelah update tidak bisa dibuka", labels(pembaruan_aplikasi="negatif", performa="negatif")),
        ("sertifikat vaksin tidak muncul", labels(fitur_kesehatan="negatif")),
        ("aplikasi bagus sekali", labels(umum="positif")),
        ("cs cepat membalas email", labels(layanan_pelanggan="positif")),
        ("tampilan ribet dan bingung", labels(kemudahan_penggunaan="negatif")),
        ("daftar nik sudah terdaftar", labels(registrasi_data="negatif")),
    ]
    clean, split, lab = [], [], {}
    names = ["kalibrasi"] * 50 + ["gold_train"] * 400 + ["gold_val"] * 100 + ["gold_test"] * 300
    names += ["silver"] * (n_reviews - len(names))
    for i in range(n_reviews):
        text, row = templates[i % len(templates)]
        rid = f"id-{i:04}"
        text = f"{text} kode{rng.randint(0, 999)}"
        clean.append({"reviewId": rid, "at": "2024-01-01 00:00:00", "score": "1", "reviewCreatedVersion": "1.0",
                      "text_llm": text, "text_model": text, "n_words": 5, "in_pool": 1})
        split.append({"reviewId": rid, "split": names[i]})
        lab[rid] = row
    paths = {k: Path(root) / f"{k}.csv" for k in ("clean", "split", "labels", "raw")}
    for key, rows in (("clean", clean), ("split", split)):
        with paths[key].open("w", encoding="utf-8", newline="") as stream:
            w = csv.DictWriter(stream, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    with paths["raw"].open("w", encoding="utf-8", newline="") as stream:
        w = csv.DictWriter(stream, fieldnames=["reviewId", "at", "score", "content", "reviewCreatedVersion"])
        w.writeheader()
        for r in clean:
            w.writerow({"reviewId": r["reviewId"], "at": r["at"], "score": r["score"], "content": r["text_llm"],
                        "reviewCreatedVersion": "1.0"})
    label_excel.write_label_csv(paths["labels"], lab, {"model": "uji", "prompt_version": "v1"})
    return paths, lab


class ModelTests(unittest.TestCase):
    @unittest.skipUnless(__import__("importlib").util.find_spec("sklearn"), "scikit-learn belum terpasang")
    def test_classic_models_learn_keywords(self):
        from src import models_classic
        from src.model_data import Dataset
        with tempfile.TemporaryDirectory() as tmp:
            paths, gold = synthetic_project(tmp)
            dataset = Dataset(paths["clean"], paths["split"], paths["labels"])
            test_ids = sorted(r for r, s in dataset.split.items() if s == "gold_test")
            for code in ("B1-LR", "B1-SVM", "B1-NB"):
                pred, config, val, _ = models_classic.run(code, dataset, {"gak": "tidak"}, test_ids)
                self.assertEqual(set(pred), set(test_ids))
                self.assertGreater(ev.evaluate(gold, pred, test_ids)["f1_pasangan"], 0.95, code)
                self.assertTrue(all(r["umum"] == NONE or not any(r[a] != NONE for a in schema.SPECIFIC)
                                    for r in pred.values()))

    @unittest.skipUnless(__import__("importlib").util.find_spec("torch"), "torch belum terpasang")
    def test_bilstm_smoke_without_vectors(self):
        from src import model_bilstm
        from src.model_data import Dataset
        with tempfile.TemporaryDirectory() as tmp:
            paths, _ = synthetic_project(tmp)
            dataset = Dataset(paths["clean"], paths["split"], paths["labels"])
            ids = sorted(r for r, s in dataset.split.items() if s == "gold_test")[:20]
            pred, config, val, _ = model_bilstm.train_one(dataset, 42, ids, None, max_epochs=2, log=lambda *_: 0)
        self.assertEqual(len(pred), 20)
        self.assertIn("TANPA fastText", config["catatan"])


class VerificationTests(unittest.TestCase):
    @unittest.skipUnless(__import__("importlib").util.find_spec("openpyxl"), "openpyxl belum terpasang")
    def test_two_step_sheet_and_export(self):
        import openpyxl
        from src import verification
        with tempfile.TemporaryDirectory() as tmp:
            paths, gold = synthetic_project(tmp)
            llm = {rid: dict(row) for rid, row in gold.items()}
            first = sorted(r for r in llm)[60]
            label_excel.write_label_csv(Path(tmp) / "llm.csv", llm, {"model": "uji", "prompt_version": "v1"})
            ws_dir = Path(tmp) / "ver"
            counts = verification.prepare(Path(tmp) / "llm.csv", paths["split"], paths["raw"], None, ws_dir)
            self.assertEqual(counts, {"bambang": 125, "efraim": 125, "jap": 125, "geraldyn": 125})
            target = None
            for member in counts:
                path = ws_dir / f"verifikasi_{member}.xlsx"
                wb = openpyxl.load_workbook(path)
                header = [c.value for c in wb["Verifikasi"][1]]
                self.assertTrue(all("_" not in h for h in header))
                self.assertNotIn("gold_test", {r[2] for r in wb["Verifikasi"].iter_rows(min_row=2, values_only=True)})
                wb["Info"]["B4"], wb["Info"]["B5"] = "2026-11-12 09:00", "2026-11-12 10:15"
                ws = wb["Verifikasi"]
                for r in range(2, ws.max_row + 1):
                    for k in range(len(schema.ASPECTS)):
                        ws.cell(r, 7 + 3 * k, "setuju")
                    if target is None and llm[ws.cell(r, 2).value]["umum"] == NONE:
                        target = ws.cell(r, 2).value
                        aspect = schema.ASPECTS.index("akun_login")
                        old = llm[target]["akun_login"]
                        ws.cell(r, 7 + 3 * aspect, "salah")
                        ws.cell(r, 8 + 3 * aspect, "netral" if old != "netral" else "positif")
                wb.save(path)
            out = Path(tmp) / "verified.csv"
            summary = verification.export(Path(tmp) / "llm.csv", paths["split"], paths["raw"], ws_dir, out,
                                          Path(tmp) / "ringkasan.json")
            verified = label_excel.read_label_csv(out)
        self.assertEqual(len(verified), 500)
        self.assertNotEqual(verified[target]["akun_login"], llm[target]["akun_login"])
        self.assertAlmostEqual(summary["tingkat_koreksi_keseluruhan"], 1 / (500 * len(schema.ASPECTS)))
        self.assertAlmostEqual(summary["ulasan_diterima_utuh"], 499 / 500)
        self.assertAlmostEqual(summary["detik_per_ulasan"], 4 * 75 * 60 / 500)
        self.assertNotEqual(first, None)

    @unittest.skipUnless(__import__("importlib").util.find_spec("openpyxl"), "openpyxl belum terpasang")
    def test_single_verifier_fills_rest_with_llm(self):
        import csv
        import openpyxl
        from src import verification
        with tempfile.TemporaryDirectory() as tmp:
            paths, gold = synthetic_project(tmp)
            llm = {rid: dict(row) for rid, row in gold.items()}
            label_excel.write_label_csv(Path(tmp) / "llm.csv", llm, {"model": "uji", "prompt_version": "v1"})
            ws_dir = Path(tmp) / "ver"
            verification.prepare(Path(tmp) / "llm.csv", paths["split"], paths["raw"], None, ws_dir)
            path = ws_dir / "verifikasi_jap.xlsx"
            wb = openpyxl.load_workbook(path)
            ws = wb["Verifikasi"]
            for r in range(2, ws.max_row + 1):
                for k in range(len(schema.ASPECTS)):
                    ws.cell(r, 7 + 3 * k, "setuju")
            wb.save(path)
            out = Path(tmp) / "verified.csv"
            with self.assertRaises(SystemExit):  # sebagian lembar tanpa izin eksplisit ditolak
                verification.export(Path(tmp) / "llm.csv", paths["split"], paths["raw"], ws_dir, out,
                                    Path(tmp) / "r.json", members=("jap",))
            summary = verification.export(Path(tmp) / "llm.csv", paths["split"], paths["raw"], ws_dir, out,
                                          Path(tmp) / "r.json", members=("jap",), fill_unverified=True)
            with out.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 500)
        self.assertEqual(sum(r["verifier"] == "jap" for r in rows), 125)
        self.assertEqual(sum(r["verifier"] == "" for r in rows), 375)
        self.assertEqual(summary["ulasan"], 125)
        self.assertEqual(summary["tingkat_koreksi_keseluruhan"], 0)
        self.assertIsNone(summary["detik_per_ulasan"])


class SingleAnnotatorTests(unittest.TestCase):
    def test_compare_counts_agreement_and_kappa(self):
        from src.single_annotator import compare
        base = {a: NONE for a in schema.ASPECTS}
        left = {"a": {**base, "performa": "negatif"}, "b": {**base, "umum": "positif"}}
        right = {"a": {**base, "performa": "negatif"}, "b": {**base, "umum": "netral"}}
        result = compare(left, right, ["a", "b"])
        self.assertAlmostEqual(result["agreement_sel"], 15 / 16)
        self.assertAlmostEqual(result["ulasan_persis_sama"], 0.5)
        self.assertEqual(result["per_aspek"]["performa"]["kappa"], 1.0)
        self.assertEqual(result["beda_terbanyak"], {"umum: positif -> netral": 1})


if __name__ == "__main__":
    unittest.main()


class CompareTests(unittest.TestCase):
    @unittest.skipUnless(__import__("importlib").util.find_spec("openpyxl"), "openpyxl belum terpasang")
    def test_manual_vs_llm_sheet(self):
        from src import compare_labels
        reviews = {f"id-{i}": {"No": i, "reviewId": f"id-{i}", "Tanggal": "2024-01-01 00:00:00",
                               "Versi Aplikasi": "", "Rating": 1, "Komentar": "gak bisa login, update terus"}
                   for i in range(3)}
        manual = [{"reviewId": f"id-{i}", "kata": "login", "seragam": "login", "aspek": "akun_login",
                   "label": "negatif", "bukti": "gak bisa login"} for i in range(3)]
        llm = manual[:2] + [{"reviewId": "id-2", "kata": "update", "seragam": "update", "aspek": "pembaruan_aplikasi",
                             "label": "negatif", "bukti": "update terus"}]
        overlap = compare_labels.mention_overlap(manual, llm)
        self.assertEqual(overlap["kategori_dan_label"]["sama"], 2)
        gold = label_excel.review_labels(reviews, manual)
        pred = label_excel.review_labels(reviews, llm)
        result = ev.evaluate(gold, pred)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "banding.xlsx"
            compare_labels.write_excel(path, reviews, gold, pred, result, overlap)
            import openpyxl
            wb = openpyxl.load_workbook(path)
            self.assertEqual(wb.sheetnames, ["Ringkasan", "Per Ulasan", "Daftar Beda"])
            kinds = [r[6] for r in wb["Daftar Beda"].iter_rows(min_row=2, values_only=True)]
        self.assertEqual(sorted(kinds), ["LLM melewatkan aspek", "LLM menambah aspek"])
