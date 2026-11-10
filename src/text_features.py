"""Preprocessing tahap fitur: normalisasi slang (aturan 12) dan tokenisasi.

`text_model` dari `preprocess.py` sudah huruf kecil, emoji menjadi teks, dan
huruf berulang dipendekkan. Modul ini menambah langkah khusus model:

- Normalisasi slang hanya untuk model TF-IDF (B1-LR, B1-SVM, B1-NB). TF-IDF
  menganggap "gak", "ga", "gk", dan "tdk" sebagai fitur berbeda. Encoder dan
  LLM tidak memakai normalisasi karena sudah mengenal slang.
- Tokenisasi kata dan tanda baca untuk BiLSTM (B4) dan TF-IDF.

Tanpa stopword removal dan tanpa stemming (aturan 10 dan 11): kata negasi
dipertahankan dan "terdaftar" tidak disamakan dengan "daftar".

Jalankan ``python src/text_features.py`` untuk ringkasan normalisasi pada
`reviews_clean.csv`.
"""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

LEXICON_PATH = Path("data/external/colloquial-indonesian-lexicon.csv")
LEXICON_URL = ("https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/"
               "colloquial-indonesian-lexicon.csv")

# Tambahan proyek di atas kamus Salsabila dkk. (2018), dicek pada pilot.
# Kamus memetakan "ga/gak/gk" ke "enggak"; negasi disatukan menjadi "tidak"
# agar TF-IDF melihat satu fitur negasi. Istilah domain aplikasi dipertahankan.
OVERRIDES = {
    "enggak": "tidak", "engga": "tidak", "nggak": "tidak", "ngga": "tidak",
    "gak": "tidak", "ga": "tidak", "gk": "tidak", "g": "tidak", "kagak": "tidak",
    "kaga": "tidak", "tdk": "tidak", "tak": "tidak", "ndak": "tidak", "nda": "tidak",
    "gabisa": "tidak bisa", "gbs": "tidak bisa", "gakbisa": "tidak bisa",
    "apk": "aplikasi", "app": "aplikasi", "apl": "aplikasi", "aplikasih": "aplikasi",
    "aplikasinya": "aplikasinya", "eror": "error", "erorr": "error", "errornya": "errornya",
    "apdet": "update", "updet": "update", "updte": "update", "upgrade": "update",
    "in": "in", "otp": "otp", "pin": "pin", "nik": "nik", "login": "login", "log": "log",
    "min": "admin", "mimin": "admin", "cs": "cs", "wa": "whatsapp",
    "vaksin": "vaksin", "booster": "booster", "boster": "booster", "bosster": "booster",
    "serifikat": "sertifikat", "srtifikat": "sertifikat",
}

TOKEN_RE = re.compile(r"\[[a-z]+\]|[a-z0-9]+(?:[-'][a-z0-9]+)*|[^\sa-z0-9]", re.IGNORECASE)


def tokenize(text):
    """Kata, angka, dan tanda baca; penanda privasi seperti [NIK] tetap utuh."""
    return TOKEN_RE.findall(text)


def load_lexicon(path=LEXICON_PATH, overrides=OVERRIDES):
    """Kamus slang -> bentuk baku. Bentuk paling sering dipakai bila ganda."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Kamus slang belum ada di {path}. Unduh sekali dengan:\n"
            f"  curl -L -o {path.as_posix()} {LEXICON_URL}")
    choices = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            slang, formal = row["slang"].strip().lower(), row["formal"].strip().lower()
            if slang and formal and slang != formal:
                choices.setdefault(slang, Counter())[formal] += 1
    lexicon = {slang: counts.most_common(1)[0][0] for slang, counts in choices.items()}
    # Hasil kamus yang berupa "enggak" ikut disatukan menjadi "tidak".
    lexicon = {slang: overrides.get(formal, formal) for slang, formal in lexicon.items()}
    lexicon.update(overrides)
    return {k: v for k, v in lexicon.items() if k != v}


def normalize_slang(text, lexicon, counter=None):
    """Ganti token slang pada `text_model`; tanda baca dan urutan dipertahankan."""
    out = []
    for token in tokenize(text):
        replacement = lexicon.get(token)
        if replacement is not None:
            if counter is not None:
                counter[(token, replacement)] += 1
            out.append(replacement)
        else:
            out.append(token)
    return " ".join(out)


def b1_text(text_model, lexicon):
    """Masukan model TF-IDF: `text_model` + normalisasi slang."""
    return normalize_slang(text_model, lexicon)


def summarize(clean_path, lexicon_path, output):
    lexicon = load_lexicon(lexicon_path)
    counter, changed, total, tokens = Counter(), 0, 0, 0
    examples = []
    with Path(clean_path).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["in_pool"] != "1":
                continue
            total += 1
            before = row["text_model"]
            tokens += len(tokenize(before))
            local = Counter()
            after = normalize_slang(before, lexicon, local)
            counter.update(local)
            if local:
                changed += 1
                if len(examples) < 8 and 5 <= len(before.split()) <= 18:
                    examples.append({"reviewId": row["reviewId"], "text_model": before, "text_b1": after})
    report = {
        "lexicon_entries": len(lexicon), "pool_reviews": total, "pool_tokens": tokens,
        "reviews_changed": changed, "reviews_changed_pct": round(100 * changed / max(total, 1), 1),
        "tokens_replaced": sum(counter.values()),
        "tokens_replaced_pct": round(100 * sum(counter.values()) / max(tokens, 1), 1),
        "top_replacements": [{"slang": s, "baku": f, "jumlah": n} for (s, f), n in counter.most_common(25)],
        "examples": examples,
    }
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--lexicon", type=Path, default=LEXICON_PATH)
    parser.add_argument("--output", type=Path, default=Path("results/preprocessing/v1/slang_summary.json"))
    args = parser.parse_args()
    report = summarize(args.clean, args.lexicon, args.output)
    print(json.dumps({k: v for k, v in report.items() if k not in ("examples", "top_replacements")}, indent=2))


if __name__ == "__main__":
    main()
