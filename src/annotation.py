"""Lembar anotasi manusia, audit kesepakatan, dan ekspor label ABSA.

Tidak mengambil sampel ulang, memprediksi label, atau mengubah split Efraim.
Jalankan ``python src/annotation.py --help`` dari akar repository.
"""

import argparse
import csv
import hashlib
import itertools
import json
import random
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

try:  # dijalankan sebagai modul (tes, notebook) atau sebagai skrip
    from src.absa_schema import ASPECTS, LABELS
except ImportError:  # python src/annotation.py
    from absa_schema import ASPECTS, LABELS

MEMBERS = ("bambang", "efraim", "jap", "geraldyn")
COUNTS = {"kalibrasi": 50, "gold_train": 400, "gold_val": 100, "gold_test": 300}
LABEL_FIELDS = ["reviewId", "annotator", *ASPECTS]
SHEET_FIELDS = ["reviewId", "annotator", "text_llm", *ASPECTS, "catatan"]
RESOLUTION_FIELDS = ["reviewId", "aspek", "labels_awal", "final_label", "adjudicator", "catatan"]
DEFAULT_WORKSPACE = Path("data/annotation_workspace")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path, required, allowed=None):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not set(required) <= set(fields):
            raise ValueError(f"{path}: header wajib {', '.join(required)}; header harus unik")
        if allowed is not None and not set(fields) <= set(allowed):
            raise ValueError(f"{path}: kolom tidak dikenal: {set(fields) - set(allowed)}")
        rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError(f"{path}: jumlah sel tidak sesuai header")
        return rows


def write_csv(path, fields, rows):
    # BOM agar teks Indonesia terbaca saat dibuka di Excel Windows.
    with Path(path).open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def unique_rows(rows, source):
    result = {}
    for row in rows:
        key = row["reviewId"]
        if not key.strip() or key != key.strip() or key in result:
            raise ValueError(f"{source}: reviewId kosong, berspasi, atau duplikat: {key!r}")
        result[key] = row
    return result


def validate_labels(row, source):
    for aspect in ASPECTS:
        if row[aspect] not in LABELS:
            raise ValueError(f"{source}: {row['reviewId']} / {aspect}: label kosong/tidak valid")
    if row["umum"] != "tidak_disebut" and any(row[a] != "tidak_disebut" for a in ASPECTS[:-1]):
        raise ValueError(f"{source}: {row['reviewId']}: umum tidak boleh bersamaan dengan aspek khusus")


def cohen_kappa(left, right):
    """Kappa nominal tanpa bobot. None berarti tidak terdefinisi, bukan nol."""
    if not left or len(left) != len(right):
        raise ValueError("Kappa memerlukan pasangan label dengan panjang sama dan tidak kosong")
    n = len(left)
    a, b = Counter(left), Counter(right)
    observed = Fraction(sum(x == y for x, y in zip(left, right)), n)
    expected = sum((Fraction(a[k] * b[k], n * n) for k in set(a) | set(b)), Fraction(0))
    return None if expected == 1 else float((observed - expected) / (1 - expected))


def assign(selected):
    """Pembagian deterministik (seed 42); dipakai juga oleh lembar verifikasi."""
    rng = random.Random(42)
    assignments = {"kalibrasi": {m: [] for m in MEMBERS}, "gold": {m: [] for m in MEMBERS}}
    pairs = list(itertools.combinations(MEMBERS, 2))
    for name in COUNTS:
        ids = sorted(key for key, row in selected.items() if row["split"] == name)
        rng.shuffle(ids)
        phase = "kalibrasi" if name == "kalibrasi" else "gold"
        for index, key in enumerate(ids):
            owners = MEMBERS if phase == "kalibrasi" else (
                pairs[index % len(pairs)] if name == "gold_test" else (MEMBERS[index % len(MEMBERS)],)
            )
            for member in owners:
                assignments[phase][member].append(key)
    return assignments


