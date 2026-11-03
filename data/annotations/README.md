# Panduan aspek dan label acuan

Draf awal, 3 November 2026. Kategori final ditetapkan setelah kalibrasi
anotasi pada week 11.

## Bentuk anotasi

Satu baris per ulasan. Untuk setiap kategori aspek, isi satu label:

| Label | Arti |
|---|---|
| `tidak_disebut` | Aspek tidak dibahas |
| `positif` | Pengguna puas atau memuji aspek tersebut |
| `negatif` | Pengguna mengeluh atau melaporkan masalah pada aspek tersebut |
| `netral` | Aspek dibahas tanpa penilaian, misalnya pertanyaan atau saran |

Satu ulasan boleh memiliki beberapa aspek dengan sentimen berbeda.

## Kategori aspek awal

Kategori disusun dari contoh ulasan pilot. Persentase adalah perkiraan kata
kunci pada 2.000 ulasan, bukan label.

| Kategori | Cakupan | Contoh | Perkiraan |
|---|---|---|---|
| `akun_login` | Login, PIN, OTP, kata sandi, akun | "pin salah terus", "OTP tidak masuk" | 26% |
| `registrasi_data` | Pendaftaran, NIK, data diri, data sudah terdaftar | "NIK sudah terdaftar padahal belum daftar" | 14% |
| `fitur_kesehatan` | Cek kesehatan gratis, hasil pemeriksaan, vaksin, sertifikat, faskes | "hasil CKG tidak keluar" | 12% |
| `performa` | Error, force close, lambat, server, bug | "force close setelah input PIN" | 8% |
| `kemudahan_penggunaan` | Tampilan, alur, mudah atau sulit dipakai | "ribet untuk orang tua" | 17% |
| `umum` | Penilaian keseluruhan tanpa aspek khusus | "aplikasi bagus", "tidak berguna" | sisa |

Kandidat tambahan bila cukup sering setelah pilot: `dukungan_layanan`
(respon CS/aduan) dan `privasi_data` (data disalahgunakan). Saat ini
masing-masing di bawah 2% dan sementara digolongkan ke `umum`.

## Aturan

- `umum` hanya diisi bila tidak ada aspek khusus yang disebut.
- Sentimen dinilai dari teks, bukan dari rating bintang.
- Saran atau pertanyaan tanpa keluhan diberi `netral`.
- Keluhan yang menyebabkan aspek lain gagal dilabeli pada aspek penyebabnya
  dan aspek yang terdampak, misalnya error saat login: `performa` dan
  `akun_login` negatif.

## Proses

1. Kalibrasi: empat anggota melabeli 50 ulasan yang sama, bahas perbedaan,
   lalu perbarui panduan ini.
2. Anotasi gold: 800 ulasan (400 latih, 100 validasi, 300 uji).
3. Set uji dianotasi dua orang. Hitung Cohen's kappa per aspek; perbedaan
   diselesaikan oleh anotator ketiga.
4. Label manual dan label LLM disimpan di file terpisah, dihubungkan dengan
   `reviewId`.
