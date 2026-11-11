"""Bandingkan lembar label manual dengan lembar label LLM (format sama).

Dua tingkat perbandingan:

1. Per ulasan (ACSA, delapan aspek): label manual dipakai sebagai acuan.
   F1 pasangan, F1 deteksi aspek, macro-F1 sentimen, kesepakatan, dan
   Cohen's kappa per aspek (`evaluate.py`).
2. Per penyebutan: berapa penyebutan (kategori + label) di lembar manual yang
   juga ditemukan LLM, dan sebaliknya; serta kesamaan aspek seragam.

  python src/compare_labels.py --manual "Label Manual Sentimen Komentar Satu Sehat.xlsx" \
      --llm "Label LLM Sentimen Komentar Satu Sehat.xlsx" \
      --excel-out "Perbandingan Label Manual dan LLM.xlsx" --out results/perbandingan_manual_llm
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import label_excel  # noqa: E402
from src.absa_schema import ASPECT_TITLES, ASPECTS, LABEL_NAMES, NONE  # noqa: E402
from src.evaluate import evaluate, write_tables  # noqa: E402


def mention_overlap(manual, llm):
    def keys(mentions, with_label):
        out = Counter()
        for m in mentions:
            out[(m["reviewId"], m["aspek"], m["label"]) if with_label else (m["reviewId"], m["aspek"])] += 1
        return out

    result = {}
    for name, with_label in (("kategori_dan_label", True), ("kategori_saja", False)):
        a, b = set(keys(manual, with_label)), set(keys(llm, with_label))
        both = len(a & b)
        p, r = both / len(b) if b else 0.0, both / len(a) if a else 0.0
        result[name] = {"manual": len(a), "llm": len(b), "sama": both, "presisi": p, "recall": r,
                        "f1": 2 * p * r / (p + r) if p + r else 0.0}
    terms_m = {(m["reviewId"], m["seragam"].lower()) for m in manual}
    terms_l = {(m["reviewId"], m["seragam"].lower()) for m in llm}
    result["aspek_seragam_sama"] = {"manual": len(terms_m), "llm": len(terms_l), "sama": len(terms_m & terms_l)}
    return result


def write_excel(path, reviews, gold, pred, results, overlap):
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    bold, normal = Font(name="Arial", size=10, bold=True), Font(name="Arial", size=10)
    center = Alignment(wrap_text=True, vertical="center", horizontal="center")
    top = Alignment(wrap_text=True, vertical="top")
    diff = PatternFill("solid", fgColor="FCE4D6")

    def put(ws, r, c, value, head=False, left=False):
        cell = ws.cell(r, c, value)
        cell.font, cell.border = (bold if head else normal), border
        cell.alignment = top if left else center
        return cell

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ringkasan"
    head = ["Kategori Aspek", "Disebut (manual)", "Disebut (LLM)", "Kesepakatan 4 label", "Kappa",
            "F1 pasangan", "F1 deteksi", "Macro-F1 sentimen"]
    for c, h in enumerate(head, start=1):
        put(ws, 1, c, h, head=True)
    r = 2
    for a in ASPECTS:
        v = results["per_aspek"][a]
        vals = [ASPECT_TITLES[a], v["n_gold_disebut"], v["n_pred_disebut"], v["akurasi_4_label"], v["kappa"],
                v["f1_pasangan"], v["f1_deteksi"], v["macro_f1_sentimen"]]
        for c, value in enumerate(vals, start=1):
            cell = put(ws, r, c, round(value, 3) if isinstance(value, float) else value, left=c == 1)
            if isinstance(value, float):
                cell.number_format = "0.000"
        r += 1
    put(ws, r, 1, "Keseluruhan", head=True)
    total = [sum(results["per_aspek"][a]["n_gold_disebut"] for a in ASPECTS),
             sum(results["per_aspek"][a]["n_pred_disebut"] for a in ASPECTS),
             None, None, results["f1_pasangan"], results["f1_deteksi_micro"], results["macro_f1_sentimen_rata2"]]
    for c, value in enumerate(total, start=2):
        cell = put(ws, r, c, round(value, 3) if isinstance(value, float) else value, head=True)
        if isinstance(value, float):
            cell.number_format = "0.000"
    r += 2
    notes = [
        f"Jumlah ulasan: {results['n_ulasan']}. Label manual dipakai sebagai acuan.",
        f"Ulasan dengan kedelapan label persis sama: {results['ulasan_persis_sama']:.1%}.",
        f"Penyebutan kategori + label yang sama: {overlap['kategori_dan_label']['sama']} dari "
        f"{overlap['kategori_dan_label']['manual']} (manual) dan {overlap['kategori_dan_label']['llm']} (LLM).",
        "F1 pasangan: kecocokan pasangan (ulasan, aspek, sentimen) yang disebut.",
        "Kappa: kesepakatan empat label per aspek setelah dikoreksi faktor kebetulan.",
    ]
    for note in notes:
        ws.cell(r, 1, note).font = normal
        r += 1
    ws.column_dimensions["A"].width = 24
    for c in range(2, len(head) + 1):
        ws.column_dimensions[get_column_letter(c)].width = 14

    ws = wb.create_sheet("Per Ulasan")
    head = ["No", "reviewId", "Rating", "Komentar"]
    for a in ASPECTS:
        head += [f"{ASPECT_TITLES[a]} Manual", f"{ASPECT_TITLES[a]} LLM"]
    head.append("Jumlah Beda")
    for c, h in enumerate(head, start=1):
        put(ws, 1, c, h, head=True)
    for i, (rid, meta) in enumerate(reviews.items(), start=2):
        put(ws, i, 1, i - 1)
        put(ws, i, 2, rid, left=True)
        put(ws, i, 3, meta["Rating"])
        put(ws, i, 4, meta["Komentar"], left=True)
        beda = 0
        for k, a in enumerate(ASPECTS):
            g, p = gold[rid][a], pred[rid][a]
            c1 = put(ws, i, 5 + 2 * k, LABEL_NAMES[g])
            c2 = put(ws, i, 6 + 2 * k, LABEL_NAMES[p])
            if g != p:
                beda += 1
                c1.fill = c2.fill = diff
        put(ws, i, len(head), beda)
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 7
    ws.column_dimensions["D"].width = 60
    for c in range(5, len(head) + 1):
        ws.column_dimensions[get_column_letter(c)].width = 11
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(head))}{len(reviews) + 1}"

    ws = wb.create_sheet("Daftar Beda")
    head = ["No", "reviewId", "Komentar", "Kategori Aspek", "Manual", "LLM", "Jenis Beda"]
    for c, h in enumerate(head, start=1):
        put(ws, 1, c, h, head=True)
    r = 2
    for rid, meta in reviews.items():
        for a in ASPECTS:
            g, p = gold[rid][a], pred[rid][a]
            if g == p:
                continue
            kind = ("LLM menambah aspek" if g == NONE else "LLM melewatkan aspek" if p == NONE
                    else "sentimen berbeda")
            for c, value in enumerate([r - 1, rid, meta["Komentar"], ASPECT_TITLES[a], LABEL_NAMES[g],
                                       LABEL_NAMES[p], kind], start=1):
                put(ws, r, c, value, left=c in (2, 3))
            r += 1
    for c, w in enumerate([5, 12, 60, 22, 13, 13, 22], start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:G{max(r - 1, 1)}"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manual", type=Path, default=Path("Label Manual Sentimen Komentar Satu Sehat.xlsx"))
    parser.add_argument("--llm", type=Path, default=Path("Label LLM Sentimen Komentar Satu Sehat.xlsx"))
    parser.add_argument("--excel-out", type=Path, default=Path("Perbandingan Label Manual dan LLM.xlsx"))
    parser.add_argument("--out", type=Path, default=Path("results/perbandingan_manual_llm"))
    args = parser.parse_args()
    m_reviews, m_mentions = label_excel.read_mentions(args.manual)
    l_reviews, l_mentions = label_excel.read_mentions(args.llm)
    if set(m_reviews) != set(l_reviews):
        raise SystemExit("Kedua lembar harus berisi ulasan yang sama")
    gold = label_excel.review_labels(m_reviews, m_mentions)
    pred = label_excel.review_labels(l_reviews, l_mentions)
    results = evaluate(gold, pred)
    overlap = mention_overlap(m_mentions, l_mentions)
    differences = Counter()
    for rid in gold:
        for a in ASPECTS:
            g, p = gold[rid][a], pred[rid][a]
            if g != p:
                differences["LLM menambah aspek" if g == NONE else "LLM melewatkan aspek" if p == NONE
                            else "sentimen berbeda"] += 1
    write_tables(args.out, {"Gemini vs manual": results})
    report = {"manual": str(args.manual), "llm": str(args.llm), "ulasan": len(gold),
              "per_ulasan": results, "per_penyebutan": overlap, "jenis_beda": dict(differences)}
    (args.out / "perbandingan.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    write_excel(args.excel_out, m_reviews, gold, pred, results, overlap)
    print(json.dumps({"ulasan": len(gold), "f1_pasangan": round(results["f1_pasangan"], 3),
                      "f1_deteksi_micro": round(results["f1_deteksi_micro"], 3),
                      "macro_f1_sentimen_rata2": round(results["macro_f1_sentimen_rata2"], 3),
                      "kappa_per_aspek": {a: round(results["per_aspek"][a]["kappa"], 3)
                                          for a in ASPECTS if results["per_aspek"][a]["kappa"] is not None},
                      "jenis_beda": dict(differences), "per_penyebutan": overlap["kategori_dan_label"]},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
