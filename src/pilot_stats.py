"""Hitung statistik eksplorasi dari CSV hasil scrape_reviews.py.

Contoh:
    python src/pilot_stats.py data/raw/com.telkom.tracencare_reviews.csv

Angka di data/README.md berasal dari 2.000 ulasan terbaru pada 3 November
2026. Menjalankan ulang pada tanggal lain memberi angka berbeda.
"""

import csv
import re
import sys
from collections import Counter


def main(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    texts = [r["content"] or "" for r in rows]
    words = [len(t.split()) for t in texts]
    norm = [re.sub(r"\s+", " ", t.lower()).strip() for t in texts]
    dates = sorted(r["at"] for r in rows)
    versions = [r["reviewCreatedVersion"] for r in rows if r["reviewCreatedVersion"]]
    per_version = Counter(versions)

    print(f"ulasan: {n}")
    print(f"rentang: {dates[0][:10]} sampai {dates[-1][:10]}")
    print(f"median kata: {sorted(words)[n // 2]}")
    for k in (3, 5, 8):
        print(f"minimal {k} kata: {sum(w >= k for w in words) / n:.1%}")
    print(f"duplikat persis (huruf kecil, spasi dirapikan): {n - len(set(norm))}")
    print(f"versi terisi: {len(versions) / n:.1%}")
    print(f"versi berbeda: {len(per_version)}")
    print(f"versi dengan minimal 50 ulasan: {sum(v >= 50 for v in per_version.values())}")
    stars = Counter(r["score"] for r in rows)
    print("rating:", {k: stars[k] for k in sorted(stars)})


if __name__ == "__main__":
    main(sys.argv[1])
