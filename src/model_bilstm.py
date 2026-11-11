"""B4: BiLSTM + embedding fastText `cc.id.300` untuk ABSA multi-aspek.

Satu encoder BiLSTM dipakai bersama; max-pooling; delapan kepala linear
(satu per aspek, empat kelas). Loss: cross-entropy berbobot kelas per aspek,
dijumlah untuk semua aspek. Pengaturan mengikuti method-decisions.md:
token maks 128, embedding 300 dimensi dibekukan, [UNK] dilatih, BiLSTM
1 lapis 128 unit per arah, dropout 0,5, Adam 1e-3, batch 32, maks 30 epoch,
early stopping patience 3 (F1 pasangan validasi), seed 42/43/44.

Vektor fastText (sekitar 1,2 GB terkompresi) diunduh terpisah dari
https://fasttext.cc/docs/en/crawl-vectors.html lalu diekstrak menjadi
`data/external/cc.id.300.vec`. Hanya kata yang muncul di data dimuat.

  python src/model_bilstm.py --labels data/annotations/verified.csv --predict-split gold_test
"""

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECTS, LABELS  # noqa: E402
from src.model_data import (Dataset, enforce_umum, prediction_ids, val_score,  # noqa: E402
                            write_predictions, write_run)
from src.text_features import tokenize  # noqa: E402

MAX_TOKENS = 128
PAD, UNK = "[PAD]", "[UNK]"


def build_vocab(texts):
    words = Counter(token for text in texts for token in tokenize(text))
    return [PAD, UNK] + sorted(words)


def load_vectors(path, vocab, dim=300, seed=42):
    """Matriks embedding untuk kosakata data; kata tanpa vektor -> [UNK]."""
    import numpy as np

    index = {w: i for i, w in enumerate(vocab)}
    matrix = np.zeros((len(vocab), dim), dtype="float32")
    found = set()
    if path and Path(path).exists():
        with Path(path).open(encoding="utf-8", errors="ignore") as stream:
            first = stream.readline().split()
            if len(first) != 2:  # file tanpa baris header
                stream.seek(0)
            for line in stream:
                word, _, rest = line.rstrip().partition(" ")
                if word in index and word not in found:
                    values = rest.split()
                    if len(values) == dim:
                        matrix[index[word]] = np.asarray(values, dtype="float32")
                        found.add(word)
    known = [w for w in vocab[2:] if w in found]
    return matrix, {w for w in known}, len(known) / max(len(vocab) - 2, 1)


def encode(text, word_index, known):
    ids = [word_index[t] if t in known else 1 for t in tokenize(text)[:MAX_TOKENS]]
    return ids or [1]


def build_model(matrix, hidden=128, dropout=0.5):
    import torch
    from torch import nn

    class BiLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            weights = torch.tensor(matrix)
            self.frozen = nn.Embedding.from_pretrained(weights, freeze=True, padding_idx=0)
            self.unk = nn.Parameter(torch.zeros(weights.shape[1]).normal_(0, 0.1))
            self.lstm = nn.LSTM(weights.shape[1], hidden, batch_first=True, bidirectional=True)
            self.dropout = nn.Dropout(dropout)
            self.heads = nn.ModuleList([nn.Linear(2 * hidden, len(LABELS)) for _ in ASPECTS])

        def forward(self, ids, lengths):
            emb = self.frozen(ids)
            emb = torch.where((ids == 1).unsqueeze(-1), self.unk.expand_as(emb), emb)
            packed = nn.utils.rnn.pack_padded_sequence(emb, lengths.cpu(), batch_first=True, enforce_sorted=False)
            out, _ = self.lstm(packed)
            out, _ = nn.utils.rnn.pad_packed_sequence(out, batch_first=True, padding_value=-1e4)
            pooled = self.dropout(out.max(dim=1).values)
            return [head(pooled) for head in self.heads]

    return BiLSTM()


def collate(seqs):
    import torch

    lengths = torch.tensor([len(s) for s in seqs])
    ids = torch.zeros(len(seqs), int(lengths.max()), dtype=torch.long)
    for i, s in enumerate(seqs):
        ids[i, :len(s)] = torch.tensor(s)
    return ids, lengths


