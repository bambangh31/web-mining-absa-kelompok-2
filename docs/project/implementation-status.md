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

## Perangkat anotasi Bambang (3 November 2026)

- `src/annotation.py`: lembar kalibrasi yang sama (50 ulasan per anggota),
  pembagian gold 275 penugasan per anggota (800 ulasan unik; set uji ganda),
  pemeriksaan label/ID/teks, kappa per aspek sebelum adjudikasi, dan ekspor
  label tanpa teks setelah perbedaan diselesaikan.
- [Alur penggunaan](annotation-workflow.md): bahan dari Efraim, kalibrasi,
  format keputusan, dan penyelesaian perbedaan oleh pihak ketiga.
- `tests/test_annotation.py`: delapan tes perilaku dengan 850 ulasan buatan
  dalam folder sementara, bukan dataset atau hasil anotasi nyata.
  CI ditambah untuk menjalankan tes pada Python 3.14.
- Pengguna mengonfirmasi dataset belum dibagikan. Belum ada kalibrasi
  manusia, kappa kelompok, gold aktual, atau pedoman yang diklaim final.
  Preprocessing/model serta tugas Efraim, Jap, dan Geraldyn tetap mengikuti
  keputusan yang ada.

## Revisi masukan dosen dan pipeline ABSA (10 November 2026)

| Bagian | Hasil | Batas |
|---|---|---|
| Skema | Delapan kategori aspek (tambah `pembaruan_aplikasi`, `layanan_pelanggan`), aturan agregasi penyebutan ke label per ulasan (`src/absa_schema.py`); `annotation.py` memakai skema yang sama | Lembar kalibrasi/gold lama berisi enam kolom; buat workspace baru sebelum diisi |
| Preprocessing | Hash clean/split diulang dan sama persis; normalisasi slang B1 diterapkan (75,1% ulasan, 12,7% token berubah); tokenisasi untuk BiLSTM | Kamus slang tidak berlisensi eksplisit, diunduh terpisah |
| Lembar label manual | 354 ulasan, 674 penyebutan diperiksa terhadap data asli; 33 koreksi (kata aspek tidak cocok dengan bukti, kategori tertukar, opini terlewat); versi kosong dikembalikan kosong; ditambah lembar Kategori Aspek dan Label per Ulasan | Hanya 5 ulasan termasuk set uji; bukan pengganti 300 ulasan uji dua anotator |
| Label LLM | `src/llm_label.py`, prompt v1, `gemini-3.5-flash-lite`; lembar Excel versi LLM; perbandingan `src/compare_labels.py` | Kuota gratis kecil (20 permintaan/hari per model pada gemini-3.5-flash). 300 ulasan uji sudah dilabeli (`data/annotations/llm_gemini-3.5-flash-lite.csv`); 500 ulasan latih/validasi dilanjutkan pada hari berikutnya |
| Verifikasi | Lembar dua langkah per anggota dan ekspor `verified.csv` + tingkat koreksi (`src/verification.py`) | Menunggu label LLM 800 ulasan dan pengisian anggota |
| Model | Kode B1-LR/SVM/NB, B4, B2, B2-L, B3 (Gemini/Ollama) dengan data dan aturan keluaran yang sama | IndoBERT berhenti karena RAM laptop habis setelah model termuat; dijalankan di Colab. fastText belum diunduh |
| Evaluasi | Metrik keseluruhan dan per aspek, kappa, paired bootstrap (`src/evaluate.py`); pratinjau 5-fold B1 pada lembar manual (`src/preview_cv.py`) | Pratinjau bukan hasil set uji |
| Tes | 30 tes data buatan lulus (sebelumnya 15) | Tes tidak menilai kualitas label manusia atau model pada data asli |

Cara menjalankan setiap langkah dan keluarannya ada di
[pipeline](pipeline.md).

## Menunggu pengerjaan

- Konfirmasi topik dan format BOD dari dosen.
- Kode preprocessing dan pembagian data, kalibrasi anotasi, serta label gold.
- Label Gemini untuk 500 ulasan latih/validasi (lanjut setelah kuota harian pulih; 300 uji sudah selesai), verifikasi anggota, label uji dua anotator.
- Pelatihan IndoBERT base/large di Colab, unduh fastText untuk B4, Ollama untuk B3-Qwen.
- Eksperimen aktual, hasil per aspek bila relevan, serta analisis kesalahan.
- Laporan pertama, artikel, slide, dan ketentuan tenggat pengumpulan dari dosen.

Belum ada klaim bahwa pengumpulan data, eksperimen, atau laporan selesai.

## Format pembaruan status

Saat satu bagian selesai, catat tanggal, commit/versi, cara menjalankan,
hasil pemeriksaan, tautan bukti, keterbatasan, dan ketergantungan yang tersisa.
Bedakan hasil otomatis, pemeriksaan manual, rencana, serta keputusan kelompok.
Jika ada demo atau deployment di kemudian hari, dokumentasikan cara akses
dan status aktual setelah implementasinya tersedia.
