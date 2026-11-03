# Status implementasi ABSA

Catatan awal: 1 November 2026. Ini adalah status fondasi repository;
pembaruan berikutnya mengikuti commit dan pekerjaan nyata.

## Sudah tersedia

| Bagian | Hasil | Batas |
|---|---|---|
| Struktur kerja | data/raw, processed, annotations; notebooks; src; results; docs | Berisi petunjuk; belum ada dataset atau implementasi ABSA |
| Kolaborasi | CONTRIBUTING, SECURITY, template issue/PR, empat nama/NRP, peran dan rencana per minggu; kalender Rabu dengan acuan week 11 pada 4 November 2026 | Pembagian dapat disesuaikan dengan beban nyata; tanggal kelas bukan otomatis tenggat pengumpulan |
| Python | Acuan 3.14 (diganti dari 3.12 pada 3 November 2026), requirements.txt, format file dan ignore | Library model ditambahkan saat kodenya tersedia |
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
| Topik dan metode | [Usulan week 10](../week-10/README.md): ACSA ulasan SATUSEHAT Mobile, label manual vs label LLM, analisis per versi | Disetujui kelompok 3 November 2026; menunggu konfirmasi dosen |
| Keputusan teknis | [Keputusan metode](method-decisions.md): LLM, encoder, preprocessing, pembagian data, format file, metrik | Batas kuota Gemini belum diperiksa di akun kelompok |
| Pengambilan data | `src/scrape_reviews.py` diuji lokal (Python 3.14, `google-play-scraper` 1.2.7): 15.000 ulasan tersimpan dengan 9 kolom | File uji ada di laptop Efraim, belum dibagikan |
| Eksplorasi data | `src/pilot_stats.py`; statistik 2.000 dan 15.000 ulasan di [data/README.md](../../data/README.md) | Persentase aspek masih perkiraan kata kunci, bukan label |
| Panduan anotasi | Kategori aspek, label, dan format file di [data/annotations](../../data/annotations/README.md) | Belum dikalibrasi |

## Menunggu pengerjaan

- Konfirmasi topik dan format BOD dari dosen.
- Kode preprocessing dan pembagian data, kalibrasi anotasi, serta label gold.
- Kunci API Gemini, prompt v1, kode pelabelan LLM, model, dan evaluasi.
- Eksperimen aktual, hasil per aspek bila relevan, serta analisis kesalahan.
- Laporan pertama, artikel, slide, dan ketentuan tenggat pengumpulan dari dosen.

Belum ada klaim bahwa pengumpulan data, eksperimen, atau laporan selesai.

## Format pembaruan status

Saat satu bagian selesai, catat tanggal, commit/versi, cara menjalankan,
hasil pemeriksaan, tautan bukti, keterbatasan, dan ketergantungan yang tersisa.
Bedakan hasil otomatis, pemeriksaan manual, rencana, serta keputusan kelompok.
Jika ada demo atau deployment di kemudian hari, dokumentasikan cara akses
dan status aktual setelah implementasinya tersedia.
