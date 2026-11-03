# Bahan week 10: usulan topik dan metode

Status: usulan Efraim, 3 November 2026. Topik dan metode ini perlu disepakati
berempat dan dikonfirmasi dosen. Format BOD mengikuti arahan dosen; bagian
tujuan di bawah disiapkan sebagai bahannya.

## Judul kerja

Analisis Sentimen Berbasis Aspek pada Ulasan Google Play SATUSEHAT Mobile:
Perbandingan Label Manual dan Label LLM serta Pelacakan Sentimen Aspek per
Versi Aplikasi.

## Latar belakang dan celah

- Penelitian ABSA berbahasa Indonesia umumnya memakai dataset kecil yang
  dilabeli manual untuk satu domain. Anotasi manual mahal dan lambat.
- LA-ABSA (LREC 2026) melatih model ringan dengan label buatan LLM dan
  hasilnya mendekati prompting LLM langsung. Studi tersebut tidak menguji
  bahasa Indonesia.
- SATUSEHAT Mobile (Kementerian Kesehatan) memiliki sekitar 444 ribu ulasan
  dan rating terendah di antara aplikasi layanan publik yang diperiksa (3,38).
  Studi yang ditemukan pada aplikasi ini memakai sentimen tingkat dokumen,
  atau LDA tanpa label aspek acuan (JESICA 2026, 1.460 ulasan dari tiga
  aplikasi). Belum ditemukan ABSA dengan label acuan manual atau analisis
  per versi untuk aplikasi ini.
- Mobile JKN tidak dipilih karena sudah memiliki beberapa studi ABSA
  (UPR 2025, INFOTECH 2026, JATI 2026).
- Google Play menyimpan versi aplikasi pada setiap ulasan
  (`reviewCreatedVersion`), sehingga sentimen aspek dapat dilacak antarrilis.

## Tujuan (bahan BOD)

1. Mengukur apakah label aspek-sentimen buatan LLM dapat menggantikan sebagian
   anotasi manual untuk ABSA bahasa Indonesia.
2. Menghasilkan model ABSA ringan untuk ulasan SATUSEHAT Mobile.
3. Menunjukkan aspek yang paling banyak dikeluhkan dan perubahannya per versi,
   sebagai bahan prioritas perbaikan bagi pengelola aplikasi.

## Pertanyaan penelitian

