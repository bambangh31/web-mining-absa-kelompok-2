# Panduan aspek dan label acuan

Draf awal 3 November 2026; diperbarui 10 November 2026 menjadi delapan
kategori berdasarkan pelabelan manual 354 ulasan. Kategori final tetap
dikonfirmasi saat kalibrasi.

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
| `pembaruan_aplikasi` | Update, versi, diminta update terus, gagal update, peralihan atau ganti nama dari PeduliLindungi, perbandingan dengan aplikasi lama | "udah diupdate malah gak bisa dibuka", "enakan peduli lindungi" | 26% |
| `layanan_pelanggan` | CS, helpdesk, aduan lewat email/WA, tanggapan pengembang | "wa nggk pernah dibalas", "ditangani dengan cepat" | 4% |
| `umum` | Penilaian keseluruhan tanpa aspek khusus | "aplikasi bagus", "tidak berguna" | sisa |

Dua kategori terakhir sebelum `umum` ditambahkan 10 November 2026. Pada
lembar manual 354 ulasan terdapat 121 penyebutan pembaruan aplikasi dan 24
penyebutan layanan pelanggan. Perkiraan persentase keduanya memakai daftar
kata kunci `src/aspect_keywords.py` pada pool 32.035 ulasan, bukan label.
`privasi_data` tetap digolongkan ke `umum` karena belum ditemukan cukup
contoh.

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
- `pembaruan_aplikasi` diisi bila update/versi/peralihan aplikasi disebut.
  "Setelah update tidak bisa dibuka" adalah `pembaruan_aplikasi` negatif dan
  `performa` negatif. Mengubah nomor telepon atau email di profil adalah
  `registrasi_data`, bukan `akun_login`.
- `layanan_pelanggan` diisi bila CS, helpdesk, admin, atau tanggapan aduan
  dinilai. Sapaan "min" saja tanpa penilaian tidak dihitung.

## Anotasi rinci dan label per ulasan

Lembar Excel ("Label Manual Sentimen Komentar Satu Sehat.xlsx") mencatat
satu baris per penyebutan aspek: Kata Aspek (persis dari ulasan), Aspek
(seragam), Kategori Aspek, Label, dan Bukti dari komentar. Kata aspek dan
bukti harus potongan persis dari komentar. reviewId, tanggal, versi
aplikasi, rating, dan komentar harus sama persis dengan data asli; versi
kosong tetap kosong.

Label per ulasan (delapan kolom) diturunkan otomatis, di lembar "Label per
Ulasan" dan di `src/absa_schema.py`:

1. Aspek tanpa penyebutan: `tidak_disebut`.
2. Semua penyebutan netral: `netral`.
3. Selain itu label mayoritas positif/negatif; jumlah sama dihitung
   `negatif`.
4. `umum` dikosongkan bila ada aspek khusus.

Lembar versi LLM memakai format yang sama sehingga keduanya bisa
dibandingkan dengan `src/compare_labels.py`.

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
| `gold_<nama>.csv` | Label satu anotator: `reviewId`, `annotator`, delapan kolom aspek |
| `gold.csv` | Label manual final setelah perbedaan diselesaikan, kolom sama tanpa `annotator` |
| `llm_<model>.csv` | Label LLM untuk 800 ulasan latih/validasi/uji: `reviewId`, `model`, `prompt_version`, delapan kolom aspek |
| `verified.csv` | Label latih dan validasi setelah verifikasi: `reviewId`, `verifier`, `model`, `prompt_version`, delapan kolom aspek |

Delapan kolom aspek memakai nama kategori di atas dan berisi salah satu dari
empat label. Respons mentah LLM dan daftar penyebutan (berisi potongan
teks) disimpan di `data/annotation_workspace/llm/` yang tidak diunggah.

## Perangkat kalibrasi dan anotasi

Gunakan [alur kalibrasi dan anotasi](../../docs/project/annotation-workflow.md)
untuk membuat lembar kosong melalui `src/annotation.py`, memeriksa hasil
empat anotator, dan mengekspor label setelah perbedaan diselesaikan.

Lembar berisi teks disimpan di `data/annotation_workspace/` dan tidak
diunggah. Hasil ekspor tanpa teks disimpan dalam subfolder berversi,
misalnya `data/annotations/final_v1/gold.csv`. Dataset sudah tersedia pada
4 November 2026; lembar kosong kalibrasi/gold telah dibuat lokal.
Kalibrasi manusia, label gold, dan kappa aktual belum tersedia.
