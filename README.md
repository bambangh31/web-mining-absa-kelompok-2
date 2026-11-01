# Web Mining - ABSA Kelompok 2

Proyek mata kuliah Web Mining Kelompok 2: analisis sentimen berbasis aspek
(Aspect-Based Sentiment Analysis / ABSA), mencakup pengumpulan data,
preprocessing, pemodelan, dan evaluasi.

## Status dan anggota

Repository sudah memiliki konfigurasi awal. Dataset, daftar aspek, metode,
dan library belum ditentukan; belum ada hasil eksperimen.
Daftar anggota diisi setelah informasinya tersedia.

## Tahap tugas

| Week | Kegiatan |
|---|---|
| 10 | Dataset dari Kaggle atau scraping (disarankan); contoh dan karakteristik data, BOD, serta algoritma |
| 11-12 | Coding: preprocessing, mining, evaluation |
| 13 | Laporan pertama |
| 14 | Percobaan tambahan jika diminta |
| 15 | Artikel bahasa Indonesia |
| 16 | Presentasi |

Tanggal kelas, tenggat, format BOD, dan template artikel mengikuti arahan
dosen. Jadwal Data Mining tidak dijadikan jadwal Web Mining.

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

Perintah menjalankan pipeline ditambahkan setelah kode awal tersedia.

## CI dan Dependabot

CI berjalan saat push ke `main`, pull request, atau melalui pemicu manual.
Pemeriksaannya: memasang `requirements.txt`, memeriksa kompatibilitas
dependensi, dan sintaks `.py` di `src/`. Saat ini belum ada dependensi proyek
atau kode `.py`; CI belum menjalankan scraping, notebook, atau menguji ABSA.

Dependabot memeriksa library Python dan GitHub Actions setiap bulan.
Pembaruan dibuat sebagai PR untuk diperiksa sebelum digabung; auto-merge
nonaktif. Dependabot alerts dan PR perbaikan keamanan juga diaktifkan.

## Kolaborasi dan dokumentasi

Gunakan **Issues → New issue** untuk laporan masalah atau usulan perubahan;
issue kosong tetap tersedia untuk tugas lain. Isi template saat membuat PR.
Panduan kerja dan tahapan ada di [docs/project/README.md](docs/project/README.md).
Ringkasan pemeriksaan setup ada di [review setup](docs/project/review-setup.md).
