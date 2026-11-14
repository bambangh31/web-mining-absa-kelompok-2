# Cara menjalankan dan menguji pipeline ABSA

Disusun 10 November 2026 untuk week 12. Semua perintah dijalankan dari akar
repository. Alasan setiap langkah ada di [keputusan metode](method-decisions.md).

## Gambaran alur

```text
data/raw/…reviews.csv
  └─ src/preprocess.py ─────────► data/processed/reviews_clean.csv + data/annotations/split.csv
       ├─ src/text_features.py ─► normalisasi slang (khusus B1) + ringkasan
       ├─ src/llm_label.py ─────► label Gemini (800 ulasan) + lembar Excel versi LLM
       ├─ src/verification.py ──► lembar verifikasi dua langkah ─► data/annotations/verified.csv
       ├─ src/annotation.py ────► lembar uji manual (2 orang, tanpa label LLM) ─► gold.csv
       ├─ src/models_classic.py ► B1-LR, B1-SVM, B1-NB
       ├─ src/model_bilstm.py ──► B4 BiLSTM + fastText
       ├─ src/model_indobert.py ► B2 IndoBERT-p1 base, B2-L large (Colab)
       └─ src/evaluate.py ──────► metrik keseluruhan dan per aspek + paired bootstrap
src/compare_labels.py ──────────► perbandingan lembar manual vs lembar LLM
```

## 0. Persiapan

```text
python -m pip install -r requirements.txt          # preprocessing, LLM, B1, evaluasi, Excel
python -m pip install -r requirements-model.txt    # B4 dan IndoBERT (torch, transformers)
copy .env.example .env                             # isi GEMINI_API_KEY
curl -L -o data/external/colloquial-indonesian-lexicon.csv https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv
```

## 1. Tes otomatis (tanpa data asli, tanpa API)

```text
python -m unittest discover -s tests -v
```

Keluaran revisi week 13: `Ran 34 tests … OK` (satu tes BiLSTM dilewati jika
PyTorch belum terpasang). Tes memakai data buatan dan
memeriksa preprocessing, alat anotasi, skema delapan aspek, agregasi
penyebutan, baca/tulis Excel (header tanpa garis bawah, komentar tidak
berubah), pelabelan LLM dengan respons tiruan (retry dan lanjut dari
`raw.jsonl`), metrik yang dihitung manual, paired bootstrap, B1 pada pola
kata kunci (F1 > 0,95), BiLSTM tanpa fastText (uji asap), dan lembar
verifikasi (tingkat koreksi dan waktu per ulasan). Tes BiLSTM dilewati bila
`torch` belum terpasang.

## 2. Preprocessing

```text
python src/preprocess.py --clean tmp/ulang/clean.csv --split tmp/ulang/split.csv --report tmp/ulang/report
python src/text_features.py
python src/aspect_keywords.py
```

- Hash `clean.csv` dan `split.csv` harus sama dengan
  `results/preprocessing/v1/summary.json` (`98c18740…` dan `67036c5d…`).
  Diperiksa ulang 10 November 2026: sama persis.
- `text_features.py` menulis `results/preprocessing/v1/slang_summary.json`:
  75,1% ulasan pool dan 12,7% token berubah; pengganti terbanyak `gak`,
  `ga`, `gk` → `tidak`, `yg` → `yang`, `apk` → `aplikasi`.
- `aspect_keywords.py` menulis `results/eksplorasi/aspek_kata_kunci.json`
  (perkiraan kata kunci, bukan label).

Contoh perubahan teks (ulasan nyata dari pool):

| Tahap | Teks |
|---|---|
| Asli (`content`) | `belum 100% bisa berjalan,pdhl sdh update...perbaiki bug...loading lambat,jaringan internet pdhl sangat baik.` |
| `text_model` (encoder) | huruf kecil, emoji menjadi teks, huruf berulang dipendekkan |
| B1 (TF-IDF) | `belum 100 % bisa berjalan , padahal sudah update . . . perbaiki bug . . . loading lambat , jaringan internet padahal sangat baik .` |

## 3. Label LLM (Gemini)

```text
python src/llm_label.py --set manual --manual-excel "Label Manual Sentimen Komentar Satu Sehat.xlsx" --excel-out "Label LLM Sentimen Komentar Satu Sehat.xlsx"
python src/llm_label.py --set split
```

