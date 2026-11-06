# Tinjauan pustaka dan posisi penelitian

Dikumpulkan 6 November 2026 untuk menindaklanjuti masukan dosen. Dokumen ini
mencatat penelitian yang menjadi dasar
[keputusan metode](method-decisions.md), terutama alur label dan pemilihan
algoritma.

Kolom "Diperiksa" menunjukkan sumber angka:

- Abstrak: angka dibaca langsung dari abstrak atau halaman artikel.
- Tabel: angka dibaca dari tabel hasil di naskah.
- Cuplikan: hanya dari cuplikan hasil pencarian. Periksa naskah lengkap
  sebelum dikutip di laporan atau artikel.

## Ringkasan posisi

Belum ditemukan penelitian yang menggabungkan ketiga hal berikut:

1. Label ABSA bahasa Indonesia dari LLM yang diverifikasi manusia, dengan
   tingkat koreksi diukur dan set uji dilabeli tanpa label LLM.
2. ABSA ulasan SATUSEHAT Mobile dengan label acuan manusia.
3. Pelacakan sentimen per aspek antarversi aplikasi.

Penelitian terdekat untuk tiap poin ada di tabel di bawah, beserta
perbedaannya dengan proyek ini.

## 1. Pelabelan dengan bantuan LLM

| Penelitian | Temuan | Dampak untuk proyek | Diperiksa |
|---|---|---|---|
| Schroeder, Roy, & Kabbara (2025), *Just Put a Human in the Loop? Investigating LLM-Assisted Annotation for Subjective Tasks*, Findings of ACL | Eksperimen pra-registrasi dengan 350-410 anotator dan lebih dari 7.000 anotasi. Saran LLM tidak mempercepat kerja, tetapi menaikkan rasa yakin anotator. Anotator banyak mengikuti saran, sebaran label bergeser, dan skor model terlihat lebih tinggi bila label bantuan LLM dipakai untuk evaluasi | Dasar utama keputusan set uji dilabeli tanpa label LLM | Abstrak |
| *Bias in the Loop: How Humans Evaluate AI-Generated Suggestions* (2025), arXiv 2509.08514 | Bila anotator wajib langsung mengisi nilai pengganti untuk setiap koreksi, mereka lebih jarang mengoreksi. Disarankan memisahkan penilaian benar/salah dari pengisian koreksi | Lembar verifikasi memakai dua langkah: tandai setuju/salah, lalu isi label pengganti | Cuplikan |
| LLM-assisted FrameNet annotation (2025), arXiv 2510.25904 | Pra-label hanya sedikit menghemat waktu. Sekitar 6,6% anotasi LLM diterima utuh dan sekitar 19,7% dibuang seluruhnya | Jangan mengklaim verifikasi jauh lebih cepat. Catat waktu verifikasi dan persentase label yang diterima utuh | Cuplikan |
| Hellwig, Fehle, Kruschwitz, & Wolff (2026), *LLM-as-an-Annotator* (LA-ABSA), LREC 2026 | Model ringan yang dilatih dengan label LLM mendapat F1 49,85 pada ASQP Rest16, mendekati prompting Gemma-3-27B (51,10), dengan biaya komputasi jauh lebih rendah. Bahasa yang diuji tidak termasuk Indonesia | Mendukung ide melatih model ringan dari label LLM; proyek ini menambah verifikasi manusia | Abstrak |
| Hellwig, Fehle, Kruschwitz, & Wolff (2025), *Do we still need Human Annotators? Prompting LLMs for Aspect Sentiment Quad Prediction*, arXiv 2502.13044 | LLM few-shot mendekati model fine-tuned pada TASD (68,93 vs 72,76 F1), tetapi masih jauh pada ASQP (51,54 vs 60,39) | LLM langsung (B3) layak menjadi pembanding, tetapi belum tentu menang | Abstrak |
| AnnoABSA (2026), LREC 2026, arXiv 2603.01773 | Alat anotasi ABSA dengan saran LLM berbasis retrieval; keputusan akhir tetap pada manusia | Contoh alat human-in-the-loop untuk ABSA | Cuplikan |

