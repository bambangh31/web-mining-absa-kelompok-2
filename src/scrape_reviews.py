"""Ambil ulasan Google Play untuk satu aplikasi dan simpan sebagai CSV.

Contoh:
    python src/scrape_reviews.py --app com.telkom.tracencare --count 15000

Kolom identitas pengguna (nama dan foto profil) tidak disimpan.
"""

import argparse
import csv
import time
from pathlib import Path

from google_play_scraper import Sort, reviews

FIELDS = [
    "reviewId",
    "at",
    "score",
    "content",
    "thumbsUpCount",
    "reviewCreatedVersion",
    "appVersion",
    "replyContent",
    "repliedAt",
]


def scrape(app_id, count, lang, country, batch=200, pause=1.0):
    rows, token = [], None
    while len(rows) < count:
        batch_rows, token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=min(batch, count - len(rows)),
            continuation_token=token,
        )
        if not batch_rows:
            break
        rows.extend({k: r.get(k) for k in FIELDS} for r in batch_rows)
        print(f"{len(rows)} ulasan")
        if token is None or token.token is None:
            break
        time.sleep(pause)
    # continuation_token memakai ukuran batch awal, jadi batch terakhir bisa lebih.
    return rows[:count]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", default="com.telkom.tracencare")
    parser.add_argument("--count", type=int, default=15000)
    parser.add_argument("--lang", default="id")
    parser.add_argument("--country", default="id")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    rows = scrape(args.app, args.count, args.lang, args.country)
    out = args.out or Path("data/raw") / f"{args.app}_reviews.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Tersimpan {len(rows)} ulasan di {out}")


if __name__ == "__main__":
    main()
