"""Metrik ABSA multi-aspek, keseluruhan dan per aspek, untuk setiap model.

Definisi mengikuti docs/project/method-decisions.md#definisi-metrik:

- F1 pasangan (utama): micro-F1 atas tuple (ulasan, aspek, sentimen) yang
  labelnya bukan `tidak_disebut`. Benar jika aspek dan sentimen sama.
- F1 deteksi aspek: micro- dan macro-F1 atas pasangan (ulasan, aspek) yang
  disebut, tanpa melihat sentimen.
- Macro-F1 sentimen per aspek: pada ulasan yang aspeknya disebut di label
  acuan; kelas positif/negatif/netral yang muncul di acuan. Prediksi
  `tidak_disebut` pada ulasan itu dihitung salah.
- Cohen's kappa per aspek atas empat label.

Contoh:

  python src/evaluate.py --gold data/annotations/final_v1/gold.csv \
      --pred B1-LR=results/predictions/B1-LR_42.csv --pred B3-Gemini=data/annotations/llm_gemini-3.5-flash.csv \
      --ids-split gold_test --out results/metrics/uji
"""

import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECT_TITLES, ASPECTS, LABELS, NONE, POLAR  # noqa: E402


def confusion_matrix(gold, pred):
    """Baris = acuan, kolom = prediksi, urutan LABELS tetap (empat label)."""
    if len(gold) != len(pred):
        raise ValueError("Jumlah label acuan dan prediksi harus sama")
    matrix = [[0 for _ in LABELS] for _ in LABELS]
    for actual, predicted in zip(gold, pred):
        matrix[LABELS.index(actual)][LABELS.index(predicted)] += 1
    return matrix


