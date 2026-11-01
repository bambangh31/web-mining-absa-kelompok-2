# Keamanan data dan repository

Panduan ini berlaku untuk kode, notebook, dataset, konfigurasi, dan dokumen
proyek Web Mining Kelompok 2 (ABSA).

## Kredensial dan data

- Simpan token/password pada environment lokal atau GitHub Actions secrets
  jika diperlukan. `.env` sudah dikecualikan melalui `.gitignore`.
- Periksa keluaran notebook, log, screenshot, dan lampiran sebelum diunggah.
  Keluaran tersebut dapat memuat kredensial atau data pribadi.
- Gunakan dataset sesuai izin sumber. Catat batas pembagian ulang pada
  `data/README.md`; sediakan petunjuk unduh bila berkas tidak boleh dibagikan.
- Jika data memuat informasi pribadi, gunakan hanya bagian yang diperlukan
  dan tentukan penanganannya sebelum membagikan data atau hasil.

## Pengumpulan teks dari web

Catat sumber dan izin/ketentuan pengumpulan yang berlaku. Gunakan akses resmi
atau data yang boleh digunakan; sesuaikan laju pengambilan dengan sumber.
Hindari menyimpan identitas pengguna yang tidak dibutuhkan untuk analisis.
Jika data hanya boleh dianalisis tanpa didistribusikan, bagikan prosedur
pengambilan atau ringkasan yang sesuai ketentuannya.

## Melaporkan temuan

Sampaikan kebocoran kredensial atau data pribadi kepada anggota kelompok
melalui kanal pribadi yang disepakati. Jangan menempelkan nilai kredensial
atau data pribadi ke issue, PR, maupun screenshot.

Sertakan lokasi berkas/commit, jenis paparan, dampak yang diketahui, dan cara
memeriksa tanpa menyalin data sensitif. Setelah informasi sensitif dihapus,
pekerjaan perbaikan dapat dicatat sebagai issue dengan uraian yang aman.

Jika kredensial telanjur terunggah, cabut atau ganti kredensial tersebut,
periksa dampaknya, lalu tangani berkas dan riwayat Git yang terkait bersama.
Menghapus nilai hanya dari commit terbaru tidak mencabut kredensialnya.

## Pemeriksaan yang tersedia

Dependabot alerts dan PR pembaruan keamanan telah diaktifkan pada pengaturan
repo. Pembaruan versi rutin diatur di `.github/dependabot.yml`.

CI dasar saat ini memeriksa dependensi dan sintaks Python. Repo belum memiliki
pemindaian rahasia atau audit dataset otomatis. Periksa isi yang akan
diunggah, termasuk keluaran notebook, sebagai bagian dari review.
