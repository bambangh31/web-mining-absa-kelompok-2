# Pratinjau: B1 dilatih dari label Gemini yang belum diverifikasi

Dijalankan 11 November 2026. **Bukan hasil set uji** dan bukan hasil akhir
penelitian.

- Label latih dan validasi: `data/annotations/llm_gemini-3.5-flash-lite.csv`
  (400 `gold_train` + 100 `gold_val`, label Gemini **belum diverifikasi
  manusia**).
- Data penilaian: lembar `Label Manual Sentimen Komentar Satu Sehat.xlsx`
  (label manusia). 10 ulasan latih/validasi dibuang agar tidak bocor,
  jadi yang dinilai 344 ulasan.
- "F1 pasangan validasi" di `metrics/*.json` diukur terhadap label Gemini
  pada `gold_val`, bukan terhadap label manusia.

Perintah:

```text
python src/models_classic.py --labels data/annotations/llm_gemini-3.5-flash-lite.csv --predict-from "Label Manual Sentimen Komentar Satu Sehat.xlsx" --out results/pratinjau_llm
python src/evaluate.py --gold "Label Manual Sentimen Komentar Satu Sehat.xlsx" --exclude-split gold_train,gold_val --out results/pratinjau_llm/evaluasi --pred B1-LR=results/pratinjau_llm/predictions/B1-LR_42.csv --pred B1-SVM=results/pratinjau_llm/predictions/B1-SVM_42.csv --pred B1-NB=results/pratinjau_llm/predictions/B1-NB_42.csv --pred B3-Gemini=data/annotation_workspace/llm/gemini-3.5-flash-lite/manual_v1/llm_gemini-3.5-flash-lite_manual.csv
```

Hasil (344 ulasan, acuan label manual):

| Model | F1 pasangan | F1 deteksi (micro) | Macro-F1 sentimen |
|---|---|---|---|
| B1-LR (C = 10) | 0.681 | 0.740 | 0.216 |
| B1-SVM (C = 10) | 0.655 | 0.718 | 0.182 |
| B1-NB (alpha = 0,1) | 0.551 | 0.595 | 0.134 |
| B3-Gemini | 0.832 | 0.888 | 0.716 |

Tabel per aspek ada di `evaluasi/tabel.md`; paired bootstrap 1.000 kali di
`evaluasi/metrik.json`.
