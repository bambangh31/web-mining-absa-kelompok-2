"""Data bersama untuk semua model terlatih (B1, B4, B2, B2-L).

Semua model memakai ulasan latih dan validasi yang sama, label yang sama,
dan aturan keluaran yang sama, sehingga perbedaan skor berasal dari model.
"""

import csv
import json
import platform
import time
from pathlib import Path

from src.absa_schema import ASPECTS, NONE, SPECIFIC
from src.evaluate import evaluate, load_labels


def read_csv_dict(path, key="reviewId"):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return {row[key]: row for row in csv.DictReader(stream)}


def read_split(path="data/annotations/split.csv"):
    return {rid: row["split"] for rid, row in read_csv_dict(path).items()}


def enforce_umum(row):
    """Aturan skema pada keluaran model: umum kosong bila ada aspek khusus."""
    row = dict(row)
    if any(row[a] != NONE for a in SPECIFIC):
        row["umum"] = NONE
    return row


class Dataset:
    """Teks + label per split. `labels` dapat berupa verified.csv atau gold."""

    def __init__(self, clean_path, split_path, labels_path, train_split="gold_train", val_split="gold_val"):
        self.clean = read_csv_dict(clean_path)
        self.split = read_split(split_path)
        self.labels = load_labels(labels_path)
        self.labels_path = str(labels_path)
        self.train_ids = sorted(r for r, s in self.split.items() if s == train_split)
        self.val_ids = sorted(r for r, s in self.split.items() if s == val_split)
        for name, ids in (("latih", self.train_ids), ("validasi", self.val_ids)):
            missing = [r for r in ids if r not in self.labels]
            if missing:
                raise ValueError(f"{len(missing)} ulasan {name} tidak punya label di {labels_path}")

    def text(self, rid, field="text_model"):
        return self.clean[rid][field]

    def y(self, ids, aspect):
        return [self.labels[r][aspect] for r in ids]


def prediction_ids(dataset, predict_split=None, predict_from=None):
    """ID yang diprediksi: satu split (mis. gold_test) atau ID pada file label/Excel."""
    if predict_from:
        ids = sorted(load_labels(predict_from))
    else:
        ids = sorted(r for r, s in dataset.split.items() if s == predict_split)
    leak = set(ids) & (set(dataset.train_ids) | set(dataset.val_ids))
    if leak:
        print(f"Catatan: {len(leak)} ulasan latih/validasi dikeluarkan dari prediksi agar tidak bocor")
        ids = [r for r in ids if r not in leak]
    return ids


def write_predictions(path, code, seed, predictions):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["reviewId", "model_code", "seed", *ASPECTS])
        writer.writeheader()
        for rid, row in sorted(predictions.items()):
            writer.writerow({"reviewId": rid, "model_code": code, "seed": seed, **row})


def write_run(metrics_dir, code, seed, config, val_metrics, seconds_per_1000):
    metrics_dir = Path(metrics_dir)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    report = {"model_code": code, "seed": seed, "config": config, "python": platform.python_version(),
              "validasi": val_metrics, "detik_per_1000_ulasan": seconds_per_1000,
              "dibuat": time.strftime("%Y-%m-%d %H:%M:%S")}
    (metrics_dir / f"{code}_{seed}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    return report


def val_score(dataset, predictions):
    return evaluate(dataset.labels, predictions, dataset.val_ids)