- RQ1: Seberapa sesuai label LLM dengan label manual (Cohen's kappa, F1)?
- RQ2: Apakah IndoBERT yang dilatih dengan label LLM menyamai atau melampaui
  IndoBERT yang dilatih dengan sedikit label manual dan LLM yang dipakai
  langsung, pada set uji manual yang sama?
- RQ3: Aspek apa yang paling negatif dan bagaimana proporsinya berubah antar
  versi aplikasi? Seberapa sering rating bintang bertentangan dengan sentimen
  aspek?

## Data

- Sumber: ulasan Google Play SATUSEHAT Mobile (`com.telkom.tracencare`),
  bahasa Indonesia, diambil dengan `src/scrape_reviews.py`.
- Target: 15.000 ulasan terbaru. Setelah membuang duplikat dan ulasan kurang
  dari 5 kata, diperkirakan tersisa 8.000-10.000 ulasan.
- Rincian sumber, kolom, dan hasil pilot ada di
  [data/README.md](../../data/README.md).

## Lingkup ABSA

Tugas: aspect category sentiment analysis (ACSA). Untuk setiap ulasan dan
setiap kategori aspek, label berupa `tidak_disebut`, `positif`, `negatif`,
atau `netral`. Ekstraksi frasa aspek/opini (triplet atau quad) di luar
lingkup karena waktu pengerjaan.

Kategori aspek awal ada di
[data/annotations/README.md](../../data/annotations/README.md). Kategori
final ditetapkan setelah anotasi pilot week 11.

## Metode

1. Pengumpulan: scraping ulasan dan metadata (rating, versi, tanggal).
2. Preprocessing: buang duplikat dan ulasan sangat pendek, normalisasi
   ringan (huruf kecil, URL, emoji, singkatan umum). Teks untuk IndoBERT
   tidak di-stemming.
3. Label acuan manual (gold), 800 ulasan diambil acak berstrata rating:
   400 latih, 100 validasi, 300 uji. Set uji dianotasi dua orang.
4. Label LLM (silver): ulasan sisanya dilabeli LLM dengan prompt few-shot
   dari panduan anotasi. Pilihan LLM diputuskan week 11: API dengan kuota
   gratis, atau model terbuka lokal lewat Ollama.
5. Model yang dibandingkan pada set uji manual yang sama:

| Kode | Model | Data latih |
|---|---|---|
| B1 | TF-IDF + Logistic Regression per aspek | Gold latih (400) |
| B2 | IndoBERT (`indobenchmark/indobert-base-p1`) | Gold latih (400) |
| B3 | LLM langsung, zero-shot dan few-shot | Tanpa pelatihan |
| P1 | IndoBERT | Silver (label LLM) |
| P2 | IndoBERT | Silver, lalu dilanjutkan dengan gold latih |

6. Analisis per versi dan konsistensi rating memakai prediksi model terbaik
   pada seluruh ulasan.

## Evaluasi

- Deteksi aspek: F1 micro dan macro per kategori.
- Sentimen aspek: F1 pasangan (aspek, sentimen) sebagai metrik utama, dan
  macro-F1 sentimen per aspek.
- Kesepakatan: Cohen's kappa antar-anotator manusia dan antara LLM dengan
  label manual.
- Efisiensi: waktu inferensi per 1.000 ulasan untuk LLM dan IndoBERT.
- Konfigurasi dipilih dengan set validasi. Set uji dipakai sekali di akhir.
  Ulasan gold tidak boleh masuk data silver.

## Keluaran

- Dataset ulasan beranotasi aspek-sentimen (800 gold, ribuan silver) dan
  panduan anotasinya.
- Tabel perbandingan B1-B3 dan P1-P2 untuk menjawab RQ1-RQ2. Hasil apa pun
  tetap informatif: jika label LLM buruk, temuan itu juga dilaporkan.
- Grafik proporsi sentimen negatif per aspek per versi, daftar aspek
  prioritas, dan contoh ulasan yang ratingnya bertentangan dengan isinya.
- Bahan laporan week 13, artikel week 15, dan presentasi week 16.

## Kelayakan

Pilot 3 November 2026 (2.000 ulasan terbaru):

- Scraping berjalan tanpa API key. Rentang 3 Desember 2025 sampai
  2 November 2026.
- 48% ulasan memiliki minimal 8 kata. 79% ulasan menyimpan versi aplikasi,
  dengan 77 versi berbeda dan 9 versi yang memiliki minimal 50 ulasan.
- Rating: 41% bintang 1, 44% bintang 5. Keluhan cukup banyak untuk analisis
  aspek negatif.
- Contoh keluhan berulang: login/PIN/OTP, data sudah terdaftar, hasil cek
  kesehatan gratis (CKG) tidak muncul, aplikasi force close.

Beban kerja:

- Anotasi 800 + 300 ulasan (set uji dua kali) dibagi berempat, kira-kira
  275 ulasan per orang, 2-3 jam per orang.
- IndoBERT base dapat di-fine-tune pada GPU 6 GB (RTX 4050) atau Google
  Colab dengan panjang 128 token.
- Pelabelan LLM untuk sekitar 10.000 ulasan: beberapa jam dengan model
  lokal, lebih cepat melalui API.

## Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Banyak ulasan pendek tanpa aspek ("bagus", "mantap") | Kategori `umum`, filter minimal 5 kata |
| Kategori aspek jarang sehingga F1 tidak stabil | Gabungkan kategori sesudah pilot, laporkan jumlah data per aspek |
| Kuota atau biaya API LLM | Model terbuka lokal sebagai cadangan |
| Kesepakatan anotator rendah | Kalibrasi 50 ulasan bersama sebelum anotasi penuh |
| Ketentuan Google Play terkait distribusi ulasan | Data mentah tidak diunggah; repo berisi skrip dan ID ulasan |

## Pembagian peran

- Efraim: scraping, eksplorasi data, statistik per versi, tujuan/BOD.
- Bambang: preprocessing, panduan anotasi, koordinasi label gold dan kappa.
- Jap: prompt LLM, pelabelan silver, B1-B3 dan P1-P2.
- Geraldyn: fungsi evaluasi, tabel metrik, grafik, analisis kesalahan dan
  analisis per versi.

Anotasi gold dikerjakan berempat.

## Referensi awal

- LLM-as-an-Annotator (LA-ABSA), LREC 2026: https://aclanthology.org/2026.lrec-1.632/
- Beyond Stars, arXiv 2509.20953: https://arxiv.org/abs/2509.20953
- Fault in your stars, arXiv 1708.04968: https://arxiv.org/abs/1708.04968
- ABSA ulasan aplikasi kesehatan dengan LDA dan IndoBERT (JESICA 2026):
  https://jesica.itsk-soepraoen.ac.id/index.php/jesica/article/view/47
- ABSA Mobile JKN berbasis transformer (UPR 2025):
  https://e-journal.upr.ac.id/index.php/jcoms/article/view/25348
- IndoNLU (HoASA, TermA): https://huggingface.co/datasets/indonlp/indonlu
- Analisis sentimen SATUSEHAT Mobile, SVM dan Naive Bayes (JATI):
  https://ejournal.itn.ac.id/jati/article/view/17629

Sebagian rujukan Indonesia berasal dari jurnal lokal. Periksa naskah asli
sebelum mengutip angka.
