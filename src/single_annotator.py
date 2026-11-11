"""Ekspor label satu anotator dan analisis kesepakatan pengganti kappa antar-manusia.

Keputusan 11 November 2026: kalibrasi, gold, dan verifikasi hanya dikerjakan
satu anggota (jap). Karena itu:

- `gold_test` yang dipakai untuk evaluasi adalah 150 ulasan uji milik jap
  (dilabeli tanpa label LLM); 150 ulasan uji lain tidak punya label manusia
  dan tidak dievaluasi.
- Kalibrasi 50 ulasan menjadi pedoman satu orang, tanpa kappa antar-anggota.
- Kappa antar-manusia diganti dengan dua perbandingan yang tersedia:
  (a) label manual jap vs Gemini pada 150 ulasan uji (jap tidak melihat
  label LLM), (b) hasil verifikasi jap vs Gemini pada 125 ulasan
  latih/validasi (setara tingkat koreksi). Baris latih/validasi pada lembar
  gold juga dibandingkan dengan hasil verifikasi; bila identik, keduanya
  dicatat sebagai satu keputusan, bukan dua penilaian independen.

Lembar kerja tetap di `data/annotation_workspace/v2`; teks tidak ikut
diekspor.

  python src/single_annotator.py --annotator jap
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECT_TITLES, ASPECTS, LABELS, NONE  # noqa: E402
from src.annotation import (LABEL_FIELDS, SHEET_FIELDS, cohen_kappa, digest, read_csv,  # noqa: E402
                            unique_rows, validate_labels, write_csv)
from src.label_excel import read_label_csv  # noqa: E402


def load_sheet(workspace, phase, annotator, manifest):
    path = Path(workspace) / f"{phase}_{annotator}.csv"
    rows = unique_rows(read_csv(path, SHEET_FIELDS, SHEET_FIELDS), path)
    expected = manifest["assignments"][phase][annotator]
    if set(rows) != set(expected):
        raise ValueError(f"{path}: ID hilang, tambahan, atau tidak sesuai pembagian manifest")
    for row in rows.values():
        if row["annotator"] != annotator:
            raise ValueError(f"{path}: nama anotator tidak sesuai lembar")
        text_hash = hashlib.sha256(row["text_llm"].encode("utf-8")).hexdigest()
        if text_hash != manifest["text_sha256"][row["reviewId"]]:
            raise ValueError(f"{path}: {row['reviewId']}: teks/ID berubah")
        validate_labels(row, path)
    return rows


def compare(left, right, ids):
    """Kesepakatan per aspek dan keseluruhan antara dua sumber label."""
    per_aspect = {}
    for a in ASPECTS:
        x = [left[r][a] for r in ids]
        y = [right[r][a] for r in ids]
        detected = [(p != NONE, q != NONE) for p, q in zip(x, y)]
        per_aspect[a] = {
            "n": len(ids),
            "agreement": sum(p == q for p, q in zip(x, y)) / len(ids),
            "kappa": cohen_kappa(x, y),
            "kappa_deteksi": cohen_kappa([p for p, _ in detected], [q for _, q in detected]),
            "disebut_kiri": sum(p != NONE for p in x),
            "disebut_kanan": sum(q != NONE for q in y),
        }
    cells = [(left[r][a], right[r][a]) for r in ids for a in ASPECTS]
    kappas = [v["kappa"] for v in per_aspect.values() if v["kappa"] is not None]
    return {
        "n_ulasan": len(ids),
        "agreement_sel": sum(p == q for p, q in cells) / len(cells),
        "ulasan_persis_sama": sum(all(left[r][a] == right[r][a] for a in ASPECTS) for r in ids) / len(ids),
        "kappa_rata2_aspek": sum(kappas) / len(kappas) if kappas else None,
        "beda_terbanyak": dict(Counter(f"{a}: {left[r][a]} -> {right[r][a]}" for r in ids for a in ASPECTS
                                       if left[r][a] != right[r][a]).most_common(10)),
        "per_aspek": per_aspect,
    }


def distribution(rows):
    return {a: {label: sum(r[a] == label for r in rows.values()) for label in LABELS} for a in ASPECTS}


def fmt(value):
    return "-" if value is None else f"{value:.3f}"


def run(annotator, workspace, split_path, llm_path, verified_path, labels_out, results_out):
    workspace, labels_out, results_out = Path(workspace), Path(labels_out), Path(results_out)
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    with Path(split_path).open(encoding="utf-8-sig", newline="") as stream:
        split = {r["reviewId"]: r["split"] for r in csv.DictReader(stream)}
    kalibrasi = load_sheet(workspace, "kalibrasi", annotator, manifest)
    gold = load_sheet(workspace, "gold", annotator, manifest)
    llm = read_label_csv(llm_path)
    verified_rows = {}
    with Path(verified_path).open(encoding="utf-8-sig", newline="") as stream:
        for r in csv.DictReader(stream):
            if r["verifier"] == annotator:
                verified_rows[r["reviewId"]] = {a: r[a] for a in ASPECTS}

    test_ids = sorted(r for r in gold if split[r] == "gold_test")
    trainval_ids = sorted(r for r in gold if split[r] in ("gold_train", "gold_val"))
    both = sorted(set(trainval_ids) & set(verified_rows))

    # Label akhir: gold.csv hanya berisi ulasan uji (acuan evaluasi model).
    final_dir = labels_out / "final_v1"
    kal_dir = labels_out / "kalibrasi_v1"
    final_dir.mkdir(parents=True, exist_ok=False)
    kal_dir.mkdir(parents=True, exist_ok=False)
    write_csv(final_dir / "gold.csv", ["reviewId", *ASPECTS],
              [{"reviewId": r, **{a: gold[r][a] for a in ASPECTS}} for r in test_ids])
    write_csv(final_dir / f"gold_{annotator}.csv", ["split", *LABEL_FIELDS],
              [{"split": split[r], **{f: gold[r][f] for f in LABEL_FIELDS}} for r in sorted(gold)])
    write_csv(final_dir / "provenance.csv", ["reviewId", "aspek", "sumber", "annotators", "adjudicator"],
              [{"reviewId": r, "aspek": a, "sumber": "anotasi_tunggal", "annotators": annotator,
                "adjudicator": ""} for r in test_ids for a in ASPECTS])
    write_csv(kal_dir / "kalibrasi.csv", ["reviewId", *ASPECTS],
              [{"reviewId": r, **{a: kalibrasi[r][a] for a in ASPECTS}} for r in sorted(kalibrasi)])

    report = {
        "anotator": annotator,
        "catatan": "Satu anotator: tidak ada kappa antar-manusia dan tidak ada adjudikasi. "
                   "gold.csv berisi 150 ulasan uji milik anotator ini; 150 ulasan uji lain tidak berlabel manusia.",
        "jumlah": {"kalibrasi": len(kalibrasi), "gold_total": len(gold),
                   "gold_per_split": dict(Counter(split[r] for r in gold)),
                   "gold_csv_uji": len(test_ids), "verifikasi": len(verified_rows)},
        "sha256": {"kalibrasi": digest(workspace / f"kalibrasi_{annotator}.csv"),
                   "gold": digest(workspace / f"gold_{annotator}.csv"),
                   "llm": digest(llm_path), "verified": digest(verified_path)},
        "source_sha256": manifest["source_sha256"],
        "distribusi": {"kalibrasi": distribution(kalibrasi),
                       "gold_uji": distribution({r: gold[r] for r in test_ids})},
        "kesepakatan": {
            "uji_manual_vs_gemini": compare(gold, llm, test_ids),
            "latih_validasi_verifikasi_vs_gemini": compare(verified_rows, llm, both),
        },
    }
    same = compare(gold, verified_rows, both)
    report["lembar_gold_latih_validasi"] = {
        "n_ulasan": len(both), "identik_dengan_verifikasi": same["ulasan_persis_sama"] == 1.0,
        "agreement_sel": same["agreement_sel"],
        "catatan": "Baris latih/validasi pada lembar gold dibandingkan dengan hasil verifikasi anotator yang "
                   "sama. Jika identik, bukan ukuran konsistensi independen.",
    }
    for path in (final_dir / "report.json", ):
        path.write_text(json.dumps({k: report[k] for k in ("anotator", "catatan", "jumlah", "sha256",
                                                            "source_sha256")}, indent=2) + "\n", encoding="utf-8")
    results_out.mkdir(parents=True, exist_ok=True)
    (results_out / "ringkasan.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")

    names = {"uji_manual_vs_gemini": "Uji: manual vs Gemini",
             "latih_validasi_verifikasi_vs_gemini": "Latih/val: verifikasi vs Gemini"}
    k = report["kesepakatan"]
    lines = ["| Perbandingan | Ulasan | Agreement sel | Ulasan persis sama | Kappa rata-rata aspek |",
             "|---|---|---|---|---|"]
    for key, title in names.items():
        v = k[key]
        lines.append(f"| {title} | {v['n_ulasan']} | {fmt(v['agreement_sel'])} | {fmt(v['ulasan_persis_sama'])} "
                     f"| {fmt(v['kappa_rata2_aspek'])} |")
    lines += ["", "Kappa per aspek (empat label):", "",
              "| Aspek | " + " | ".join(names.values()) + " |", "|---|" + "---|" * len(names)]
    for a in ASPECTS:
        lines.append(f"| {ASPECT_TITLES[a]} | " + " | ".join(fmt(k[key]["per_aspek"][a]["kappa"]) for key in names)
                     + " |")
    g = report["lembar_gold_latih_validasi"]
    lines += ["", f"Baris latih/validasi lembar gold vs hasil verifikasi ({g['n_ulasan']} ulasan): "
              f"agreement sel {fmt(g['agreement_sel'])}"
              + (" (identik; satu keputusan, bukan dua penilaian independen)." if g["identik_dengan_verifikasi"]
                 else ".")]
    (results_out / "tabel.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--annotator", default="jap")
    parser.add_argument("--workspace", type=Path, default=Path("data/annotation_workspace/v2"))
    parser.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--llm", type=Path, default=Path("data/annotations/llm_gemini-3.5-flash-lite.csv"))
    parser.add_argument("--verified", type=Path, default=Path("data/annotations/verified.csv"))
    parser.add_argument("--labels-out", type=Path, default=Path("data/annotations"))
    parser.add_argument("--results-out", type=Path, default=Path("results/kesepakatan"))
    args = parser.parse_args()
    report = run(args.annotator, args.workspace, args.split, args.llm, args.verified, args.labels_out,
                 args.results_out)
    print(json.dumps(report["jumlah"], indent=2))
    print((args.results_out / "tabel.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
