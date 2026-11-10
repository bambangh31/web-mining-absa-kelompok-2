"""Verifikasi manusia atas label LLM untuk 400 ulasan latih dan 100 validasi.

Lembar Excel dua langkah per aspek (sesuai tinjauan pustaka): pemeriksa
menandai label LLM `setuju` atau `salah`, lalu mengisi label pengganti hanya
untuk yang `salah`. Waktu mulai dan selesai dicatat per lembar.

Pembagian ulasan sama dengan lembar gold `annotation.py` (100 latih + 25
validasi per anggota). Lembar uji TIDAK dibuat di sini: set uji dilabeli
manual tanpa melihat label LLM.

  python src/verification.py prepare --llm data/annotations/llm_gemini-3.5-flash.csv
  python src/verification.py export  --llm data/annotations/llm_gemini-3.5-flash.csv
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import (ASPECT_TITLES, ASPECTS, LABEL_NAMES, NONE, label_from_name,  # noqa: E402
                             validate_labels)
from src.annotation import MEMBERS, assign  # noqa: E402

WORKSPACE = Path("data/annotation_workspace/verifikasi")
SPLITS = ("gold_train", "gold_val")
CHECK = ("setuju", "salah")


def read_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_inputs(llm_path, split_path, raw_path):
    llm = {r["reviewId"]: r for r in read_rows(llm_path)}
    split = {r["reviewId"]: {"split": r["split"]} for r in read_rows(split_path)}
    raw = {r["reviewId"]: r for r in read_rows(raw_path)}
    ids = [rid for rid, s in split.items() if s["split"] in SPLITS]
    missing = [rid for rid in ids if rid not in llm]
    if missing:
        raise SystemExit(f"{len(missing)} ulasan latih/validasi belum punya label LLM di {llm_path}")
    assignment = assign(split)["gold"]
    owned = {m: [rid for rid in assignment[m] if split[rid]["split"] in SPLITS] for m in MEMBERS}
    return llm, split, raw, owned


def evidence_text(mentions):
    by_review = {}
    for m in mentions:
        by_review.setdefault(m["reviewId"], []).append(
            f"{m['aspek'].replace('_', ' ')}: {m['label']} ({m['bukti'] or m['kata']})")
    return {rid: "\n".join(items) for rid, items in by_review.items()}


def prepare(llm_path, split_path, raw_path, mentions_path, workspace):
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    llm, split, raw, owned = load_inputs(llm_path, split_path, raw_path)
    evidence = evidence_text(read_rows(mentions_path)) if mentions_path and Path(mentions_path).exists() else {}
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=False)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    bold, normal = Font(name="Arial", size=10, bold=True), Font(name="Arial", size=10)
    wrap = Alignment(wrap_text=True, vertical="top")
    shade = PatternFill("solid", fgColor="F2F2F2")
    model = next(iter(llm.values())).get("model", "")
    for member in MEMBERS:
        wb = openpyxl.Workbook()
        info = wb.active
        info.title = "Info"
        for r, (k, v) in enumerate([("Pemeriksa", member), ("Model LLM", model),
                                    ("Versi prompt", next(iter(llm.values())).get("prompt_version", "")),
                                    ("Mulai", ""), ("Selesai", ""),
                                    ("Cara isi", "Baca komentar. Untuk tiap aspek isi kolom Cek dengan setuju atau "
                                                 "salah. Hanya bila salah, isi kolom Pengganti dengan label yang "
                                                 "benar. Isi Mulai dan Selesai (tanggal dan jam) saat mulai dan "
                                                 "selesai memeriksa lembar ini.")], start=1):
            info.cell(r, 1, k).font = bold
            info.cell(r, 2, v).font = normal
            info.cell(r, 2).alignment = wrap
        info.column_dimensions["A"].width = 14
        info.column_dimensions["B"].width = 80
        ws = wb.create_sheet("Verifikasi")
        header = ["No", "reviewId", "Bagian", "Komentar", "Ringkasan LLM"]
        for a in ASPECTS:
            header += [f"{ASPECT_TITLES[a]} LLM", f"{ASPECT_TITLES[a]} Cek", f"{ASPECT_TITLES[a]} Pengganti"]
        header.append("Catatan")
        for c, title in enumerate(header, start=1):
            cell = ws.cell(1, c, title)
            cell.font, cell.border, cell.alignment = bold, border, Alignment(wrap_text=True, vertical="center",
                                                                                horizontal="center")
        check_dv = DataValidation(type="list", formula1='"setuju,salah"', allow_blank=True)
        label_dv = DataValidation(type="list", formula1='"' + ",".join(LABEL_NAMES.values()) + '"', allow_blank=True)
        ws.add_data_validation(check_dv)
        ws.add_data_validation(label_dv)
        ids = owned[member]
        for i, rid in enumerate(ids, start=2):
            values = [i - 1, rid, "latih" if split[rid]["split"] == "gold_train" else "validasi",
                      raw[rid]["content"], evidence.get(rid, "")]
            for a in ASPECTS:
                values += [LABEL_NAMES[llm[rid][a]], None, None]
            values.append(None)
            for c, value in enumerate(values, start=1):
                cell = ws.cell(i, c, value)
                cell.font, cell.border, cell.alignment = normal, border, wrap
            for k in range(len(ASPECTS)):
                col = 6 + 3 * k
                ws.cell(i, col).fill = shade
                check_dv.add(ws.cell(i, col + 1))
                label_dv.add(ws.cell(i, col + 2))
        widths = {1: 5, 2: 12, 3: 9, 4: 55, 5: 40}
        for c in range(1, len(header) + 1):
            ws.column_dimensions[get_column_letter(c)].width = widths.get(c, 12)
        ws.freeze_panes = "F2"
        wb.save(workspace / f"verifikasi_{member}.xlsx")
    manifest = {"llm": str(llm_path), "dibuat": datetime.now().isoformat(timespec="seconds"),
                "pembagian": owned}
    (workspace / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {m: len(v) for m, v in owned.items()}


def parse_time(value):
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M"):
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            pass
    return None


def export(llm_path, split_path, raw_path, workspace, output, summary_path):
    import openpyxl

    llm, split, raw, owned = load_inputs(llm_path, split_path, raw_path)
    workspace = Path(workspace)
    final, errors = {}, []
    changed = Counter()
    accepted_whole = 0
    seconds, reviews_timed = 0.0, 0
    for member in MEMBERS:
        wb = openpyxl.load_workbook(workspace / f"verifikasi_{member}.xlsx", data_only=True)
        info = {wb["Info"].cell(r, 1).value: wb["Info"].cell(r, 2).value for r in range(1, 7)}
        start, end = parse_time(info.get("Mulai")), parse_time(info.get("Selesai"))
        ws = wb["Verifikasi"]
        header = [c.value for c in ws[1]]
        col = {name: i for i, name in enumerate(header)}
        rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[1]]
        if sorted(r[1] for r in rows) != sorted(owned[member]):
            errors.append(f"{member}: daftar reviewId berubah")
            continue
        if start and end and end > start:
            seconds += (end - start).total_seconds()
            reviews_timed += len(rows)
        for r in rows:
            rid = r[1]
            out = {}
            whole = True
            for a in ASPECTS:
                title = ASPECT_TITLES[a]
                check = (r[col[f"{title} Cek"]] or "").strip().lower()
                if check not in CHECK:
                    errors.append(f"{member}/{rid}/{title}: kolom Cek harus setuju atau salah")
                    continue
                if check == "setuju":
                    out[a] = llm[rid][a]
                    continue
                whole = False
                try:
                    replacement = label_from_name(r[col[f"{title} Pengganti"]] or "")
                except ValueError:
                    errors.append(f"{member}/{rid}/{title}: salah tetapi Pengganti kosong/tidak sah")
                    continue
                if replacement == llm[rid][a]:
                    errors.append(f"{member}/{rid}/{title}: Pengganti sama dengan label LLM")
                    continue
                out[a] = replacement
                changed[a] += 1
            if len(out) == len(ASPECTS):
                try:
                    validate_labels({"reviewId": rid, **out}, member)
                except ValueError as error:
                    errors.append(str(error))
                    continue
                final[rid] = {"verifier": member, **out}
                accepted_whole += whole
    if errors:
        raise SystemExit("Lembar verifikasi belum lengkap/valid:\n- " + "\n- ".join(errors[:40]))
    model = next(iter(llm.values())).get("model", "")
    prompt = next(iter(llm.values())).get("prompt_version", "")
    output = Path(output)
    with output.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["reviewId", "verifier", "model", "prompt_version", *ASPECTS])
        writer.writeheader()
        for rid in sorted(final):
            writer.writerow({"reviewId": rid, "model": model, "prompt_version": prompt, **final[rid]})
    n = len(final)
    summary = {
        "ulasan": n, "sel": n * len(ASPECTS),
        "tingkat_koreksi_keseluruhan": sum(changed.values()) / (n * len(ASPECTS)),
        "tingkat_koreksi_per_aspek": {a: changed[a] / n for a in ASPECTS},
        "ulasan_diterima_utuh": accepted_whole / n,
        "detik_per_ulasan": seconds / reviews_timed if reviews_timed else None,
        "koreksi_dari_ke": {},
    }
    transitions = Counter()
    for rid, row in final.items():
        for a in ASPECTS:
            if row[a] != llm[rid][a]:
                transitions[f"{a}: {llm[rid][a]} -> {row[a]}"] += 1
    summary["koreksi_dari_ke"] = dict(transitions.most_common())
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_path).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "export"):
        p = sub.add_parser(name)
        p.add_argument("--llm", type=Path, required=True, help="data/annotations/llm_<model>.csv")
        p.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
        p.add_argument("--raw", type=Path, default=Path("data/raw/com.telkom.tracencare_reviews.csv"))
        p.add_argument("--workspace", type=Path, default=WORKSPACE)
        if name == "prepare":
            p.add_argument("--mentions", type=Path, default=None,
                           help="mentions.csv dari llm_label.py untuk kolom Ringkasan LLM")
        else:
            p.add_argument("--output", type=Path, default=Path("data/annotations/verified.csv"))
            p.add_argument("--summary", type=Path, default=Path("results/verifikasi/ringkasan.json"))
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps(prepare(args.llm, args.split, args.raw, args.mentions, args.workspace), indent=2))
    else:
        print(json.dumps(export(args.llm, args.split, args.raw, args.workspace, args.output, args.summary),
                         indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
