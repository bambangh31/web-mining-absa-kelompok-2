# Status implementasi ABSA

Catatan awal: 1 November 2026. Ini adalah status fondasi repository;
pembaruan berikutnya mengikuti commit dan pekerjaan nyata.

## Sudah tersedia

| Bagian | Hasil | Batas |
|---|---|---|
| Struktur kerja | data/raw, processed, annotations; notebooks; src; results; docs | Berisi petunjuk; belum ada dataset atau implementasi ABSA |
| Kolaborasi | CONTRIBUTING, SECURITY, template issue/PR, empat nama/NRP, peran dan rencana per minggu; kalender Rabu dengan acuan week 11 pada 4 November 2026 | Pembagian dapat disesuaikan dengan beban nyata; tanggal kelas bukan otomatis tenggat pengumpulan |
| Python | Acuan 3.12, requirements.txt, format file dan ignore | Daftar library belum diisi karena metode belum ditentukan |
| CI | Instalasi requirements, pip check, sintaks .py dalam src | Belum menjalankan scraping, notebook, ekstraksi aspek, atau sentimen |
| Dependabot | Pembaruan pip/Actions bulanan; alerts dan PR perbaikan keamanan | PR perlu diperiksa; bukan audit dataset atau hasil model |
| Pengaturan repo | Private, main, squash merge, hapus branch setelah merge | Auto-merge nonaktif; tidak mengklaim branch protection aktif |

CI fondasi pada commit `43aa953` telah berhasil:
[Python CI](https://github.com/bambangh31/web-mining-absa-kelompok-2/actions/runs/41279423912).
Keberhasilan itu membuktikan setup awal dapat dijalankan, bukan kualitas
hasil ABSA. Status CI perubahan berikutnya diperiksa pada commit terkait.

## Usulan topik dan pilot data (3 November 2026)

| Bagian | Hasil | Batas |
|---|---|---|
| Topik dan metode | [Usulan week 10](../week-10/README.md): ACSA ulasan SATUSEHAT Mobile, label manual vs label LLM, analisis per versi | Usulan Efraim; menunggu persetujuan kelompok dan dosen |
| Pengambilan data | `src/scrape_reviews.py` diuji lokal (Python 3.14, `google-play-scraper` 1.2.7): 450 ulasan tersimpan dengan 9 kolom | Belum diuji dengan Python 3.12; dataset penuh belum diambil |
| Pilot data | 2.000 ulasan terbaru, statistik di [data/README.md](../../data/README.md) | Persentase aspek masih perkiraan kata kunci, bukan label |
| Panduan anotasi | Draf kategori aspek dan label di [data/annotations](../../data/annotations/README.md) | Belum dikalibrasi |

## Menunggu pengerjaan

- Persetujuan topik oleh kelompok dan dosen; format BOD dari dosen.
- Scraping penuh, preprocessing, kalibrasi anotasi, serta label acuan.
- Pemilihan LLM, dependensi pemodelan, kode model, dan evaluasi.
- Eksperimen aktual, hasil per aspek bila relevan, serta analisis kesalahan.
- Laporan pertama, artikel, slide, dan ketentuan tenggat pengumpulan dari dosen.

Belum ada klaim bahwa pengumpulan data, eksperimen, atau laporan selesai.

## Format pembaruan status

Saat satu bagian selesai, catat tanggal, commit/versi, cara menjalankan,
hasil pemeriksaan, tautan bukti, keterbatasan, dan ketergantungan yang tersisa.
Bedakan hasil otomatis, pemeriksaan manual, rencana, serta keputusan kelompok.
Jika ada demo atau deployment di kemudian hari, dokumentasikan cara akses
dan status aktual setelah implementasinya tersedia.
