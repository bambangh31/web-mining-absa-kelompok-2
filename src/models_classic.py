"""B1: TF-IDF + Logistic Regression / Linear SVM / Multinomial Naive Bayes.

Satu classifier empat kelas per aspek (multi-aspek: delapan classifier per
model). Masukan `text_model` + normalisasi slang (aturan 12). Fitur TF-IDF
kata 1-2 gram, `sublinear_tf`. LR dan SVM memakai `class_weight="balanced"`.
Parameter regularisasi dipilih dengan F1 pasangan pada set validasi:
C dari {0,1; 1; 10} (LR, SVM) dan alpha dari {0,1; 0,5; 1} (NB).

Contoh (setelah verified.csv tersedia):

  python src/models_classic.py --labels data/annotations/verified.csv --predict-split gold_test
"""

import argparse
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECTS, NONE  # noqa: E402
from src.model_data import (Dataset, enforce_umum, prediction_ids, val_score,  # noqa: E402
                            write_predictions, write_run)
from src.text_features import LEXICON_PATH, b1_text, load_lexicon  # noqa: E402

GRID = {"B1-LR": [0.1, 1.0, 10.0], "B1-SVM": [0.1, 1.0, 10.0], "B1-NB": [0.1, 0.5, 1.0]}


def make_classifier(code, value, seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import LinearSVC

    if code == "B1-LR":
        return LogisticRegression(C=value, class_weight="balanced", max_iter=5000, random_state=seed)
    if code == "B1-SVM":
        return LinearSVC(C=value, class_weight="balanced", random_state=seed)
    if code == "B1-NB":
        return MultinomialNB(alpha=value)
    raise ValueError(code)


class Constant:
    """Dipakai bila suatu aspek hanya punya satu label di data latih."""

    def __init__(self, label):
        self.label = label

    def predict(self, x):
        return [self.label] * x.shape[0]


def fit_predict(code, value, x_train, labels_train, x_pred, seed=42):
    out = {}
    for a in ASPECTS:
        y = labels_train[a]
        model = Constant(y[0]) if len(set(y)) < 2 else make_classifier(code, value, seed).fit(x_train, y)
        out[a] = list(model.predict(x_pred))
    return out


def to_rows(ids, columns):
    return {rid: enforce_umum({a: columns[a][i] for a in ASPECTS}) for i, rid in enumerate(ids)}


def run(code, dataset, lexicon, predict_ids, seed=42):
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = {rid: b1_text(dataset.text(rid), lexicon)
             for rid in set(dataset.train_ids) | set(dataset.val_ids) | set(predict_ids)}
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")
    x_train = vectorizer.fit_transform([texts[r] for r in dataset.train_ids])
    x_val = vectorizer.transform([texts[r] for r in dataset.val_ids])
    y_train = {a: dataset.y(dataset.train_ids, a) for a in ASPECTS}
    search = []
    for value in GRID[code]:
        pred = to_rows(dataset.val_ids, fit_predict(code, value, x_train, y_train, x_val, seed))
        search.append((val_score(dataset, pred)["f1_pasangan"], value, pred))
    best_f1, best_value, best_val_pred = max(search, key=lambda t: (t[0], -t[1]))
    x_pred = vectorizer.transform([texts[r] for r in predict_ids])
    began = time.perf_counter()
    predictions = to_rows(predict_ids, fit_predict(code, best_value, x_train, y_train, x_pred, seed))
    seconds = (time.perf_counter() - began) / max(len(predict_ids), 1) * 1000
    config = {"param": "alpha" if code == "B1-NB" else "C", "nilai_terpilih": best_value,
              "pencarian": [{"nilai": v, "f1_pasangan_validasi": f} for f, v, _ in search],
              "fitur_tfidf": len(vectorizer.vocabulary_), "masukan": "text_model + normalisasi slang",
              "label_latih": dataset.labels_path, "n_latih": len(dataset.train_ids), "n_validasi": len(dataset.val_ids)}
    return predictions, config, val_score(dataset, best_val_pred), seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", default="B1-LR,B1-SVM,B1-NB")
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--labels", type=Path, required=True, help="label latih+validasi (verified.csv)")
    parser.add_argument("--lexicon", type=Path, default=LEXICON_PATH)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--predict-split")
    group.add_argument("--predict-from", type=Path, help="prediksi ulasan pada file label/Excel ini")
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    dataset = Dataset(args.clean, args.split, args.labels)
    lexicon = load_lexicon(args.lexicon)
    ids = prediction_ids(dataset, args.predict_split, args.predict_from)
    for code in args.models.split(","):
        predictions, config, val_metrics, seconds = run(code, dataset, lexicon, ids, args.seed)
        write_predictions(args.out / "predictions" / f"{code}_{args.seed}.csv", code, args.seed, predictions)
        write_run(args.out / "metrics", code, args.seed, config, val_metrics, seconds)
        print(f"{code}: {config['param']}={config['nilai_terpilih']}, F1 pasangan validasi "
              f"{val_metrics['f1_pasangan']:.3f}, {len(ids)} ulasan diprediksi")


if __name__ == "__main__":
    main()
