# Catatan belajar presentasi ABSA SATUSEHAT

Disusun 11 November 2026 dari kode dan data di repo (commit `34b0ed9`).
Semua angka dan contoh di sini diambil dari file sungguhan, bukan perkiraan.
Kalau ada yang belum dijalankan, ditulis jelas "belum ada hasil".

Isi:

1. [Lima kelompok data (split)](#1-lima-kelompok-data-split)
2. [Satu ulasan lewat empat pendekatan](#2-satu-ulasan-lewat-empat-pendekatan)
3. [Tiga file Excel](#3-tiga-file-excel)
4. [Ringkasan untuk dihafal](#4-ringkasan-untuk-dihafal)

---

## Istilah dasar

- **Ulasan**: satu komentar Google Play tentang aplikasi SATUSEHAT Mobile.
  Setiap ulasan punya `reviewId` unik.
- **Delapan aspek** (`src/absa_schema.py`, `ASPECTS`): `akun_login`,
  `registrasi_data`, `fitur_kesehatan`, `performa`, `kemudahan_penggunaan`,
  `pembaruan_aplikasi`, `layanan_pelanggan`, `umum`.
- **Empat label per aspek** (`LABELS`): `tidak_disebut`, `positif`,
  `negatif`, `netral`.
- Jadi setiap ulasan mendapat **8 label sekaligus** (multi-aspek). Satu
  ulasan bisa punya dua aspek dengan sentimen berbeda.
- **Aturan `umum`**: `umum` hanya boleh diisi kalau tidak ada aspek khusus.
  Aturan ini dijalankan oleh `aggregate_mentions()` dan `validate_labels()`
  di `src/absa_schema.py`, serta `enforce_umum()` di `src/model_data.py`
  untuk keluaran model.
- **Penyebutan → label per ulasan**: di Excel, satu baris = satu penyebutan
  aspek. `aggregate_mentions()` menggabungkannya: kalau semua penyebutan
  netral → `netral`; selain itu suara terbanyak positif/negatif; kalau seri
  → `negatif`.

## Dari data mentah sampai split

`src/preprocess.py` (fungsi `clean_rows()` lalu `make_split()`):

| Tahap | Jumlah | Sumber angka |
|---|---|---|
| Ulasan mentah (`data/raw/com.telkom.tracencare_reviews.csv`) | 39.995 | `results/preprocessing/v1/summary.json` |
| Dibuang karena kurang dari 3 kata | 7.152 | sama |
| Ditandai duplikat (tidak masuk pool) | 808 | sama |
| **Pool** (boleh diambil untuk split) | 32.035 | sama |

Setiap ulasan di `data/processed/reviews_clean.csv` punya dua versi teks:

- `text_llm`: teks asli yang dirapikan spasinya, dan URL, email, NIK, serta
  nomor telepon diganti penanda (`redact()`). Dipakai oleh Gemini/Qwen.
- `text_model`: `text_llm` yang dibuat huruf kecil, emoji diubah jadi teks,
  dan huruf berulang dipendekkan (`model_text()`). Dipakai oleh B1, BiLSTM,
  dan IndoBERT.

`make_split()` memakai seed 42 dan `stratified_take()`: sampel diambil
berstrata rating bintang, supaya proporsi bintang 1-5 di tiap kelompok
mirip dengan pool. Hasilnya ditulis ke `data/annotations/split.csv` (hanya
dua kolom: `reviewId`, `split`).

---

## 1. Lima kelompok data (split)

Angka dihitung langsung dari `data/annotations/split.csv`.

| Split | Jumlah | Fungsi |
|---|---|---|
| `kalibrasi` | 50 | Latihan menyamakan cara melabel antar-anggota |
| `gold_train` | 400 | Data latih model |
| `gold_val` | 100 | Memilih parameter dan kapan berhenti melatih |
| `gold_test` | 300 | Ujian akhir semua model |
| `silver` | 31.185 | Sisa pool; tidak dipakai untuk melatih, hanya analisis per versi |

Total: 50 + 400 + 100 + 300 + 31.185 = 32.035 (= pool).

Distribusi rating (`summary.json`, `rating_by_split`), contoh `gold_test`:
bintang 1 = 222, 2 = 25, 3 = 15, 4 = 7, 5 = 31.

### 1.1 `kalibrasi` (50 ulasan)

- **Fungsi**: keempat anggota (bambang, efraim, jap, geraldyn) melabeli 50
  ulasan yang **sama**, lalu perbedaan dibahas dan panduan diperbarui.
  Ulasan ini tidak masuk set gold.
- **Siapa yang melabeli**: manusia, 4 orang. Pembagiannya ada di
  `src/annotation.py`, fungsi `assign()`: untuk `kalibrasi`, setiap ulasan
  diberikan ke semua anggota (`MEMBERS`). Lembarnya dibuat oleh
  `prepare()`, diperiksa oleh `audit()` (Cohen's kappa lewat
  `cohen_kappa()`), dan diekspor oleh `finalize()`.
- **Gemini sengaja tidak melabeli**: `src/llm_label.py`, fungsi `main()`,
  berhenti dengan pesan kalau `kalibrasi` diminta, karena kalibrasi
  direncanakan jadi sumber contoh few-shot.
- **Dipakai di skrip**: hanya `annotation.py`. Tidak dipakai oleh model,
  `evaluate.py`, `verification.py`, maupun `llm_label.py`.
- **Status**: label kalibrasi manusia belum ada di repo.

**Contoh nyata** (`reviewId` `8aea7d72-4f98-4147-8020-05062c135d89`,
rating 1). Satu-satunya ulasan kalibrasi yang kebetulan ada di Excel manual:

> Arsip sya malah hilang setlh update ke satusehat. Sertifikat yg sudah di
> unduh hilang data nya

| Sumber | Label (aspek yang disebut saja) |
|---|---|
| Excel manual | `fitur_kesehatan` negatif, `pembaruan_aplikasi` negatif |
| Excel Gemini | `fitur_kesehatan` negatif, `pembaruan_aplikasi` negatif |

Penyebutan di Excel manual: "Arsip", "Sertifikat", dan "unduh" →
fitur kesehatan negatif; "update" → pembaruan aplikasi negatif. Enam aspek
lain `tidak_disebut`.

### 1.2 `gold_train` (400 ulasan)

- **Fungsi**: data latih. Semua model terlatih (B1, B4, B2, B2-L) memakai
  400 ulasan yang sama, supaya perbedaan skor berasal dari model, bukan dari
  datanya (masukan dosen 6 November 2026).
- **Siapa yang melabeli**: Gemini lebih dulu, lalu diperiksa manusia.
  1. `src/llm_label.py --set split`: fungsi `label_reviews()` mengirim
     `text_llm` ke Gemini, `clean_mentions()` memeriksa jawabannya, lalu
     `aggregate_mentions()` mengubahnya jadi 8 label. Hasilnya ditulis ke
     `data/annotations/llm_gemini-3.5-flash-lite.csv`.
  2. `src/verification.py prepare`: membuat 4 lembar
     `verifikasi_<nama>.xlsx` (100 latih + 25 validasi per orang; pembagian
     dari `annotation.assign()`). Untuk tiap aspek, pemeriksa mengisi
     `setuju` atau `salah`; kolom Pengganti diisi hanya kalau `salah`.
  3. `src/verification.py export`: menggabungkan lembar menjadi
     `data/annotations/verified.csv` dan menghitung tingkat koreksi.
- **Dipakai di skrip**: `src/model_data.py` kelas `Dataset` (`train_ids`),
  yang dipakai `models_classic.py`, `model_bilstm.py`, dan
  `model_indobert.py`. Juga `verification.py` dan `llm_label.py`.
- **Status (11 November 2026)**: Gemini **sudah** melabeli 400 ulasan ini.
  `llm_gemini-3.5-flash-lite.csv` sekarang berisi 800 baris (400 latih,
  100 validasi, 300 uji; 1.524 penyebutan, 27 catatan validasi di
  `split_v1/issues.csv`). Lembar verifikasi kosong sudah dibuat di
  `data/annotation_workspace/verifikasi/verifikasi_<nama>.xlsx`, masing-masing
  125 ulasan. Lembar itu **belum diisi**, jadi `verified.csv` belum ada.

**Contoh nyata** (`a0585fef-f347-43cc-a437-1db3f0b017aa`, rating 2):

> Aplikasi Satusehat sulit,ribet wa nggk pernah dibalas,padahal kami sangat
> butuh ...enakkn yg dulu pedulilindungi

| Sumber | Label |
|---|---|
| Excel manual | `kemudahan_penggunaan` negatif, `pembaruan_aplikasi` negatif, `layanan_pelanggan` negatif |
| Excel Gemini | `pembaruan_aplikasi` **positif**, `layanan_pelanggan` negatif |

Contoh ini bagus untuk menjelaskan **kenapa label Gemini harus
diverifikasi**: Gemini melewatkan "sulit, ribet" (kemudahan penggunaan) dan
salah membaca "enakkn yg dulu pedulilindungi" sebagai pujian, padahal
maksudnya membandingkan dengan aplikasi lama (keluhan).

### 1.3 `gold_val` (100 ulasan)

- **Fungsi**: bukan untuk melatih, tetapi untuk **memilih**:
  - B1: memilih nilai C (LR, SVM) atau alpha (NB) dari `GRID` di
    `models_classic.py`.
  - B4 dan IndoBERT: memilih epoch terbaik dan berhenti lebih awal (early
    stopping) kalau F1 validasi tidak naik.
  - Skornya dihitung oleh `model_data.val_score()` → `evaluate.evaluate()`.
- **Siapa yang melabeli**: sama dengan `gold_train` (Gemini lalu
  verifikasi manusia, `verification.py` memakai `SPLITS = ("gold_train",
  "gold_val")`).
- **Dipakai di skrip**: `model_data.Dataset` (`val_ids`), ketiga skrip
  model, `verification.py`, `llm_label.py`.
- **Status**: sama seperti `gold_train`: sudah dilabeli Gemini, belum
  diverifikasi.

**Contoh nyata** (`e8d4c4ad-8814-42f8-adef-239589267c15`, rating 5). Ulasan
ini dipakai lagi di bagian 2:

> min tolong segera bisa dibuka untuk sertifikat vaksin covidnya,dibuka
> loading terus gamau masuk

| Sumber | Label |
|---|---|
| Excel manual | `fitur_kesehatan` negatif, `performa` negatif |
| Excel Gemini | `fitur_kesehatan` negatif, `performa` negatif |

Perhatikan: ratingnya bintang 5 tetapi isinya keluhan. Inilah alasan aturan
"sentimen dinilai dari teks, bukan dari rating".

### 1.4 `gold_test` (300 ulasan)

- **Fungsi**: ujian akhir. Semua model (termasuk Gemini sebagai B3) dinilai
  pada 300 ulasan ini. Tidak boleh dipakai untuk latih atau memilih
  parameter. `model_data.prediction_ids()` otomatis membuang ulasan latih
  atau validasi dari daftar prediksi supaya tidak bocor.
- **Siapa yang melabeli**: manusia, **tanpa melihat label Gemini**.
  `annotation.assign()` memberikan setiap ulasan `gold_test` ke **dua
  orang** (pasangan dari `itertools.combinations(MEMBERS, 2)`).
  `annotation.finalize()` menolak ekspor kalau perbedaan belum diselesaikan
  oleh anotator ketiga. Hasil akhirnya `data/annotations/final_v1/gold.csv`.
- **Gemini juga melabeli 300 ulasan ini**, tetapi sebagai **peserta ujian**
  (B3-Gemini), bukan sebagai kunci jawaban.
- **Dipakai di skrip**: `llm_label.py --set split`, `annotation.py`,
  ketiga skrip model (`--predict-split gold_test`), dan `evaluate.py
  --ids-split gold_test`.
- **Status**: label Gemini untuk 300 ulasan **sudah ada**
  (`llm_gemini-3.5-flash-lite.csv`). Lembar kosong untuk label manual sudah
  dibuat di `data/annotation_workspace/v2/gold_<nama>.csv` (isi hanya baris
  `gold_test`). Label manual dua orang (`gold.csv`) **belum ada**, jadi skor
  set uji belum bisa dihitung.

**Contoh nyata** (`9ddacc56-f3e2-47b7-8bf3-b06acc154cd9`, rating 1):

> Aneh di update status vaksin saya jadi merah. Padahal sudah vaksin dosis 3
> balikin lagi ke awal parah ini developernya status vaksin orang jadi
> hilang.

| Sumber | Label |
|---|---|
| `llm_gemini-3.5-flash-lite.csv` (B3, prompt `v1`) | `fitur_kesehatan` negatif, `pembaruan_aplikasi` negatif |
| Excel manual (bukan gold resmi) | `fitur_kesehatan` negatif, `pembaruan_aplikasi` negatif |

### 1.5 `silver` (31.185 ulasan)

- **Fungsi**: sisa pool. Sejak masukan dosen 6 November 2026, **tidak
  dilabeli untuk pelatihan** dan hanya dipakai untuk analisis per versi
  aplikasi (RQ3). Namanya tetap "silver" supaya `split.csv` tidak berubah.
- **Siapa yang melabeli**: tidak ada label resmi. Tetapi 338 dari 354
  ulasan di Excel manual kebetulan berasal dari silver (lihat bagian 3).
- **Dipakai di skrip**: hanya dibuat oleh `preprocess.make_split()`.
  `annotation.prepare()` membuangnya. Tidak dipakai oleh model,
  `evaluate.py`, `verification.py`, maupun `llm_label.py --set split`.

**Contoh nyata** (`e35c6511-a4c3-4431-be3f-0e53caa8ed97`):

> Diupdate, malah gak bisa dibuka...nge close terus..

| Sumber | Label |
|---|---|
| Excel manual | `performa` negatif, `pembaruan_aplikasi` negatif |

---

## 2. Satu ulasan lewat empat pendekatan

Ulasan yang dipakai: `gold_val`, `e8d4c4ad-8814-42f8-adef-239589267c15`,
punya **2 aspek**.

| Kolom | Isi |
|---|---|
| `content` (asli) | `min tolong segera bisa dibuka untuk sertifikat vaksin covidnya,dibuka loading terus gamau masuk` |
| `text_llm` | sama persis (tidak ada URL/NIK/telepon) |
| `text_model` | sama persis (sudah huruf kecil, tanpa emoji, tanpa huruf berulang) |
| Jawaban benar (Excel manual) | `fitur_kesehatan` negatif, `performa` negatif; 6 aspek lain `tidak_disebut` |

> **Catatan jujur tentang angka.** Pelatihan resmi (latih di `gold_train`,
> uji di `gold_test`) **belum pernah dijalankan** karena `verified.csv` dan
> `gold.csv` belum ada. `results/metrics/` masih kosong (hanya README).
> Angka nyata yang ada:
> - B1 dan Gemini: **pratinjau** validasi silang 5-fold pada 354 ulasan
>   Excel manual (`src/preview_cv.py`, hasil di `results/pratinjau/`).
>   Prediksi B1 untuk ulasan ini di bawah adalah hasil menjalankan ulang
>   `cross_predict()` yang sama; skor totalnya cocok persis dengan
>   `results/pratinjau/tabel.md` (LR 0,684; SVM 0,670; NB 0,581).
> - BiLSTM dan IndoBERT: **belum ada hasil**. Yang ditunjukkan hanya
>   bentuk data menurut kode.

### 2.1 B1: TF-IDF + LR / SVM / NB

File: `src/models_classic.py` (resmi) dan `src/preview_cv.py` (pratinjau).

**Langkah 1: input teks.** `text_model` diproses
`text_features.b1_text()` → `normalize_slang()` dengan kamus slang (4.349
entri dari `load_lexicon()`):

```text
sebelum: min tolong segera bisa dibuka untuk sertifikat vaksin covidnya,dibuka loading terus gamau masuk
sesudah: admin tolong segera bisa dibuka untuk sertifikat vaksin covidnya , dibuka loading terus enggak mau masuk
```

Yang berubah: `min` → `admin`, `gamau` → `enggak mau`, dan koma dipisah jadi
token sendiri oleh `tokenize()`.

> Temuan kecil: `gamau` jadi `enggak mau`, bukan `tidak mau`. Override
> negasi di `OVERRIDES` hanya mencocokkan satu kata utuh (`enggak` →
> `tidak`), sedangkan hasil kamus di sini dua kata (`enggak mau`), jadi
> tidak ikut diubah.

**Langkah 2: TF-IDF.** `TfidfVectorizer(ngram_range=(1, 2),
sublinear_tf=True)`: fitur = kata tunggal + pasangan dua kata berurutan.

Bentuk data nyata pada fold pratinjau tempat ulasan ini menjadi data uji
(fold 4 dari 5):

| Benda | Bentuk |
|---|---|
| Matriks latih `X_train` | 283 ulasan × 3.808 fitur |
| Vektor ulasan ini | 1 × 3.808, hanya **19** sel tidak nol |
| Fitur di teks ulasan ini | 28 (9 tidak dikenal karena tidak ada di data latih) |

Bobot TF-IDF terbesar untuk ulasan ini:

| Fitur | Bobot |
|---|---|
| `dibuka` | 0,327 |
| `tolong segera` | 0,310 |
| `terus enggak` | 0,310 |
| `loading` | 0,289 |
| `admin tolong` | 0,289 |
| `segera` | 0,262 |
| `sertifikat vaksin` | 0,188 |

**Langkah 3: delapan classifier.** `fit_predict()` melatih **satu
classifier per aspek** (8 classifier), masing-masing memilih 1 dari 4 label.
Contoh label latih aspek `performa` di fold ini: `tidak_disebut` 201,
`negatif` 73, `positif` 6, `netral` 3 (sangat tidak seimbang; karena itu LR
dan SVM memakai `class_weight="balanced"`).

**Langkah 4: aturan umum.** `to_rows()` → `enforce_umum()`.

**Keluaran per aspek (pratinjau, ulasan ini):**

| Model | Parameter terpilih per fold | Prediksi | Benar? |
|---|---|---|---|
| B1-LR | C = 10; 1; 0,1; 0,1; 1 | `fitur_kesehatan` negatif, `performa` negatif | 2 dari 2 |
| B1-SVM | C = 10; 1; 10; 10; 1 | `fitur_kesehatan` negatif saja | 1 dari 2 (performa terlewat) |
| B1-NB | alpha = 0,1 di semua fold | semua `tidak_disebut` | 0 dari 2 |

Pada jalur resmi, `models_classic.run()` memilih C/alpha dengan F1
pasangan di `gold_val`, lalu menulis
`results/predictions/B1-LR_42.csv` dan `results/metrics/B1-LR_42.json`.

### 2.2 B4: BiLSTM + fastText

File: `src/model_bilstm.py`. **Belum ada hasil**: `torch` belum terpasang
di laptop dan file `data/external/cc.id.300.vec` (±1,2 GB) belum diunduh.

**Langkah 1: input teks.** `text_model` **tanpa** normalisasi slang (slang
dibiarkan). Dipotong jadi token oleh `text_features.tokenize()`:

```text
['min', 'tolong', 'segera', 'bisa', 'dibuka', 'untuk', 'sertifikat', 'vaksin',
 'covidnya', ',', 'dibuka', 'loading', 'terus', 'gamau', 'masuk']   → 15 token
```

**Langkah 2: token → angka.** `build_vocab()` membuat kamus dari semua teks
latih, validasi, dan uji; `encode()` mengubah tiap token jadi nomor indeks
(maksimal 128 token). Kata yang tidak punya vektor fastText diberi `[UNK]`
(indeks 1).

**Langkah 3: bentuk data di dalam model** (menurut `build_model()`, untuk 1
ulasan):

| Tahap | Bentuk |
|---|---|
| Nomor token | 1 × 15 |
| Embedding fastText (beku) | 1 × 15 × 300 |
| BiLSTM 128 unit per arah | 1 × 15 × 256 |
| Max-pooling atas 15 token | 1 × 256 |
| 8 kepala linear (1 per aspek) | 8 × (1 × 4) |

**Langkah 4: keluaran.** `predict()` memilih label dengan skor tertinggi
(`argmax`) di setiap kepala, lalu `enforce_umum()`. Hasil: 8 label, seperti
B1.

Pelatihan: `train_one()`, Adam lr 1e-3, batch 32, maks 30 epoch, berhenti
kalau F1 pasangan `gold_val` tidak naik 3 epoch (patience 3), seed 42/43/44.

### 2.3 B2 / B2-L: IndoBERT (sentence-pair)

File: `src/model_indobert.py`. **Belum ada hasil**: base butuh RAM lebih
dari 7,7 GB laptop (uji 10 November 2026 berhenti karena RAM habis), jadi
direncanakan di Google Colab.

**Langkah 1: input teks.** `text_model` tanpa normalisasi slang (IndoBERT
punya tokenizer sendiri).

**Langkah 2: satu ulasan jadi 8 pasangan.** Fungsi `pairs()` memasangkan
teks dengan **deskripsi setiap aspek** dari `ASPECT_DESCRIPTIONS`:

| Pasangan | Kalimat A | Kalimat B (deskripsi aspek) | Jawaban benar |
|---|---|---|---|
| 1 | teks ulasan | akun dan login: masuk aplikasi, PIN, OTP, … | tidak_disebut |
| 2 | teks ulasan | registrasi dan data diri: … | tidak_disebut |
| 3 | teks ulasan | fitur kesehatan: sertifikat dan riwayat vaksin, … | **negatif** |
| 4 | teks ulasan | performa teknis: tidak bisa dibuka, error, …, loading, … | **negatif** |
| 5-8 | teks ulasan | kemudahan, pembaruan, layanan pelanggan, umum | tidak_disebut |

Model menjawab pertanyaan "untuk aspek ini, labelnya apa?" sebanyak 8 kali.

**Langkah 3: bentuk data** (menurut `encode()` dan `predict()`):

| Tahap | Bentuk |
|---|---|
| Token pasangan (`[CLS] teks [SEP] deskripsi [SEP]`) | 8 × maks 160 token; yang dipotong hanya teks ulasan (`truncation="only_first"`) |
| Logit dari kepala klasifikasi | 8 × 4 |
| Label per pasangan (`argmax`) | 8 label → 1 baris berisi 8 aspek |

Model: `indobenchmark/indobert-base-p1` (B2, lr 2e-5, batch 16) dan
`indobert-large-p1` (B2-L, lr 1e-5, batch 8 × akumulasi 2), maks 10 epoch,
patience 2.

### 2.4 B3: LLM (Gemini / Qwen)

File: `src/llm_label.py`. Ada hasil nyata untuk ulasan ini.

**Langkah 1: input teks.** `text_llm` (teks asli yang disamarkan, **tanpa**
huruf kecil dan tanpa normalisasi slang). Tidak ada pelatihan.

**Langkah 2: prompt.** `system_prompt()` = `GUIDE` (definisi 8 aspek + 8
aturan) + `few_shot_text()` (12 contoh buatan tim, bukan dari dataset).
`batch_prompt()` menggabungkan banyak ulasan dengan kunci `r1`, `r2`, dst.
Ulasan ini menjadi `r41` dalam batch 60 ulasan.

**Langkah 3: panggil model.** `call_gemini()`: model
`gemini-3.5-flash-lite`, temperature 0, jawaban dipaksa berbentuk JSON
sesuai `RESPONSE_SCHEMA`. Data nyata dari
`data/annotation_workspace/llm/gemini-3.5-flash-lite/manual_v1/raw.jsonl`:

| Isi | Nilai |
|---|---|
| Ulasan per batch | 60 |
| Waktu batch | 15,97 detik |
| Token prompt / jawaban | 3.647 / 7.299 |

(Ulasan ini juga tercatat di satu batch 30 ulasan lain dengan jawaban sama.)

Jawaban mentah Gemini untuk ulasan ini:

```json
[
  {"kata": "sertifikat vaksin", "seragam": "sertifikat", "kategori": "fitur kesehatan",
   "label": "negatif", "bukti": "sertifikat vaksin covidnya,dibuka loading terus gamau masuk"},
  {"kata": "dibuka", "seragam": "buka aplikasi", "kategori": "performa",
   "label": "negatif", "bukti": "dibuka loading terus gamau masuk"}
]
```

**Langkah 4: periksa dan gabungkan.** `clean_mentions()` memastikan
kategori dan label sah serta `kata` dan `bukti` benar-benar ada di teks asli
(`locate()`). Lalu `aggregate_mentions()` → 8 label:

| Aspek | Gemini | Manual |
|---|---|---|
| `fitur_kesehatan` | negatif | negatif |
| `performa` | negatif | negatif |
| 6 aspek lain | tidak_disebut | tidak_disebut |

Keluaran ditulis ke
`manual_v1/llm_gemini-3.5-flash-lite_manual.csv` (untuk Excel) atau
`data/annotations/llm_gemini-3.5-flash-lite.csv` (untuk split).

**Qwen**: jalurnya sama, hanya `call_ollama()` dengan model `qwen3.5:4b`
lokal (`--backend ollama`). **Belum dijalankan.**

### 2.5 Perbandingan singkat keempatnya

| | B1 TF-IDF | B4 BiLSTM | B2 IndoBERT | B3 LLM |
|---|---|---|---|---|
| Kolom teks | `text_model` | `text_model` | `text_model` | `text_llm` |
| Fungsi tambahan di `text_features.py` | `b1_text()` (normalisasi slang) + `tokenize()` | `tokenize()` saja | tidak ada (tokenizer IndoBERT) | tidak ada |
| Belajar dari `gold_train`? | ya | ya | ya | tidak (hanya prompt) |
| Bentuk keluaran | 8 classifier × 4 kelas | 1 encoder + 8 kepala × 4 | 8 pasangan × 4 logit | daftar penyebutan JSON → 8 label |
| Hasil untuk ulasan contoh | LR 2/2, SVM 1/2, NB 0/2 (pratinjau) | belum ada | belum ada | 2/2 |
| F1 pasangan pratinjau (354 ulasan) | LR 0,684; SVM 0,670; NB 0,581 | - | - | 0,828 |

Skor pratinjau ini **bukan** skor set uji. B1 di sini dilatih dari label
manual (5-fold), sedangkan Gemini tidak dilatih sama sekali.

---

## 3. Tiga file Excel

Ketiganya ada di akar repo dan memakai format yang sama (`label_excel.HEADER`):
satu baris = satu penyebutan aspek, dengan kolom `No`, `reviewId`,
`Tanggal`, `Versi Aplikasi`, `Rating`, `Komentar`, `Kata Aspek (persis dari
ulasan)`, `Aspek (seragam)`, `Kategori Aspek`, `Label`, `Bukti dari
komentar`.

### 3.1 Alur

```text
Label Manual Sentimen Komentar Satu Sehat.xlsx   ← diisi manusia (tidak dibuat skrip)
        │
        ├─► src/llm_label.py --set manual
        │      (label_excel.read_mentions() mengambil 354 reviewId,
        │       Gemini melabeli text_llm-nya,
        │       label_excel.write_mentions() menulis file baru)
        │                  │
        │                  ▼
        │   Label LLM Sentimen Komentar Satu Sehat.xlsx
        │                  │
        └──────────┬───────┘
                   ▼
          src/compare_labels.py
           (write_excel() + evaluate())
                   │
                   ├─► Perbandingan Label Manual dan LLM.xlsx
                   └─► results/perbandingan_manual_llm/*.json, *.csv, tabel.md
```

| File | Dibuat oleh | Dibaca oleh |
|---|---|---|
| Label Manual (354 ulasan, 674 penyebutan) | **Manusia**, langsung di Excel. Versi sebelum dikoreksi disimpan di `data/annotation_workspace/Label Manual … (sebelum koreksi).xlsx`; 33 koreksi dicatat di `Catatan koreksi label manual.csv` | `llm_label.py --set manual` (daftar ulasan), `compare_labels.py` (acuan), `preview_cv.py` (label latih/uji B1 pratinjau), `evaluate.load_labels()` (bisa membaca .xlsx), `models_classic.py --predict-from` |
| Label LLM (354 ulasan, 641 penyebutan) | `llm_label.py --set manual --excel-out …` lewat `label_excel.write_mentions()` | `compare_labels.py` |
| Perbandingan (lembar Ringkasan, Per Ulasan, Daftar Beda) | `compare_labels.py`, fungsi `write_excel()` | Tidak dibaca skrip lain; untuk dibaca manusia dan laporan |

Lembar "Label per Ulasan" di Excel berisi rumus `COUNTIFS` yang meniru
aturan `aggregate_mentions()`, jadi 8 label per ulasan bisa dilihat
langsung di Excel.

### 3.2 Hasil perbandingan (dari `results/perbandingan_manual_llm/`)

| Ukuran | Nilai |
|---|---|
| F1 pasangan (Gemini vs manual) | 0,828 |
| F1 deteksi aspek (micro) | 0,885 |
| Macro-F1 sentimen rata-rata | 0,706 |
| Ulasan dengan 8 label persis sama | 68,6% |
| Jenis beda | LLM menambah aspek 62; LLM melewatkan aspek 62; sentimen berbeda 31 |

Kappa per aspek: akun login 0,903; pembaruan aplikasi 0,863; fitur
kesehatan 0,848; performa 0,835; layanan pelanggan 0,774; registrasi data
0,733; kemudahan penggunaan 0,559; umum 0,531.

Yang paling lemah: `umum` (manual 13 penyebutan, Gemini 29, artinya Gemini
terlalu sering memberi "umum") dan `kemudahan_penggunaan` (manual 27,
Gemini 21, artinya Gemini sering melewatkannya; contohnya ulasan
`gold_train` di bagian 1.2).

### 3.3 Hubungan dengan `split.csv`

Excel tidak punya kolom split. Hubungannya hanya lewat `reviewId`. Hasil
pencocokan 354 `reviewId` di Excel manual dengan `split.csv`:

| Split | Ulasan di Excel manual |
|---|---|
| `silver` | 338 |
| `gold_train` | 7 |
| `gold_test` | 5 |
| `gold_val` | 3 |
| `kalibrasi` | 1 |
| **Total** | **354** |

Excel LLM berisi 354 ulasan yang sama, jadi pembagiannya identik.

Kalau Excel manual dipakai sebagai daftar prediksi
(`models_classic.py --predict-from`), `model_data.prediction_ids()` otomatis
membuang 10 ulasan latih/validasi (7 + 3) supaya tidak bocor.

### 3.4 Kenapa Excel manual tidak bisa menggantikan `gold_test`

1. **Ulasannya berbeda.** Hanya 5 dari 300 ulasan `gold_test` ada di Excel.
   95,5% isi Excel (338 ulasan) berasal dari `silver`. Skor di Excel tidak
   mengukur kemampuan pada set uji yang sudah ditetapkan.
2. **Bukan sampel acak berstrata.** `gold_test` diambil
   `make_split()` dengan seed 42 dan strata rating, sehingga proporsinya
   mewakili pool. Excel dipilih di luar proses itu.
3. **Hanya satu pelabel, tanpa kappa.** `gold_test` dilabeli **dua orang**
   secara mandiri, diukur Cohen's kappa, dan perbedaannya diputus orang
   ketiga (`annotation.finalize()`). Excel manual dilabeli tanpa proses
   itu, jadi keandalan labelnya tidak bisa diukur.
4. **Ada ulasan yang bocor.** 7 ulasan latih dan 3 validasi ada di Excel.
   Model yang dilatih di `gold_train` lalu dinilai di Excel akan "menebak
   soal yang sudah pernah dilihat".
5. **Sudah dipakai untuk merancang skema.** Kategori `pembaruan_aplikasi`
   dan `layanan_pelanggan` ditambahkan setelah melihat 354 ulasan ini
   (`docs/project/method-decisions.md`, Implementasi 10 November 2026).
   Data yang dipakai untuk merancang aturan tidak netral lagi sebagai
   ujian.

Karena itu Excel manual hanya dipakai untuk: (a) memeriksa seberapa cocok
Gemini dengan label manusia sejak awal, dan (b) pratinjau B1 dengan
validasi silang (`results/pratinjau/`). Keduanya selalu disebut "pratinjau,
bukan hasil set uji".

---

## 4. Ringkasan untuk dihafal

- **39.995 → 32.035 → 5 split**: kalibrasi 50, latih 400, validasi 100, uji
  300, silver 31.185 (`preprocess.py`, seed 42, berstrata rating).
- **Siapa melabeli**: kalibrasi = 4 orang; latih + validasi = Gemini lalu
  diverifikasi 1 orang; uji = 2 orang + orang ketiga, tanpa melihat Gemini;
  silver = tidak dilabeli.
- **Status saat ini**: Gemini sudah melabeli 800 ulasan (400 latih, 100
  validasi, 300 uji). Lembar verifikasi dan lembar uji sudah dibuat tetapi
  **belum diisi**. Pelatihan resmi dan BiLSTM/IndoBERT **belum**.
- **Input teks**: B1 = `text_model` + `b1_text()`; BiLSTM = `text_model` +
  `tokenize()`; IndoBERT = `text_model` + deskripsi aspek; LLM = `text_llm`.
- **Angka nyata yang sudah ada**: Gemini vs manual F1 pasangan 0,828 (354
  ulasan). Pratinjau B1 5-fold pada label manual: LR 0,684, SVM 0,670,
  NB 0,581. Pratinjau B1 dilatih dari label Gemini (belum diverifikasi),
  dinilai pada 344 ulasan Excel manual: LR 0,681, SVM 0,655, NB 0,551,
  Gemini 0,832; selisih Gemini dengan setiap B1 nyata menurut paired
  bootstrap (`results/pratinjau_llm/`).
- **Excel manual ≠ gold_test**: hanya 5 ulasan yang sama, sisanya silver,
  satu pelabel, ada ulasan latih yang bocor.

### Perintah untuk memeriksa ulang angka di catatan ini

```text
python src/compare_labels.py
python src/preview_cv.py --llm data/annotation_workspace/llm/gemini-3.5-flash-lite/manual_v1/llm_gemini-3.5-flash-lite_manual.csv
```

`compare_labels.py` menimpa `Perbandingan Label Manual dan LLM.xlsx` dan
`results/perbandingan_manual_llm/`; `preview_cv.py` menimpa
`results/pratinjau/`. Hasilnya harus sama dengan yang dikutip di atas.
