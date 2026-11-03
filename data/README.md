# Dataset ABSA

Dataset yang diusulkan: ulasan Google Play SATUSEHAT Mobile. Alasan dan
metode ada di [usulan week 10](../docs/week-10/README.md). Pilihan ini perlu
disepakati kelompok.

## Sumber

| Item | Nilai |
|---|---|
| Aplikasi | SATUSEHAT Mobile, Kementerian Kesehatan RI |
| Package ID | `com.telkom.tracencare` |
| Halaman | https://play.google.com/store/apps/details?id=com.telkom.tracencare |
| Bahasa / negara | `id` / `id` |
| Statistik 3 Nov 2026 | 1.117.764 rating, 444.063 ulasan, skor 3,38, versi 8.10.2 |
| Alat | `google-play-scraper` 1.2.7, skrip `src/scrape_reviews.py` |
| Urutan | Terbaru (`Sort.NEWEST`) |

Menjalankan pengambilan:

```text
python src/scrape_reviews.py --app com.telkom.tracencare --count 15000
```

Keluaran: `data/raw/com.telkom.tracencare_reviews.csv`. Catat tanggal
pengambilan dan jumlah baris setiap kali menjalankan skrip, karena ulasan
terbaru terus berubah.

## Kolom

| Kolom | Isi |
|---|---|
| `reviewId` | ID ulasan Google Play, kunci penghubung data, label, dan prediksi |
| `at` | Waktu ulasan |
| `score` | Rating bintang 1-5 |
| `content` | Teks ulasan |
| `thumbsUpCount` | Jumlah pengguna yang menandai ulasan membantu |
| `reviewCreatedVersion` | Versi aplikasi saat ulasan dibuat, bisa kosong |
| `appVersion` | Versi aplikasi pada ulasan, bisa kosong |
| `replyContent`, `repliedAt` | Balasan pengembang, bisa kosong |

Nama dan foto profil pengguna tidak disimpan.

## Hasil pilot (2.000 ulasan terbaru, 3 Nov 2026)

- Rentang: 3 Desember 2025 sampai 2 November 2026.
- Panjang: median 7 kata; 48% minimal 8 kata.
- Versi: 79% terisi, 77 versi berbeda, 9 versi dengan minimal 50 ulasan.
- Rating: bintang 1 = 823, 2 = 102, 3 = 88, 4 = 108, 5 = 879.

## Penyimpanan dan izin

Ulasan bersifat publik, tetapi ketentuan Google Play membatasi distribusi
ulang. File CSV di `data/raw/` dan `data/processed/` tidak diunggah ke
repository (lihat `.gitignore`). Bagikan antaranggota melalui kanal pribadi;
repository menyimpan skrip, ID ulasan, dan label. Jika dosen meminta dataset,
sertakan tanggal pengambilan dan langkah pengulangannya.

- `raw/`: hasil scraping asli, tidak diubah.
- `processed/`: hasil pembersihan dan pembagian data.
- `annotations/`: panduan aspek/sentimen dan label acuan.
