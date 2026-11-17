# Metrik

Pembaruan 17 November 2026: hasil IndoBERT base tiga seed tersedia di
[`uji_indobert/`](uji_indobert/tabel.md) dan
[ringkasan lima model](../indobert/README.md). F1 pasangan B2 rata-rata
0,775 ± 0,013 pada 150 ulasan yang sama. Folder `uji/` tetap menyimpan
baseline empat model tanggal 14 November; skor lamanya tidak ditimpa.

Simpan tabel skor beserta konfigurasi dan definisi metriknya. Metrik dipilih
setelah target ABSA dan label acuan tersedia. Nyatakan set validasi/CV/uji
final yang dipakai dan jangan menuliskan angka sebelum eksperimen dilakukan.

## Revisi 14 November 2026

Hasil pada `uji/` dihitung ulang dari file prediksi yang sudah ada di
repository commit `2d72baf`, dengan 150 ulasan uji berlabel manual oleh Jap.
Tidak ada pelatihan ulang atau perubahan label. Skor empat model tetap sama:

| Model | Algoritma | Presisi | Recall | F1 pasangan | Macro-F1 sentimen |
|---|---|---|---|---|---|
| B1-LR | TF-IDF + Logistic Regression | 0,828 | 0,648 | 0,727 | 0,307 |
| B1-SVM | TF-IDF + Linear SVM | 0,817 | 0,620 | 0,705 | 0,291 |
| B1-NB | TF-IDF + Naive Bayes | 0,807 | 0,505 | 0,621 | 0,244 |
| B3-Gemini | Gemini langsung | 0,811 | 0,875 | 0,842 | 0,765 |

`uji/confusion_matrix/gabungan.png` memperlihatkan empat model pada 1.200
keputusan (150 ulasan × 8 aspek). Baris = label manual, kolom = prediksi.
Urutan label selalu `tidak_disebut`, `positif`, `negatif`, `netral`.
Sebanyak 984 label acuan adalah `tidak_disebut`; matriks ini bukan skor
sentimen tiga kelas atau confusion matrix 1.200 ulasan independen.

`model_01.png` sampai `model_04.png` berisi delapan matriks per aspek, sesuai
urutan LR, SVM, NB, Gemini. Setiap matriks aspek berjumlah 150 keputusan.
`matriks.csv` menyimpan seluruh sel, termasuk sel nol. `uji/metrik.json`
menyimpan urutan label, matriks gabungan dan per aspek, serta metrik sebelumnya.
Macro-F1 sentimen dihitung pada aspek yang disebut di acuan, sesuai definisi
di `src/evaluate.py`; sel `tidak_disebut` tidak menjadi kelas sentimen.

`uji/provenance.json` mencatat SHA-256 sumber dan hasil. Hash mengacu pada
byte berkas yang tersimpan di Git (`git show HEAD:path`), sehingga perubahan
newline pada checkout Windows tidak mengubah acuan pemeriksaan.

Jalankan dari akar repository (PowerShell atau terminal lain), setelah
memasang `requirements.txt`:

```text
python src/evaluate.py --gold data/annotations/final_v1/gold.csv --ids-split gold_test --out results/metrics/uji --pred B1-LR=results/predictions/B1-LR_42.csv --pred B1-SVM=results/predictions/B1-SVM_42.csv --pred B1-NB=results/predictions/B1-NB_42.csv --pred B3-Gemini=data/annotations/llm_gemini-3.5-flash-lite.csv
```

Pemeriksaan revisi: 34 tes dijalankan; 33 lulus dan 1 tes BiLSTM dilewati
karena PyTorch belum terpasang. Dua tes baru memeriksa orientasi matriks,
aspek terlewat/tambahan, subset evaluasi, dan jumlah keputusan gabungan.

## IndoBERT base dan large — 17 November 2026

`uji_indobert_lengkap/` memuat evaluasi ulang sepuluh run (empat pembanding + tiga base + tiga large), pada 150 ID uji yang sama. `confusion_matrix/enam_model.png` memakai base seed 44 dan large seed 43 berdasarkan validasi. Skor utama kedua varian tetap rata-rata ± SD sampel tiga seed. [Audit large](../indobert_large/README.md). Folder `uji/` dan `uji_indobert/` dipertahankan sebagai versi empat dan lima model.

## Tujuh jenis model termasuk BiLSTM — 17 November 2026

`uji_tujuh_model/` memuat evaluasi 13 run: empat pembanding, tiga base, tiga large, dan tiga BiLSTM. Semua memakai 150 ID uji yang sama. `confusion_matrix/tujuh_model.png` memakai base seed 44, large 43, BiLSTM 44, dipilih dari validasi. Skor utama model tiga seed tetap rata-rata ± SD sampel. [Audit BiLSTM](../bilstm/README.md). Folder evaluasi sebelumnya dipertahankan sebagai arsip.

## Delapan jenis model termasuk Qwen — 17 November 2026

`uji_delapan_model/` memuat evaluasi 14 run: empat pembanding, tiga base, tiga large, tiga BiLSTM, dan satu Qwen. Semua pada 150 ID uji yang sama. `confusion_matrix/delapan_model.png` memakai base seed 44, large 43, dan BiLSTM 44 berdasarkan validasi; Gemini/Qwen satu run. Skor utama ketiga model neural tetap rata-rata ± SD sampel. [Audit Qwen](../qwen/README.md). Folder evaluasi terdahulu dipertahankan sebagai arsip.
