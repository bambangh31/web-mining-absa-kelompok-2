"""Analisis keluhan per aspek, per versi, dan konsistensi rating (RQ3, TB1, TB2).

Dua sumber label, dilaporkan terpisah:

1. Label yang diperiksa manusia (275 ulasan: 150 uji label manual dan 125
   latih/validasi terverifikasi). Dipakai untuk urutan aspek yang paling
   dikeluhkan (TB1) dan konsistensi rating, karena paling dapat dipercaya.
2. Prediksi model terlatih terbaik (B1-LR, dilatih pada label latih yang sama)
   untuk semua ulasan bersih, termasuk duplikat, agar setiap versi punya
   cukup ulasan (TB2). Gemini (model terbaik) tidak dipakai di sini karena
   kuota gratis tidak cukup untuk 32.843 ulasan. Aspek yang F1 pasangan uji
   B1-LR-nya di bawah `--min-f1` ditandai tidak andal dan tidak digambar.

  python src/version_analysis.py
"""

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECT_NAMES, ASPECTS, NONE, SPECIFIC  # noqa: E402
from src.evaluate import load_labels  # noqa: E402
from src.model_data import Dataset  # noqa: E402
from src.models_classic import run  # noqa: E402
from src.text_features import LEXICON_PATH, load_lexicon  # noqa: E402


def wilson(k, n, z=1.96):
    if not n:
        return None, None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def version_key(v):
    return tuple(int(x) if x.isdigit() else 0 for x in v.split("."))


def complaint_table(labels, ids):
    """Porsi ulasan yang menyebut aspek dengan sentimen negatif."""
    n = len(ids)
    out = {}
    for a in ASPECTS:
        neg = sum(labels[r][a] == "negatif" for r in ids)
        lo, hi = wilson(neg, n)
        out[a] = {"negatif": neg, "disebut": sum(labels[r][a] != NONE for r in ids),
                  "porsi_negatif": neg / n, "ci95": [lo, hi]}
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["negatif"]))


