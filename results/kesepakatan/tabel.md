| Perbandingan | Ulasan | Agreement sel | Ulasan persis sama | Kappa rata-rata aspek |
|---|---|---|---|---|
| Uji: manual vs Gemini | 150 | 0.946 | 0.673 | 0.777 |
| Latih/val: verifikasi vs Gemini | 125 | 0.975 | 0.840 | 0.850 |

Kappa per aspek (empat label):

| Aspek | Uji: manual vs Gemini | Latih/val: verifikasi vs Gemini |
|---|---|---|
| Akun Login | 0.893 | 0.963 |
| Registrasi Data | 0.777 | 0.977 |
| Fitur Kesehatan | 0.800 | 1.000 |
| Performa | 0.844 | 0.877 |
| Kemudahan Penggunaan | 0.491 | 0.937 |
| Pembaruan Aplikasi | 0.875 | 0.869 |
| Layanan Pelanggan | 0.795 | 0.744 |
| Umum | 0.740 | 0.430 |

Baris latih/validasi lembar gold vs hasil verifikasi (125 ulasan): agreement sel 1.000 (identik; satu keputusan, bukan dua penilaian independen).
