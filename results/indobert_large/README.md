# Hasil aktual IndoBERT large

ZIP `hasil_indobert_large_lengkap.zip` diterima 17 November 2026; isi asli di `colab_v1/`, hash dan pemeriksaan di `verifikasi.json`. Pelatihan dilakukan pengguna di Colab; skor dihitung ulang dari prediksi.

| Seed | F1 pasangan uji | F1 pasangan validasi | Epoch terbaik / total |
|---|---|---|---|
| 42 | 0,742857 | 0,784053 | 1 / 3 |
| 43 | 0,781553 | 0,800000 | 6 / 8 |
| 44 | 0,770642 | 0,790698 | 4 / 6 |

Rata-rata F1 pasangan **0,765018 ± 0,019952**; macro-F1 sentimen **0,407664 ± 0,085555**. SD adalah simpangan baku sampel antar-seed. Base mencapai 0,775459 ± 0,012503; selisih rata-rata tidak diklaim signifikan.

Konfigurasi: IndoBERT large-p1, 400 ulasan latih (3.200 pasangan), 100 validasi, 150 uji manual yang sama; panjang 160, learning rate 1e-5, maksimal 10 epoch, patience 2. Micro-batch 4 × akumulasi 4 = batch efektif 16. Perangkat Tesla T4/CUDA. Hash keempat input cocok dengan commit sumber f8f8f2b7dbd986788c68acf2a9b0aa246b94c15c. ID/label/seed valid dan metrik tujuh run dalam ZIP cocok setelah dihitung ulang.

Prediksi `results/predictions/B2-L_<seed>.csv`; konfigurasi/riwayat `results/metrics/B2-L_<seed>.json`; notebook `notebooks/04_indobert_large_colab.ipynb`. Evaluasi gabungan terbaru di `results/metrics/uji_indobert_lengkap/` berisi empat pembanding, tiga base, dan tiga large. Matriks enam model menggunakan large seed 43 dan base seed 44, dipilih dari validasi, bukan skor uji. Setiap panel berjumlah 1.200 keputusan, bukan 450 ulasan.

Urutan F1 pasangan: Gemini 0,842; base 0,775; large 0,765; LR 0,727; SVM 0,705; NB 0,621. Hasil [BiLSTM](../bilstm/README.md) telah tersedia (0,373 ± 0,016); Hasil [Qwen](../qwen/README.md) juga telah tersedia (F1 pasangan 0,741). Keterbatasan satu anotator dan 375 label latih/validasi belum diverifikasi tetap berlaku. Laporan Week 12 dan 13 diperbarui; arsip laporan sebelumnya tetap tersedia.
