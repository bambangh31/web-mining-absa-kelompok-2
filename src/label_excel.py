"""Baca/tulis lembar anotasi rinci (format "Label Manual Sentimen Komentar").

Satu baris = satu penyebutan aspek dalam satu ulasan:

| No | reviewId | Tanggal | Versi Aplikasi | Rating | Komentar |
| Kata Aspek (persis dari ulasan) | Aspek (seragam) | Kategori Aspek | Label |
| Bukti dari komentar |

Lembar yang sama dipakai untuk label manual dan label LLM, sehingga keduanya
bisa dibandingkan baris demi baris maupun per ulasan (ACSA). Konversi ke label
per ulasan memakai ``absa_schema.aggregate_mentions``.
"""

import csv
from collections import Counter, OrderedDict
from pathlib import Path

try:
    from src.absa_schema import ASPECTS, ASPECT_NAMES, ASPECT_TITLES, aggregate_mentions, aspect_from_name, label_from_name
except ImportError:
    from absa_schema import ASPECTS, ASPECT_NAMES, ASPECT_TITLES, aggregate_mentions, aspect_from_name, label_from_name

SHEET = "Data Berlabel"
HEADER = ["No", "reviewId", "Tanggal", "Versi Aplikasi", "Rating", "Komentar",
          "Kata Aspek (persis dari ulasan)", "Aspek (seragam)", "Kategori Aspek", "Label",
          "Bukti dari komentar"]
WIDTHS = [5, 38, 19, 10, 8, 70, 26, 22, 20, 11, 50]
CATEGORY_ORDER = {a: i for i, a in enumerate(ASPECTS)}


def read_raw(path="data/raw/com.telkom.tracencare_reviews.csv"):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return {row["reviewId"]: row for row in csv.DictReader(stream)}


def read_mentions(path, sheet=SHEET):
    """Kembalikan (meta per ulasan, daftar penyebutan) dari lembar Excel."""
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    ws = wb[sheet]
    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h is not None else "" for h in next(rows)]
    if header[:len(HEADER)] != HEADER:
        raise ValueError(f"{path}: header harus {HEADER}")
    reviews, mentions = OrderedDict(), []
    for values in rows:
        row = dict(zip(HEADER, values))
        if not row["reviewId"]:
            continue
        rid = str(row["reviewId"]).strip()
        reviews.setdefault(rid, {
            "No": row["No"], "reviewId": rid, "Tanggal": row["Tanggal"],
            "Versi Aplikasi": row["Versi Aplikasi"] or "", "Rating": row["Rating"],
            "Komentar": row["Komentar"]})
        if not row["Kategori Aspek"]:
            continue  # ulasan tanpa aspek (semua tidak disebut)
        mentions.append({
            "reviewId": rid, "kata": row["Kata Aspek (persis dari ulasan)"] or "",
            "seragam": row["Aspek (seragam)"] or "",
            "aspek": aspect_from_name(row["Kategori Aspek"]),
            "label": label_from_name(row["Label"]), "bukti": row["Bukti dari komentar"] or ""})
    wb.close()
    return reviews, mentions


def review_labels(reviews, mentions):
    """Label ACSA per ulasan untuk semua ulasan di lembar."""
    grouped = {rid: [] for rid in reviews}
    for m in mentions:
        grouped.setdefault(m["reviewId"], []).append((m["aspek"], m["label"]))
    return {rid: aggregate_mentions(items) for rid, items in grouped.items()}


def check_against_raw(reviews, mentions, raw):
    """Pastikan identitas ulasan sama persis dengan data asli dan kata/bukti ada di komentar."""
    problems = []
    for rid, meta in reviews.items():
        original = raw.get(rid)
        if original is None:
            problems.append((rid, "reviewId tidak ada di data asli"))
            continue
        if meta["Komentar"] != original["content"]:
            problems.append((rid, "komentar berbeda dari data asli"))
        if (meta["Versi Aplikasi"] or "") != original["reviewCreatedVersion"]:
            problems.append((rid, "versi aplikasi berbeda dari data asli"))
        if str(meta["Rating"]) != original["score"] or str(meta["Tanggal"]) != original["at"]:
            problems.append((rid, "rating/tanggal berbeda dari data asli"))
    for m in mentions:
        text = reviews[m["reviewId"]]["Komentar"]
        if m["kata"] and m["kata"] not in text:
            problems.append((m["reviewId"], f"kata aspek tidak persis: {m['kata']!r}"))
        for piece in str(m["bukti"]).split("; "):
            if piece and piece not in text:
                problems.append((m["reviewId"], f"bukti tidak persis: {piece!r}"))
    return problems


