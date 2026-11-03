# Rencana kolaborasi Kelompok 2

Topik tugas: Aspect Based Analysis, dengan rencana analisis sentimen berbasis
aspek (ABSA). Empat peran mengikuti pilihan pengguna. Penempatan nama dan
rincian mingguan berikut merupakan usulan pembagian awal, dapat disesuaikan
berdasarkan beban nyata, tanpa PIC khusus.

## Anggota dan peran

| Anggota | NRP | Peran | Pekerjaan |
|---|---|---|---|
| Bambang Herlambang | 5803024019 | Preprocessing dan anotasi | Membersihkan teks, memeriksa duplikasi, menentukan definisi aspek/sentimen, serta menyiapkan atau memeriksa label acuan. |
| Efraim Melvyn Rafelino Lahai | 5803024009 | Pengumpulan dan eksplorasi data | Mencari dataset atau scraping ulasan, mencatat sumber, menampilkan contoh dan karakteristik data. |
| Jap Robertus Kurniawan Setiabudi | 5803024004 | Pemodelan ABSA | Menerapkan metode untuk mengenali aspek dan menentukan sentimen pada setiap aspek. |
| Robertus Geraldyn Alexandro Gabeler | 5803024025 | Evaluasi dan analisis | Membandingkan prediksi dengan label acuan, menghitung metrik, membuat grafik, dan menjelaskan kesalahan. |

Nama singkat di bawah: Bambang, Efraim, Jap, dan Geraldyn. Peran menunjukkan
fokus kontribusi, bukan seluruh pekerjaan harus dilakukan sendiri. Jika
scraping, anotasi, atau model ternyata berat, bagi subtugas kepada anggota
lain. Catatan metode dan referensi disiapkan saat pekerjaan berlangsung.

## Pembagian pekerjaan per minggu

Setiap minggu dikerjakan berempat sesuai peran. Kelas setiap Rabu;
week 11 pada 4 November 2026 menjadi acuan. Week 10 dipetakan mundur,
minggu berikutnya dipetakan per Rabu dan mengikuti perubahan jadwal dosen.
Tanggal kelas bukan otomatis tenggat pengumpulan.

| Week / kelas 2026 | Pembagian dan hasil |
|---|---|
| 10 / 28 Oktober | Efraim mencari kandidat/sumber, menyusun tujuan/BOD serta rancangan pengumpulan dan karakteristik data. Bambang memeriksa kualitas teks, kebutuhan preprocessing dan label/aspek yang tersedia. Jap mengkaji serta merencanakan metode/model ABSA dan kebutuhan masukan/keluaran. Geraldyn merancang metrik, protokol evaluasi dan kebutuhan label acuan. Dataset serta lingkup akhir disepakati berempat. |
| 11 / 4 November | Efraim menulis pengambilan data dan eksplorasi. Bambang menulis pembersihan, panduan anotasi dan pembagian data. Jap menyiapkan model awal dengan masukan/keluaran yang disepakati. Geraldyn menyiapkan format prediksi-label, fungsi evaluasi dan pembanding awal bila relevan. |
| 12 / 11 November | Efraim memeriksa kelengkapan/sumber dan keterulangan pengambilan. Bambang menyelesaikan data/label acuan serta catatan transformasi. Jap menjalankan analisis aspek dan sentimen. Geraldyn menghitung metrik, membuat grafik dan menjelaskan pola kesalahan. Semua menghubungkan pipeline serta memeriksa hasil. |
| 13 / 18 November | Efraim menulis latar belakang, tujuan/BOD, sumber dan karakteristik data. Bambang menulis preprocessing, anotasi dan pembagian data. Jap menulis metode/model ABSA dan konfigurasi percobaan. Geraldyn menulis evaluasi, hasil, grafik, analisis kesalahan dan keterbatasan. Pembahasan, kesimpulan, referensi, penyatuan format dan pemeriksaan akhir dikerjakan bersama pada satu dokumen. |
| 14 / 25 November | Jika diminta dosen, berempat membagi tindak lanjut sesuai peran: Efraim menangani pengumpulan/eksplorasi data, Bambang preprocessing/anotasi, Jap metode/model ABSA, dan Geraldyn evaluasi/analisis. Detail perubahan mengikuti masukan dosen; hasil dan keputusan diperiksa bersama. Jika tidak diminta, tidak ada percobaan tambahan wajib. |
| 15 / 2 Desember | Efraim menulis latar/tujuan dan sumber data; Bambang menulis pengolahan data/anotasi; Jap menulis metode/model; Geraldyn menulis evaluasi dan hasil. Pembahasan, abstrak/kesimpulan bila diperlukan, referensi dan pemeriksaan akhir bersama. Artikel berbahasa Indonesia mengikuti template dosen. |
| 16 / 9 Desember | Efraim membuat slide tujuan, sumber dan karakteristik data; Bambang membuat slide preprocessing dan anotasi; Jap membuat slide metode/model ABSA; Geraldyn membuat slide evaluasi, hasil dan keterbatasan. Identitas, kesimpulan dan referensi dirapikan bersama. Semua memeriksa alur/angka, latihan dan menyiapkan jawaban; presenter mengikuti arahan dosen. |

## Rincian week 11-12 untuk topik SATUSEHAT Mobile

Mengikuti [usulan week 10](../week-10/README.md) dan
[keputusan metode](method-decisions.md). Urutan menunjukkan ketergantungan.

