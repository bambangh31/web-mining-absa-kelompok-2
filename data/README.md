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

## Hasil eksplorasi (3 Nov 2026)

Dihitung dengan `src/pilot_stats.py`. Ulasan terbaru terus bertambah, jadi
angka berubah bila skrip dijalankan pada tanggal lain.

| Ukuran | 2.000 terbaru | 15.000 terbaru |
|---|---|---|
| Rentang | 3 Des 2025 - 2 Nov 2026 | 17 Jul 2023 - 2 Nov 2026 |
| Median kata | 7 | 10 |
| Minimal 3 kata | 72,2% | 83,3% |
| Minimal 8 kata | 47,5% | 59,7% |
| Duplikat persis | 329 | 1.676 |
| Versi terisi | 79% | 73,8% |
| Versi dengan minimal 50 ulasan | 9 | 54 |
| Bintang 1 / 2 / 3 / 4 / 5 | 823 / 102 / 88 / 108 / 879 | 10.179 / 845 / 593 / 463 / 2.920 |

Catatan:

- Semua 15.000 ulasan dibuat setelah PeduliLindungi resmi menjadi
  SATUSEHAT Mobile (1 Maret 2023). 709 ulasan masih menyebut PeduliLindungi.
- Ulasan lama jauh lebih negatif: 68% bintang 1 pada 15.000 ulasan,
  dibanding 41% pada 2.000 terbaru.
- Setelah aturan preprocessing (minimal 3 kata, tanpa duplikat), tersisa
  12.297 ulasan.
- Tidak ditemukan NIK 16 digit, nomor telepon, atau email pada 15.000 ulasan.
  Penyamaran tetap dijalankan sebelum teks dikirim ke API.

## Contoh ulasan

Contoh dari pilot, ditulis apa adanya. Label adalah contoh penerapan
[panduan anotasi](annotations/README.md), bukan label gold.

| Bintang | Versi | Ulasan | Aspek |
|---|---|---|---|
| 1 | 8.8.1 | "baru coba login, langsung error dan force close" | akun_login negatif, performa negatif |
| 1 | 8.8.1 | "padahal udah ckg , tapi hasil ckg ngaa keluar selama 24 jam sampai apk kurangg" | fitur_kesehatan negatif |
| 1 | 8.6.1 | "ini saya nomor hp lama cuma bisa isi 11 karena 0 nya di hilangkan dari aplikasi jadi gk bisa daftar tolong di perbaiki" | registrasi_data negatif |
| 3 | - | "aplikasi nya bagus tpu proses nya agak ribet" | kemudahan_penggunaan negatif (`umum` tidak diisi karena ada aspek khusus) |
| 5 | - | "Mudah operasionalnya, bagus untuk monitoring rekam medis" | kemudahan_penggunaan positif, fitur_kesehatan positif |
| 5 | - | "belum di coba" | umum netral |
| 1 | - | "Bintang minus bisa gak ya? ... login berulang gabisa terus, ... sayang sekali padahal latest UI sudah bagus tapi servernya kocak." | akun_login negatif, performa negatif, kemudahan_penggunaan positif |

## Penyimpanan dan izin

Ulasan bersifat publik. Ketentuan distribusi ulang teks ulasan Google Play
belum diperiksa, jadi kelompok mengambil sikap hati-hati: file CSV di
`data/raw/` dan `data/processed/` tidak diunggah ke repository (lihat
`.gitignore`). Bagikan antaranggota melalui kanal pribadi. Repository
menyimpan skrip, ID ulasan, dan file label tanpa teks ulasan. Jika dosen meminta dataset,
sertakan tanggal pengambilan dan langkah pengulangannya.

- `raw/`: hasil scraping asli, tidak diubah.
- `processed/`: hasil pembersihan dan pembagian data.
- `annotations/`: panduan aspek/sentimen dan label acuan.