## 2. ABSA ulasan aplikasi bahasa Indonesia

| Penelitian | Data dan metode | Hasil | Perbedaan dengan proyek ini | Diperiksa |
|---|---|---|---|---|
| Pangestu, Christian, & Lestari (2025), JCOMS 5(4), Mobile JKN | 55.688 ulasan Google Play. Aspek dari LDA, pelabelan dibantu Gemini 2.0 Flash. IndoBERT, RoBERTa, DistilBERT multitask | IndoBERT terbaik: akurasi sentimen 96%, aspek 91% | Abstrak tidak menyebut verifikasi manusia atau set uji manual. Proyek ini mengukur akurasi LLM terhadap label manual | Abstrak |
| Alfiana, Doewes, & Widoyono (2026), JUTIF 7(1), Access by KAI | Google Play, label hibrida, IndoBERT multi-label. Pembanding: SVM dan XGBoost + TF-IDF, BiLSTM dengan embedding IndoBERT, mBERT, XLM-R | IndoBERT terbaik pada ketiga tugas. F1 aspek 0,785; F1 sentimen 0,752; F1 gabungan aspek-sentimen 0,549 | Contoh susunan pembanding yang mirip dengan proyek ini. F1 gabungan 0,549 memberi gambaran skor realistis untuk tugas multi-aspek | Abstrak |
| IndoBERT ABSA ulasan hotel bintang lima (2025), Sisfokom | Gemini menyarankan label aspek awal, lalu diperiksa manual. IndoBERT fine-tuned | Macro-F1 0,92, di atas baseline klasik | Alur paling mirip. Perlu diperiksa apakah akurasi LLM dan tingkat koreksi diukur | Cuplikan |
| JESICA (2026), Halodoc, Alodokter, SATUSEHAT Mobile | 1.460 ulasan; LDA untuk aspek, IndoBERT untuk sentimen tiga kelas | Tujuh aspek utama | Tanpa label aspek manusia; SATUSEHAT hanya sebagian kecil data | Cuplikan, sudah dipakai di laporan week 10 |

## 3. Studi sentimen SATUSEHAT Mobile

| Penelitian | Isi | Diperiksa |
|---|---|---|
| Sostech (2025-2026) | 3.000 ulasan 1 Januari-7 November 2025, tiga kelas, IndoBERT | Cuplikan |
| JATI 10(2), April 2026 | Naive Bayes dan SVM dengan SMOTE | Cuplikan |
| JARS (sekitar 2025) | 700 ulasan, regresi logistik; 87% negatif | Cuplikan |
| JATI 7(5), Oktober 2023 | 16.245 ulasan; keluhan alur ribet, bug, dan error | Cuplikan |

Semua studi ini menganalisis sentimen tingkat dokumen, bukan per aspek.

## 4. Perbandingan algoritma

### Benchmark multi-aspek bahasa Indonesia

IndoNLU (Wilie dkk., 2020) memuat dua tugas yang paling mirip dengan proyek
ini. CASA berisi ulasan mobil dengan 6 aspek (810 latih), dan HoASA berisi
ulasan hotel dengan 10 aspek (2.283 latih). Keduanya memberi satu label
sentimen per aspek. Diperiksa dari Tabel 5 naskah (F1):

| Model | CASA | HoASA | SmSA |
|---|---|---|---|
| Transformer tanpa pretraining (scratch) | 67,15 | 76,28 | 67,35 |
| Transformer kecil + embedding fastText-cc-id | 79,02 | 85,32 | 76,92 |
| Transformer kecil + embedding fastText-indo4b | 82,20 | 85,88 | 82,13 |
| mBERT | 72,23 | 84,63 | 84,14 |
| XLM-R base | 91,71 | 91,57 | 91,39 |
| XLM-R large | 92,40 | 94,27 | 92,35 |
| IndoBERT-lite base | 89,68 | 88,07 | 90,85 |
| IndoBERT base | 93,23 | 92,07 | 87,73 |
| IndoBERT large | 95,69 | 93,75 | 92,72 |