def prepare(reviews_path, split_path, workspace):
    reviews_path, split_path, workspace = map(Path, (reviews_path, split_path, workspace))
    reviews = unique_rows(read_csv(reviews_path, ["reviewId", "text_llm"]), reviews_path)
    split = unique_rows(read_csv(split_path, ["reviewId", "split"], ["reviewId", "split"]), split_path)
    unknown = set(r["split"] for r in split.values()) - (set(COUNTS) | {"silver"})
    if unknown or not set(split) <= set(reviews):
        raise ValueError("Split tidak dikenal atau ada ID split yang tidak ditemukan dalam reviews_clean.csv")
    for name, count in COUNTS.items():
        actual = sum(r["split"] == name for r in split.values())
        if actual != count:
            raise ValueError(f"Split {name}: perlu {count} ulasan, ditemukan {actual}; jangan sampling ulang otomatis")
    selected = {key: row for key, row in split.items() if row["split"] != "silver"}
    if any(not reviews[key]["text_llm"].strip() for key in selected):
        raise ValueError("Teks ulasan untuk anotasi tidak boleh kosong")
    assignments = assign(selected)
    # Semua pemeriksaan input selesai sebelum membuat keluaran.
    workspace.mkdir(parents=True, exist_ok=False)
    text_hashes = {}
    for phase, members in assignments.items():
        for member, ids in members.items():
            rows = []
            for key in ids:
                text = reviews[key]["text_llm"]
                # Escape hanya pada lembar kerja, tidak pada teks model/dataset.
                if text.lstrip().startswith(("=", "+", "-", "@")):
                    text = "'" + text
                text_hashes[key] = hashlib.sha256(text.encode("utf-8")).hexdigest()
                rows.append({"reviewId": key, "annotator": member, "text_llm": text,
                             **{a: "" for a in ASPECTS}, "catatan": ""})
            write_csv(workspace / f"{phase}_{member}.csv", SHEET_FIELDS, rows)
    manifest = {
        "schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {"reviews_clean": digest(reviews_path), "split": digest(split_path)},
        "split_counts": dict(Counter(r["split"] for r in split.values())),
        "assignment_seed": 42, "assignments": assignments,
        "text_sha256": text_hashes,
    }
    (workspace / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def load_phase(workspace, phase):
    workspace = Path(workspace)
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Versi manifest tidak didukung")
    expected = manifest["assignments"][phase]
    if set(expected) != set(MEMBERS):
        raise ValueError("Daftar anotator pada manifest berubah")
    counts = Counter(key for ids in expected.values() for key in ids)
    if phase == "kalibrasi":
        if len(counts) != 50 or set(counts.values()) != {4}:
            raise ValueError("Kalibrasi harus 50 ulasan yang sama untuk empat anotator")
    elif len(counts) != 800 or Counter(counts.values()) != {1: 500, 2: 300}:
        raise ValueError("Gold harus 500 ulasan berlabel tunggal dan 300 berlabel ganda")
    labels, hashes = {}, {}
    for member in MEMBERS:
        path = workspace / f"{phase}_{member}.csv"
        rows = unique_rows(read_csv(path, SHEET_FIELDS, SHEET_FIELDS), path)
        if len(expected[member]) != len(set(expected[member])) or set(rows) != set(expected[member]):
            raise ValueError(f"{path}: ID hilang, tambahan, atau tidak sesuai pembagian")
        for row in rows.values():
            if row["annotator"] != member:
                raise ValueError(f"{path}: nama anotator tidak sesuai lembar")
            if hashlib.sha256(row["text_llm"].encode("utf-8")).hexdigest() != manifest["text_sha256"][row["reviewId"]]:
                raise ValueError(f"{path}: {row['reviewId']}: teks/ID berubah; jangan mengurutkan satu kolom saja")
            validate_labels(row, path)
        labels[member] = rows
        hashes[member] = digest(path)
    return labels, hashes, manifest


def inspect_phase(labels):
    grouped = {}
    for member, rows in labels.items():
        for key, row in rows.items():
            grouped.setdefault(key, {})[member] = row
    conflicts, agreement = [], []
    for key, owners in sorted(grouped.items()):
        for aspect in ASPECTS:
            values = {m: row[aspect] for m, row in owners.items()}
            if len(set(values.values())) > 1:
                conflicts.append({"reviewId": key, "aspek": aspect,
                                  "labels_awal": json.dumps(values, sort_keys=True),
                                  "final_label": "", "adjudicator": "", "catatan": ""})
    for a, b in itertools.combinations(MEMBERS, 2):
        common = sorted(set(labels[a]) & set(labels[b]))
        if not common:
            continue
        for aspect in ASPECTS:
            left = [labels[a][key][aspect] for key in common]
            right = [labels[b][key][aspect] for key in common]
            kappa = cohen_kappa(left, right)
            agreement.append({"anotator_a": a, "anotator_b": b, "aspek": aspect,
                              "n": len(common), "agreement": sum(x == y for x, y in zip(left, right)) / len(common),
                              "kappa": kappa,
                              "catatan": "tidak_terdefinisi_satu_kelas" if kappa is None else ""})
    return grouped, conflicts, agreement


def audit(workspace, phase, output):
    labels, hashes, manifest = load_phase(workspace, phase)
    grouped, conflicts, agreement = inspect_phase(labels)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / "resolutions.csv", RESOLUTION_FIELDS, conflicts)
    write_csv(output / "agreement.csv", list(agreement[0]), agreement)
    report = {"phase": phase, "review_count": len(grouped), "conflict_cells": len(conflicts),
              "annotation_sha256": hashes, "source_sha256": manifest["source_sha256"],
              "kappa_stage": "sebelum_adjudikasi", "agreement": agreement}
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def finalize(workspace, phase, resolutions_path, output):
    labels, hashes, manifest = load_phase(workspace, phase)
    grouped, conflicts, agreement = inspect_phase(labels)
    needed = {(r["reviewId"], r["aspek"]) for r in conflicts}
    resolutions = {}
    if resolutions_path:
        for row in read_csv(resolutions_path, RESOLUTION_FIELDS, RESOLUTION_FIELDS):
            key = (row["reviewId"], row["aspek"])
            if key in resolutions or key not in needed:
                raise ValueError("Keputusan berulang atau tidak cocok dengan perbedaan label terbaru")
            if row["final_label"] not in LABELS or row["adjudicator"] not in MEMBERS or not row["catatan"].strip():
                raise ValueError("Setiap keputusan perlu label sah, adjudicator, dan alasan pada catatan")
            owners = grouped[row["reviewId"]]
            current = {m: r[row["aspek"]] for m, r in owners.items()}
            if json.loads(row["labels_awal"]) != current:
                raise ValueError("Label awal berubah setelah audit; buat audit baru")
            if phase == "gold" and row["adjudicator"] in owners:
                raise ValueError("Perbedaan gold_test harus diselesaikan anotator ketiga")
            resolutions[key] = row
    if set(resolutions) != needed:
        raise ValueError(f"Ada {len(needed - set(resolutions))} sel yang belum diselesaikan; gold belum boleh diekspor")
    final, provenance = [], []
    for key, owners in sorted(grouped.items()):
        row = {"reviewId": key}
        for aspect in ASPECTS:
            decision = resolutions.get((key, aspect))
            row[aspect] = decision["final_label"] if decision else next(iter(owners.values()))[aspect]
            provenance.append({"reviewId": key, "aspek": aspect,
                               "sumber": "adjudikasi" if decision else ("kesepakatan" if len(owners) > 1 else "anotasi_tunggal"),
                               "annotators": ";".join(sorted(owners)),
                               "adjudicator": decision["adjudicator"] if decision else ""})
        validate_labels(row, "hasil akhir")
        final.append(row)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / f"{phase}.csv", ["reviewId", *ASPECTS], final)
    for member, rows in labels.items():
        write_csv(output / f"{phase}_{member}.csv", LABEL_FIELDS,
                  [{f: row[f] for f in LABEL_FIELDS} for _, row in sorted(rows.items())])
    write_csv(output / "provenance.csv", list(provenance[0]), provenance)
    report = {"phase": phase, "review_count": len(final), "resolved_cells": len(resolutions),
              "source_sha256": manifest["source_sha256"], "annotation_sha256": hashes,
              "resolutions_sha256": digest(resolutions_path) if resolutions_path else None,
              "kappa_stage": "sebelum_adjudikasi", "agreement": agreement}
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="Buat lembar kosong dari clean + split yang disepakati")
    prep.add_argument("--reviews", type=Path, required=True)
    prep.add_argument("--split", type=Path, required=True)
    prep.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    for name in ("audit", "finalize"):
        command = commands.add_parser(name)
        command.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
        command.add_argument("--phase", choices=("kalibrasi", "gold"), required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "finalize":
            command.add_argument("--resolutions", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.reviews, args.split, args.workspace)
            print(json.dumps({phase: {m: len(ids) for m, ids in members.items()}
                              for phase, members in result["assignments"].items()}, indent=2))
        else:
            if args.command == "audit":
                result = audit(args.workspace, args.phase, args.output)
            else:
                result = finalize(args.workspace, args.phase, args.resolutions, args.output)
            print(json.dumps({k: result[k] for k in ("phase", "review_count")}, indent=2))
        print("Hasil disimpan. Tidak ada label yang diprediksi atau diisi otomatis.")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"Gagal: {error}\n")


if __name__ == "__main__":
    main()
