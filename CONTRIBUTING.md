# Panduan kontribusi

## Menyiapkan lingkungan

Gunakan Python 3.14, sesuai `.python-version` dan CI. Google Colab memakai
versinya sendiri; kode harus tetap berjalan di Colab bila training dilakukan
di sana. Buat environment lokal:

```text
python -m venv .venv
```

Aktifkan di PowerShell dengan `.venv\Scripts\Activate.ps1`, atau jalankan
Python environment secara langsung tanpa aktivasi:

```text
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Di Linux/macOS, gunakan `.venv/bin/python` sebagai pengganti path tersebut.
Tambahkan ke `requirements.txt` hanya library dan versi yang benar-benar
digunakan dan diuji. PyTorch dengan GPU NVIDIA dipasang terpisah, lihat
[keputusan metode](docs/project/method-decisions.md#lingkungan).

## Alur kerja kelompok

1. Ambil perubahan terbaru dari `main` sebelum mulai.
2. Buat branch yang menjelaskan pekerjaan, misalnya `docs/dataset`,
   `feat/aspect-extraction`, atau `fix/evaluation-labels`.
3. Kerjakan satu perubahan yang jelas, kemudian jalankan pemeriksaan terkait.
4. Push branch dan buat pull request ke `main`. Isi template perubahan dan
   pemeriksaan; tautkan issue bila ada.
5. Setelah anggota bergabung, minta anggota lain meninjau perubahan. Usahakan
   satu review sebelum merge; hindari mengedit notebook yang sama bersamaan.
6. Gunakan squash merge. Branch dapat dihapus otomatis setelah merge.

Panduan review ini adalah alur kerja kelompok; dokumen tidak menyatakan bahwa
branch protection sudah diaktifkan. Perubahan awal pengaturan repo telah
dibuat langsung pada `main` sebelum alur kontribusi kelompok dimulai.

## Pesan commit

Gunakan pesan singkat yang menjelaskan hasil. Awalan yang dapat dipakai:
`feat`, `fix`, `docs`, `chore`, `ci`, dan `test`.

```text
docs: describe dataset characteristics
feat: add aspect extraction pipeline
fix: correct aspect sentiment labels
```

Bahasa Indonesia atau Inggris boleh digunakan secara konsisten.

## Pengumpulan data, anotasi, dan eksperimen ABSA

- Catat sumber, izin, versi, target, dan cara memperoleh data di `data/README.md`.
- Pertahankan data asli. Hasil transformasi ditempatkan di `data/processed/`
  atau dibuat ulang melalui kode bila tidak diunggah.
- Catat asal teks, waktu pengambilan, dan cara pengumpulan. Bila scraping,
  simpan skrip, parameter, dan batas pengambilannya agar proses dapat diulang.
- Tentukan aspek yang dianalisis, bentuk anotasi, arti label sentimen, serta
  cara menangani satu teks yang memuat beberapa aspek.
- Simpan panduan dan label acuan di `data/annotations/`; bedakan anotasi
  manual dari prediksi model.
- Pisahkan kode pengumpulan, pembersihan, analisis aspek/sentimen, dan
  evaluasi. Fungsi bersama masuk `src/`.
- Untuk setiap eksperimen, catat versi kode/data, fitur, parameter, seed,
  skema pembagian, metrik, dan lokasi hasil.
- Periksa teks duplikat dan unit pembagian data agar teks/ulasan yang sama
  tidak masuk data latih sekaligus uji melalui anotasi aspek yang berbeda.
- Beri label hasil validasi/CV atau uji final. Pemilihan parameter menggunakan
  validasi; data uji final disimpan untuk evaluasi sesudah konfigurasi dipilih.
- Jalankan notebook dari kernel bersih sebelum membagikan hasilnya. Simpan
  keluaran penting yang relevan dan hapus keluaran berukuran besar/tidak perlu.
- Samakan angka pada `results/`, laporan, artikel, dan slide.

## Pemeriksaan sebelum merge

CI memasang dependensi, memeriksa kompatibilitas, menjalankan tes anotasi
dengan data buatan, dan memeriksa sintaks `.py` dalam `src/`.
Pemeriksaan lokal:

```text
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python -m compileall -q src
git diff --check
```

Gunakan environment proyek untuk menjalankan perintah Python di atas.
CI belum menjalankan notebook, menguji perilaku model, atau membuktikan
kebenaran metrik. Tambahkan pengujian yang relevan saat pipeline tersedia.
Periksa dokumen dan hasil secara manual sesuai isi perubahan.

## Dokumen dan pelaporan masalah

Setiap anggota menulis dan memperbarui bagian yang dikerjakannya. Struktur
kerja kelompok ada di [docs/project/README.md](docs/project/README.md).
Gunakan template issue untuk bug atau usulan dan isi bukti yang relevan.
Untuk kredensial atau data sensitif, ikuti [SECURITY.md](SECURITY.md).

Dependabot membuat PR pembaruan bulanan. Baca perubahan dan periksa CI sebelum
merge; jalankan ulang eksperimen yang terpengaruh oleh pembaruan library.
