| Model | F1 pasangan | F1 deteksi (micro) | Macro-F1 sentimen |
|---|---|---|---|
| B1-LR | 0.684 | 0.731 | 0.230 |
| B1-SVM | 0.670 | 0.715 | 0.207 |
| B1-NB | 0.581 | 0.620 | 0.159 |
| B3-Gemini | 0.828 | 0.885 | 0.706 |

F1 pasangan per aspek:

| Aspek | B1-LR | B1-SVM | B1-NB | B3-Gemini |
|---|---|---|---|---|
| Akun Login | 0.790 | 0.796 | 0.639 | 0.913 |
| Registrasi Data | 0.543 | 0.492 | 0.128 | 0.742 |
| Fitur Kesehatan | 0.752 | 0.722 | 0.692 | 0.854 |
| Performa | 0.717 | 0.690 | 0.636 | 0.872 |
| Kemudahan Penggunaan | 0.000 | 0.000 | 0.000 | 0.583 |
| Pembaruan Aplikasi | 0.721 | 0.716 | 0.638 | 0.842 |
| Layanan Pelanggan | 0.000 | 0.000 | 0.000 | 0.750 |
| Umum | 0.333 | 0.133 | 0.000 | 0.524 |

Macro-F1 sentimen per aspek:

| Aspek | B1-LR | B1-SVM | B1-NB | B3-Gemini |
|---|---|---|---|---|
| Akun Login | 0.302 | 0.295 | 0.244 | 0.591 |
| Registrasi Data | 0.211 | 0.179 | 0.045 | 0.787 |
| Fitur Kesehatan | 0.595 | 0.568 | 0.486 | 0.726 |
| Performa | 0.281 | 0.263 | 0.248 | 0.779 |
| Kemudahan Penggunaan | 0.000 | 0.000 | 0.000 | 0.798 |
| Pembaruan Aplikasi | 0.272 | 0.266 | 0.246 | 0.574 |
| Layanan Pelanggan | 0.000 | 0.000 | 0.000 | 0.574 |
| Umum | 0.182 | 0.083 | 0.000 | 0.819 |