- Model bawaan `gemini-3.5-flash-lite`, 30 ulasan per permintaan,
  temperature 0, JSON dibatasi skema. Kuota gratis 20 permintaan/hari per
  model (terbukti pada gemini-3.5-flash) dan permintaan gagal 503 ikut
  terhitung; dengan batch bawaan 60 ulasan, 800 ulasan butuh 14 permintaan. Lembar manual 10 November 2026 dikerjakan dengan 4 batch 30
  ulasan lalu batch 60 ulasan (`--batch-size 60`) agar muat dalam kuota. Bila kuota
  habis skrip berhenti dengan pesan; jalankan perintah yang sama besok, batch
  yang sudah berhasil tidak dikirim ulang.
- Keluaran `--set split`: `data/annotations/llm_gemini-3.5-flash-lite.csv`
  (reviewId, model, prompt_version, delapan label). Respons mentah, daftar
  penyebutan, dan masalah validasi di
  `data/annotation_workspace/llm/gemini-3.5-flash-lite/split_v1/`.
- Keluaran `--set manual`: lembar Excel versi LLM dengan format yang sama
  persis dengan lembar manual (Data Berlabel, Kata Aspek, Kategori Aspek,
  Label per Ulasan).

## 4. Bandingkan lembar manual dan LLM

```text
python src/compare_labels.py
```

Menghasilkan `Perbandingan Label Manual dan LLM.xlsx` (Ringkasan per
kategori, Per Ulasan dengan sel beda diwarnai, Daftar Beda) serta
`results/perbandingan_manual_llm/` (`perbandingan.json`, `ringkasan.csv`,
`per_aspek.csv`, `tabel.md`). Contoh keluaran terminal:

```text
{
  "ulasan": 354,
  "f1_pasangan": …,
  "kappa_per_aspek": {"akun_login": …, …},
  "jenis_beda": {"LLM menambah aspek": …, "LLM melewatkan aspek": …, "sentimen berbeda": …}
}
```

## 5. Verifikasi label latih dan validasi (manusia)

```text
python src/verification.py prepare --llm data/annotations/llm_gemini-3.5-flash-lite.csv --mentions data/annotation_workspace/llm/gemini-3.5-flash-lite/split_v1/mentions.csv
```

Empat file `data/annotation_workspace/verifikasi/verifikasi_<nama>.xlsx`,
masing-masing 125 ulasan. Isi lembar Info (Mulai, Selesai), lalu untuk
setiap aspek pilih `setuju` atau `salah` pada kolom Cek; kolom Pengganti
diisi hanya bila `salah`. Setelah keempat lembar lengkap:

```text
python src/verification.py export --llm data/annotations/llm_gemini-3.5-flash-lite.csv
```

Menghasilkan `data/annotations/verified.csv` dan
`results/verifikasi/ringkasan.json` (tingkat koreksi per aspek, persentase
ulasan diterima utuh, detik per ulasan, dan pola koreksi). Ekspor menolak
lembar yang belum lengkap, Pengganti yang kosong atau sama dengan label LLM,
dan `umum` yang bertabrakan dengan aspek khusus.

### Satu pemeriksa (keputusan 11 November 2026)

Hanya lembar `verifikasi_jap.xlsx` yang diisi. Sisa ulasan tetap memakai
label LLM dengan kolom `verifier` kosong:

```text
python src/verification.py export --llm data/annotations/llm_gemini-3.5-flash-lite.csv --members jap --fill-unverified
```

## 6. Label uji manual (dua orang, tanpa label LLM)

Pelaksanaan 11 November 2026 hanya satu anotator. Ekspor kalibrasi, 150
label uji, dan kesepakatan dengan Gemini:

```text
python src/single_annotator.py --annotator jap
```

Keluaran: `data/annotations/kalibrasi_v1/kalibrasi.csv`,
`data/annotations/final_v1/` (`gold.csv` 150 ulasan uji, `gold_jap.csv`,
`provenance.csv`, `report.json`), dan `results/kesepakatan/`.

Rancangan awal dua anotator:

Ikuti [alur anotasi](annotation-workflow.md). Karena kategori menjadi
delapan, buat workspace baru:

```text
python src/annotation.py prepare --reviews data/processed/reviews_clean.csv --split data/annotations/split.csv --workspace data/annotation_workspace/v2
```

Isi hanya baris `gold_test`, lalu `audit` dan `finalize` seperti di alur
anotasi. Hasil akhir: `data/annotations/final_v1/gold.csv`.

## 7. Model dan evaluasi

Untuk empat model yang sudah tersedia sampai laporan pertama week 13:

```text
python src/evaluate.py --gold data/annotations/final_v1/gold.csv --ids-split gold_test --out results/metrics/uji --pred B1-LR=results/predictions/B1-LR_42.csv --pred B1-SVM=results/predictions/B1-SVM_42.csv --pred B1-NB=results/predictions/B1-NB_42.csv --pred B3-Gemini=data/annotations/llm_gemini-3.5-flash-lite.csv
```

