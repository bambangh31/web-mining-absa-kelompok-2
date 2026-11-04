# Keputusan metode

Ditetapkan 3 November 2026 setelah topik disetujui kelompok. Setiap keputusan
disertai alasan dan bukti. Jika keputusan berubah, catat di bagian
[Riwayat](#riwayat) beserta eksperimen yang perlu diulang.

## Ringkasan

| Bagian | Keputusan |
|---|---|
| LLM label silver | Gemini Flash melalui kuota gratis Gemini API; cadangan model lokal `qwen3.5:4b` lewat Ollama |
| Pemilihan akhir LLM | LLM dengan F1 pasangan tertinggi pada set validasi gold (100 ulasan) |
| Encoder | `indolem/indobertweet-base-uncased`, klasifikasi sentence-pair (ulasan, aspek) |
| Preprocessing | 13 aturan di bawah; tanpa stopword removal, tanpa stemming |
| Pembagian data | 50 kalibrasi, 800 gold (400/100/300), sisanya silver; seed 42 |
| Python | 3.14; PyTorch CUDA dari indeks PyTorch |

## Spesifikasi laptop acuan

Laptop Efraim, diperiksa 3 November 2026: Intel Core i5-13500HX (14 core,
20 thread), RAM 7,7 GB, NVIDIA GeForce RTX 4050 Laptop 6 GB VRAM, driver
610.74, ruang kosong C: 73 GB dan D: 143 GB.

RAM 7,7 GB dan VRAM 6 GB membatasi model lokal ke kelas 4B. Model 8B pada
kuantisasi 4-bit membutuhkan sekitar 5 GB VRAM ditambah konteks, sehingga
tidak muat sepenuhnya di GPU dan akan melimpah ke RAM yang juga kecil.

## LLM untuk label silver

### Kebutuhan

- Sekitar 11.850 ulasan: 11.400 silver, 300 uji dan 100 validasi untuk B3,
  serta 50 kalibrasi.
- Satu permintaan API berisi 20 ulasan dan contoh few-shot. Perkiraan
  sekitar 3.000 token per permintaan, jadi sekitar 600 permintaan dan
  1,8 juta token.
- Keluaran JSON yang mengikuti skema, agar tidak ada label di luar empat
  pilihan.

### Pilihan yang diperiksa

| Pilihan | Batas gratis (sumber sekunder, Nov 2026) | Waktu untuk 600 permintaan | Catatan |
|---|---|---|---|
| Gemini API, Flash / Flash-Lite | Tidak dipublikasikan resmi; laporan 250-1.500 permintaan/hari untuk Flash, sekitar 500 untuk Flash-Lite | 1-3 hari | Mendukung JSON schema. Konten kuota gratis dapat dipakai Google untuk pengembangan produk |
| Groq, `gpt-oss-120b` | 1.000 permintaan/hari, 200.000 token/hari | Sekitar 9 hari karena batas token | Model terbuka |
| Groq, `llama-3.1-8b-instant` | 14.400 permintaan/hari, 500.000 token/hari | Sekitar 4 hari | Model kecil, tidak lebih baik dari model lokal |
| OpenRouter, model `:free` | 50 permintaan/hari tanpa pembelian kredit | Sekitar 12 hari | 1.000/hari setelah membeli kredit 10 USD |
| Lokal, Ollama `qwen3.5:4b` | Tanpa batas | Sekitar 7,5 jam (diukur) | 3,3 GB, 3,7 GB VRAM terpakai |
| Lokal, SEA-LION v4 4B (Gemma) | Tanpa batas | Tidak diukur | Dilatih lanjut untuk bahasa Asia Tenggara termasuk Indonesia; gagal dipasang saat uji |

### Keputusan

Utama: Gemini Flash dengan kuota gratis. Pakai model Flash terbaru yang
tercantum gratis di halaman rate limit AI Studio. Jika kuota harian Flash
di bawah 300 permintaan, pakai Flash-Lite. Catat ID model persis dan tanggal
pemakaian.

Alasan:

1. Model terbesar yang tersedia tanpa biaya. Pada studi ABSA multibahasa
   zero-shot, model besar (GPT-4o) jauh di atas model 7-9B; rata-rata
   seluruh model prompting juga masih di bawah model fine-tuned (41,8 vs
   68,9 micro-F1). Kualitas label silver menentukan batas atas P1 dan P2.
2. Kuota cukup bila 20 ulasan digabung per permintaan: sekitar 600
   permintaan selesai dalam 1-3 hari.
3. Mendukung JSON schema, sehingga label selalu valid.
4. Tidak membebani laptop dengan RAM 7,7 GB.

Cadangan dan pembanding: model lokal lewat Ollama. Dipakai bila kuota Gemini
habis atau berubah, dan dipakai sebagai pembanding B3 (LLM besar lewat API
vs LLM kecil lokal).

Aturan pemilihan akhir: jalankan kedua LLM pada 100 ulasan validasi gold.
LLM dengan F1 pasangan lebih tinggi menjadi pelabel silver. Set uji tidak
dipakai untuk memilih.

### Risiko

| Risiko | Penanganan |
|---|---|
| Batas kuota gratis berubah atau tidak cukup | Simpan progres per batch; lanjutkan dengan model lokal |
| Teks kuota gratis dapat dibaca dan dipakai Google | Hanya teks ulasan publik yang sudah disamarkan; tanpa nama pengguna. Disebutkan di laporan |
| Model tertutup bisa berubah | Simpan respons mentah (`llm_<model>.jsonl`), ID model, tanggal, dan versi prompt |
| Keluaran tidak valid | JSON schema; ulangi permintaan yang gagal maksimal 3 kali |

### Pengaturan

- Temperature 0.
- Prompt sistem: panduan anotasi ringkas dan 8-12 contoh dari set kalibrasi
  (bukan dari gold). Versi prompt dicatat (`prompt_version`, mulai `v1`).
- Gemini: 20 ulasan per permintaan, keluaran array JSON berisi `reviewId`
  dan enam label.
- Ollama: satu ulasan per permintaan, `format` berisi JSON schema,
  `think: false`, `num_ctx` 2048.
- Kunci API disimpan di `.env` (`GEMINI_API_KEY`), lihat `.env.example`.

### Uji lokal

Uji asap 3 November 2026 di laptop acuan dengan Ollama 0.40.13 dan
`qwen3.5:4b`. Masukan: 30 ulasan pilot acak (minimal 3 kata, seed 42),
prompt zero-shot berisi panduan anotasi, JSON schema.

| Ukuran | Hasil |
|---|---|
| JSON tidak valid | 0 dari 30 |
| VRAM terpakai | 3,7 GB dari 6 GB, 100% di GPU |
| Kecepatan | 2,29 detik per ulasan, 37,5 token/detik |
| Perkiraan 11.850 ulasan | Sekitar 7,5 jam |
| F1 deteksi aspek / F1 pasangan | 0,63 / 0,61 |

Pembanding F1 adalah label yang dibuat asisten untuk uji ini, bukan label
gold. Angka hanya menunjukkan bahwa model kecil bekerja dan di mana
kesalahannya, bukan kualitas akhir.

Pola kesalahan: model menambah aspek yang tidak disebut. "Susah login"
juga diberi `performa` dan `kemudahan_penggunaan` negatif, aspek yang tidak
disebut diberi `netral`, dan `umum` diisi walaupun ada aspek khusus. Aturan
anotasi diperjelas untuk ketiga hal ini, dan prompt v1 harus memuat contoh
few-shot untuk kasus tersebut.

SEA-LION v4 4B (`aisingapore/Gemma-SEA-LION-v4-4B-VL-GGUF`) tidak diuji:
pengambilan model dari Hugging Face lewat Ollama gagal pada tahap manifest.
Model ini tetap menjadi kandidat jika tim berhasil memasangnya.

## Encoder

### Keputusan

`indolem/indobertweet-base-uncased` dengan klasifikasi sentence-pair. Masukan
berupa pasangan (teks ulasan, deskripsi aspek), keluaran salah satu dari
empat label. Satu ulasan menghasilkan enam pasangan.

Alasan memilih IndoBERTweet:

1. Teks ulasan informal. Pada 2.000 ulasan pilot terdapat `gak` 211 kali,
   `ga` 196, `yg` 152, `udah` 148, `apk` 91, `gk` 59, `bgt` 32. IndoBERTweet
   dilatih pada tweet berbahasa Indonesia dan kosakatanya disesuaikan
   dengan teks media sosial.
2. Pada tabel model card IndoBERTweet, varian dengan adaptasi kosakata
   mendapat 86,6 (sentimen IndoLEM) dan 92,7 (SmSA), dibanding IndoBERT
   indobenchmark 84,1 dan 88,7. Beberapa studi lokal pada teks informal juga
   melaporkan IndoBERTweet lebih baik dari IndoBERT.
3. Ukuran sama (base, sekitar 110 juta parameter), sehingga waktu training
   tidak bertambah.
4. Tokenizer memotong ulasan pilot menjadi median 10, persentil 99 sebanyak
   77, dan maksimum 116 token. Panjang 160 token mencakup ulasan terpanjang
   ditambah deskripsi aspek.

Alasan sentence-pair: studi ABSA ulasan Indonesia dengan IndoBERT (BEEI)
mendapat hasil terbaik dengan sentence-pair dibanding single-sentence.
Deskripsi aspek dalam masukan juga membantu ketika data gold hanya 400
ulasan.

Pemeriksaan: B2 juga dilatih dengan `indobenchmark/indobert-base-p1`, yang
paling sering dipakai pada studi ABSA Indonesia. Jika IndoBERT-p1 lebih tinggi
pada set validasi, P1 dan P2 memakai IndoBERT-p1. Perbandingan ini murah
karena gold latih kecil.

### Hiperparameter

| Parameter | Nilai | Alasan |
|---|---|---|
| Panjang maksimum | 160 token, pemotongan hanya pada teks ulasan | Ulasan terpanjang pilot 116 token ditambah deskripsi aspek |
| Learning rate | 2e-5 | Nilai umum untuk fine-tuning BERT base |
| Batch | 16 | Muat di 6 GB VRAM dengan fp16 |
| Epoch gold (B2) | Maksimal 10, early stopping patience 2 | Data kecil, 2.400 pasangan |
| Epoch silver (P1) | 3 | Sekitar 68.000 pasangan |
| Lanjutan gold (P2) | Maksimal 5, early stopping patience 2 | Penyesuaian setelah silver |
| Warmup / weight decay | 10% / 0,01 | Pengaturan standar |
| Kriteria early stopping | F1 pasangan pada set validasi | Sama dengan metrik utama |
| Seed | 42, 43, 44 | Data kecil; laporkan rata-rata dan simpangan baku |

Training dapat dijalankan di laptop acuan atau Google Colab.

## Preprocessing

Ada dua versi teks. `text_llm` dikirim ke LLM. `text_model` dipakai TF-IDF
dan encoder.

| No | Aturan | Berlaku untuk | Alasan dan bukti |
|---|---|---|---|
| 1 | Buang ulasan sebelum 1 Maret 2023 | Semua | Sebelum tanggal itu aplikasi masih PeduliLindungi. 15.000 ulasan terbaru dimulai 17 Juli 2023, jadi aturan ini berjaga-jaga |
| 2 | Buang ulasan kosong; rapikan spasi dan baris baru | Semua | Teks kosong tidak bisa dilabeli |
| 3 | Buang ulasan kurang dari 3 kata | Semua | Kata kunci aspek muncul pada 1% ulasan 1 kata, 6% ulasan 2 kata, 12% ulasan 3 kata, 25% ulasan 4 kata. Ulasan 3 kata masih membawa aspek, misalnya "ga bisa daftar". Menyisakan 83,3% |
| 4 | Buang duplikat persis setelah huruf kecil dan spasi dirapikan; simpan yang paling awal | Data latih dan evaluasi | 1.676 dari 15.000 ulasan duplikat, didominasi "bagus" dan "mantap". Duplikat di latih dan uji sekaligus menggelembungkan skor |
| 5 | Samarkan NIK 16 digit `[NIK]`, nomor telepon `[TELEPON]`, email `[EMAIL]`, URL `HTTPURL` | Semua | Tidak ditemukan pada 15.000 ulasan, tetapi teks dikirim ke API pihak ketiga. Biaya aturan ini kecil |
| 6 | Pertahankan huruf besar dan emoji | `text_llm` | LLM memahami emoji dan huruf kapital sebagai penekanan |
| 7 | Huruf kecil | `text_model` | IndoBERTweet uncased |
| 8 | Ubah emoji menjadi teks bahasa Indonesia (`emoji.demojize(language="id")`, garis bawah menjadi spasi) | `text_model` | 4,7% ulasan memakai emoji. Mengikuti praproses IndoBERTweet; contoh 👍 menjadi "jempol ke atas" |
| 9 | Huruf berulang 3 kali atau lebih menjadi 2 ("lamaaaaa" menjadi "lamaa") | `text_model` | 3,0% ulasan. Dua huruf menjaga kata seperti "maaf" dan tetap menandai penekanan |
| 10 | Tanpa stopword removal | Semua | 34,9% ulasan memuat negasi (tidak, gak, ga, belum, bukan). Daftar stopword umum memuat kata negasi, sehingga sentimen bisa terbalik |
| 11 | Tanpa stemming | Semua | "terdaftar" (sudah terdaftar, keluhan data) dan "daftar" (mendaftar) bermakna berbeda untuk aspek `registrasi_data`. Encoder memakai subword |
| 12 | Normalisasi slang dengan `colloquial-indonesian-lexicon.csv` (Salsabila dkk., 2018) | Hanya B1 (TF-IDF) | TF-IDF menganggap "gak", "ga", "gk", "tdk" sebagai fitur berbeda (lebih dari 500 kemunculan pada pilot). Encoder dan LLM sudah mengenal slang; kamus bisa salah ganti |
| 13 | Tanpa filter bahasa | Semua | Hanya 1 dari 2.000 ulasan pilot terdeteksi berbahasa Inggris |

Tanda baca dipertahankan untuk encoder dan LLM. Balasan pengembang tidak
dipakai sebagai masukan.

Untuk analisis per versi (RQ3), duplikat tidak dibuang karena tiap ulasan
berasal dari pengguna berbeda. Aturan 1, 2, 3, dan 5 tetap berlaku.

## Pembagian data

1. Terapkan aturan preprocessing. Hasilnya `pool` (12.297 ulasan pada uji
   15.000 ulasan).
2. Dengan seed 42, ambil 50 ulasan kalibrasi acak berstrata rating.
3. Dari sisa `pool`, ambil 800 ulasan gold acak berstrata rating
   proporsional, lalu bagi 400 latih, 100 validasi, 300 uji, juga berstrata
   rating.
4. Sisanya menjadi `silver`.
5. Simpan di `data/annotations/split.csv`.

Proporsi rating di `pool`: bintang 1 75,7%, 2 6,5%, 3 4,4%, 4 2,4%, 5 11,0%.
Sampel proporsional dipilih agar skor uji mencerminkan data nyata. Jumlah
label per aspek dan sentimen dilaporkan, karena sentimen positif akan
jarang.

## Format file

| File | Kolom |
|---|---|
| `data/raw/com.telkom.tracencare_reviews.csv` | Keluaran `src/scrape_reviews.py` |
| `data/processed/reviews_clean.csv` | `reviewId`, `at`, `score`, `reviewCreatedVersion`, `text_llm`, `text_model`, `n_words`, `in_pool` |
| `data/annotations/split.csv` | `reviewId`, `split` |
| `data/annotations/gold_<nama>.csv`, `gold.csv` | `reviewId`, (`annotator`), enam kolom aspek |
| `data/annotations/llm_<model>.csv` | `reviewId`, `model`, `prompt_version`, enam kolom aspek |
| `results/predictions/<model>_<seed>.csv` | `reviewId`, `model_code`, `seed`, enam kolom aspek |
| `results/metrics/<model>_<seed>.json` | Nilai metrik dan konfigurasi run |

Enam kolom aspek: `akun_login`, `registrasi_data`, `fitur_kesehatan`,
`performa`, `kemudahan_penggunaan`, `umum`. Nilainya `tidak_disebut`,
`positif`, `negatif`, atau `netral`.

## Definisi metrik

- F1 pasangan (utama): micro-F1 atas tuple (ulasan, aspek, sentimen) yang
  labelnya bukan `tidak_disebut`. Prediksi benar jika aspek dan sentimen sama.
- F1 deteksi aspek: micro- dan macro-F1 atas pasangan (ulasan, aspek) yang
  labelnya bukan `tidak_disebut`, tanpa melihat sentimen.
- Macro-F1 sentimen per aspek: dihitung pada ulasan yang aspeknya disebut
  dalam label gold.
- Cohen's kappa per aspek atas empat label: antar-anotator dan LLM vs gold.
- Efisiensi: detik per 1.000 ulasan saat inferensi.

## Analisis per versi dan konsistensi rating

- Versi: kolom `reviewCreatedVersion`. Ulasan tanpa versi dikeluarkan dari
  analisis ini (73,8% terisi pada 15.000 ulasan).
- Hanya versi dengan minimal 50 ulasan (54 versi pada uji 15.000 ulasan).
- Proporsi negatif per aspek per versi: jumlah ulasan dengan aspek tersebut
  `negatif` dibagi jumlah ulasan pada versi itu, dengan interval kepercayaan
  Wilson 95%.
- Rating bertentangan: bintang 4-5 dengan minimal satu aspek negatif dan
  tanpa aspek positif, atau bintang 1-2 dengan minimal satu aspek positif
  dan tanpa aspek negatif.
- Memakai prediksi model terbaik pada seluruh ulasan setelah aturan 1, 2,
  3, dan 5.

## Lingkungan

- Python 3.14 untuk lokal dan CI. Google Colab memakai versinya sendiri
  (dilaporkan 3.13 sejak Agustus 2026); periksa dengan `!python --version`.
- Paket model terverifikasi tersedia untuk Python 3.14 Windows pada
  3 November 2026: `torch` 2.15.0 (CPU, PyPI), `transformers` 5.22.1,
  `scikit-learn` 1.9.1, `pandas` 3.1.0, `datasets` 5.1.0,
  `accelerate` 1.15.0.
- PyTorch dengan GPU NVIDIA:

```text
python -m pip install torch --index-url https://download.pytorch.org/whl/cu130
```

  Versi yang tersedia saat diperiksa: `torch` 2.14.1+cu130.
- Ollama 0.40.13 untuk model lokal.

## Riwayat

| Tanggal | Perubahan | Alasan | Eksperimen yang perlu diulang |
|---|---|---|---|
| 3 Nov 2026 | Keputusan awal | Topik disetujui kelompok | - |
| 4 Nov 2026 | Dataset final: semua ulasan sejak 1 Maret 2023 (39.995 baris, pool 32.035), menggantikan 15.000 ulasan uji | Permintaan kelompok untuk memakai seluruh data era SATUSEHAT | Belum ada eksperimen. Angka pool dan beban LLM di dokumen ini masih berdasarkan uji 15.000 ulasan; silver menjadi sekitar 31.000 ulasan (perkiraan sekitar 1.600 permintaan Gemini atau sekitar 20 jam dengan model lokal) |

## Rujukan

- Zero-shot multilingual ABSA dengan LLM: https://arxiv.org/abs/2412.12564
- LA-ABSA, LREC 2026: https://aclanthology.org/2026.lrec-1.632/
- IndoBERTweet: https://arxiv.org/abs/2109.04607
- Model IndoBERTweet: https://huggingface.co/indolem/indobertweet-base-uncased
- ABSA ulasan Indonesia sentence-pair (BEEI): https://beei.org/index.php/EEI/article/view/8032
- SEA-LION v4: https://huggingface.co/collections/aisingapore/sea-lion-v4
- Ketentuan tambahan Gemini API: https://ai.google.dev/gemini-api/terms
- Batas OpenRouter: https://openrouter.ai/docs/api/reference/limits
- Model Ollama untuk 6 GB VRAM: https://localaimaster.com/vram/best-ollama-models-6gb-vram
- Kamus slang: https://github.com/nasalsabila/kamus-alay
- PeduliLindungi menjadi SATUSEHAT Mobile: https://covid19.go.id/en/artikel/2023/03/01/mulai-1-maret-2023-pedulilindungi-menjadi-satusehat-mobile