| Week | Anggota | Tugas | Selesai jika |
|---|---|---|---|
| 11 | Efraim | Scraping 15.000 ulasan, `reviews_clean.csv`, `split.csv`, notebook eksplorasi | File dibagikan; jumlah baris dan tanggal scraping dicatat di `data/README.md` |
| 11 | Bambang | Kalibrasi 50 ulasan berempat, revisi panduan anotasi, mulai anotasi gold | Panduan final; kappa kalibrasi dicatat |
| 11 | Jap | Kunci API Gemini, prompt v1 dari contoh kalibrasi, uji Gemini dan model lokal pada 50 ulasan kalibrasi | Kedua LLM menghasilkan JSON valid; skor pada kalibrasi dicatat |
| 11 | Geraldyn | Fungsi evaluasi (F1 aspek, F1 pasangan, macro-F1, kappa) dan uji dengan label buatan | Fungsi memberi hasil benar pada contoh kecil yang dihitung manual |
| 11 | Semua | Anotasi gold, sekitar 275 ulasan per orang | `gold.csv` lengkap 800 ulasan |
| 12 | Jap | Pilih LLM silver dengan set validasi, label silver, latih B1, B2, P1, P2 | Prediksi set uji untuk semua model tersimpan |
| 12 | Geraldyn | Skor semua model, grafik, analisis kesalahan, analisis per versi | Tabel metrik dan grafik di `results/` |
| 12 | Efraim | Statistik per versi dan konsistensi rating dari prediksi model terbaik | Grafik dan tabel per versi |
| 12 | Bambang | Penyelesaian perbedaan anotasi set uji, kappa per aspek | Kappa per aspek dicatat |

## Alasan dan batas pembagian

- Keempat anggota berkontribusi setiap minggu sesuai peran, termasuk
  menyiapkan bahan week 10 dan menyusun laporan week 13 bersama.
- Penyusunan presentasi dibagi berempat sesuai peran, menggunakan satu materi
  bersama dengan format yang disepakati. Setiap anggota membuat dan merapikan
  slide bagiannya; alur, kesimpulan dan referensi diperiksa bersama.
- Bambang menangani preprocessing dan anotasi. Bila anotasi manual banyak
  atau sulit, sebagian anotasi/pemeriksaannya dibagi agar bebannya seimbang.
- Semua mendapat kontribusi coding sesuai peran dan menulis bagian artikel
  yang paling dipahami. Berat aktual diperiksa setelah dataset/metode dipilih.
- Setiap anggota menulis dan merapikan bagian laporannya dari catatan,
  konfigurasi dan hasil pekerjaannya. Semua memeriksa konsistensi angka,
  alur pembahasan dan format pada dokumen bersama.
- Jika satu bagian lebih berat, bagi ulang subtugas agar beban seimbang.
  Tidak ada tambahan
  kewajiban metode atau format artikel yang tidak diberikan dosen.

## Bahan dan urutan integrasi

| Bagian | Bahan yang diserahkan | Waktu |
|---|---|---|
| Efraim | Sumber/izin, versi data, kode/parameter pengambilan, contoh dan karakteristik | Week 10-12; siap sebelum laporan disusun |
| Bambang | Aturan pembersihan, kamus label, pedoman anotasi, data/label acuan, skema pembagian | Week 11-12; siap sebelum hasil akhir dievaluasi |
| Jap | Penjelasan metode, kode, konfigurasi dan prediksi dengan ID teks/aspek yang jelas | Week 11-12; siap untuk evaluasi dan laporan |
| Geraldyn | Definisi metrik, set evaluasi, skor, angka sumber grafik dan analisis kesalahan | Week 11-12; menjadi bahan laporan week 13 |
| Semua sesuai bagian | Naskah artikel dan hasil/gambar yang sudah diperiksa | Week 15; menjadi bahan slide masing-masing pada week 16 |

1. Sepakati sumber, tujuan/BOD, unit analisis, aspek, dan lingkup ABSA.
2. Tentukan format masukan/keluaran dan pembagian data sebelum menguji metode.
   Pemeriksaan sumber, pembersihan/anotasi, kerangka model dan evaluasi dapat
   berjalan paralel ketika bahan yang dibutuhkan sudah jelas.
3. Cocokkan ID teks, aspek, label acuan dan prediksi. Pisahkan label manual
   atau label dari sumber dengan prediksi model.
4. Periksa teks duplikat dan pembagian ulasan agar satu teks tidak masuk
   latih sekaligus uji melalui anotasi aspek yang berbeda.
5. Simpan versi kode/data, parameter, hasil dan keterbatasan. Bedakan hasil
   validasi/CV dari uji final; pilih konfigurasi melalui validasi.

## Review, keputusan dan pencatatan

Ikuti [CONTRIBUTING.md](../../CONTRIBUTING.md). Setelah anggota bergabung,
usahakan satu review anggota lain sebelum merge. Periksa sumber serta
kesesuaian tugas untuk dokumen; periksa perilaku, label, pembagian dan
keterulangan untuk kode. CI sintaks belum menguji ketepatan ABSA.

Keputusan dataset, label, metode dan metrik dicatat pada dokumen tahap
terkait. Jika berubah, catat alasan dan eksperimen yang perlu diulang.
Gunakan issue atau satu tracker bersama:

| Tugas / week | Anggota | Hasil | Target | Status | Bukti / kendala |
|---|---|---|---|---|---|
| Diisi saat pembagian | Diisi | Diisi | Disepakati | Sesuai progres nyata | Tautan atau hambatan |

Tahap dan ketentuan dosen ada di [timeline.md](timeline.md). Pembagian
kontribusi tidak dianggap sebagai hasil pekerjaan yang sudah selesai.