Keluaran mencakup `confusion_matrix/gabungan.png` (empat model),
`model_01.png` sampai `model_04.png` (delapan aspek per model), dan
`matriks.csv`. Baris = acuan manual, kolom = prediksi, dengan urutan label
`tidak_disebut`, `positif`, `negatif`, `netral`. Matriks gabungan memuat
150 × 8 keputusan; setiap matriks aspek memuat 150 keputusan.

Perintah di bawah merupakan rencana perluasan setelah semua model berikut
selesai dilatih; berkas B4, B2, dan B2-L belum tersedia pada laporan week 13:

```text
python src/models_classic.py --labels data/annotations/verified.csv --predict-split gold_test
python src/model_bilstm.py   --labels data/annotations/verified.csv --predict-split gold_test
python src/model_indobert.py --variant base  --labels data/annotations/verified.csv --predict-split gold_test
python src/model_indobert.py --variant large --labels data/annotations/verified.csv --predict-split gold_test
python src/evaluate.py --gold data/annotations/final_v1/gold.csv --ids-split gold_test --out results/metrics/uji ^
  --pred B1-LR=results/predictions/B1-LR_42.csv --pred B1-SVM=results/predictions/B1-SVM_42.csv ^
  --pred B1-NB=results/predictions/B1-NB_42.csv --pred B4=results/predictions/B4_42.csv ^
  --pred B2=results/predictions/B2_42.csv --pred B2-L=results/predictions/B2-L_42.csv ^
  --pred B3-Gemini=data/annotations/llm_gemini-3.5-flash-lite.csv
```

- Setiap model menulis `results/predictions/<kode>_<seed>.csv` dan
  `results/metrics/<kode>_<seed>.json` (parameter terpilih, riwayat epoch,
  skor validasi, detik per 1.000 ulasan).
- `evaluate.py` menulis `ringkasan.csv` (F1 pasangan, presisi, recall, F1
  deteksi micro/macro, macro-F1 sentimen), `per_aspek.csv` (setiap aspek ×
  setiap model: F1 pasangan, F1 deteksi, macro-F1 sentimen, akurasi, kappa),
  `tabel.md`, dan `metrik.json` berisi paired bootstrap 1.000 kali.
- IndoBERT base butuh GPU atau RAM lebih dari yang tersisa di laptop 7,7 GB;
  jalankan di Google Colab (T4) seperti B2-L. Uji 10 November 2026: model
  `indobenchmark/indobert-base-p1` berhasil diunduh dan dimuat dengan kepala
  empat label, lalu proses berhenti karena RAM laptop habis.
- B4 butuh `data/external/cc.id.300.vec` (unduh dari fastText, sekitar
  1,2 GB terkompresi). Tanpa file itu skrip tetap jalan tetapi menandai
  hasil sebagai uji asap.
- B3-Qwen: `python src/llm_label.py --backend ollama --model qwen3.5:4b --set split`
  setelah Ollama terpasang.

Analisis keluhan per aspek, per versi, dan konsistensi rating (RQ3):

```text
python src/version_analysis.py
```

Hasil 11 November 2026 (150 ulasan uji): B3-Gemini 0,842, B1-LR 0,727,
B1-SVM 0,705, B1-NB 0,621 F1 pasangan.

## Pratinjau sebelum verifikasi selesai

Selama label latih terverifikasi dan label uji belum ada, B1 diuji dengan
validasi silang 5-fold pada label manual (parameter dipilih dengan
validasi silang dalam 3-fold di setiap fold), lalu dibandingkan dengan
Gemini langsung pada ulasan yang sama. Hasil ini bukan hasil set uji dan
disimpan terpisah:

```text
python src/preview_cv.py --llm data/annotation_workspace/llm/gemini-3.5-flash-lite/manual_v1/llm_gemini-3.5-flash-lite_manual.csv
```

Keluaran: `results/pratinjau/tabel.md` (F1 pasangan dan macro-F1 sentimen
per aspek untuk B1-LR, B1-SVM, B1-NB, dan B3-Gemini), `ringkasan.csv`,
`per_aspek.csv`, dan `metrik.json` dengan paired bootstrap.

Setelah 400 ulasan latih punya label Gemini, B1 juga bisa dilatih dari
label yang belum diverifikasi dan diuji pada lembar manual (ulasan
latih/validasi otomatis dikeluarkan dari prediksi):

```text
python src/models_classic.py --labels data/annotations/llm_gemini-3.5-flash-lite.csv --predict-from "Label Manual Sentimen Komentar Satu Sehat.xlsx" --out results/pratinjau_llm
```
