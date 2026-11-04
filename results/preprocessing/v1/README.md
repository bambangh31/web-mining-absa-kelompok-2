# Hasil preprocessing dataset lengkap

Dijalankan lokal 4 November 2026 dari dataset Melvyn pada `main` (`4da0c2e`).
Hash sumber/keluaran dan distribusi rating ada di [summary.json](summary.json).
Tidak menjalankan model/API LLM atau membuat label manusia.

| Tahap | Jumlah ulasan |
|---|---:|
| Data mentah | 39.995 |
| Dihapus: kurang dari 3 kata | 7.152 |
| Bersih untuk analisis versi, termasuk duplikat | 32.843 |
| Duplikat setelah filter panjang | 808 |
| Pool unik | 32.035 |
| Kalibrasi | 50 |
| Gold latih / validasi / uji | 400 / 100 / 300 |
| Silver, belum berlabel | 31.185 |

Duplikat 808 dihitung setelah filter tiga kata. Angka 5.527 pada eksplorasi
Melvyn mencakup ulasan pendek; populasi perhitungannya berbeda. Tidak ada
ulasan kosong/sebelum 1 Maret 2023 atau benturan tambahan hasil transformasi
model pada sumber ini.

## Aturan dan batas

- Jumlah kata dihitung sebelum masking/konversi emoji, setelah spasi rapi.
- `text_llm`: spasi rapi, masking pola NIK/telepon/email/URL, kapital dan emoji
  tetap. Tidak ada kecocokan regex pada data yang lolos filter. Regex tidak
  menjamin seluruh informasi pribadi terdeteksi; periksa sebelum memakai API.
- `text_model`: huruf kecil, emoji ke kata Indonesia, huruf berulang tiga
  atau lebih menjadi dua. Tanpa stemming/stopword removal; negasi tetap.
  Konversi memakai [emoji](https://pypi.org/project/emoji/).
- Pool menyimpan duplikat huruf kecil/spasi rapi yang paling awal berdasarkan
  tanggal (ID untuk tanggal sama). Teks model identik juga dikeluarkan dari
  pool. Duplikat tetap ada pada clean untuk analisis versi (`in_pool=0`).
- Sampling berstrata rating berurutan: kalibrasi, gold latih, validasi, uji,
  sisa silver. Alokasi sisa terbesar, seed 42, input ID diurutkan. Rating
  bukan label aspek/sentimen. Split acak ini bukan split temporal.
- ID pool unik dan teks model/LLM ternormalisasi tidak tumpang tindih
  antar-split. Parafrasa/duplikat dekat belum diperiksa.
- Kalibrasi terpisah dari gold dan silver. Gold/kalibrasi tidak boleh masuk
  pelabelan silver. Contoh prompt hanya dari kalibrasi; pilih model di validasi.
- Normalisasi slang khusus TF-IDF B1 belum diterapkan di sini dan perlu
  ditambahkan di pipeline B1. `text_model` belum memakai kamus slang.

## Keluaran lokal

| File | Isi |
|---|---|
| `data/processed/reviews_clean.csv` | 32.843 ulasan, dua versi teks, penanda pool |
| `data/annotations/split.csv` | 32.035 ID dan split; tanpa label |
| `data/annotation_workspace/kalibrasi_<nama>.csv` | 50 ulasan sama per anggota; label kosong |
| `data/annotation_workspace/gold_<nama>.csv` | 275 tugas per anggota; label kosong |
| `data/annotation_workspace/manifest.json` | Hash sumber, teks, penugasan |

Gold: 800 ulasan unik (500 dilabel sekali, 300 uji dilabel dua orang).
1.100 penugasan gold dibagi rata 275 per anggota, ditambah 50 kalibrasi.
Gold dikerjakan setelah panduan kalibrasi disepakati. Clean dan lembar teks
tetap lokal; split tanpa teks boleh dibagikan bersama kode. Data asli utuh.

## Reproduksi

```text
python -m pip install -r requirements.txt
python src/preprocess.py --clean tmp/reproduce/reviews_clean.csv --split tmp/reproduce/split.csv --report tmp/reproduce/report
python src/annotation.py prepare --reviews tmp/reproduce/reviews_clean.csv --split tmp/reproduce/split.csv --workspace data/annotation_workspace/reproduce
python -m unittest discover -s tests -v
```

Kode menolak menimpa hasil. Gunakan folder baru setiap reproduksi. Cocokkan
hash clean/split dengan summary; jangan mengganti split anotasi diam-diam.
15 tes lulus (8 anotasi, 7 preprocessing/integrasi) pada Python 3.12.14.
Target repo tetap Python 3.14, belum diuji lokal pada versi tersebut.

## Berikutnya

Isi kalibrasi mandiri, audit kesepakatan, bahas perbedaan, revisi panduan
bersama, lalu isi gold. Kappa/gold final menunggu label manusia lengkap dan
penyelesaian perbedaan. Ikuti
[alur anotasi](../../../docs/project/annotation-workflow.md).
