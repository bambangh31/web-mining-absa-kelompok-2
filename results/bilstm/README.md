# Hasil aktual BiLSTM dan fastText

Paket `hasil_bilstm_lengkap.zip` diterima dari pengguna pada 17 November 2026.
Isi asli disimpan di `colab_v1/`; `verifikasi.json` memuat hash ZIP, manifest,
konfigurasi, dan metrik yang dihitung ulang. Pelatihan dilakukan pengguna di Colab T4.

| Seed | F1 pasangan uji | F1 pasangan validasi | Epoch terbaik / total |
|---|---|---|---|
| 42 | 0,355062 | 0,386588 | 5 / 8 |
| 43 | 0,380841 | 0,382403 | 4 / 7 |
| 44 | 0,383901 | 0,398249 | 2 / 5 |

F1 pasangan rata-rata ± SD sampel **0,373268 ± 0,015841**; F1 deteksi micro
**0,397381 ± 0,015036**; macro-F1 sentimen **0,271798 ± 0,048298**.
Periksa nilai validasi presisi penuh pada JSON tiap run.

## Data dan konfigurasi

- Input sama: 400 ulasan latih, 100 validasi, 150 uji manual. Hash empat input
  dan seluruh berkas kode cocok dengan commit `a410e0981f77c51f8ed81e92d40b980b3cf155fc`.
- Kosakata hanya dari latih, 1.508 kata; hash kosakata dihitung ulang.
  Cakupan fastText tercatat 1.419 kata (94,098%). Dimensi 300, embedding
  dibekukan, UNK dilatih. Format text memakai UNK untuk kata tanpa vektor;
  tidak membangkitkan vektor subword seperti model bin fastText.
- BiLSTM 128 unit per arah, satu lapis, max-pooling, delapan kepala empat
  kelas, dropout 0,5, Adam 1e-3, batch 32, maksimum 128 token, 30 epoch,
  early stopping patience 3 berdasarkan F1 pasangan validasi.
- GPU Tesla T4/CUDA; Python 3.13.16, torch 2.14.1+cu130, numpy 2.4.2.
- Seluruh 13 metrik paket dihitung ulang dan cocok dengan prediksi, termasuk
  sepuluh run pembanding yang tidak berubah. ID unik, label, seed, konfigurasi,
  riwayat epoch, serta rata-rata/SD juga diperiksa.
- Hash arsip/subset fastText dicatat oleh runtime di `fasttext.json`.
  ZIP tidak memuat vektor; hash byte vektor tidak diverifikasi ulang secara lokal.

## Interpretasi dan berkas

F1 pasangan BiLSTM lebih rendah daripada enam metode lainnya. Ketiga seed
hanya menghasilkan label negatif/tidak disebut, dengan 505/640/430 prediksi
negatif dari 1.200 keputusan; acuan memuat total 216 aspek yang disebut.
Ini menunjukkan banyak aspek tambahan serta kegagalan positif/netral;
penyebabnya belum dibuktikan melalui percobaan terkontrol. Tidak dilakukan
penyesuaian parameter berdasarkan hasil uji ini. Macro-F1 sentimen BiLSTM
0,272 berada di atas NB 0,244, tetapi metrik utama tetap F1 pasangan.

Prediksi: `results/predictions/B4_<seed>.csv`. Konfigurasi/riwayat:
`results/metrics/B4_<seed>.json`. Evaluasi lengkap:
`results/metrics/uji_tujuh_model/`. Confusion matrix perwakilan memakai
BiLSTM seed 44 karena F1 validasi tertinggi, bukan dipilih dari uji.
Setiap matriks gabungan memuat 1.200 keputusan; tiga seed bukan 450 ulasan independen.

Urutan F1 pasangan: Gemini 0,842; base 0,775; large 0,765; LR 0,727;
SVM 0,705; NB 0,621; BiLSTM 0,373. Qwen belum dievaluasi. Batas satu
anotator dan 375 label latih/validasi yang belum diverifikasi tetap berlaku.
Laporan Week 12 dan 13 telah diperbarui.
