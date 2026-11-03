# Web Mining - ABSA Kelompok 2

Proyek mata kuliah Web Mining Kelompok 2: analisis sentimen berbasis aspek
(Aspect-Based Sentiment Analysis / ABSA), mencakup pengumpulan data,
preprocessing, pemodelan, dan evaluasi.

## Status dan anggota

Topik yang diusulkan (3 November 2026, menunggu persetujuan kelompok dan
dosen): ABSA ulasan Google Play SATUSEHAT Mobile, dengan perbandingan label
manual dan label LLM serta pelacakan sentimen aspek per versi aplikasi.
Rincian ada di [usulan week 10](docs/week-10/README.md). Skrip scraping sudah
tersedia; belum ada hasil eksperimen.

| Anggota | NRP | Peran awal |
|---|---|---|
| Bambang Herlambang | 5803024019 | Preprocessing dan anotasi |
| Efraim Melvyn Rafelino Lahai | 5803024009 | Pengumpulan dan eksplorasi data |
| Jap Robertus Kurniawan Setiabudi | 5803024004 | Pemodelan ABSA |
| Robertus Geraldyn Alexandro Gabeler | 5803024025 | Evaluasi dan analisis |

Rincian [pembagian per minggu](docs/project/collaboration-plan.md#pembagian-pekerjaan-per-minggu)
menjelaskan kontribusi berempat setiap minggu sesuai peran. Subtugas dapat
disesuaikan berdasarkan beban nyata; week 14 hanya jika diminta dosen.

## Tahap tugas

| Week | Kegiatan |
|---|---|
| 10 | Dataset dari Kaggle atau scraping (disarankan); contoh dan karakteristik data, BOD, serta algoritma |
| 11-12 | Coding: preprocessing, mining, evaluation |
| 13 | Laporan pertama |
| 14 | Percobaan tambahan jika diminta |
| 15 | Artikel bahasa Indonesia |
| 16 | Presentasi |

Kelas setiap Rabu, dengan acuan week 11 pada 4 November 2026.
Kalender lengkap ada di [timeline](docs/project/timeline.md).
Tanggal kelas bukan otomatis tenggat pengumpulan; tenggat, format BOD,
dan template artikel mengikuti arahan dosen.

## Struktur repository

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/ci.yml
│   ├── dependabot.yml
│   └── pull_request_template.md
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .python-version
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── annotations/
├── notebooks/
├── src/
├── results/
│   ├── metrics/
│   └── figures/
└── docs/
    ├── project/
    ├── week-10/
    ├── laporan/
    ├── artikel/
    └── presentasi/
```

Folder berisi README penjelas. Notebook/modul dibuat saat pengerjaan dimulai.
Sumber, izin, dan petunjuk dataset dicatat di [data/README.md](data/README.md).
Data berukuran besar atau yang distribusinya dibatasi dapat disertakan melalui
tautan dan prosedur pengambilan.

## Pengembangan

Gunakan Python 3.12 sesuai `.python-version`. Cara membuat environment,
menambah dependensi, mengerjakan branch/PR, dan mencatat eksperimen ada di
[CONTRIBUTING.md](CONTRIBUTING.md). Perhatikan [SECURITY.md](SECURITY.md)
untuk kredensial, sumber teks, dan data pribadi.

Pengambilan ulasan:

```text
python src/scrape_reviews.py --app com.telkom.tracencare --count 15000
```

Perintah tahap berikutnya ditambahkan setelah kodenya tersedia.

## CI dan Dependabot

CI berjalan saat push ke `main`, pull request, atau melalui pemicu manual.
Pemeriksaannya: memasang `requirements.txt`, memeriksa kompatibilitas
dependensi, dan sintaks `.py` di `src/`. CI belum menjalankan scraping,
notebook, atau menguji ABSA.

Dependabot memeriksa library Python dan GitHub Actions setiap bulan.
Pembaruan dibuat sebagai PR untuk diperiksa sebelum digabung; auto-merge
nonaktif. Dependabot alerts dan PR perbaikan keamanan juga diaktifkan.

## Kolaborasi dan dokumentasi

Gunakan **Issues → New issue** untuk laporan masalah atau usulan perubahan;
issue kosong tetap tersedia untuk tugas lain. Isi template saat membuat PR.
Panduan kerja dan tahapan ada di [docs/project/README.md](docs/project/README.md).
Ringkasan pemeriksaan setup ada di [review setup](docs/project/review-setup.md).
