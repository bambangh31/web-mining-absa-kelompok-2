# Kode bersama

Tempat modul pengumpulan/scraping, preprocessing, aspek, sentimen, dan evaluasi.
Buat modul yang diperlukan saat coding.

- `scrape_reviews.py`: ambil ulasan Google Play ke CSV tanpa identitas
  pengguna. Lihat [data/README.md](../data/README.md).
- `pilot_stats.py`: statistik eksplorasi dari CSV hasil scraping.
- `annotation.py`: lembar kalibrasi/gold kosong, validasi label, audit
  kesepakatan, dan ekspor label manusia. Memakai clean + split dari Efraim;
  tidak menghasilkan label otomatis. Lihat
  [panduan penggunaan](../docs/project/annotation-workflow.md).

Kode `.py` pada folder ini diperiksa sintaksnya oleh CI.