Catatan: versi naskah lain melaporkan angka IndoBERT sedikit berbeda.
Kutip versi arXiv yang dipakai.

Pola yang terlihat:

1. Pada data multi-aspek berukuran kecil (CASA, 810 latih), IndoBERT base
   dan large paling tinggi.
2. IndoBERT base di atas XLM-R base pada CASA dan HoASA.
3. Model tanpa pretraining bahasa (scratch dan embedding fastText)
   tertinggal 8-26 poin dari IndoBERT. Baseline IndoNLU ini memakai encoder
   Transformer 2-6 lapis, bukan LSTM, tetapi embedding fastText-cc-id yang
   sama akan dipakai BiLSTM di proyek ini.

### Studi ulasan aplikasi Indonesia

| Penelitian | Hasil | Diperiksa |
|---|---|---|
| Shopee, IndoBERT vs Bi-LSTM (JAIC) | IndoBERT 85,61% vs Bi-LSTM 78,27% (akurasi dan F1, dua kelas) | Cuplikan |
| Tokopedia 2025, LR/SVM/NB vs IndoBERT, arXiv 2605.03439 | Linear SVM macro-F1 0,5510, IndoBERT 0,5088. Penulis menyebut penyebabnya IndoBERT hanya dilatih pada subset data | Abstrak |
| Ulasan ChatGPT di Google Play | 312 ulasan berlabel; hibrida IndoBERT-SVM di atas NB (87%) dan SVM (92%) | Cuplikan |
| Ulasan Spotify Indonesia | BiLSTM di atas ML klasik, dengan catatan data latih tidak setara | Cuplikan |

Pola yang terlihat: IndoBERT biasanya terbaik bila dilatih pada data yang
sama, tetapi SVM bisa menang ketika data latih kecil atau tidak setara.
Karena itu SVM wajib ada sebagai pembanding.

### Kandidat lain

| Kandidat | Temuan | Diperiksa |
|---|---|---|
| NusaBERT (LazarusNLP, 2024) | Turunan IndoBERT dengan bahasa daerah. Sentimen NusaTranslation: NusaBERT-base 77,07 vs IndoBERT-base 75,24. Penulis menyebut sedikit menurun pada beberapa tugas klasifikasi | Cuplikan |
| SetFit (Tunstall dkk., 2022) | Efisien untuk 8-16 contoh per kelas. Untuk ratusan contoh, fine-tuning biasa umumnya cukup. Tidak ditemukan bukti untuk ABSA | Cuplikan |

## 5. Analisis per versi aplikasi

Tidak ditemukan studi 2024-2026 yang melacak sentimen per aspek antarversi
aplikasi. Yang ada adalah tren sentimen per waktu, misalnya alat Appsent
(arXiv 1907.10191), dan studi lama tentang ulasan setelah pembaruan aplikasi.
RQ3 mengisi celah ini.

## Dampak pada keputusan

| Temuan | Keputusan |
|---|---|
| Anchoring pada saran LLM (Schroeder dkk., 2025) | Set uji dilabeli tanpa label LLM |
| Koreksi berkurang bila wajib langsung mengisi pengganti (Bias in the Loop) | Lembar verifikasi dua langkah |
| Pra-label tidak selalu menghemat waktu (FrameNet 2025) | Catat waktu verifikasi dan persentase diterima utuh |
| IndoBERT terbaik pada CASA/HoASA | IndoBERT-p1 base sebagai model utama; IndoBERT-p1 large sebagai pembanding |
| Embedding fastText tertinggal dari model pretrained; BiLSTM umum di studi Indonesia (Shopee, Spotify, KAI) | BiLSTM + fastText cc.id sebagai pembanding deep learning tanpa pretraining bahasa |
| SVM bisa mengalahkan IndoBERT pada data kecil | TF-IDF + LR, SVM, NB tetap dipakai |
| LLM few-shot mendekati model fine-tuned pada tugas kategori (Hellwig dkk., 2025) | Gemini dan `qwen3.5:4b` langsung sebagai pembanding |

## Rujukan

