# Sumber eksternal

File di folder ini diunduh terpisah dan tidak diunggah ke repository.

| File | Dipakai oleh | Cara mendapatkan |
|---|---|---|
| `colloquial-indonesian-lexicon.csv` | Normalisasi slang B1 (`src/text_features.py`) | `curl -L -o data/external/colloquial-indonesian-lexicon.csv https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv` |
| `cc.id.300.vec` | Embedding BiLSTM B4 (`src/model_bilstm.py`) | Unduh `cc.id.300.vec.gz` dari https://fasttext.cc/docs/en/crawl-vectors.html lalu ekstrak (sekitar 1,2 GB terkompresi) |

Kamus slang (Salsabila dkk., 2018) tidak mencantumkan lisensi di
repositorinya, jadi hanya dirujuk dan diunduh, tidak didistribusikan ulang.
Diunduh 10 November 2026: 15.396 baris, 4.331 slang unik.
