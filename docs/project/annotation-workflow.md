# Alur kalibrasi dan anotasi Bambang

Disiapkan 3 November 2026 untuk week 11-12. Mengikuti
[keputusan metode](method-decisions.md) dan
[panduan aspek](../../data/annotations/README.md). Ini perangkat kerja,
bukan klaim bahwa kalibrasi atau anotasi manusia sudah dilakukan.

## Batas pekerjaan

- Efraim/Melvyn menyediakan dataset mentah, sumber, dan catatan scraping.
  Dataset lengkap tersedia sejak 4 November 2026. Preprocessing dan split
  sekarang dibuat dengan `src/preprocess.py` untuk melanjutkan pekerjaan
  Bambang. Seluruh tim menggunakan satu versi split yang sama.
- Bambang menyiapkan lembar, memeriksa label, merangkum perbedaan, memperbarui
  pedoman setelah diskusi, dan mengekspor hasil kesepakatan.
- Semua anggota memberi label secara mandiri sebelum melihat label lain.
- Geraldyn dapat memakai laporan kappa sebelum adjudikasi; implementasi
  evaluasi model/F1 tetap terpisah. Jap memakai kalibrasi final untuk prompt.

Lembar kosong dari data nyata sudah disiapkan lokal pada 4 November 2026:
50 kalibrasi dan 275 penugasan gold per orang. Hasil preprocessing ada di
[laporan preprocessing](../../results/preprocessing/v1/README.md).
Label gold, kappa kelompok, dan pedoman final belum tersedia.
Jangan mengambil sampel baru yang berbeda untuk tiap anggota. Kalibrasi
tetap terpisah dari gold dan silver.

## 1. Buat lembar kosong setelah data diterima

Kode hanya memakai standard library Python; target proyek tetap Python 3.14.
Dari akar repo:

```text
python src/annotation.py prepare --reviews data/processed/reviews_clean.csv --split data/annotations/split.csv
```

Input clean harus memiliki `reviewId` dan `text_llm`; input split tepat
`reviewId,split`. Split yang diterima adalah 50 `kalibrasi`, 400 `gold_train`,
100 `gold_val`, 300 `gold_test`, serta sisanya `silver`. ID harus unik dan
ditemukan di clean. Kode ini tidak menggantikan pemeriksaan duplikasi teks
atau stratifikasi rating oleh pembuat split.

Keluaran lokal di `data/annotation_workspace/` sudah diabaikan Git:

- Empat `kalibrasi_<nama>.csv`: 50 ID dan teks yang sama untuk semua anggota.
- Empat `gold_<nama>.csv`: masing-masing 275 ulasan (100 latih, 25 validasi,
  150 uji). Setiap pasangan anggota berbagi 50 ulasan uji. Total 800 ulasan
  unik dengan 1.100 penugasan gold; kalibrasi menambah 50 per orang.
- `manifest.json`: hash SHA-256 sumber, pembagian ID, dan hash teks. Seed 42
  hanya mengacak urutan/penugasan; keanggotaan split tidak diubah.

Nama anggota pada file: `bambang`, `efraim` (Melvyn), `jap`, `geraldyn`.
Label awal sengaja kosong. Rating, jenis split, versi, dan prediksi LLM
tidak ditampilkan agar anotasi berdasarkan teks. Teks yang diawali karakter
formula diberi apostrof pada lembar kerja saja; teks model tidak diubah.

Folder keluaran harus belum ada; kode menolak menimpa hasil. Untuk putaran
baru, gunakan `--workspace` baru di dalam `data/annotation_workspace/` dan
pertahankan paket lama. Gunakan parameter workspace yang sama pada audit
dan finalize putaran tersebut.

## 2. Kalibrasi 50 ulasan secara mandiri

Bagikan satu lembar kepada masing-masing anggota secara privat. Buka di
Excel/Sheets atau editor CSV. Simpan kembali sebagai CSV UTF-8, pemisah koma,
dengan nama yang sama (UTF-8 dengan/tanpa BOM diterima).

- Hanya isi enam aspek dan `catatan`. Jangan ubah ID, anotator, atau teks;
  jangan mengurutkan satu kolom tanpa kolom lainnya.