def predict(model, seqs, ids_order, batch=128):
    import torch

    model.eval()
    rows = {}
    with torch.no_grad():
        for i in range(0, len(seqs), batch):
            ids, lengths = collate(seqs[i:i + batch])
            outs = model(ids, lengths)
            for j in range(ids.shape[0]):
                rid = ids_order[i + j]
                rows[rid] = enforce_umum({a: LABELS[int(outs[k][j].argmax())] for k, a in enumerate(ASPECTS)})
    return rows


def train_one(dataset, seed, predict_ids, vectors, max_epochs=30, patience=3, log=print):
    import random

    import numpy as np
    import torch
    from torch import nn

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    all_ids = list(dict.fromkeys(dataset.train_ids + dataset.val_ids + list(predict_ids)))
    texts = {rid: dataset.text(rid) for rid in all_ids}
    vocab = build_vocab(texts.values())
    matrix, known, coverage = load_vectors(vectors, vocab, seed=seed)
    word_index = {w: i for i, w in enumerate(vocab)}
    seq = {rid: encode(texts[rid], word_index, known) for rid in all_ids}
    model = build_model(matrix)
    optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=1e-3)
    losses = []
    for a in ASPECTS:  # bobot kelas per aspek: kebalikan frekuensi pada data latih
        counts = Counter(dataset.labels[r][a] for r in dataset.train_ids)
        weights = [len(dataset.train_ids) / (len(LABELS) * counts[label]) if counts[label] else 0.0 for label in LABELS]
        losses.append(nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float)))
    targets = {rid: [LABELS.index(dataset.labels[rid][a]) for a in ASPECTS] for rid in dataset.train_ids}
    rng = random.Random(seed)
    best, best_state, wait, history = -1.0, None, 0, []
    for epoch in range(1, max_epochs + 1):
        model.train()
        order = list(dataset.train_ids)
        rng.shuffle(order)
        for i in range(0, len(order), 32):
            chunk = order[i:i + 32]
            ids, lengths = collate([seq[r] for r in chunk])
            outs = model(ids, lengths)
            y = torch.tensor([targets[r] for r in chunk])
            loss = sum(losses[k](outs[k], y[:, k]) for k in range(len(ASPECTS)))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        val_pred = predict(model, [seq[r] for r in dataset.val_ids], dataset.val_ids)
        f1 = val_score(dataset, val_pred)["f1_pasangan"]
        history.append({"epoch": epoch, "f1_pasangan_validasi": f1})
        log(f"  B4 seed {seed} epoch {epoch}: F1 pasangan validasi {f1:.3f}")
        if f1 > best:
            best, wait = f1, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    model.load_state_dict(best_state)
    val_pred = predict(model, [seq[r] for r in dataset.val_ids], dataset.val_ids)
    began = time.perf_counter()
    test_pred = predict(model, [seq[r] for r in predict_ids], list(predict_ids))
    seconds = (time.perf_counter() - began) / max(len(predict_ids), 1) * 1000
    config = {"seed": seed, "vectors": str(vectors) if vectors and Path(vectors).exists() else None,
              "kosakata": len(vocab) - 2, "cakupan_fasttext": coverage,
              "catatan": None if vectors and Path(vectors).exists() else
              "TANPA fastText: embedding nol + [UNK] dilatih; hanya uji asap, bukan hasil B4",
              "riwayat": history, "label_latih": dataset.labels_path}
    return test_pred, config, val_score(dataset, val_pred), seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seeds", default="42,43,44")
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--split", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--vectors", type=Path, default=Path("data/external/cc.id.300.vec"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--predict-split")
    group.add_argument("--predict-from", type=Path)
    parser.add_argument("--max-epochs", type=int, default=30)
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()
    if not args.vectors.exists():
        print(f"Peringatan: {args.vectors} tidak ada; model berjalan tanpa fastText (uji asap saja)")
    dataset = Dataset(args.clean, args.split, args.labels)
    ids = prediction_ids(dataset, args.predict_split, args.predict_from)
    for seed in map(int, args.seeds.split(",")):
        predictions, config, val_metrics, seconds = train_one(dataset, seed, ids, args.vectors, args.max_epochs)
        write_predictions(args.out / "predictions" / f"B4_{seed}.csv", "B4", seed, predictions)
        write_run(args.out / "metrics", "B4", seed, config, val_metrics, seconds)
        print(f"B4 seed {seed}: F1 pasangan validasi {val_metrics['f1_pasangan']:.3f}, "
              f"cakupan fastText {config['cakupan_fasttext']:.1%}")


if __name__ == "__main__":
    main()
