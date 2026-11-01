# Pemeriksaan setup

Setup pada 1 November 2026 mengadaptasi fondasi repo Data Mining dan struktur
repo contoh UMKM Marketplace untuk Web Mining Kelompok 2 (ABSA).

| Bagian | Penerapan |
|---|---|
| Identitas dan tugas | README, roadmap Web Mining week 10-16, tanpa mengarang anggota/tanggal |
| Struktur proyek | data/raw, processed, annotations; notebooks; src; results; docs |
| Panduan | CONTRIBUTING.md dan SECURITY.md, mencakup teks web serta anotasi ABSA |
| Format/versi | .editorconfig, .gitattributes, .gitignore, .python-version 3.12 |
| Kolaborasi | Template issue dan PR bahasa Indonesia; issue kosong tersedia |
| CI | Dependensi dan sintaks Python; belum mengeksekusi scraping/notebook/model |
| Dependabot | pip dan GitHub Actions diperiksa bulanan, PR diperiksa sebelum merge |
| Pengaturan repo | Private, main, Issues; squash merge dan hapus branch setelah merge |
| Keamanan | Alerts dan PR pembaruan keamanan aktif; auto-merge nonaktif |
| Akses lokal | Akun bambangh31 dipilih khusus repo; workflow berizin read-only |

Dataset, aspek/label, metode, dependensi, kode, hasil eksperimen, laporan,
artikel, dan slide dilengkapi dari pekerjaan nyata. Pemindaian rahasia dan
audit dataset otomatis belum diaktifkan. Kebijakan review tidak diklaim
sebagai branch protection yang dipaksakan GitHub.

Konfigurasi frontend, API, database, deployment, dan Postman pada contoh UMKM
tidak menjadi kebutuhan setup ABSA ini. .env.example ditambahkan jika kode
mulai membutuhkan variabel environment. Lisensi belum ditentukan; dataset
tetap mengikuti izin sumber. Undangan collaborator ditangani setelah setup.