- Schroeder, H., Roy, D., & Kabbara, J. (2025). Just put a human in the loop? Investigating LLM-assisted annotation for subjective tasks. *Findings of ACL 2025*. https://arxiv.org/abs/2507.15821
- Bias in the loop: How humans evaluate AI-generated suggestions. (2025). arXiv. https://arxiv.org/abs/2509.08514
- Evaluating the impact of LLM-assisted annotation in a perspectivized setting: The case of FrameNet annotation. (2025). arXiv. https://arxiv.org/abs/2510.25904
- Hellwig, N. C., Fehle, J., Kruschwitz, U., & Wolff, C. (2026). LLM-as-an-annotator: Training lightweight models with LLM-annotated examples for aspect sentiment tuple prediction. *LREC 2026*, 7955-7972. https://aclanthology.org/2026.lrec-1.632/
- Hellwig, N. C., Fehle, J., Kruschwitz, U., & Wolff, C. (2025). Do we still need human annotators? Prompting large language models for aspect sentiment quad prediction. arXiv. https://arxiv.org/abs/2502.13044
- AnnoABSA: A web-based annotation tool for aspect-based sentiment analysis with retrieval-augmented suggestions. (2026). *LREC 2026*. https://arxiv.org/abs/2603.01773
- Pangestu, A. S., Christian, E., & Lestari, A. (2025). Aspect-based sentiment analysis pada ulasan pengguna aplikasi Mobile JKN menggunakan model berbasis transformer. *JCOMS, 5*(4). https://e-journal.upr.ac.id/index.php/jcoms/article/view/25348
- Alfiana, H. N., Doewes, A., & Widoyono, B. (2026). Aspect-based sentiment analysis of Access by KAI application reviews using IndoBERT for multi-label classification tasks. *JUTIF, 7*(1), 286-306. https://jutif.if.unsoed.ac.id/index.php/jurnal/article/view/5402
- Fine-tuned IndoBERT for aspect-based sentiment analysis of Indonesian five-star hotel reviews. (2025). *Sisfokom*. https://jurnal.atmaluhur.ac.id/index.php/sisfokom/article/download/2491/1359
- Aspect-based sentiment analysis of Indonesian healthcare application reviews using LDA and IndoBERT. (2026). *JESICA*. https://jesica.itsk-soepraoen.ac.id/index.php/jesica/article/view/47
- Analisis sentimen multi-kelas ulasan aplikasi SATUSEHAT. *Sostech*. https://sostech.greenvest.co.id/index.php/sostech/article/download/32787/1914/14211
- *JATI, 10*(2), April 2026. https://ejournal.itn.ac.id/jati/article/download/17629/9306
- Wilie, B., dkk. (2020). IndoNLU: Benchmark and resources for evaluating Indonesian natural language understanding. *AACL-IJCNLP 2020*. https://arxiv.org/abs/2009.05387
- Wongso, W., dkk. (2024). NusaBERT: Teaching IndoBERT to be multilingual and multicultural. arXiv. https://arxiv.org/abs/2403.01817
- Performance comparison of IndoBERT and Bi-LSTM models for sentiment analysis of Shopee app users in Indonesia. *JAIC*. https://jurnal.polibatam.ac.id/index.php/JAIC/article/view/10996
- Zahra, N. Z., dkk. (2026). Benchmarking logistic regression, SVM, naive Bayes, and IndoBERT fine-tuning for sentiment analysis on Indonesian product reviews. arXiv. https://arxiv.org/abs/2605.03439
- Tunstall, L., dkk. (2022). Efficient few-shot learning without prompts (SetFit). arXiv. https://arxiv.org/abs/2209.11055
- Ventirozos, F., Appleby, P., & Shardlow, M. (2025). Exploring zero-shot ACSA with unified meaning representation in chain-of-thought prompting. arXiv. https://arxiv.org/abs/2512.19651
- Grave, E., dkk. (2018). Learning word vectors for 157 languages. *LREC 2018*. https://fasttext.cc/docs/en/crawl-vectors.html
- Appsent: A tool that analyzes app reviews. (2019). arXiv. https://arxiv.org/abs/1907.10191
