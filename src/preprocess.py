"""Preprocessing dan split deterministik; tidak membuat label sentimen."""

import argparse
import csv
import hashlib
import json
import platform
import random
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import emoji

FIELDS = ['reviewId', 'at', 'score', 'reviewCreatedVersion', 'text_llm',
          'text_model', 'n_words', 'in_pool']
SINCE = datetime(2023, 3, 1)
SIZES = [('kalibrasi', 50), ('gold_train', 400), ('gold_val', 100), ('gold_test', 300)]


def tidy(text):
    return re.sub(r'\s+', ' ', text).strip()


def redact(text):
    counts = Counter()
    patterns = [
        ('url', r'(?i)\b(?:https?://|www\.)\S+', 'HTTPURL'),
        ('email', r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[EMAIL]'),
        ('nik', r'(?<!\d)\d{16}(?!\d)', '[NIK]'),
        ('telepon', r'(?<!\w)(?:\+62|62|0)[\s().-]*8(?:[\s().-]*\d){7,11}(?!\d)', '[TELEPON]'),
    ]
    for name, pattern, replacement in patterns:
        text, counts[name] = re.subn(pattern, replacement, text)
    return tidy(text), counts


def model_text(text):
    text = text.lower()
    text = emoji.replace_emoji(text, replace=lambda chars, data:
                               ' ' + emoji.demojize(chars, language='id',
                                                    delimiters=('', '')).replace('_', ' ') + ' ')
    text = re.sub(r'([a-z])\1{2,}', r'\1\1', text)
    return tidy(text)


def clean_rows(raw):
    seen_ids, seen_text, seen_model = set(), set(), set()
    stats, masks = Counter(), Counter()
    cleaned = []
    # Paling awal berarti waktu ulasan, bukan urutan CSV terbaru dahulu.
    ordered = sorted(raw, key=lambda r: (datetime.fromisoformat(r['at']), r['reviewId']))
    for row in ordered:
        key = row['reviewId']
        if not key or key.strip() != key or key in seen_ids:
            raise ValueError('reviewId kosong, berspasi, atau duplikat')
        seen_ids.add(key)
        if row['score'] not in {'1', '2', '3', '4', '5'}:
            raise ValueError('Rating harus 1-5')
        if datetime.fromisoformat(row['at']) < SINCE:
            stats['before_since'] += 1
            continue
        original = tidy(row['content'])
        if not original:
            stats['empty'] += 1
            continue
        n_words = len(original.split())
        if n_words < 3:
            stats['short'] += 1
            continue
        llm, counts = redact(original)
        masks.update(counts)
        model = model_text(llm)
        normalized = original.lower()
        reason = ''
        if normalized in seen_text:
            reason = 'duplicate_original'
        elif model in seen_model:
            reason = 'duplicate_after_transform'
        if reason:
            stats[reason] += 1
        seen_text.add(normalized)
        seen_model.add(model)
        cleaned.append(dict(zip(FIELDS, [key, row['at'], row['score'],
                            row.get('reviewCreatedVersion', ''), llm, model,
                            n_words, int(not reason)])))
    stats['raw'] = len(raw)
    stats['clean_for_version_analysis'] = len(cleaned)
    stats['pool'] = sum(r['in_pool'] for r in cleaned)
    return cleaned, dict(stats), dict(masks)


def stratified_take(rows, count, rng):
    """Alokasi proporsional dengan sisa terbesar; ID input diurutkan dahulu."""
    if len(rows) < count:
        raise ValueError(f'Pool tidak cukup: {len(rows)} < {count}')
    groups = {score: sorted([r for r in rows if r['score'] == score],
                           key=lambda r: r['reviewId']) for score in '12345'}
    allocation = {s: len(g) * count // len(rows) for s, g in groups.items()}
    order = sorted(groups, key=lambda s: (-(len(groups[s]) * count % len(rows)), s))
    for s in order[:count - sum(allocation.values())]:
        allocation[s] += 1
    chosen = []
    for s, group in groups.items():
        rng.shuffle(group)
        chosen.extend(group[:allocation[s]])
    ids = {r['reviewId'] for r in chosen}
    return chosen, [r for r in rows if r['reviewId'] not in ids]


def make_split(cleaned, seed=42):
    rest = [r for r in cleaned if r['in_pool']]
    rng = random.Random(seed)
    result = []
    for name, count in SIZES:
        chosen, rest = stratified_take(rest, count, rng)
        result.extend({'reviewId': r['reviewId'], 'split': name} for r in chosen)
    result.extend({'reviewId': r['reviewId'], 'split': 'silver'} for r in rest)
    return sorted(result, key=lambda r: r['reviewId'])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, fields, rows):
    with Path(path).open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(source, clean_path, split_path, report_dir, seed=42):
    source, clean_path, split_path, report_dir = map(Path, (source, clean_path, split_path, report_dir))
    if clean_path.exists() or split_path.exists() or report_dir.exists():
        raise FileExistsError('Keluaran sudah ada; gunakan path versi baru, jangan timpa split/anotasi')
    with source.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'reviewId', 'at', 'score', 'content', 'reviewCreatedVersion'} <= set(reader.fieldnames or []):
            raise ValueError('Kolom sumber tidak lengkap')
        raw = list(reader)
    cleaned, counts, masks = clean_rows(raw)
    split = make_split(cleaned, seed)
    for path in (clean_path.parent, split_path.parent, report_dir):
        path.mkdir(parents=True, exist_ok=True)
    write_csv(clean_path, FIELDS, cleaned)
    write_csv(split_path, ['reviewId', 'split'], split)
    by_id = {r['reviewId']: r for r in cleaned}
    ratings = {name: dict(sorted(Counter(by_id[r['reviewId']]['score'] for r in split
                                       if r['split'] == name).items()))
               for name in [n for n, _ in SIZES] + ['silver']}
    report = {'source_sha256': sha(source), 'code_sha256': sha(__file__),
              'python': platform.python_version(), 'emoji': emoji.__version__,
              'seed': seed, 'since': SINCE.isoformat(), 'counts': counts,
              'redaction_matches': masks, 'split_counts': dict(Counter(r['split'] for r in split)),
              'rating_by_split': ratings,
              'outputs_sha256': {'reviews_clean': sha(clean_path), 'split': sha(split_path)},
              'human_labels_created': False, 'slang_normalization_B1': 'belum diterapkan; bagian pipeline B1',
              'privacy_limit': 'Regex pola umum; tidak menjamin seluruh informasi pribadi terdeteksi.'}
    (report_dir / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/raw/com.telkom.tracencare_reviews.csv'))
    parser.add_argument('--clean', type=Path, default=Path('data/processed/reviews_clean.csv'))
    parser.add_argument('--split', type=Path, default=Path('data/annotations/split.csv'))
    parser.add_argument('--report', type=Path, default=Path('results/preprocessing/v1'))
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.clean, args.split, args.report, args.seed), indent=2))


if __name__ == '__main__':
    main()
