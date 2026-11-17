"""Ambil vektor kata latih dari arsip text fastText tanpa memuat semuanya ke RAM."""
import gzip
import hashlib
import math
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_subset(archive, target, words, dim=300, log=print):
    """Baca sampai EOF agar gzip/CRC dan jumlah baris turut diperiksa.

    Hanya kosakata latih disertakan. Kata di luar vektor text memakai UNK;
    ini tidak menghasilkan vektor subword untuk kata baru seperti format bin.
    """
    words = set(words)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    body = target.with_suffix(".body.part")
    partial = target.with_suffix(".part")
    found = set()
    try:
        with gzip.open(archive, "rt", encoding="utf-8", errors="strict") as source, body.open(
                "w", encoding="utf-8", newline="\n") as out:
            header = source.readline().split()
            if len(header) != 2 or int(header[1]) != dim or int(header[0]) < 1:
                raise ValueError("Header fastText tidak sesuai")
            expected = int(header[0])
            count = 0
            for line in source:
                if not line.strip():
                    continue
                count += 1
                word, _, values = line.rstrip().partition(" ")
                if word in words and word not in found:
                    fields = values.split()
                    if len(fields) != dim or not all(math.isfinite(float(v)) for v in fields):
                        raise ValueError(f"Vektor fastText tidak valid: {word}")
                    out.write(word + " " + " ".join(fields) + "\n")
                    found.add(word)
                if count % 250000 == 0:
                    log(f"fastText: {count:,}/{expected:,} baris; {len(found)} kata latih cocok", flush=True)
            if count != expected:
                raise ValueError(f"fastText tidak lengkap: {count} dari {expected} baris")
        if not found:
            raise ValueError("Tidak ada vektor yang cocok dengan kata latih")
        with partial.open("wb") as out, body.open("rb") as source:
            out.write(f"{len(found)} {dim}\n".encode())
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                out.write(chunk)
        partial.replace(target)
        return {"n_source_vectors": expected, "n_train_words": len(words), "n_matched": len(found),
                "coverage": len(found) / max(len(words), 1), "dim": dim,
                "subset_sha256": sha256_file(target), "archive_sha256": sha256_file(archive)}
    finally:
        body.unlink(missing_ok=True)
        partial.unlink(missing_ok=True)