- Isi setiap aspek dengan `tidak_disebut`, `positif`, `negatif`, atau `netral`.
- Aspek: `akun_login`, `registrasi_data`, `fitur_kesehatan`, `performa`,
  `kemudahan_penggunaan`, `umum`. Umum tidak boleh bersama aspek khusus.
- Catat kasus ambigu untuk diskusi. Jangan mengisi gold memakai prediksi
  LLM; gold dan silver adalah kondisi eksperimen yang berbeda.

Setelah empat lembar lengkap:

```text
python src/annotation.py audit --phase kalibrasi --output data/annotation_workspace/audit_kalibrasi_v1
```

Hasil: `agreement.csv` (kesepakatan dan Cohen's kappa nominal tanpa bobot
per pasangan/per aspek), `resolutions.csv` (sel yang berbeda), dan
`report.json` (jumlah, hash input, serta metrik sebelum adjudikasi).
Jika hanya ada satu kelas yang sama, kappa tidak terdefinisi: JSON `null`,
CSV kosong, dengan catatan khusus; bukan kappa nol atau bukti sempurna.
Kode tidak menetapkan ambang lulus kalibrasi sepihak.

Bahas perbedaan berempat. Isi `final_label`, `adjudicator` (nama anggota),
dan alasan di `catatan` pada `resolutions.csv`; perbarui pedoman sesuai
kesepakatan. Simpan anotasi awal agar kappa tetap mengukur penilaian mandiri,
bukan kesepakatan setelah diskusi. Jika perlu kalibrasi ulang, simpan sebagai
putaran baru dengan versi pedoman yang dicatat.

```text
python src/annotation.py finalize --phase kalibrasi --resolutions data/annotation_workspace/audit_kalibrasi_v1/resolutions.csv --output data/annotations/kalibrasi_v1
```

## 3. Anotasi gold setelah pedoman disepakati

Isi lembar `gold_<nama>.csv` masing-masing, lalu jalankan:

```text
python src/annotation.py audit --phase gold --output data/annotation_workspace/audit_gold_v1
```

Perbedaan set uji diputuskan anggota ketiga yang bukan kedua anotator awal
pada ulasan tersebut; alat menegakkan aturan itu. Isi label, adjudicator,
dan alasan. Jangan mengubah label berdasarkan prediksi model agar skor naik.

```text
python src/annotation.py finalize --phase gold --resolutions data/annotation_workspace/audit_gold_v1/resolutions.csv --output data/annotations/final_v1
```

Jika tidak ada konflik, `--resolutions` boleh dihilangkan. Label kosong,
konflik belum selesai, atau label awal yang berubah sesudah audit ditolak.
Buat audit baru jika anotasi awal diubah. Kontradiksi umum/aspek khusus
pada label akhir juga ditolak dan perlu dibahas ulang.

Ekspor berisi `gold.csv` (800 ID, enam label), `gold_<nama>.csv` (label awal
tanpa teks), `provenance.csv` (asal keputusan tiap sel), dan `report.json`
(metrik sebelum adjudikasi, hash input/keputusan). Teks dan catatan bebas
tidak ikut diekspor. Simpan lembar dan alasan asli di workspace privat.

Gunakan versi gold yang ditinjau bersama pada pipeline Jap/Geraldyn. Jika
pipeline memerlukan `data/annotations/gold.csv`, salin hasil final yang
sudah diperiksa ke path itu dan catat versi sumber; jangan menimpa label
lama secara diam-diam. Jangan unggah lembar kerja berisi teks.

## Pertanyaan yang perlu diselesaikan saat kalibrasi

- Bagaimana memilih satu label jika pujian dan keluhan membahas aspek sama?
- Bagaimana membedakan pertanyaan netral dari keluhan berbentuk tanya?
- Apakah keluhan CS/privasi cukup sering untuk mengubah kategori? Catat
  perubahan sebelum anotasi gold, beserta contoh dan alasan keputusan.

Ini pertanyaan terbuka, bukan penambahan label atau perubahan metode sepihak.

## Pemeriksaan kode

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

Delapan tes memakai 850 ulasan buatan di folder sementara yang otomatis
dihapus. Tes memeriksa penugasan, pemisahan ID, label kosong, kecocokan teks,
kappa yang dihitung manual, adjudikasi pihak ketiga, ekspor tanpa teks, dan
larangan menimpa hasil. Tes ini bukan penilaian anotator atau model ABSA.