def write_mentions(path, reviews, mentions):
    """Tulis lembar dengan tata letak sama seperti lembar label manual."""
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, Side
    from openpyxl.utils import get_column_letter

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    head_font, body_font = Font(name="Arial", size=10, bold=True), Font(name="Arial", size=10)
    center = Alignment(wrap_text=True, vertical="center", horizontal="center")
    top_center = Alignment(wrap_text=True, vertical="top", horizontal="center")
    top_left = Alignment(wrap_text=True, vertical="top")

    def style(cell, header=False, left=False):
        cell.font = head_font if header else body_font
        cell.border = border
        cell.alignment = center if header else (top_left if left else top_center)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = SHEET
    for c, title in enumerate(HEADER, start=1):
        style(ws.cell(1, c, title), header=True)
        ws.column_dimensions[get_column_letter(c)].width = WIDTHS[c - 1]
    ws.row_dimensions[1].height = 30
    by_review = OrderedDict((rid, []) for rid in reviews)
    for m in mentions:
        by_review[m["reviewId"]].append(m)
    r = 2
    for number, (rid, items) in enumerate(by_review.items(), start=1):
        meta = reviews[rid]
        items = sorted(items, key=lambda m: CATEGORY_ORDER[m["aspek"]]) or [None]
        for m in items:
            values = [number, rid, meta["Tanggal"], meta["Versi Aplikasi"] or None, meta["Rating"],
                      meta["Komentar"]]
            values += ([m["kata"], m["seragam"], ASPECT_NAMES[m["aspek"]], m["label"], m["bukti"]]
                       if m else [None, None, None, None, None])
            for c, value in enumerate(values, start=1):
                style(ws.cell(r, c, value), left=c in (6, 7, 8, 11))
            ws.row_dimensions[r].height = 25.5
            r += 1
    last = r - 1
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:K{last}"
    ws.sheet_view.zoomScale = 85

    rng_h, rng_i, rng_j, rng_b = (f"'{SHEET}'!${c}$2:${c}${last}" for c in "HIJB")

    def summary(title, first_col, keys, rng):
        sheet = wb.create_sheet(title)
        for c, name in enumerate([first_col, "Jumlah", "positif", "negatif", "netral"], start=1):
            style(sheet.cell(1, c, name), header=True)
        for i, key in enumerate(keys, start=2):
            sheet.cell(i, 1, key)
            sheet.cell(i, 2, f"=COUNTIF({rng},A{i})")
            for c, lab in zip((3, 4, 5), ("positif", "negatif", "netral")):
                sheet.cell(i, c, f'=COUNTIFS({rng},$A{i},{rng_j},"{lab}")')
            for c in range(1, 6):
                style(sheet.cell(i, c), left=c == 1)
        sheet.column_dimensions["A"].width = 26
        for col in "BCDE":
            sheet.column_dimensions[col].width = 10
        return sheet, len(keys) + 2

    counts = Counter(m["seragam"] for m in mentions)
    first = {}
    for m in mentions:
        first.setdefault(m["seragam"], len(first))
    summary("Kata Aspek", "Aspek (seragam)", sorted(counts, key=lambda t: (-counts[t], first[t])), rng_h)
    sheet, total = summary("Kategori Aspek", "Kategori Aspek", [ASPECT_NAMES[a] for a in ASPECTS], rng_i)
    sheet.cell(total, 1, "Total")
    for c, col in zip(range(2, 6), "BCDE"):
        sheet.cell(total, c, f"=SUM({col}2:{col}{total - 1})")
    for c in range(1, 6):
        style(sheet.cell(total, c), header=True)

    lu = wb.create_sheet("Label per Ulasan")
    titles = ["No", "reviewId", "Rating", "Komentar"] + [ASPECT_TITLES[a] for a in ASPECTS]
    for c, name in enumerate(titles, start=1):
        style(lu.cell(1, c, name), header=True)
        lu.column_dimensions[get_column_letter(c)].width = {1: 5, 2: 38, 3: 8, 4: 70}.get(c, 13)
    for i, (rid, meta) in enumerate(reviews.items(), start=2):
        for c, value in enumerate([i - 1, rid, meta["Rating"], meta["Komentar"]], start=1):
            lu.cell(i, c, value)
        for j, aspect in enumerate(ASPECTS):
            cat = ASPECT_NAMES[aspect]

            def cnt(lab):
                return f'COUNTIFS({rng_b},$B{i},{rng_i},"{cat}",{rng_j},"{lab}")'
            core = (f'IF({cnt("positif")}+{cnt("negatif")}+{cnt("netral")}=0,"tidak disebut",'
                    f'IF({cnt("positif")}+{cnt("negatif")}=0,"netral",'
                    f'IF({cnt("positif")}>{cnt("negatif")},"positif","negatif")))')
            if aspect == "umum":
                core = (f'IF(COUNTIFS({rng_b},$B{i},{rng_i},"<>umum",{rng_i},"<>")>0,'
                        f'"tidak disebut",{core})')
            lu.cell(i, 5 + j, "=" + core)
        for c in range(1, len(titles) + 1):
            style(lu.cell(i, c), left=c == 4)
    lu.freeze_panes = "E2"
    lu.auto_filter.ref = f"A1:{get_column_letter(len(titles))}{len(reviews) + 1}"
    lu.sheet_view.zoomScale = 85
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return last - 1


def write_label_csv(path, labels, extra=None):
    """CSV tanpa teks: reviewId (+ kolom tambahan) + delapan kolom aspek."""
    extra = extra or {}
    fields = ["reviewId", *extra, *ASPECTS]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for rid, row in labels.items():
            writer.writerow({"reviewId": rid, **extra, **{a: row[a] for a in ASPECTS}})


def read_label_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    missing = set(ASPECTS) - set(rows[0] if rows else ASPECTS)
    if missing:
        raise ValueError(f"{path}: kolom aspek hilang: {sorted(missing)}")
    return {r["reviewId"]: {a: r[a] for a in ASPECTS} for r in rows}
