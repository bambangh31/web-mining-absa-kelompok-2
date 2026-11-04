"""Perilaku cleaning, privasi, stratifikasi, dan keterulangan split."""
import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from src import preprocess as p


def row(key, text, at='2024-01-01 00:00:00', score='1'):
    return dict(reviewId=key, content=text, at=at, score=score, reviewCreatedVersion='1.0')


class PreprocessingTests(unittest.TestCase):
    def test_transform_preserves_negation_and_llm_emoji(self):
        rows, _, _ = p.clean_rows([row('a', '  BELUM\n bisa login 👍 lamaaaaa  ')])
        self.assertEqual(rows[0]['text_llm'], 'BELUM bisa login 👍 lamaaaaa')
        self.assertEqual(rows[0]['text_model'], 'belum bisa login jempol ke atas lamaa')
        self.assertEqual(p.model_text('akun_login tidak maaf'), 'akun_login tidak maaf')

    def test_redacts_common_patterns(self):
        text, counts = p.redact('NIK 1234567890123456 hp +62 812-3456-7890 email a@contoh.id https://contoh.id')
        for token in ('[NIK]', '[TELEPON]', '[EMAIL]', 'HTTPURL'):
            self.assertIn(token, text)
        self.assertEqual(sum(counts.values()), 4)

    def test_oldest_duplicate_kept_and_version_rows_retained(self):
        rows, stats, _ = p.clean_rows([
            row('new', 'TIDAK  bisa login', '2025-01-01'),
            row('old', 'tidak bisa login', '2024-01-01'),
            row('short', 'bagus sekali'), row('empty', ' '),
            row('before', 'tidak bisa daftar', '2023-02-28')])
        self.assertEqual([(r['reviewId'], r['in_pool']) for r in rows], [('old', 1), ('new', 0)])
        self.assertEqual(stats['short'], 1)
        self.assertEqual(stats['before_since'], 1)

    def test_transform_collision_removed_from_pool(self):
        rows, stats, _ = p.clean_rows([row('a', 'lamaaaa sekali login'), row('b', 'lamaaa sekali login')])
        self.assertEqual(sum(r['in_pool'] for r in rows), 1)
        self.assertEqual(stats['duplicate_after_transform'], 1)

    def test_bad_ids_and_ratings_rejected(self):
        for rows in ([row('a', 'teks contoh saja'), row('a', 'teks lain saja')],
                     [row('b', 'teks contoh saja', score='6')]):
            with self.assertRaises(ValueError):
                p.clean_rows(rows)

    def test_split_disjoint_stratified_and_order_independent(self):
        clean = [dict(reviewId=f'id-{i:04}', score=str(i % 5 + 1), in_pool=1) for i in range(1000)]
        split = p.make_split(clean)
        self.assertEqual(split, p.make_split(list(reversed(clean))))
        self.assertEqual(len({r['reviewId'] for r in split}), 1000)
        self.assertEqual(Counter(r['split'] for r in split),
                         dict(kalibrasi=50, gold_train=400, gold_val=100, gold_test=300, silver=150))
        scores = {r['reviewId']: r['score'] for r in clean}
        self.assertEqual(Counter(scores[r['reviewId']] for r in split if r['split'] == 'kalibrasi'),
                         {s: 10 for s in '12345'})

    def test_full_export_and_annotation_contract(self):
        from src.annotation import prepare
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, clean, split = [root / name for name in ('raw.csv', 'clean.csv', 'split.csv')]
            data = [row(f'id-{i}', f'tidak bisa login kode{i}', score=str(i % 5 + 1)) for i in range(900)]
            with source.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(data[0]))
                writer.writeheader()
                writer.writerows(data)
            report = p.run(source, clean, split, root / 'report')
            manifest = prepare(clean, split, root / 'workspace')
            self.assertEqual(report['counts']['pool'], 900)
            self.assertEqual(len(manifest['assignments']['gold']['bambang']), 275)
            with self.assertRaises(FileExistsError):
                p.run(source, clean, split, root / 'report')
