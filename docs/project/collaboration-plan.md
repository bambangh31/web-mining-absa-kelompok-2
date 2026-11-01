# Rencana kolaborasi Kelompok 2

Status: usulan pembagian kerja ABSA. Nama anggota dan pembagian personal
belum diberikan, sehingga dokumen ini tidak menetapkan penugasan nama.
Semua anggota berkontribusi tiap minggu; beban dibagi menurut waktu,
kesulitan, serta ketergantungan pekerjaan, tanpa PIC khusus.

## Paket kontribusi

| Paket | Pekerjaan | Bahan untuk anggota lain |
|---|---|---|
| Pengumpulan dan eksplorasi | Kandidat sumber, izin, scraping/unduhan bila dipilih, karakteristik dan contoh teks | Data asli, petunjuk pengambilan, kamus kolom, keterbatasan |
| Preprocessing dan anotasi | Pembersihan teks, duplikasi, unit pembagian, panduan aspek/sentimen, label acuan | Data/prosedur olahan, panduan anotasi, definisi label dan split |
| Aspek dan sentimen | Metode ekstraksi/kategori aspek dan sentimen per aspek sesuai lingkup | Kode, konfigurasi, hasil prediksi, alasan metode |
| Evaluasi dan visualisasi | Metrik sesuai target, rekap, analisis kesalahan dan grafik | Angka sumber, penjelasan unit evaluasi, hasil per aspek bila relevan |

Paket bukan jumlah anggota. Satu paket dapat dipecah atau dikerjakan bersama.
Setiap pelaksana juga menulis penjelasan dan referensi bagiannya. Penulisan
laporan, artikel, serta slide tidak dibebankan seluruhnya pada satu orang.

## Urutan dan pekerjaan paralel

1. Semua mengusulkan kandidat data dan memilih masalah/tujuan bersama.
2. Sepakati unit analisis, aspek, ketersediaan label, serta bentuk hasil ABSA.
3. Tentukan pembagian data dan format masukan/keluaran sebelum membandingkan
   metode. Pembersihan, panduan anotasi, kerangka model, dan fungsi evaluasi
   dapat dikerjakan bersamaan setelah batasnya jelas.
4. Hubungkan pipeline dari data sampai hasil; cocokkan ID teks, aspek, dan
   label agar keluaran tiap bagian dapat dievaluasi.
5. Masing-masing menyerahkan kode, konfigurasi, penjelasan, serta bukti
   hasil. Anggota lain melakukan pemeriksaan silang.

## Review dan keputusan

Ikuti [CONTRIBUTING.md](../../CONTRIBUTING.md) untuk branch, PR, dan CI.
Usahakan satu review anggota lain sebelum merge setelah anggota bergabung.
Review dokumen memeriksa sumber dan kesesuaian tugas; review kode memeriksa
perilaku, pembagian data, dan keterulangan hasil. CI sintaks belum menguji
ketepatan ekstraksi aspek atau hasil sentimen.

Catat keputusan dataset, label, metode, dan metrik pada dokumen tahap
terkait. Jika keputusan berubah, jelaskan perubahan, alasannya, dan hasil
yang perlu dijalankan ulang. Jumlah metode mengikuti arahan Web Mining;
ketentuan perbandingan algoritma Data Mining tidak otomatis dipindahkan.

## Pencatatan kontribusi

Gunakan Issues atau satu tracker bersama dengan kolom:

| Tugas / week | Anggota | Hasil yang diharapkan | Target | Status | Bukti / kendala |
|---|---|---|---|---|---|
| Diisi saat tugas dibagi | Diisi kelompok | Diisi | Disepakati | Sesuai progres nyata | Tautan hasil atau hambatan |

Jika satu tugas lebih berat, bagi subtugas tersisa. Laporan kontribusi
mengikuti pekerjaan nyata, bukan banyaknya commit atau jumlah berkas saja.
