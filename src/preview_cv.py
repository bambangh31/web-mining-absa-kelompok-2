"""Pratinjau: validasi silang 5-fold B1 pada lembar label manual, dibanding LLM.

Bukan hasil akhir penelitian. Dipakai selama label latih terverifikasi dan
set uji dua anotator belum selesai, untuk memeriksa pipeline dan melihat
gambaran awal per aspek pada label manusia yang sudah ada.

- Data: ulasan pada lembar manual (label per ulasan hasil agregasi).
- B1-LR/SVM/NB: 5-fold berstrata sederhana (seed 42). Di setiap fold,
  parameter dipilih dengan validasi silang dalam 3-fold pada data latih
  fold itu, lalu model dilatih ulang dan memprediksi fold uji. Prediksi
  out-of-fold digabung menjadi satu prediksi untuk semua ulasan.
- LLM: label LLM pada ulasan yang sama (tanpa pelatihan).

  python src/preview_cv.py --llm data/annotation_workspace/llm/gemini-3.5-flash-lite/manual_v1/llm_gemini-3.5-flash-lite_manual.csv
"""

import argparse
import json
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import label_excel  # noqa: E402
from src.absa_schema import ASPECTS  # noqa: E402
from src.evaluate import evaluate, load_labels, paired_bootstrap, write_tables  # noqa: E402
from src.model_data import read_csv_dict  # noqa: E402
from src.models_classic import GRID, fit_predict, to_rows  # noqa: E402
from src.text_features import LEXICON_PATH, b1_text, load_lexicon  # noqa: E402


def folds(ids, k, seed):
    ids = sorted(ids)
    random.Random(seed).shuffle(ids)
    return [ids[i::k] for i in range(k)]


def cross_predict(code, ids, texts, gold, k=5, inner=3, seed=42):
    from sklearn.feature_extraction.text import TfidfVectorizer

    def train_predict(train_ids, pred_ids, value):
        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")
        x_train = vec.fit_transform([texts[r] for r in train_ids])
        x_pred = vec.transform([texts[r] for r in pred_ids])
        y = {a: [gold[r][a] for r in train_ids] for a in ASPECTS}
        return to_rows(pred_ids, fit_predict(code, value, x_train, y, x_pred, seed))

    predictions, chosen = {}, []
    for test in folds(ids, k, seed):
        train = [r for r in ids if r not in set(test)]
        scores = []
        for value in GRID[code]:
            inner_pred = {}
            for inner_test in folds(train, inner, seed + 1):
                inner_train = [r for r in train if r not in set(inner_test)]
                inner_pred.update(train_predict(inner_train, inner_test, value))
            scores.append((evaluate(gold, inner_pred, train)["f1_pasangan"], -value, value))
        value = max(scores)[2]
        chosen.append(value)
        predictions.update(train_predict(train, test, value))
    return predictions, chosen


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manual", type=Path, default=Path("Label Manual Sentimen Komentar Satu Sehat.xlsx"))
    parser.add_argument("--llm", type=Path, required=True, help="label LLM per ulasan untuk ulasan yang sama")
    parser.add_argument("--llm-name", default="B3-Gemini")
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--lexicon", type=Path, default=LEXICON_PATH)
    parser.add_argument("--out", type=Path, default=Path("results/pratinjau"))
    args = parser.parse_args()
    reviews, mentions = label_excel.read_mentions(args.manual)
    gold = label_excel.review_labels(reviews, mentions)
    clean = read_csv_dict(args.clean)
    lexicon = load_lexicon(args.lexicon)
    ids = sorted(gold)
    texts = {r: b1_text(clean[r]["text_model"], lexicon) for r in ids}
    preds, config = {}, {}
    for code in ("B1-LR", "B1-SVM", "B1-NB"):
        preds[code], chosen = cross_predict(code, ids, texts, gold)
        config[code] = {"param": "alpha" if code == "B1-NB" else "C", "terpilih_per_fold": chosen}
    preds[args.llm_name] = load_labels(args.llm)
    results = {name: evaluate(gold, pred, ids) for name, pred in preds.items()}
    write_tables(args.out, results)
    report = {"jenis": "pratinjau validasi silang 5-fold pada lembar manual; bukan hasil set uji",
              "n_ulasan": len(ids), "acuan": str(args.manual), "llm": str(args.llm), "konfigurasi": config,
              "hasil": results, "bootstrap": paired_bootstrap(gold, preds, ids)}
    (args.out / "metrik.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print((args.out / "tabel.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
