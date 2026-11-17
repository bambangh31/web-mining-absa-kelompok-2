# Hasil aktual IndoBERT base

Paket `hasil_indobert_lengkap.zip` diterima dari pengguna pada 17 November
2026. Isi aslinya disimpan di `colab_v1/`; `verifikasi.json` mencatat hash
ZIP, manifest sumber, dan hasil penghitungan ulang.

| Model | F1 pasangan uji | Macro-F1 sentimen |
|---|---|---|
| Gemini langsung | 0,842 | 0,765 |
| IndoBERT base, rata-rata ± SD tiga seed | 0,775 ± 0,013 | 0,427 ± 0,033 |
| Logistic Regression | 0,727 | 0,307 |
| Linear SVM | 0,705 | 0,291 |
| Naive Bayes | 0,621 | 0,244 |

Seluruhnya dinilai pada 150 ulasan manual yang sama. Empat pembanding memakai
hasil yang sebelumnya tersedia; B2 dilatih dengan seed 42, 43, dan 44.
SD menggunakan simpangan baku sampel antar-seed, bukan interval kepercayaan.
F1 pasangan uji per seed: 42 = 0,774194; 43 = 0,763636; 44 = 0,788546.

## Pemeriksaan

- Hash clean, split, label latih/validasi, serta gold cocok dengan byte pada
  commit sumber `f8f8f2b7dbd986788c68acf2a9b0aa246b94c15c`.
- Tiap file prediksi memuat tepat 150 ID unik dari `gold_test`, empat label
  yang valid pada delapan aspek, dan metadata seed yang sesuai.
- Konfigurasi memuat 400 ulasan latih (3.200 pasangan), panjang 160, batch 16,
  learning rate 2e-5, maksimum 10 epoch, patience 2, dan perangkat CUDA.
- Hasil tujuh run dihitung ulang dari prediksi dan identik dengan JSON ZIP.
  Rata-rata serta SD tiga seed juga cocok. Data, split, dan label tidak diubah.
- Pelatihan: Tesla T4; Python 3.13.16, torch 2.14.1+cu130,
  transformers 5.22.2, numpy 2.4.2; riwayat tiap run disimpan di JSON.

Epoch terbaik seed 42/43/44 adalah 5/4/5, berdasarkan validasi. Seed 44
dipakai hanya sebagai matriks perwakilan karena F1 validasi tertinggi
(0,819355); tidak dipilih dari skor uji. Matriks berjumlah 1.200 keputusan,
bukan gabungan hasil tiga seed menjadi 450 ulasan.

## Berkas dan reproduksi evaluasi

- `results/predictions/B2_<seed>.csv`: prediksi untuk setiap seed.
- `results/metrics/B2_<seed>.json`: konfigurasi, riwayat, validasi, waktu inferensi.
- `results/metrics/uji_indobert/`: evaluasi ulang tujuh run dan paired bootstrap.
- `results/metrics/uji_indobert/confusion_matrix/lima_model.png`: empat
  pembanding dan IndoBERT base seed 44; skor utama B2 tetap rata-rata tiga seed.
- `notebooks/03_indobert_colab.ipynb`: notebook pelatihan yang digunakan.

```text
python src/evaluate.py --gold data/annotations/final_v1/gold.csv --ids-split gold_test --out results/metrics/uji_indobert --pred B1-LR=results/predictions/B1-LR_42.csv --pred B1-SVM=results/predictions/B1-SVM_42.csv --pred B1-NB=results/predictions/B1-NB_42.csv --pred B3-Gemini=data/annotations/llm_gemini-3.5-flash-lite.csv --pred B2_42=results/predictions/B2_42.csv --pred B2_43=results/predictions/B2_43.csv --pred B2_44=results/predictions/B2_44.csv
```

Model terbaik pada hasil saat ini adalah Gemini; di antara model terlatih,
IndoBERT base memiliki F1 pasangan rata-rata tertinggi. Selisih rata-rata
antar-model tidak diklaim signifikan tanpa pengujian khusus. Batas satu
anotator dan 375 label latih/validasi yang belum diverifikasi tetap berlaku.
IndoBERT large, BiLSTM, dan Qwen belum memiliki hasil evaluasi di paket ini.
