# Keputusan metode

Ditetapkan 3 November 2026 setelah topik disetujui kelompok, lalu diubah
6 November 2026 mengikuti [masukan dosen](#masukan-dosen-6-november-2026).
Setiap keputusan disertai alasan dan bukti. Jika keputusan berubah, catat di
bagian [Riwayat](#riwayat) beserta eksperimen yang perlu diulang.

## Ringkasan

| Bagian | Keputusan |
|---|---|
| Bentuk tugas | ACSA multi-aspek: satu ulasan bisa memuat beberapa aspek, masing-masing dengan sentimennya sendiri |
| Label latih dan validasi | 400 + 100 ulasan diberi label oleh LLM, lalu diverifikasi dan dikoreksi manusia |
| Label uji | 300 ulasan dilabeli manual oleh dua orang tanpa melihat label LLM |
| Data latih | Sama untuk semua model: 400 ulasan latih terverifikasi |
| LLM pra-label | Gemini Flash melalui kuota gratis Gemini API; cadangan model lokal `qwen3.5:4b` lewat Ollama |
| Model yang dibandingkan | TF-IDF + Logistic Regression, Linear SVM, Naive Bayes; BiLSTM + fastText; IndoBERT-p1 base dan large; Gemini dan `qwen3.5:4b` langsung |
| Encoder | `indobenchmark/indobert-base-p1` (utama) dan `indobenchmark/indobert-large-p1`, klasifikasi sentence-pair (ulasan, aspek) |
| Pelaporan | Semua metrik dilaporkan keseluruhan dan per aspek untuk setiap model |
| Preprocessing | 13 aturan di bawah; tanpa stopword removal, tanpa stemming |
| Pembagian data | 50 kalibrasi, 400 latih, 100 validasi, 300 uji, sisanya tanpa label; seed 42 |
| Python | 3.14; PyTorch CUDA dari indeks PyTorch |

## Masukan dosen 6 November 2026

| Masukan | Keputusan kelompok |
|---|---|
| Data latih disamakan; aspek dari LLM tetapi diverifikasi | Semua model dilatih pada data yang sama. Label latih dan validasi dibuat LLM lalu diverifikasi manusia. Set uji tetap dilabeli manual tanpa label LLM |
| Pakai IndoBERT, bukan IndoBERTweet, karena IndoBERTweet khusus Twitter | Encoder diganti `indobenchmark/indobert-base-p1` |
| Aspeknya single atau multi? | Multi-aspek. Lihat [bentuk tugas](#bentuk-tugas) |
| Tambahan algoritma/LLM per aspek | (a) Hasil setiap model dilaporkan per aspek. (b) Pembanding ditambah: Linear SVM dan Naive Bayes di samping Logistic Regression, BiLSTM, IndoBERT large, serta dua LLM. Lihat [model yang dibandingkan](#model-yang-dibandingkan) |

Akibatnya, skema silver lama (P1: IndoBERTweet dilatih dengan label LLM
tanpa verifikasi; P2: silver lalu gold) tidak dipakai. Ulasan di luar set
berlabel tidak dilabeli LLM untuk pelatihan dan hanya dipakai untuk analisis
per versi.

Pertanyaan penelitian setelah perubahan ini (menggantikan RQ1 dan RQ2 di
[usulan week 10](../week-10/README.md#pertanyaan-penelitian)):

- RQ1: Seberapa sesuai label LLM dengan label manual set uji (Cohen's kappa,
  F1), dan berapa persen label LLM dikoreksi saat verifikasi?
- RQ2: Bila dilatih pada data terverifikasi yang sama, model mana yang
  terbaik secara keseluruhan dan per aspek: TF-IDF (LR, SVM, NB), BiLSTM,
  IndoBERT base dan large, atau LLM yang dipakai langsung?
- RQ3: Tidak berubah.

## Bentuk tugas

Tugasnya aspect category sentiment analysis (ACSA) multi-aspek. Setiap ulasan
mendapat label untuk keenam aspek sekaligus. Satu ulasan bisa memuat
beberapa aspek dengan sentimen berbeda, dan aspek yang tidak dibahas diberi
`tidak_disebut`.

Contoh: "setiap mau login gangguan trus! sertifikat gabisa di download!"
memuat `akun_login` negatif dan `fitur_kesehatan` negatif.

Bukti dari data: pada pool 32.035 ulasan, 14,5% memuat kata kunci dari dua
aspek khusus atau lebih (12,3% dua aspek, 2,2% tiga aspek atau lebih). Ini
perkiraan kata kunci, bukan label.

Semua model menangani multi-aspek dengan cara yang sama: setiap aspek
diklasifikasi ke empat label. Model TF-IDF memakai satu classifier per aspek.
IndoBERT memakai sentence-pair (ulasan, aspek), jadi satu ulasan menjadi enam
pasangan. LLM mengeluarkan keenam label sekaligus dalam JSON.

## Alur label

1. Kalibrasi: empat anggota melabeli 50 ulasan yang sama secara manual, lalu
   panduan anotasi diperbarui. Contoh few-shot prompt diambil dari sini.
2. Pra-label LLM: LLM pra-label melabeli 400 ulasan latih dan 100 ulasan
   validasi. LLM yang sama juga melabeli 300 ulasan uji, tetapi hasilnya
   hanya dipakai sebagai prediksi pembanding, tidak ditunjukkan ke anotator.
3. Verifikasi: setiap ulasan latih dan validasi diperiksa satu anggota. Label
   LLM disetujui atau dikoreksi. Label LLM asli dan label akhir disimpan.
   Lembar verifikasi memakai dua langkah per aspek: tandai `setuju` atau
   `salah`, lalu isi label pengganti hanya untuk yang `salah`. Penelitian
   menunjukkan pemeriksa lebih jarang mengoreksi bila setiap koreksi wajib
   langsung disertai pengganti. Waktu verifikasi per ulasan juga dicatat.
4. Set uji: dua anggota melabeli setiap ulasan uji secara mandiri tanpa label
   LLM. Perbedaan diselesaikan anggota ketiga. Cohen's kappa dihitung sebelum
   adjudikasi.

Alasan set uji tidak memakai label LLM: pemeriksa cenderung mengikuti label
yang sudah tersedia (anchoring). Jika set uji diturunkan dari label LLM,
evaluasi akan menguntungkan LLM dan model yang dilatih dari label LLM.

Tingkat koreksi, yaitu persentase sel latih dan validasi yang diubah
pemeriksa, dilaporkan per aspek sebagai ukuran kualitas label LLM, bersama
persentase ulasan yang diterima utuh dan waktu verifikasi. Ukuran
utama kualitas LLM tetap skornya pada set uji manual.

## Spesifikasi laptop acuan

Laptop Efraim, diperiksa 3 November 2026: Intel Core i5-13500HX (14 core,
20 thread), RAM 7,7 GB, NVIDIA GeForce RTX 4050 Laptop 6 GB VRAM, driver
610.74, ruang kosong C: 73 GB dan D: 143 GB.

RAM 7,7 GB dan VRAM 6 GB membatasi model lokal ke kelas 4B. Model 8B pada
kuantisasi 4-bit membutuhkan sekitar 5 GB VRAM ditambah konteks, sehingga
tidak muat sepenuhnya di GPU dan akan melimpah ke RAM yang juga kecil.

## LLM untuk pra-label dan pembanding

### Kebutuhan

- 800 ulasan per LLM: 400 latih dan 100 validasi untuk pra-label, serta 300
  uji sebagai prediksi pembanding (B3). Kalibrasi tidak dilabeli LLM karena
  menjadi sumber contoh few-shot.
- Satu permintaan API berisi 20 ulasan dan contoh few-shot. Perkiraan
  sekitar 3.000 token per permintaan, jadi 40 permintaan dan sekitar
  120.000 token per LLM.
- Keluaran JSON yang mengikuti skema, agar tidak ada label di luar empat
  pilihan.

### Pilihan yang diperiksa

Tabel ini disusun untuk rancangan awal yang membutuhkan sekitar 600
permintaan. Rancangan sekarang hanya butuh 40 permintaan per LLM, jadi
kuota gratis semua pilihan cukup.

| Pilihan | Batas gratis (sumber sekunder, Nov 2026) | Waktu untuk 600 permintaan | Catatan |
|---|---|---|---|
| Gemini API, Flash / Flash-Lite | Tidak dipublikasikan resmi; laporan 250-1.500 permintaan/hari untuk Flash, sekitar 500 untuk Flash-Lite | 1-3 hari | Mendukung JSON schema. Konten kuota gratis dapat dipakai Google untuk pengembangan produk |
| Groq, `gpt-oss-120b` | 1.000 permintaan/hari, 200.000 token/hari | Sekitar 9 hari karena batas token | Model terbuka |
| Groq, `llama-3.1-8b-instant` | 14.400 permintaan/hari, 500.000 token/hari | Sekitar 4 hari | Model kecil, tidak lebih baik dari model lokal |
| OpenRouter, model `:free` | 50 permintaan/hari tanpa pembelian kredit | Sekitar 12 hari | 1.000/hari setelah membeli kredit 10 USD |
| Lokal, Ollama `qwen3.5:4b` | Tanpa batas | Sekitar 7,5 jam (diukur) | 3,3 GB, 3,7 GB VRAM terpakai |
| Lokal, SEA-LION v4 4B (Gemma) | Tanpa batas | Tidak diukur | Dilatih lanjut untuk bahasa Asia Tenggara termasuk Indonesia; gagal dipasang saat uji |

### Keputusan

Pra-label: Gemini Flash dengan kuota gratis. Pakai model Flash terbaru yang
tercantum gratis di halaman rate limit AI Studio. Catat ID model persis dan
tanggal pemakaian.

Alasan:

1. Model terbesar yang tersedia tanpa biaya. Pada studi ABSA multibahasa
   zero-shot, model besar (GPT-4o) jauh di atas model 7-9B; rata-rata
   seluruh model prompting juga masih di bawah model fine-tuned (41,8 vs
   68,9 micro-F1). Pra-label yang lebih akurat berarti lebih sedikit
   koreksi saat verifikasi.
2. 40 permintaan selesai dalam satu hari dengan kuota gratis.
3. Mendukung JSON schema, sehingga label selalu valid.
4. Tidak membebani laptop dengan RAM 7,7 GB.

Pembanding: `qwen3.5:4b` lokal lewat Ollama melabeli 300 ulasan uji dengan
prompt yang sama (LLM besar lewat API vs LLM kecil lokal). Jika Gemini tidak
bisa dipakai, `qwen3.5:4b` menjadi LLM pra-label.

LLM pra-label tidak dipilih dengan set validasi. Label validasi berasal dari
verifikasi label LLM tersebut, jadi perbandingan pada set validasi akan
menguntungkan LLM itu. Kedua LLM hanya dibandingkan pada set uji manual.

### Risiko

| Risiko | Penanganan |
|---|---|
| Batas kuota gratis berubah atau tidak cukup | Simpan progres per batch; lanjutkan dengan model lokal |
| Pemeriksa mengikuti label LLM yang salah (anchoring) | Set uji dilabeli tanpa label LLM; tingkat koreksi dilaporkan; sebagian ulasan latih diperiksa ulang anggota lain jika waktu cukup |
| Teks kuota gratis dapat dibaca dan dipakai Google | Hanya teks ulasan publik yang sudah disamarkan; tanpa nama pengguna. Disebutkan di laporan |
| Model tertutup bisa berubah | Simpan respons mentah (`llm_<model>.jsonl`), ID model, tanggal, dan versi prompt |
| Keluaran tidak valid | JSON schema; ulangi permintaan yang gagal maksimal 3 kali |

### Pengaturan

- Temperature 0.
- Prompt sistem: panduan anotasi ringkas dan 8-12 contoh dari set kalibrasi
  (bukan dari ulasan latih, validasi, atau uji). Versi prompt dicatat (`prompt_version`, mulai `v1`).
- Gemini: 20 ulasan per permintaan, keluaran array JSON berisi `reviewId`
  dan enam label.
- Ollama: satu ulasan per permintaan, `format` berisi JSON schema,
  `think: false`, `num_ctx` 2048.
- Kunci API disimpan di `.env` (`GEMINI_API_KEY`), lihat `.env.example`.

### Uji lokal

Uji asap 3 November 2026 di laptop acuan dengan Ollama 0.40.13 dan
`qwen3.5:4b`. Masukan: 30 ulasan pilot acak (minimal 3 kata, seed 42),
prompt zero-shot berisi panduan anotasi, JSON schema.

| Ukuran | Hasil |
|---|---|
| JSON tidak valid | 0 dari 30 |
| VRAM terpakai | 3,7 GB dari 6 GB, 100% di GPU |
| Kecepatan | 2,29 detik per ulasan, 37,5 token/detik |
| Perkiraan 11.850 ulasan (rancangan awal) | Sekitar 7,5 jam |
| Perkiraan 800 ulasan (rancangan sekarang) | Sekitar 31 menit |
| F1 deteksi aspek / F1 pasangan | 0,63 / 0,61 |

Pembanding F1 adalah label yang dibuat asisten untuk uji ini, bukan label
gold. Angka hanya menunjukkan bahwa model kecil bekerja dan di mana
kesalahannya, bukan kualitas akhir.

Pola kesalahan: model menambah aspek yang tidak disebut. "Susah login"
juga diberi `performa` dan `kemudahan_penggunaan` negatif, aspek yang tidak
disebut diberi `netral`, dan `umum` diisi walaupun ada aspek khusus. Aturan
anotasi diperjelas untuk ketiga hal ini, dan prompt v1 harus memuat contoh
few-shot untuk kasus tersebut.

SEA-LION v4 4B (`aisingapore/Gemma-SEA-LION-v4-4B-VL-GGUF`) tidak diuji:
pengambilan model dari Hugging Face lewat Ollama gagal pada tahap manifest.
Model ini tetap menjadi kandidat jika tim berhasil memasangnya.

## Encoder

### Keputusan

`indobenchmark/indobert-base-p1` dengan klasifikasi sentence-pair. Masukan
berupa pasangan (teks ulasan, deskripsi aspek), keluaran salah satu dari
empat label. Satu ulasan menghasilkan enam pasangan. Versi large
(`indobenchmark/indobert-large-p1`, B2-L) dilatih dengan cara yang sama
sebagai pembanding; lihat [model yang dibandingkan](#model-yang-dibandingkan).

Alasan memilih IndoBERT-p1:

1. Masukan dosen. IndoBERTweet dilatih lanjut khusus pada tweet, sedangkan
   data kami ulasan aplikasi.
2. IndoBERT-p1 dilatih pada Indo4B, korpus bahasa Indonesia sekitar 4 miliar
   kata dari berbagai sumber formal dan informal, termasuk media sosial.
   Slang ulasan seperti `gak`, `yg`, dan `udah` tetap tercakup.
3. Model ini paling sering dipakai pada studi ABSA bahasa Indonesia dan
   menjadi acuan benchmark IndoNLU, sehingga hasil kami mudah dibandingkan.
4. Tokenizer IndoBERT-p1 mengubah teks ke huruf kecil, sesuai aturan
   preprocessing 7.
5. Diukur 6 November 2026 pada `text_model` pool 32.035 ulasan: median 16
   token, persentil 99 sebanyak 85, persentil 99,9 sebanyak 113, maksimum
   404. Hanya 6 ulasan lebih dari 140 token. Panjang 160 token mencakup
   hampir semua ulasan ditambah deskripsi aspek (2-3 token).

Alasan sentence-pair: studi ABSA ulasan Indonesia dengan IndoBERT (BEEI)
mendapat hasil terbaik dengan sentence-pair dibanding single-sentence.
Deskripsi aspek dalam masukan juga membantu ketika data latih hanya 400
ulasan.

## Model yang dibandingkan

Diputuskan 6 November 2026 dari perbandingan penelitian di
[tinjauan pustaka](literature-review.md#4-perbandingan-algoritma).

Semua model dilatih pada 400 ulasan latih terverifikasi yang sama, memakai
set validasi yang sama untuk memilih konfigurasi, dan diuji pada 300 ulasan
uji manual yang sama.

| Kode | Kelompok | Model | Masukan | Data latih |
|---|---|---|---|---|
| B1-LR | Klasik | TF-IDF + Logistic Regression | `text_model` + normalisasi slang | Latih terverifikasi (400) |
| B1-SVM | Klasik | TF-IDF + Linear SVM | `text_model` + normalisasi slang | Latih terverifikasi (400) |
| B1-NB | Klasik | TF-IDF + Multinomial Naive Bayes | `text_model` + normalisasi slang | Latih terverifikasi (400) |
| B4 | Deep learning tanpa pretraining bahasa | BiLSTM + embedding fastText `cc.id.300` | `text_model` | Latih terverifikasi (400) |
| B2 | Transformer (utama) | IndoBERT-p1 base sentence-pair | `text_model` | Latih terverifikasi (400) |
| B2-L | Transformer | IndoBERT-p1 large sentence-pair | `text_model` | Latih terverifikasi (400) |
| B3-Gemini | LLM | Gemini Flash, few-shot | `text_llm` | Tanpa pelatihan; contoh dari kalibrasi |
| B3-Qwen | LLM | `qwen3.5:4b` lokal, few-shot | `text_llm` | Tanpa pelatihan; contoh dari kalibrasi |

Kode B4 diberikan setelah B1-B3 agar kode lama tidak berubah.

### Alasan pemilihan

1. Empat kelompok menjawab pertanyaan berbeda: seberapa jauh pendekatan
   kata (B1), deep learning tanpa model bahasa (B4), model bahasa pretrained
   (B2), dan LLM tanpa pelatihan (B3) dapat bekerja dengan 400 ulasan latih
   yang sama.
2. IndoBERT-p1 base menjadi model utama. Pada benchmark multi-aspek IndoNLU
   (CASA, 810 ulasan latih), IndoBERT base mendapat F1 93,23, di atas XLM-R
   base (91,71) dan mBERT (72,23). Pada studi aplikasi Indonesia, IndoBERT
   juga terbaik untuk Access by KAI (2026) dan Mobile JKN (2025).
3. IndoBERT-p1 large mendapat skor tertinggi pada CASA (95,69). Model ini
   memakai kode training yang sama, jadi tambahan kerjanya kecil. Ukurannya
   sekitar 335 juta parameter dan tidak muat untuk training di 6 GB VRAM,
   sehingga dijalankan di Google Colab (GPU T4 16 GB).
4. BiLSTM sering dipakai di studi sentimen ulasan Indonesia (Shopee, Spotify,
   pembanding pada Access by KAI). Embedding fastText `cc.id.300` dilatih
   pada Common Crawl bahasa Indonesia dan memuat slang. Pada IndoNLU, model
   dengan embedding ini tertinggal 14 poin dari IndoBERT base pada CASA.
   Selisih antara B4 dan B2 menunjukkan manfaat pretraining.
5. TF-IDF + SVM tetap wajib. Pada ulasan Tokopedia 2025, Linear SVM
   mengalahkan IndoBERT (macro-F1 0,5510 vs 0,5088) ketika IndoBERT dilatih
   dengan data lebih sedikit. LR dan NB dipakai karena umum di studi
   sentimen SATUSEHAT dan sangat cepat.
6. LLM langsung: Hellwig dkk. (2025) menemukan LLM few-shot mendekati model
   fine-tuned pada tugas berbasis kategori aspek.

### Kandidat yang tidak dipakai

| Kandidat | Alasan |
|---|---|
| IndoBERTweet | Masukan dosen: khusus Twitter |
| XLM-R base | Di bawah IndoBERT base pada CASA dan HoASA; dosen meminta IndoBERT |
| XLM-R large | Sekitar 560 juta parameter; tidak muat di laptop dan berat di Colab gratis. Selisih dengan IndoBERT large kecil dan tidak konsisten (CASA lebih rendah, HoASA lebih tinggi) |
| mBERT | Jauh di bawah IndoBERT pada CASA (72,23) |
| IndoBERT-lite | Di bawah IndoBERT base pada CASA dan HoASA |
| NusaBERT | Fokus pada bahasa daerah; keunggulan atas IndoBERT kecil dan tidak konsisten pada klasifikasi |
| SetFit | Dirancang untuk 8-16 contoh per kelas; dengan 400 ulasan fine-tuning biasa cukup; belum ada bukti untuk ABSA |
| BiLSTM dengan embedding IndoBERT | Mencampur pretraining Transformer ke kelompok B4, sehingga perbandingan antarkelompok tidak bersih |

### Pengaturan model klasik

Model TF-IDF memakai satu classifier empat kelas per aspek. Fitur TF-IDF
kata 1-2 gram dengan `sublinear_tf`. Logistic Regression dan Linear SVM
memakai `class_weight="balanced"` karena label positif dan netral jarang.
Parameter regularisasi (`C` untuk LR dan SVM, `alpha` untuk NB) dipilih
dari {0,1; 1; 10} dan {0,1; 0,5; 1} dengan F1 pasangan pada set validasi.

### Pengaturan BiLSTM

| Parameter | Nilai | Alasan |
|---|---|---|
| Token | Kata dan tanda baca dari `text_model`, maksimal 128 token | Diukur pada pool: median 14, persentil 99 sebanyak 78, persentil 99,9 sebanyak 102; hanya 7 ulasan lebih dari 128 |
| Embedding | fastText `cc.id.300.vec`, 300 dimensi, dibekukan; kata di luar kosakata memakai satu vektor `[UNK]` yang dilatih | 400 ulasan terlalu sedikit untuk melatih embedding. Hanya kata yang muncul di pool yang dimuat, agar RAM cukup |
| Encoder | BiLSTM 1 lapis, 128 unit per arah, dropout 0,5 | Ukuran kecil untuk data kecil |
| Keluaran | Max-pooling, lalu enam kepala linear, masing-masing empat kelas | Multi-aspek: encoder dipakai bersama, setiap aspek diklasifikasi sendiri |
| Loss | Cross-entropy berbobot kelas per aspek, dijumlah untuk enam aspek | Label positif dan netral jarang |
| Optimizer | Adam, learning rate 1e-3, batch 32 | Pengaturan umum untuk LSTM |
| Epoch | Maksimal 30, early stopping patience 3 dengan F1 pasangan validasi | Training cepat; berhenti saat validasi tidak naik |
| Seed | 42, 43, 44 | Sama dengan IndoBERT |

Persentase kata di luar kosakata fastText dihitung dan dilaporkan saat
embedding dimuat.

### Hiperparameter IndoBERT

| Parameter | B2 (base) | B2-L (large) | Alasan |
|---|---|---|---|
| Panjang maksimum | 160 token, pemotongan hanya pada teks ulasan | Sama | Persentil 99,9 ulasan 113 token ditambah deskripsi aspek |
| Learning rate | 2e-5 | 1e-5 | Nilai umum; model large lebih tidak stabil pada data kecil |
| Batch | 16 | 8, akumulasi gradien 2 (efektif 16) | B2 muat di 6 GB VRAM dengan fp16; B2-L di Colab T4 |
| Epoch | Maksimal 10, early stopping patience 2 | Sama | Data kecil, 2.400 pasangan |
| Warmup / weight decay | 10% / 0,01 | Sama | Pengaturan standar |
| Kriteria early stopping | F1 pasangan pada set validasi | Sama | Sama dengan metrik utama |
| Seed | 42, 43, 44 | Sama | Data kecil; laporkan rata-rata dan simpangan baku |

B2 dapat dijalankan di laptop acuan atau Google Colab. B2-L dijalankan di
Google Colab.

### Penentuan model terbaik

1. Skor utama: F1 pasangan pada set uji. Untuk model dengan tiga seed,
   pakai rata-rata ketiganya. Model TF-IDF dan LLM (temperature 0)
   dijalankan sekali.
2. Uji beda: paired bootstrap 1.000 kali atas ulasan uji, seed 42. Pada
   setiap sampel ulang, hitung F1 pasangan setiap model (rata-rata seed bila
   ada tiga). Hitung interval 95% selisih antara model teratas dan setiap
   model lain. Selisih dianggap nyata jika interval tidak memuat nol. Dengan
   300 ulasan uji, selisih kecil kemungkinan tidak nyata, dan hal itu
   dilaporkan apa adanya.
3. Per aspek: laporkan model terbaik untuk setiap aspek berdasarkan
   macro-F1 sentimen dan F1 deteksi aspek.
4. Untuk analisis per versi (RQ3), pakai model dengan F1 pasangan uji
   tertinggi. Jika model itu LLM, Gemini dipakai bila kuota cukup untuk
   sekitar 1.600 permintaan. Jika tidak, pakai model terlatih terbaik.
   Pilihan dan alasannya dicatat.

## Preprocessing

Ada dua versi teks. `text_llm` dikirim ke LLM. `text_model` dipakai TF-IDF
dan encoder.

| No | Aturan | Berlaku untuk | Alasan dan bukti |
|---|---|---|---|
| 1 | Buang ulasan sebelum 1 Maret 2023 | Semua | Sebelum tanggal itu aplikasi masih PeduliLindungi. 15.000 ulasan terbaru dimulai 17 Juli 2023, jadi aturan ini berjaga-jaga |
| 2 | Buang ulasan kosong; rapikan spasi dan baris baru | Semua | Teks kosong tidak bisa dilabeli |
| 3 | Buang ulasan kurang dari 3 kata | Semua | Kata kunci aspek muncul pada 1% ulasan 1 kata, 6% ulasan 2 kata, 12% ulasan 3 kata, 25% ulasan 4 kata. Ulasan 3 kata masih membawa aspek, misalnya "ga bisa daftar". Menyisakan 83,3% |
| 4 | Buang duplikat persis setelah huruf kecil dan spasi dirapikan; simpan yang paling awal | Data latih dan evaluasi | 1.676 dari 15.000 ulasan duplikat, didominasi "bagus" dan "mantap". Duplikat di latih dan uji sekaligus menggelembungkan skor |
| 5 | Samarkan NIK 16 digit `[NIK]`, nomor telepon `[TELEPON]`, email `[EMAIL]`, URL `HTTPURL` | Semua | Tidak ditemukan pada 15.000 ulasan, tetapi teks dikirim ke API pihak ketiga. Biaya aturan ini kecil |
| 6 | Pertahankan huruf besar dan emoji | `text_llm` | LLM memahami emoji dan huruf kapital sebagai penekanan |
| 7 | Huruf kecil | `text_model` | Tokenizer IndoBERT-p1 memakai huruf kecil |
| 8 | Ubah emoji menjadi teks bahasa Indonesia (`emoji.demojize(language="id")`, garis bawah menjadi spasi) | `text_model` | 4,7% ulasan memakai emoji. Tokenizer IndoBERT-p1 mengubah emoji menjadi `[UNK]`; contoh 👍 menjadi "jempol ke atas" |
| 9 | Huruf berulang 3 kali atau lebih menjadi 2 ("lamaaaaa" menjadi "lamaa") | `text_model` | 3,0% ulasan. Dua huruf menjaga kata seperti "maaf" dan tetap menandai penekanan |
| 10 | Tanpa stopword removal | Semua | 34,9% ulasan memuat negasi (tidak, gak, ga, belum, bukan). Daftar stopword umum memuat kata negasi, sehingga sentimen bisa terbalik |
| 11 | Tanpa stemming | Semua | "terdaftar" (sudah terdaftar, keluhan data) dan "daftar" (mendaftar) bermakna berbeda untuk aspek `registrasi_data`. Encoder memakai subword |
| 12 | Normalisasi slang dengan `colloquial-indonesian-lexicon.csv` (Salsabila dkk., 2018) | Hanya B1-LR, B1-SVM, B1-NB (TF-IDF) | TF-IDF menganggap "gak", "ga", "gk", "tdk" sebagai fitur berbeda (lebih dari 500 kemunculan pada pilot). Encoder dan LLM sudah mengenal slang; kamus bisa salah ganti |
| 13 | Tanpa filter bahasa | Semua | Hanya 1 dari 2.000 ulasan pilot terdeteksi berbahasa Inggris |

Tanda baca dipertahankan untuk encoder dan LLM. Balasan pengembang tidak
dipakai sebagai masukan.

Untuk analisis per versi (RQ3), duplikat tidak dibuang karena tiap ulasan
berasal dari pengguna berbeda. Aturan 1, 2, 3, dan 5 tetap berlaku.

## Pembagian data

1. Terapkan aturan preprocessing. Hasilnya `pool` (12.297 ulasan pada uji
   15.000 ulasan).
2. Dengan seed 42, ambil 50 ulasan kalibrasi acak berstrata rating.
3. Dari sisa `pool`, ambil 800 ulasan gold acak berstrata rating
   proporsional, lalu bagi 400 latih, 100 validasi, 300 uji, juga berstrata
   rating.
4. Sisanya diberi nama `silver` di `split.csv`. Sejak 6 November 2026
   ulasan ini tidak dilabeli untuk pelatihan dan hanya dipakai untuk
   analisis per versi. Nama split tidak diubah agar `split.csv` dan kode
   anotasi tetap sama.
5. Simpan di `data/annotations/split.csv`.

`gold_train` dan `gold_val` di `split.csv` berisi ulasan latih dan validasi
yang labelnya diverifikasi dari label LLM. `gold_test` berisi ulasan uji
yang dilabeli manual tanpa label LLM.

Proporsi rating di `pool`: bintang 1 75,7%, 2 6,5%, 3 4,4%, 4 2,4%, 5 11,0%.
Sampel proporsional dipilih agar skor uji mencerminkan data nyata. Jumlah
label per aspek dan sentimen dilaporkan, karena sentimen positif akan
jarang.

## Format file

| File | Kolom |
|---|---|
| `data/raw/com.telkom.tracencare_reviews.csv` | Keluaran `src/scrape_reviews.py` |
| `data/processed/reviews_clean.csv` | `reviewId`, `at`, `score`, `reviewCreatedVersion`, `text_llm`, `text_model`, `n_words`, `in_pool` |
| `data/annotations/split.csv` | `reviewId`, `split` |
| `data/annotations/gold_<nama>.csv`, `gold.csv` | `reviewId`, (`annotator`), enam kolom aspek; label manual set uji |
| `data/annotations/llm_<model>.csv` | `reviewId`, `model`, `prompt_version`, enam kolom aspek |
| `data/annotations/verified.csv` | `reviewId`, `verifier`, `model`, `prompt_version`, enam kolom aspek akhir; label LLM asli tetap di `llm_<model>.csv` |
| `results/predictions/<model>_<seed>.csv` | `reviewId`, `model_code`, `seed`, enam kolom aspek |
| `results/metrics/<model>_<seed>.json` | Nilai metrik dan konfigurasi run |

Enam kolom aspek: `akun_login`, `registrasi_data`, `fitur_kesehatan`,
`performa`, `kemudahan_penggunaan`, `umum`. Nilainya `tidak_disebut`,
`positif`, `negatif`, atau `netral`.

## Definisi metrik

- F1 pasangan (utama): micro-F1 atas tuple (ulasan, aspek, sentimen) yang
  labelnya bukan `tidak_disebut`. Prediksi benar jika aspek dan sentimen sama.
- F1 deteksi aspek: micro- dan macro-F1 atas pasangan (ulasan, aspek) yang
  labelnya bukan `tidak_disebut`, tanpa melihat sentimen.
- Macro-F1 sentimen per aspek: dihitung pada ulasan yang aspeknya disebut
  dalam label manual set uji.
- Cohen's kappa per aspek atas empat label: antar-anotator pada set uji dan
  LLM vs label manual set uji.
- Tingkat koreksi verifikasi: persentase sel latih dan validasi yang diubah
  pemeriksa, per aspek dan keseluruhan.
- Efisiensi: detik per 1.000 ulasan saat inferensi.
- Semua metrik dihitung keseluruhan dan per aspek untuk setiap model. Tabel
  utama berisi F1 pasangan dan macro-F1 sentimen per aspek untuk kedelapan model.

## Analisis per versi dan konsistensi rating

- Versi: kolom `reviewCreatedVersion`. Ulasan tanpa versi dikeluarkan dari
  analisis ini (73,8% terisi pada 15.000 ulasan).
- Hanya versi dengan minimal 50 ulasan (54 versi pada uji 15.000 ulasan).
- Proporsi negatif per aspek per versi: jumlah ulasan dengan aspek tersebut
  `negatif` dibagi jumlah ulasan pada versi itu, dengan interval kepercayaan
  Wilson 95%.
- Rating bertentangan: bintang 4-5 dengan minimal satu aspek negatif dan
  tanpa aspek positif, atau bintang 1-2 dengan minimal satu aspek positif
  dan tanpa aspek negatif.
- Memakai prediksi model terbaik pada seluruh ulasan setelah aturan 1, 2,
  3, dan 5.

## Lingkungan

- Python 3.14 untuk lokal dan CI. Google Colab memakai versinya sendiri
  (dilaporkan 3.13 sejak Agustus 2026); periksa dengan `!python --version`.
- Paket model terverifikasi tersedia untuk Python 3.14 Windows pada
  3 November 2026: `torch` 2.15.0 (CPU, PyPI), `transformers` 5.22.1,
  `scikit-learn` 1.9.1, `pandas` 3.1.0, `datasets` 5.1.0,
  `accelerate` 1.15.0.
- PyTorch dengan GPU NVIDIA:

```text
python -m pip install torch --index-url https://download.pytorch.org/whl/cu130
```

  Versi yang tersedia saat diperiksa: `torch` 2.14.1+cu130.
- Ollama 0.40.13 untuk model lokal.

## Riwayat

| Tanggal | Perubahan | Alasan | Eksperimen yang perlu diulang |
|---|---|---|---|
| 3 Nov 2026 | Keputusan awal | Topik disetujui kelompok | - |
| 4 Nov 2026 | Dataset final: semua ulasan sejak 1 Maret 2023 (39.995 baris, pool 32.035), menggantikan 15.000 ulasan uji | Permintaan kelompok untuk memakai seluruh data era SATUSEHAT | Belum ada eksperimen. Angka pool dan beban LLM di dokumen ini masih berdasarkan uji 15.000 ulasan; silver menjadi sekitar 31.000 ulasan (perkiraan sekitar 1.600 permintaan Gemini atau sekitar 20 jam dengan model lokal) |
| 6 Nov 2026 | Masukan dosen: data latih sama untuk semua model dari label LLM terverifikasi; IndoBERT-p1 menggantikan IndoBERTweet; tugas dinyatakan multi-aspek; tambahan Linear SVM, Naive Bayes, dan dua LLM; hasil per aspek. P1, P2, dan pelabelan silver dihapus | Masukan dosen | Belum ada eksperimen. Panjang token diukur ulang dengan tokenizer IndoBERT-p1 |
| 6 Nov 2026 | Susunan akhir delapan model: B1-LR, B1-SVM, B1-NB, B4 BiLSTM + fastText, B2 IndoBERT-p1 base, B2-L IndoBERT-p1 large, B3-Gemini, B3-Qwen; aturan penentuan model terbaik dengan paired bootstrap | Perbandingan penelitian di [tinjauan pustaka](literature-review.md) | Belum ada eksperimen |

## Rujukan

Daftar lengkap beserta temuan dan status pemeriksaan ada di
[tinjauan pustaka](literature-review.md).

- Zero-shot multilingual ABSA dengan LLM: https://arxiv.org/abs/2412.12564
- LA-ABSA, LREC 2026: https://aclanthology.org/2026.lrec-1.632/
- IndoNLU dan IndoBERT: https://arxiv.org/abs/2009.05387
- Model IndoBERT-p1: https://huggingface.co/indobenchmark/indobert-base-p1 dan https://huggingface.co/indobenchmark/indobert-large-p1
- Vektor fastText `cc.id.300`: https://fasttext.cc/docs/en/crawl-vectors.html
- IndoBERTweet (keputusan awal): https://arxiv.org/abs/2109.04607
- ABSA ulasan Indonesia sentence-pair (BEEI): https://beei.org/index.php/EEI/article/view/8032
- SEA-LION v4: https://huggingface.co/collections/aisingapore/sea-lion-v4
- Ketentuan tambahan Gemini API: https://ai.google.dev/gemini-api/terms
- Batas OpenRouter: https://openrouter.ai/docs/api/reference/limits
- Model Ollama untuk 6 GB VRAM: https://localaimaster.com/vram/best-ollama-models-6gb-vram
- Kamus slang: https://github.com/nasalsabila/kamus-alay
- PeduliLindungi menjadi SATUSEHAT Mobile: https://covid19.go.id/en/artikel/2023/03/01/mulai-1-maret-2023-pedulilindungi-menjadi-satusehat-mobile
