# Laporan proyek

## Laporan utama untuk week 13

- [Laporan pertama week 13 (.docx)](Week_13_Laporan_Pertama_ABSA_SATUSEHAT.docx):
  versi laporan pertama, disusun 14 November 2026 dari pekerjaan week 10-12.
  Memuat ringkasan, dataset dan BOD, metode, implementasi, hasil aktual LR,
  SVM, Naive Bayes, Gemini, serta IndoBERT base, large, dan BiLSTM pada 150 ulasan uji, confusion matrix,
  analisis kesalahan, keterbatasan, serta tindak lanjut. Bagian 12.2
  memetakan isi laporan terhadap ketentuan week 10 sampai 13.
  Label uji berasal dari satu anotator; hasil model yang belum dijalankan
  tidak diklaim tersedia. Dokumen ini menjadi acuan laporan pertama.
- [PDF laporan pertama week 13](Week_13_Laporan_Pertama_ABSA_SATUSEHAT.pdf):
  ekspor terbaru dari DOCX yang sama, diperbarui 17 November 2026 dengan hasil
  IndoBERT base, large, dan BiLSTM tiga seed pada bagian 10.9.3–10.9.5. Tata letak sudah diperiksa.
  Gunakan versi ini untuk penyerahan setelah kelompok meninjau isinya.

## Laporan progres week 12 terpisah

- [Week 12 pemodelan dan evaluasi (.docx)](Week_12_Pemodelan_Evaluasi_ABSA_SATUSEHAT.docx)
  dan [PDF](Week_12_Pemodelan_Evaluasi_ABSA_SATUSEHAT.pdf): laporan progres
  diperbarui dengan hasil IndoBERT base, large, dan BiLSTM tiga seed; berfokus pada implementasi
  model, metrik, hasil tujuh jenis model
  keseluruhan dan per aspek, confusion matrix, analisis kesalahan, serta
  keterbatasan. Disusun terpisah pada 17 November 2026 dari hasil yang sama
  dengan laporan week 13. Pembaruan hasil berasal dari ZIP Colab pengguna;
  [ringkasan dan verifikasi](../../results/indobert/README.md) memuat F1
  pasangan rata-rata 0,775 ± 0,013. Bagian 8 membahas base; bagian 9 membahas large (0,765 ± 0,020), dan bagian 10 membahas
  [BiLSTM](../../results/bilstm/README.md) (0,373 ± 0,016).
- Berkas ini melengkapi arsip progres. Untuk tugas laporan pertama Sesi 13,
  laporan week 13 tetap menjadi dokumen gabungan acuan.

## Arsip laporan week 10-12

- [Laporan gabungan week 10-12 (.docx)](<Laporan ABSA SATUSEHAT.docx>): bahan
  laporan lengkap. Bab 1-5 (week 10): latar belakang, revisi masukan dosen,
  BOD CRISP-DM, dataset 39.995 ulasan, karakteristik data, dan rancangan
  delapan model. Bab 6-11 (week 11): preprocessing, pembagian data, anotasi,
  skema delapan aspek, pemeriksaan label manual, perbandingan dengan Gemini,
  verifikasi, kode model, pratinjau per aspek, dan 30 tes. Bab 12-14: tugas,
  status, dan kesimpulan. Hasil set uji tersedia untuk empat model pada 150
  ulasan berlabel satu anotator. Revisi 14 November 2026 memperjelas nama
  dan hasil LR, SVM, Naive Bayes, serta Gemini (bagian 10.9.1), menambahkan
  tabel kesalahan, dan confusion matrix empat label (bagian 10.9.2).
  Matriks gabungan memuat 1.200 keputusan aspek dari 150 ulasan; matriks
  delapan aspek per model dan CSV tersedia di
  [hasil evaluasi](../../results/metrics/uji/confusion_matrix/).
- PDF lama (`Week_10_Dataset_BOD_Algoritma_ABSA.pdf`,
  `Week_11_Coding_Preprocessing_Anotasi_ABSA.pdf`) adalah versi awal sebelum
  revisi. Untuk laporan pertama, gunakan berkas week 13 di atas.

## Laporan pertama (week 13)

Rencana pembagian penyusunan laporan week 13:

- Efraim: latar belakang, tujuan/BOD, sumber dan karakteristik data.
- Bambang: preprocessing, anotasi dan pembagian data.
- Jap: metode/model ABSA dan konfigurasi percobaan.
- Geraldyn: evaluasi, hasil, grafik, analisis kesalahan dan keterbatasan.

Setiap anggota menulis dan merapikan bagiannya dari bahan week 10-12.
Pembahasan, kesimpulan, referensi, penyatuan format dan pemeriksaan akhir
dikerjakan bersama.

File laporan week 13 telah tersedia sebagai satu dokumen yang merangkum
pekerjaan sebelumnya. Status pengumpulan ke dosen tidak dicatat sebagai
selesai; template khusus, jika diberikan, mengikuti arahan dosen.