def rating_conflict(labels, ids, score):
    """Bintang 4-5 hanya berisi aspek negatif, atau bintang 1-2 hanya berisi aspek positif."""
    high = [r for r in ids if score[r] >= 4]
    low = [r for r in ids if score[r] <= 2]

    def only(r, label):
        values = [labels[r][a] for a in ASPECTS if labels[r][a] != NONE]
        return bool(values) and all(v == label for v in values)

    hi_neg = sum(only(r, "negatif") for r in high)
    lo_pos = sum(only(r, "positif") for r in low)
    return {"bintang_4_5": len(high), "bintang_4_5_hanya_negatif": hi_neg,
            "bintang_1_2": len(low), "bintang_1_2_hanya_positif": lo_pos,
            "porsi_bertentangan": (hi_neg + lo_pos) / len(ids) if ids else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--labels", type=Path, default=Path("data/annotations/verified.csv"))
    parser.add_argument("--gold", type=Path, default=Path("data/annotations/final_v1/gold.csv"))
    parser.add_argument("--test-metrics", type=Path, default=Path("results/metrics/uji/metrik.json"))
    parser.add_argument("--min-reviews", type=int, default=50)
    parser.add_argument("--min-f1", type=float, default=0.6)
    parser.add_argument("--out", type=Path, default=Path("results/analisis_versi"))
    args = parser.parse_args()

    dataset = Dataset(args.clean, args.split, args.labels)
    score = {r: int(row["score"]) for r, row in dataset.clean.items()}
    version = {r: (row["reviewCreatedVersion"] or "").strip() for r, row in dataset.clean.items()}

    # 1. Label yang diperiksa manusia.
    gold = load_labels(args.gold)
    with args.labels.open(encoding="utf-8-sig", newline="") as stream:
        verified = {r["reviewId"]: {a: r[a] for a in ASPECTS} for r in csv.DictReader(stream) if r["verifier"]}
    human = {**verified, **gold}
    human_ids = sorted(human)
    result = {
        "manusia": {"n_ulasan": len(human_ids), "sumber": "150 uji manual + 125 latih/validasi terverifikasi",
                    "keluhan_per_aspek": complaint_table(human, human_ids),
                    "konsistensi_rating": rating_conflict(human, human_ids, score),
                    "ulasan_multi_aspek": sum(sum(human[r][a] != NONE for a in SPECIFIC) >= 2
                                              for r in human_ids) / len(human_ids)},
    }

    # 2. Prediksi B1-LR untuk semua ulasan bersih.
    f1 = json.loads(args.test_metrics.read_text(encoding="utf-8"))["hasil"]["B1-LR"]["per_aspek"]
    reliable = [a for a in ASPECTS if f1[a]["f1_pasangan"] >= args.min_f1]
    all_ids = sorted(dataset.clean)
    predictions, config, _, _ = run("B1-LR", dataset, load_lexicon(LEXICON_PATH), all_ids)
    by_version = defaultdict(list)
    for r in all_ids:
        if version[r]:
            by_version[version[r]].append(r)
    versions = sorted((v for v, ids in by_version.items() if len(ids) >= args.min_reviews), key=version_key)
    rows = []
    for v in versions:
        ids = by_version[v]
        dates = sorted(dataset.clean[r]["at"] for r in ids)
        row = {"versi": v, "n_ulasan": len(ids), "tanggal_awal": dates[0][:10], "tanggal_median": dates[len(dates) // 2][:10],
               "rating_rata2": sum(score[r] for r in ids) / len(ids)}
        for a in ASPECTS:
            neg = sum(predictions[r][a] == "negatif" for r in ids)
            lo, hi = wilson(neg, len(ids))
            row[f"{a}_negatif"] = neg / len(ids)
            row[f"{a}_ci_bawah"], row[f"{a}_ci_atas"] = lo, hi
        rows.append(row)
    result["model"] = {
        "model": "B1-LR", "config": {k: config[k] for k in ("nilai_terpilih", "label_latih", "n_latih")},
        "n_ulasan": len(all_ids), "tanpa_versi": len(all_ids) - sum(len(v) for v in by_version.values()),
        "versi_dianalisis": len(versions), "min_ulasan_per_versi": args.min_reviews,
        "aspek_andal": reliable, "f1_pasangan_uji": {a: f1[a]["f1_pasangan"] for a in ASPECTS},
        "keluhan_per_aspek": complaint_table(predictions, all_ids),
        "konsistensi_rating": rating_conflict(predictions, all_ids, score),
    }
    peaks = {}
    for a in reliable:
        top = max(rows, key=lambda r: r[f"{a}_negatif"])
        low = min(rows, key=lambda r: r[f"{a}_negatif"])
        peaks[a] = {"tertinggi": [top["versi"], top[f"{a}_negatif"], top["n_ulasan"]],
                    "terendah": [low["versi"], low[f"{a}_negatif"], low["n_ulasan"]]}
    result["model"]["puncak_per_aspek"] = peaks

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "per_versi.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})
    (args.out / "ringkasan.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = ["#2a6fdb", "#e0832b", "#2f9e6e", "#c2417a", "#7a5cc9", "#8a7a2c", "#3a9fb5"]
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=150)
    x = list(range(len(rows)))
    for color, a in zip(colors, reliable):
        y = [r[f"{a}_negatif"] * 100 for r in rows]
        ax.plot(x, y, marker="o", markersize=3, linewidth=1.6, color=color, label=ASPECT_NAMES[a])
    ax.set_xticks(x)
    ax.set_xticklabels([r["versi"] for r in rows], rotation=70, fontsize=7)
    ax.set_ylabel("Ulasan negatif pada aspek (%)")
    ax.set_xlabel(f"Versi aplikasi (minimal {args.min_reviews} ulasan), urut nomor versi")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    ax.legend(frameon=False, fontsize=8, ncol=len(reliable), loc="upper center", bbox_to_anchor=(0.5, 1.12))
    fig.tight_layout()
    fig.savefig(args.out.parent / "figures" / "keluhan_per_versi.png")
    print(json.dumps({"manusia": {a: round(v["porsi_negatif"], 3) for a, v in
                                  result["manusia"]["keluhan_per_aspek"].items()},
                      "konsistensi_manusia": result["manusia"]["konsistensi_rating"],
                      "versi": len(versions), "aspek_andal": reliable, "puncak": peaks,
                      "konsistensi_model": result["model"]["konsistensi_rating"]}, indent=1))


if __name__ == "__main__":
    main()
