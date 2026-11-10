"""B2 / B2-L: IndoBERT-p1 sentence-pair untuk ABSA multi-aspek.

Setiap ulasan menjadi delapan pasangan (teks ulasan, deskripsi aspek). Model
mengklasifikasi tiap pasangan ke empat label (tidak_disebut, positif,
negatif, netral). Hiperparameter mengikuti method-decisions.md:

| | B2 base | B2-L large |
|---|---|---|
| encoder | indobenchmark/indobert-base-p1 | indobenchmark/indobert-large-p1 |
| lr | 2e-5 | 1e-5 |
| batch | 16 | 8 x akumulasi 2 |
| panjang | 160 token, potong hanya teks ulasan | sama |
| epoch | maks 10, early stopping patience 2 (F1 pasangan validasi) | sama |
| warmup / weight decay | 10% / 0,01 | sama |
| seed | 42, 43, 44 | sama |

Contoh:

  python src/model_indobert.py --variant base --labels data/annotations/verified.csv --predict-split gold_test
  python src/model_indobert.py --variant large --labels ... --predict-split gold_test   # Google Colab T4
"""

import argparse
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECT_DESCRIPTIONS, ASPECTS, LABELS  # noqa: E402
from src.model_data import (Dataset, enforce_umum, prediction_ids, val_score,  # noqa: E402
                            write_predictions, write_run)

VARIANTS = {
    "base": {"code": "B2", "model": "indobenchmark/indobert-base-p1", "lr": 2e-5, "batch": 16, "accum": 1},
    "large": {"code": "B2-L", "model": "indobenchmark/indobert-large-p1", "lr": 1e-5, "batch": 8, "accum": 2},
}
LABEL_ID = {label: i for i, label in enumerate(LABELS)}


def pairs(dataset, ids, with_labels=True):
    out = []
    for rid in ids:
        for a in ASPECTS:
            out.append((rid, a, dataset.text(rid), ASPECT_DESCRIPTIONS[a],
                        LABEL_ID[dataset.labels[rid][a]] if with_labels else -1))
    return out


def batches(items, size, shuffle, rng):
    order = list(range(len(items)))
    if shuffle:
        rng.shuffle(order)
    for i in range(0, len(order), size):
        yield [items[j] for j in order[i:i + size]]


def encode(tokenizer, chunk, max_length, device):
    enc = tokenizer([c[2] for c in chunk], [c[3] for c in chunk], truncation="only_first",
                    max_length=max_length, padding=True, return_tensors="pt")
    return {k: v.to(device) for k, v in enc.items()}


def predict(model, tokenizer, items, batch_size, max_length, device):
    import torch

    model.eval()
    rows = {}
    with torch.no_grad():
        for chunk in batches(items, batch_size * 4, False, None):
            logits = model(**encode(tokenizer, chunk, max_length, device)).logits
            for (rid, aspect, *_), index in zip(chunk, logits.argmax(-1).tolist()):
                rows.setdefault(rid, {})[aspect] = LABELS[index]
    return {rid: enforce_umum(row) for rid, row in rows.items()}


def train_one(dataset, variant, seed, predict_ids, max_epochs=10, patience=2, max_length=160,
              limit=None, log=print):
    import random

    import numpy as np
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    cfg = VARIANTS[variant]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"])
    # Konfigurasi bawaan IndoBERT-p1 memuat id2label lima kelas; ganti dengan empat label ABSA.
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg["model"], num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=LABEL_ID,
        ignore_mismatched_sizes=True).to(device)
    train_ids = dataset.train_ids[:limit] if limit else dataset.train_ids
    train_items = pairs(dataset, train_ids)
    val_items = pairs(dataset, dataset.val_ids)
    steps_per_epoch = -(-len(train_items) // (cfg["batch"] * cfg["accum"]))
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, int(0.1 * steps_per_epoch * max_epochs),
                                                steps_per_epoch * max_epochs)
    use_amp = device == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    rng = random.Random(seed)
    best, best_state, history, wait = -1.0, None, [], 0
    for epoch in range(1, max_epochs + 1):
        model.train()
        began = time.time()
        for step, chunk in enumerate(batches(train_items, cfg["batch"], True, rng), start=1):
            labels = torch.tensor([c[4] for c in chunk], device=device)
            with torch.autocast(device_type=device, enabled=use_amp, dtype=torch.float16):
                loss = model(**encode(tokenizer, chunk, max_length, device), labels=labels).loss / cfg["accum"]
            scaler.scale(loss).backward()
            if step % cfg["accum"] == 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                scheduler.step()
        val_pred = predict(model, tokenizer, val_items, cfg["batch"], max_length, device)
        f1 = val_score(dataset, val_pred)["f1_pasangan"]
        history.append({"epoch": epoch, "f1_pasangan_validasi": f1, "detik": round(time.time() - began, 1)})
        log(f"  {cfg['code']} seed {seed} epoch {epoch}: F1 pasangan validasi {f1:.3f}")
        if f1 > best:
            best, wait = f1, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    model.load_state_dict(best_state)
    val_pred = predict(model, tokenizer, val_items, cfg["batch"], max_length, device)
    began = time.perf_counter()
    test_pred = predict(model, tokenizer, pairs(dataset, predict_ids, with_labels=False),
                        cfg["batch"], max_length, device)
    seconds = (time.perf_counter() - began) / max(len(predict_ids), 1) * 1000
    config = {**cfg, "seed": seed, "device": device, "max_length": max_length, "max_epochs": max_epochs,
              "patience": patience, "riwayat": history, "label_latih": dataset.labels_path,
              "n_latih": len(train_ids), "n_pasangan_latih": len(train_items)}
    return test_pred, config, val_score(dataset, val_pred), seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variant", choices=VARIANTS, default="base")
    parser.add_argument("--seeds", default="42,43,44")
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--labels", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--predict-split")
    group.add_argument("--predict-from", type=Path)
    parser.add_argument("--max-epochs", type=int, default=10)
    parser.add_argument("--limit", type=int, default=None, help="uji asap: batasi ulasan latih")
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()
    dataset = Dataset(args.clean, args.split, args.labels)
    ids = prediction_ids(dataset, args.predict_split, args.predict_from)
    code = VARIANTS[args.variant]["code"]
    for seed in map(int, args.seeds.split(",")):
        predictions, config, val_metrics, seconds = train_one(dataset, args.variant, seed, ids,
                                                              args.max_epochs, limit=args.limit)
        write_predictions(args.out / "predictions" / f"{code}_{seed}.csv", code, seed, predictions)
        write_run(args.out / "metrics", code, seed, config, val_metrics, seconds)
        print(f"{code} seed {seed}: F1 pasangan validasi {val_metrics['f1_pasangan']:.3f}")


if __name__ == "__main__":
    main()