def write_confusion_matrices(out_dir, results):
    """CSV seluruh matriks dan satu gambar delapan panel per model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = Path(out_dir) / "confusion_matrix"
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = [label.replace("_", " ") for label in LABELS]
    with (out_dir / "matriks.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Model", "Aspek", "Acuan", "Prediksi", "Jumlah"])
        for number, (model, result) in enumerate(results.items(), 1):
            fig, axes = plt.subplots(2, 4, figsize=(15, 8), layout="constrained")
            for axis, aspect in zip(axes.flat, ASPECTS):
                matrix = result["per_aspek"][aspect]["confusion_matrix"]
                for i, actual in enumerate(LABELS):
                    for j, predicted in enumerate(LABELS):
                        writer.writerow([model, aspect, actual, predicted, matrix[i][j]])
                axis.imshow(matrix, cmap="Greys", vmin=0, vmax=result["n_ulasan"])
                for i in range(len(LABELS)):
                    for j in range(len(LABELS)):
                        axis.text(j, i, str(matrix[i][j]), ha="center", va="center",
                                  color="white" if matrix[i][j] > result["n_ulasan"] / 2 else "black")
                axis.set_xticks(range(len(LABELS)), labels, rotation=40, ha="right", fontsize=8)
                axis.set_yticks(range(len(LABELS)), labels, fontsize=8)
                axis.set_title(ASPECT_TITLES[aspect], fontsize=11)
                axis.set_xlabel("Prediksi")
                axis.set_ylabel("Acuan manual")
            fig.suptitle(f"{model} | {result['n_ulasan']} ulasan uji | jumlah absolut", fontsize=14)
            fig.savefig(out_dir / f"model_{number:02}.png", dpi=180)
            plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(9, 9), layout="constrained", squeeze=False)
    if len(results) == 4:
        for axis, (model, result) in zip(axes.flat, results.items()):
            matrix = result["confusion_matrix_gabungan"]
            axis.imshow(matrix, cmap="Greys", vmin=0, vmax=result["n_ulasan"] * len(ASPECTS))
            for i in range(len(LABELS)):
                for j in range(len(LABELS)):
                    axis.text(j, i, str(matrix[i][j]), ha="center", va="center",
                              color="white" if matrix[i][j] > result["n_ulasan"] * len(ASPECTS) / 2 else "black")
            axis.set_xticks(range(len(LABELS)), labels, rotation=30, ha="right", fontsize=10)
            axis.set_yticks(range(len(LABELS)), labels, fontsize=10)
            axis.set_title(model)
            axis.set_xlabel("Prediksi")
            axis.set_ylabel("Acuan manual")
        fig.savefig(out_dir / "gabungan.png", dpi=200)
    plt.close(fig)


def prf(tp, n_pred, n_gold):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gold if n_gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def cohen_kappa(left, right):
    n = len(left)
    if not n:
        return None
    a, b = Counter(left), Counter(right)
    observed = sum(x == y for x, y in zip(left, right)) / n
    expected = sum(a[k] * b[k] for k in set(a) | set(b)) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def macro_f1(gold, pred, classes):
    scores = []
    for c in classes:
        tp = sum(g == c and p == c for g, p in zip(gold, pred))
        scores.append(prf(tp, sum(p == c for p in pred), sum(g == c for g in gold))[2])
    return sum(scores) / len(scores) if scores else None


def pair_counts(gold, pred, ids, aspects=ASPECTS):
    tp = n_pred = n_gold = 0
    for rid in ids:
        for a in aspects:
            g, p = gold[rid][a], pred[rid][a]
            n_gold += g != NONE
            n_pred += p != NONE
            tp += g != NONE and g == p
    return tp, n_pred, n_gold


def pair_f1(gold, pred, ids, aspects=ASPECTS):
    return prf(*pair_counts(gold, pred, ids, aspects))[2]


def evaluate(gold, pred, ids=None):
    """Semua metrik untuk satu model. `gold`/`pred`: {reviewId: {aspek: label}}."""
    ids = sorted(ids if ids is not None else gold)
    if not ids:
        raise ValueError("Set evaluasi tidak boleh kosong")
    missing = [rid for rid in ids if rid not in pred]
    if missing:
        raise ValueError(f"Prediksi tidak lengkap: {len(missing)} ulasan tidak ada")
    p, r, f = prf(*pair_counts(gold, pred, ids))
    det_tp = det_pred = det_gold = 0
    per_aspect = {}
    for a in ASPECTS:
        g = [gold[rid][a] for rid in ids]
        q = [pred[rid][a] for rid in ids]
        tp = sum(x != NONE and y != NONE for x, y in zip(g, q))
        dp, dr, df = prf(tp, sum(y != NONE for y in q), sum(x != NONE for x in g))
        det_tp += tp
        det_pred += sum(y != NONE for y in q)
        det_gold += sum(x != NONE for x in g)
        mentioned = [(x, y) for x, y in zip(g, q) if x != NONE]
        classes = [c for c in POLAR if any(x == c for x, _ in mentioned)]
        sent = macro_f1([x for x, _ in mentioned], [y for _, y in mentioned], classes) if mentioned else None
        sp, sr, sf = prf(*pair_counts(gold, pred, ids, (a,)))
        per_aspect[a] = {
            "confusion_matrix": confusion_matrix(g, q),
            "n_gold_disebut": sum(x != NONE for x in g),
            "n_pred_disebut": sum(y != NONE for y in q),
            "f1_pasangan": sf, "presisi_pasangan": sp, "recall_pasangan": sr,
            "f1_deteksi": df, "presisi_deteksi": dp, "recall_deteksi": dr,
            "macro_f1_sentimen": sent,
            "akurasi_sentimen": (sum(x == y for x, y in mentioned) / len(mentioned)) if mentioned else None,
            "akurasi_4_label": sum(x == y for x, y in zip(g, q)) / len(ids),
            "kappa": cohen_kappa(g, q),
            "distribusi_gold": dict(Counter(g)), "distribusi_pred": dict(Counter(q)),
        }
    _, _, det_micro = prf(det_tp, det_pred, det_gold)
    defined = [v["f1_deteksi"] for v in per_aspect.values() if v["n_gold_disebut"] or v["n_pred_disebut"]]
    sentiments = [v["macro_f1_sentimen"] for v in per_aspect.values() if v["macro_f1_sentimen"] is not None]
    return {
        "n_ulasan": len(ids),
        "confusion_matrix_labels": list(LABELS),
        "confusion_matrix_gabungan": [
            [sum(v["confusion_matrix"][i][j] for v in per_aspect.values()) for j in range(len(LABELS))]
            for i in range(len(LABELS))
        ],
        "f1_pasangan": f, "presisi_pasangan": p, "recall_pasangan": r,
        "f1_deteksi_micro": det_micro,
        "f1_deteksi_macro": sum(defined) / len(defined) if defined else None,
        "macro_f1_sentimen_rata2": sum(sentiments) / len(sentiments) if sentiments else None,
        "ulasan_persis_sama": sum(all(gold[rid][a] == pred[rid][a] for a in ASPECTS) for rid in ids) / len(ids),
        "per_aspek": per_aspect,
    }


def paired_bootstrap(gold, preds, ids, n=1000, seed=42):
    """Interval 95% selisih F1 pasangan model teratas vs model lain."""
    ids = sorted(ids)
    names = list(preds)
    point = {m: pair_f1(gold, preds[m], ids) for m in names}
    best = max(names, key=point.get)
    rng = random.Random(seed)
    counts = {m: {rid: pair_counts(gold, preds[m], [rid]) for rid in ids} for m in names}
    diffs = {m: [] for m in names if m != best}
    for _ in range(n):
        sample = [rng.choice(ids) for _ in ids]
        score = {}
        for m in names:
            tp = sum(counts[m][rid][0] for rid in sample)
            npred = sum(counts[m][rid][1] for rid in sample)
            ngold = sum(counts[m][rid][2] for rid in sample)
            score[m] = prf(tp, npred, ngold)[2]
        for m in diffs:
            diffs[m].append(score[best] - score[m])
    result = {}
    for m, values in diffs.items():
        values.sort()
        low, high = values[int(0.025 * n)], values[int(0.975 * n) - 1]
        result[m] = {"selisih": point[best] - point[m], "ci95": [low, high], "nyata": low > 0}
    return {"model_teratas": best, "f1_pasangan": point, "pembanding": result, "n_bootstrap": n, "seed": seed}


def load_labels(path):
    path = Path(path)
    if path.suffix.lower() == ".xlsx":
        from src import label_excel
        reviews, mentions = label_excel.read_mentions(path)
        return label_excel.review_labels(reviews, mentions)
    from src.label_excel import read_label_csv
    return read_label_csv(path)


def average_runs(results):
    """Rata-rata dan simpangan baku metrik utama untuk beberapa seed."""
    keys = ["f1_pasangan", "f1_deteksi_micro", "f1_deteksi_macro", "macro_f1_sentimen_rata2"]
    out = {}
    for k in keys:
        values = [r[k] for r in results if r[k] is not None]
        mean = sum(values) / len(values)
        sd = (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5 if len(values) > 1 else 0.0
        out[k] = {"rata2": mean, "sd": sd}
    return out


def fmt(value):
    return "-" if value is None else f"{value:.3f}"


def write_tables(out_dir, results):
    """Tabel utama (keseluruhan) dan tabel per aspek untuk semua model."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    names = list(results)
    with (out_dir / "ringkasan.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        w = csv.writer(stream)
        w.writerow(["Model", "F1 pasangan", "Presisi", "Recall", "F1 deteksi micro", "F1 deteksi macro",
                    "Macro-F1 sentimen rata-rata", "Ulasan persis sama"])
        for m in names:
            r = results[m]
            w.writerow([m] + [fmt(r[k]) for k in ("f1_pasangan", "presisi_pasangan", "recall_pasangan",
                                                    "f1_deteksi_micro", "f1_deteksi_macro",
                                                    "macro_f1_sentimen_rata2", "ulasan_persis_sama")])
    with (out_dir / "per_aspek.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        w = csv.writer(stream)
        w.writerow(["Aspek", "Model", "Jumlah disebut (acuan)", "F1 pasangan", "F1 deteksi",
                    "Macro-F1 sentimen", "Akurasi 4 label", "Kappa"])
        for a in ASPECTS:
            for m in names:
                v = results[m]["per_aspek"][a]
                w.writerow([ASPECT_TITLES[a], m, v["n_gold_disebut"], fmt(v["f1_pasangan"]), fmt(v["f1_deteksi"]),
                            fmt(v["macro_f1_sentimen"]), fmt(v["akurasi_4_label"]), fmt(v["kappa"])])
    lines = ["| Model | F1 pasangan | F1 deteksi (micro) | Macro-F1 sentimen |", "|---|---|---|---|"]
    for m in names:
        r = results[m]
        lines.append(f"| {m} | {fmt(r['f1_pasangan'])} | {fmt(r['f1_deteksi_micro'])} | {fmt(r['macro_f1_sentimen_rata2'])} |")
    lines += ["", "F1 pasangan per aspek:", "",
              "| Aspek | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for a in ASPECTS:
        lines.append(f"| {ASPECT_TITLES[a]} | " + " | ".join(fmt(results[m]['per_aspek'][a]['f1_pasangan']) for m in names) + " |")
    lines += ["", "Macro-F1 sentimen per aspek:", "",
              "| Aspek | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for a in ASPECTS:
        lines.append(f"| {ASPECT_TITLES[a]} | " + " | ".join(fmt(results[m]['per_aspek'][a]['macro_f1_sentimen']) for m in names) + " |")
    (out_dir / "tabel.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gold", type=Path, required=True, help="gold.csv atau lembar Excel rinci")
    parser.add_argument("--pred", action="append", required=True, help="NAMA=path.csv (boleh berulang)")
    parser.add_argument("--ids-split", default=None, help="hanya ulasan pada split ini, mis. gold_test")
    parser.add_argument("--exclude-split", default=None, help="buang ulasan pada split ini, dipisah koma")
    parser.add_argument("--split-file", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    gold = load_labels(args.gold)
    ids = set(gold)
    if args.ids_split or args.exclude_split:
        with args.split_file.open(encoding="utf-8-sig", newline="") as stream:
            split = {r["reviewId"]: r["split"] for r in csv.DictReader(stream)}
        if args.ids_split:
            ids = {rid for rid in ids if split.get(rid) == args.ids_split}
        if args.exclude_split:
            drop = set(args.exclude_split.split(","))
            ids = {rid for rid in ids if split.get(rid) not in drop}
    preds = {}
    for item in args.pred:
        name, path = item.split("=", 1)
        preds[name] = load_labels(path)
    results = {name: evaluate(gold, pred, ids) for name, pred in preds.items()}
    write_tables(args.out, results)
    write_confusion_matrices(args.out, results)
    report = {"gold": str(args.gold), "n_ulasan": len(ids), "hasil": results}
    if len(preds) > 1 and args.bootstrap:
        report["bootstrap"] = paired_bootstrap(gold, preds, ids, args.bootstrap)
    (args.out / "metrik.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print((args.out / "tabel.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
