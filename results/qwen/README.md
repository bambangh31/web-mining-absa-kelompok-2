# Hasil aktual Qwen melalui Ollama

Paket `hasil_qwen_lengkap.zip` diterima 17 November 2026. Pelatihan tidak
dilakukan; pengguna menjalankan inferensi Qwen3.5:4b pada Colab Tesla T4.
Isi sumber ada di `colab_v1/`, audit lokal di `verifikasi.json`.

| Metrik | Nilai |
|---|---|
| F1 pasangan | 0,741379 |
| Presisi pasangan | 0,693548 |
| Recall pasangan | 0,796296 |
| F1 deteksi micro | 0,784483 |
| F1 deteksi macro | 0,704932 |
| Macro-F1 sentimen | 0,663589 |
| Ulasan delapan label persis sama | 0,520000 |

## Konfigurasi dan pemeriksaan

- Satu run, 150 ulasan manual yang sama, 75 batch dua ulasan. Ini run baru
  penuh dari commit `30fdae6931f251d174fd4af314722cb3973eced5`; bukan gabungan
  enam hasil dari run parsial lama. Seluruh batch memakai schema ids-count-v2.
- Ollama 0.40.16, Q4_K_M; digest model
  `d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04`.
  VRAM model tercatat sebelum/sesudah inferensi; GPU Tesla T4.
- Prompt v1/contoh buatan tim dan agregasi sama dengan Gemini. Batch dua
  ulasan berbeda dari Gemini dan dicatat. Temperature 0, seed 42,
  think=false, konteks 8.192, batas keluaran 4.096 token.
- Hash lima input dan seluruh kode cocok dengan commit sumber. Hash prompt,
  teks masukan, dan teks asli dihitung ulang. Label sentimen uji tidak masuk prompt.
- Ke-75 respons mentah diparsing ulang, setiap ID tepat sekali; checkpoint,
  agregasi, CSV prediksi, mentions/issues, dan seluruh 14 metrik paket cocok.
- Ada 38 masalah kecocokan kutipan pada 28 ulasan: 17 frasa aspek dan 21
  potongan bukti. Aturan pembersihan Gemini dipertahankan; masalah kutipan
  dicatat tanpa mengoreksi label berdasarkan gold. Skor utama menilai
  pasangan aspek-sentimen, bukan ketepatan rentang kutipan.

## Perbandingan dan berkas

Urutan F1 pasangan: Gemini 0,842; IndoBERT base 0,775 ± 0,013; large
0,765 ± 0,020; Qwen 0,741; LR 0,727; SVM 0,705; NB 0,621; BiLSTM
0,373 ± 0,016. SD sampel hanya bagi tiga model neural yang dilatih tiga seed;
Qwen tidak dilaporkan dengan SD tiga seed. Macro-F1 sentimen Qwen 0,664
tertinggi kedua setelah Gemini 0,765.

Qwen memiliki 172 pasangan benar, 34 aspek terlewat, 66 aspek tambahan,
dan 10 sentimen salah. Paired bootstrap 1.000 kali (seed 42), Gemini–Qwen:
selisih F1 0,100492, interval 95% [0,045070; 0,149464]. Interpretasi terbatas
pada prosedur dan 150 ulasan ini; tidak menguji rata-rata tiga seed neural.

Prediksi: `results/predictions/B3-Qwen_42.csv`. Konfigurasi/metrik:
`results/metrics/B3-Qwen_42.json`. Evaluasi keseluruhan/per aspek, bootstrap,
dan confusion matrix: `results/metrics/uji_delapan_model/`.
Laporan Week 12/13 diperbarui. Seluruh delapan jenis model memiliki hasil,
dengan keterbatasan satu anotator dan 375 label latih/validasi belum diverifikasi.
