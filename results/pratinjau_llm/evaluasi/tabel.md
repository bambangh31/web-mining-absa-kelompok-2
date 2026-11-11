| Model | F1 pasangan | F1 deteksi (micro) | Macro-F1 sentimen |
|---|---|---|---|
| B1-LR | 0.681 | 0.740 | 0.216 |
| B1-SVM | 0.655 | 0.718 | 0.182 |
| B1-NB | 0.551 | 0.595 | 0.134 |
| B3-Gemini | 0.832 | 0.888 | 0.716 |

F1 pasangan per aspek:

| Aspek | B1-LR | B1-SVM | B1-NB | B3-Gemini |
|---|---|---|---|---|
| Akun Login | 0.811 | 0.813 | 0.667 | 0.912 |
| Registrasi Data | 0.553 | 0.412 | 0.267 | 0.736 |
| Fitur Kesehatan | 0.676 | 0.637 | 0.543 | 0.853 |
| Performa | 0.773 | 0.766 | 0.654 | 0.883 |
| Kemudahan Penggunaan | 0.077 | 0.077 | 0.000 | 0.609 |
| Pembaruan Aplikasi | 0.708 | 0.686 | 0.613 | 0.847 |
| Layanan Pelanggan | 0.000 | 0.000 | 0.000 | 0.759 |
| Umum | 0.222 | 0.125 | 0.000 | 0.513 |

Macro-F1 sentimen per aspek:

| Aspek | B1-LR | B1-SVM | B1-NB | B3-Gemini |
|---|---|---|---|---|
| Akun Login | 0.298 | 0.295 | 0.247 | 0.591 |
| Registrasi Data | 0.230 | 0.173 | 0.111 | 0.786 |
| Fitur Kesehatan | 0.389 | 0.321 | 0.238 | 0.707 |
| Performa | 0.285 | 0.281 | 0.245 | 0.847 |
| Kemudahan Penggunaan | 0.033 | 0.033 | 0.000 | 0.813 |
| Pembaruan Aplikasi | 0.261 | 0.254 | 0.232 | 0.584 |
| Layanan Pelanggan | 0.000 | 0.000 | 0.000 | 0.585 |
| Umum | 0.229 | 0.095 | 0.000 | 0.816 |
