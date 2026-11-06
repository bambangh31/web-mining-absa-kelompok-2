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

Anotasi bersifat multi-aspek: satu ulasan boleh memiliki beberapa aspek
dengan sentimen berbeda. Contoh: "setiap mau login gangguan trus!
sertifikat gabisa di download!" diberi `akun_login` negatif dan
`fitur_kesehatan` negatif; aspek lain `tidak_disebut`.

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
- `netral` hanya untuk aspek yang disebut tanpa penilaian, misalnya saran
  atau pertanyaan. Aspek yang tidak disebut selalu `tidak_disebut`.
- `performa` hanya diisi bila ada kegagalan teknis yang disebut: error,
  force close, crash, lambat, loading, server, bug, atau tidak bisa dibuka.
  "Susah login" atau "PIN salah terus" hanya `akun_login` negatif; "login
  langsung error" adalah `akun_login` dan `performa` negatif.
- `kemudahan_penggunaan` hanya diisi bila pengguna menilai alur atau
  tampilan (ribet, bingung, mudah dipakai), bukan setiap kali ada fitur
  yang gagal.

## Proses

1. Kalibrasi: empat anggota melabeli 50 ulasan yang sama, bahas perbedaan,
   lalu perbarui panduan ini. Ulasan kalibrasi tidak masuk set gold dan
   menjadi sumber contoh few-shot untuk prompt LLM.
2. Latih dan validasi (400 + 100 ulasan): LLM memberi label lebih dulu,
   lalu satu anggota memeriksa setiap ulasan dan menyetujui atau mengoreksi
   labelnya. Panduan ini tetap menjadi acuan; label LLM bukan acuan.
3. Uji (300 ulasan): dua anggota melabeli secara mandiri tanpa melihat label
   LLM. Hitung Cohen's kappa per aspek; perbedaan diselesaikan oleh anotator
   ketiga.
4. Label LLM asli, label hasil verifikasi, dan label manual disimpan di file
   terpisah, dihubungkan dengan `reviewId`.

Alur ini mengikuti masukan dosen 6 November 2026. Alasannya ada di
[keputusan metode](../../docs/project/method-decisions.md#alur-label).

Cara pengambilan sampel, format file, dan definisi metrik ada di
[keputusan metode](../../docs/project/method-decisions.md).

## File di folder ini

File label hanya berisi `reviewId` dan label, tanpa teks ulasan, sehingga
boleh diunggah.

| File | Isi |
|---|---|
| `split.csv` | `reviewId`, `split` (`kalibrasi`, `gold_train`, `gold_val`, `gold_test`, `silver`) |
| `gold_<nama>.csv` | Label satu anotator: `reviewId`, `annotator`, enam kolom aspek |
| `gold.csv` | Label manual final setelah perbedaan diselesaikan, kolom sama tanpa `annotator` |
| `llm_<model>.csv` | Label LLM: `reviewId`, `model`, `prompt_version`, enam kolom aspek |
| `verified.csv` | Label latih dan validasi setelah verifikasi: `reviewId`, `verifier`, `model`, `prompt_version`, enam kolom aspek |

Enam kolom aspek memakai nama kategori di atas dan berisi salah satu dari
empat label.

## Perangkat kalibrasi dan anotasi

Gunakan [alur kalibrasi dan anotasi](../../docs/project/annotation-workflow.md)
untuk membuat lembar kosong melalui `src/annotation.py`, memeriksa hasil
empat anotator, dan mengekspor label setelah perbedaan diselesaikan.

Lembar berisi teks disimpan di `data/annotation_workspace/` dan tidak
diunggah. Hasil ekspor tanpa teks disimpan dalam subfolder berversi,
misalnya `data/annotations/final_v1/gold.csv`. Dataset sudah tersedia pada
4 November 2026; lembar kosong kalibrasi/gold telah dibuat lokal.
Kalibrasi manusia, label gold, dan kappa aktual belum tersedia.
