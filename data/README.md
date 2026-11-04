# Dataset ABSA

Dataset: ulasan Google Play SATUSEHAT Mobile, disetujui kelompok pada
3 November 2026. Alasan dan metode ada di
[usulan week 10](../docs/week-10/README.md).

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

## Dataset final

File: [`raw/com.telkom.tracencare_reviews.csv`](raw/com.telkom.tracencare_reviews.csv).
Isinya keluaran langsung `src/scrape_reviews.py` tanpa penyuntingan manual.

| Item | Nilai |
|---|---|
| Perintah | `python src/scrape_reviews.py --since 2023-03-01 --count 1000000` |
| Waktu pengambilan | 4 November 2026, 02:31-02:36 UTC |
| Cakupan | Semua ulasan yang dikembalikan Google Play untuk bahasa `id` dan negara `id` sejak SATUSEHAT Mobile berganti nama (1 Maret 2023) |
| Jumlah baris | 39.995 ulasan |
| Rentang `at` | 1 Maret 2023 00:07 sampai 3 November 2026 08:09 |
| Zona waktu `at`, `repliedAt` | Waktu lokal komputer pengambil (WIB, UTC+7); pustaka memakai `datetime.fromtimestamp` |
| Ukuran / SHA-256 | 8.847.485 byte / `0a66aeb9650aee9cacdb603f36030c54d686b583d455302f244f762c4b337c38` |
| Lingkungan | Python 3.14.6, `google-play-scraper` 1.2.7 |

Pemeriksaan yang sudah dilakukan:

- 9 kolom sesuai skrip; tidak ada kolom nama atau foto pengguna.
- 39.995 `reviewId` unik dan tidak kosong; tidak ada `content` kosong.
- `at` terurut menurun tanpa pelanggaran, sehingga pengambilan berhenti tepat
  setelah melewati 1 Maret 2023.
- Rating hanya bernilai 1-5.
- Semua 15.000 ulasan dari scraping 3 November 2026 ada di file ini dengan
  teks dan rating yang sama.
- Tidak ditemukan NIK 16 digit, nomor telepon, atau email.

Teks ulasan dapat memuat baris baru di dalam sel CSV. `.gitattributes`
menandai file ini `-text` agar Git tidak mengubah akhir baris dan hash tetap
sama. Periksa dengan:

```text
python -c "import hashlib; print(hashlib.sha256(open('data/raw/com.telkom.tracencare_reviews.csv','rb').read()).hexdigest())"
```

Menjalankan ulang perintah di atas pada tanggal lain menghasilkan file
berbeda, karena ulasan baru terus masuk dan ulasan lama bisa dihapus.

### Ringkasan dataset final

| Ukuran | Nilai |
|---|---|
| Median kata | 9 |
| Minimal 3 kata | 82,1% |
| Minimal 8 kata | 57,6% |
| Duplikat persis (huruf kecil, spasi dirapikan) | 5.527 |
| Pool setelah preprocessing (minimal 3 kata, tanpa duplikat) | 32.035 |
| Versi terisi | 78,9%; 130 versi, 73 dengan minimal 50 ulasan |
| Bintang 1 / 2 / 3 / 4 / 5 | 25.998 / 2.845 / 1.820 / 1.344 / 7.988 |
| Ulasan Maret 2023 (bulan perubahan nama) | 16.392 (41% dari seluruh data) |

Lonjakan Maret 2023 perlu diperhatikan saat analisis per waktu dan per versi.
Pada bulan itu 63,7% ulasan memberi bintang 1, 27% memuat kata kunci login,
dan 9% menyebut PeduliLindungi (perkiraan kata kunci, bukan label).

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

## Eksplorasi awal (3 Nov 2026)

Angka berikut berasal dari scraping uji 3 November 2026 dan dipakai di
[laporan week 10](../docs/laporan/Week_10_Laporan_ABSA_SATUSEHAT.docx).
Ke-15.000 ulasan itu adalah bagian dari dataset final di atas.

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
belum diperiksa. Sejak 4 November 2026, kelompok menyimpan data mentah di
repository ini karena repository bersifat privat dan hanya dipakai anggota
kelompok. Jangan membagikan file mentah ke publik, dan periksa ulang
ketentuan ini sebelum repository dibuat publik. File `data/processed/*.csv`
tetap tidak diunggah karena dapat dibuat ulang dari kode. Jika dosen meminta
dataset, sertakan tanggal pengambilan dan langkah pengulangannya.

- `raw/`: hasil scraping asli, tidak diubah.
- `processed/`: hasil pembersihan dan pembagian data.
- `annotations/`: panduan aspek/sentimen dan label acuan.
