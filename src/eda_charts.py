"""Buat grafik eksplorasi data untuk laporan week 10.

Contoh:
    python src/eda_charts.py data/raw/com.telkom.tracencare_reviews.csv results/figures

Grafik pada laporan week 10 dibuat dari 15.000 ulasan yang diambil
3 November 2026.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLOR = "#404040"


def save(fig, out_dir, name):
    fig.tight_layout()
    fig.savefig(out_dir / name, dpi=200)
    plt.close(fig)


def main(csv_path, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    plt.rcParams.update({"font.family": "serif", "font.size": 9})

    # Distribusi rating
    stars = Counter(int(r["score"]) for r in rows)
    keys = [1, 2, 3, 4, 5]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    bars = ax.bar([str(k) for k in keys], [stars[k] for k in keys], color=COLOR)
    for b, k in zip(bars, keys):
        ax.annotate(f"{stars[k]:,}".replace(",", ".") + f"\n({stars[k] / n:.1%})".replace(".", ","),
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", fontsize=7)
    ax.set_xlabel("Rating bintang")
    ax.set_ylabel("Jumlah ulasan")
    ax.set_ylim(0, max(stars.values()) * 1.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, out_dir, "eda_rating.png")

    # Ulasan per bulan
    months = Counter(r["at"][:7] for r in rows)
    labels = sorted(months)
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.bar(range(len(labels)), [months[m] for m in labels], color=COLOR)
    ticks = [i for i, m in enumerate(labels) if m.endswith("-01")]
    ax.set_xticks(ticks, [labels[i] for i in ticks])
    ax.set_xlabel("Bulan ulasan")
    ax.set_ylabel("Jumlah ulasan")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, out_dir, "eda_per_bulan.png")

    # Panjang ulasan
    words = [len((r["content"] or "").split()) for r in rows]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.hist([min(w, 80) for w in words], bins=range(0, 82, 2), color=COLOR)
    ax.axvline(3, color="black", linestyle="--", linewidth=1)
    ax.text(4, ax.get_ylim()[1] * 0.9, "batas 3 kata", fontsize=7)
    ax.set_xlabel("Jumlah kata per ulasan (80 = 80 atau lebih)")
    ax.set_ylabel("Jumlah ulasan")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, out_dir, "eda_panjang.png")

    # Versi dengan ulasan terbanyak
    versions = Counter(r["reviewCreatedVersion"] for r in rows if r["reviewCreatedVersion"])
    top = versions.most_common(15)[::-1]
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.barh([v for v, _ in top], [c for _, c in top], color=COLOR)
    ax.set_xlabel("Jumlah ulasan")
    ax.set_ylabel("Versi aplikasi")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, out_dir, "eda_versi.png")

    print(f"{n} ulasan; grafik disimpan di {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
