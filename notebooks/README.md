# Jupyter Notebook

## Sudah tersedia

1. [01_preprocessing.ipynb](01_preprocessing.ipynb): membaca dataset lengkap,
   memeriksa versi/hash, cleaning dua bentuk teks, pembagian berstrata rating,
   pemeriksaan kebocoran teks identik, serta penyimpanan clean/split.
2. [02_kalibrasi_anotasi.ipynb](02_kalibrasi_anotasi.ipynb): menyiapkan lembar
   kosong, menghitung progres pengisian tanpa memperlihatkan label anggota
   lain, dan menyediakan langkah audit/finalisasi setelah anotasi lengkap.
3. [03_indobert_colab.ipynb](03_indobert_colab.ipynb): pelatihan IndoBERT
   base pada GPU Colab, seed 42/43/44; opsi large tidak diaktifkan pada run
   yang diterima. Hasil aktual dan pemeriksaan tercatat di
   [results/indobert](../results/indobert/README.md). Input 400 latih,
   100 validasi, dan 150 uji manual; unduh ZIP setelah selesai.

Notebook tetap berbahasa Python. Fungsi bersama di `src/` dipertahankan agar
aturan notebook sama dengan kode yang sudah diuji. Notebook dibagikan dengan
output kosong agar tampilan contoh ulasan/progres lokal tidak tersimpan
otomatis dalam Git. Hasil akan terlihat setelah sel dijalankan.

## Cara membuka

Dari akar repository, setelah environment Python dibuat:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m jupyterlab notebooks
```

Pilih kernel environment proyek. VS Code dengan dukungan Jupyter juga dapat
membuka file `.ipynb` langsung; pilih interpreter `.venv` pada pemilih kernel.
Jalankan notebook 01 terlebih dahulu, lalu 02. Gunakan **Restart Kernel → Run
All** untuk mengulang dari keadaan bersih. Root repo ditemukan otomatis saat
notebook dijalankan dari akar repo atau folder `notebooks/`.

Kode memverifikasi berkas yang sudah ada dan tidak menimpa clean/split yang
berbeda atau workspace anotasi. Hash versi sumber harus sesuai baseline;
perubahan dataset membutuhkan versi split yang disepakati bersama.

`RUN_AUDIT` dan `RUN_FINALIZE` bernilai False secara default. Kalibrasi/gold
tetap diisi manusia, tanpa prediksi label otomatis. Setelah mengisi, gunakan
folder audit/final baru; panduan lengkap ada di
[alur anotasi](../docs/project/annotation-workflow.md).

## Pemeriksaan

Kedua notebook diuji dengan kernel bersih, semua sel berurutan, pada Python
3.12.14. Hash clean/split cocok dengan baseline dan lembar anotasi yang sudah
ada tidak berubah. Notebook belum diuji pada kernel Python 3.14. Tes kode
Python pada CI terpisah dari eksekusi notebook.

## Tahap berikutnya

Notebook pengumpulan/eksplorasi, pelabelan LLM, pemodelan ABSA, dan evaluasi
belum dibuat pada perubahan ini. File Python scraping/eksplorasi tetap ada.
Notebook ini tidak menyatakan mining/evaluasi model atau label gold selesai.

## IndoBERT large

[04_indobert_large_colab.ipynb](04_indobert_large_colab.ipynb) menjalankan large saja pada GPU Colab, seed 42/43/44. Hasil aktual telah diterima dan [diverifikasi](../results/indobert_large/README.md). Micro-batch 4 dan akumulasi gradien 4 mempertahankan batch efektif 16. Unduh ZIP hasil sebelum mengakhiri runtime. Notebook dibagikan tanpa output.
