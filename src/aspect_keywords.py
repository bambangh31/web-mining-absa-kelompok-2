"""Perkiraan cakupan aspek dan multi-aspek dari kata kunci (eksplorasi, bukan label).

Dipakai untuk merancang kategori dan membuktikan bahwa banyak ulasan memuat
lebih dari satu aspek. Angka ini bukan label dan tidak dipakai untuk melatih
atau mengevaluasi model.

  python src/aspect_keywords.py
"""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

KEYWORDS = {
    "akun_login": r"log ?in|masuk|pin|otp|kata ?sandi|password|verifikasi|kode",
    "registrasi_data": r"daftar|regist|nik|data diri|biodata|profil|nomor (hp|telepon|telpon)|ganti (nomor|email|nama)",
    "fitur_kesehatan": r"vaksin|sertifikat|booster|boster|ckg|cek kesehatan|pemeriksaan|hasil|tiket|faskes|puskesmas|riwayat|skrining",
    "performa": r"error|eror|force ?close|keluar sendiri|lemot|lambat|loading|lelet|stuck|nge-?bug|bug|crash|server|tidak bisa dibuka|ga bisa dibuka|gak bisa dibuka|gabisa dibuka|tidak bisa di buka|ga bisa di buka|gak bisa di buka",
    "kemudahan_penggunaan": r"ribet|rumit|bingung|membingungkan|mudah|gampang|susah|sulit|simpel|simple|tampilan|praktis",
    "pembaruan_aplikasi": r"update|updet|apdet|pembaruan|perbarui|diperbarui|diperbaharui|versi|peduli ?lindungi|ganti nama",
    "layanan_pelanggan": r"\bcs\b|customer service|helpdesk|help desk|admin|\bmin\b|aduan|pengaduan|dibalas|balas|respon|tanggap",
}
PATTERNS = {a: re.compile(rf"\b(?:{p})", re.IGNORECASE) for a, p in KEYWORDS.items()}


def aspects_in(text):
    return [a for a, pattern in PATTERNS.items() if pattern.search(text)]


def summarize(clean_path):
    counts, multi, total = Counter(), Counter(), 0
    with Path(clean_path).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["in_pool"] != "1":
                continue
            total += 1
            found = aspects_in(row["text_model"])
            counts.update(found)
            multi[min(len(found), 3)] += 1
    return {
        "pool": total,
        "per_aspek_pct": {a: round(100 * counts[a] / total, 1) for a in KEYWORDS},
        "jumlah_aspek_khusus_pct": {("3+" if k == 3 else str(k)): round(100 * v / total, 1)
                                     for k, v in sorted(multi.items())},
        "dua_aspek_atau_lebih_pct": round(100 * (multi[2] + multi[3]) / total, 1),
        "catatan": "Perkiraan kata kunci pada text_model pool, bukan label.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/eksplorasi/aspek_kata_kunci.json"))
    args = parser.parse_args()
    report = summarize(args.clean)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
