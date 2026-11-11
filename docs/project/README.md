# Panduan kerja Web Mining Kelompok 2

## Isi folder

| Dokumen | Kegunaan |
|---|---|
| [collaboration-plan.md](collaboration-plan.md) | Paket kontribusi, ketergantungan, review dan pencatatan tugas |
| [method-decisions.md](method-decisions.md) | Keputusan LLM, encoder, preprocessing, pembagian data, format file dan metrik beserta alasannya |
| [literature-review.md](literature-review.md) | Penelitian terkait, perbandingan algoritma, dan posisi kebaruan proyek |
| [pipeline.md](pipeline.md) | Cara menjalankan dan menguji pipeline ABSA beserta keluarannya |
| [annotation-workflow.md](annotation-workflow.md) | Lembar kalibrasi/gold, audit kesepakatan, adjudikasi, dan ekspor label manusia |
| [timeline.md](timeline.md) | Tahap week 10-16, keluaran, bukti dan target internal |
| [publication-checklist.md](publication-checklist.md) | Pemeriksaan sebelum penyerahan dan publikasi jika diperlukan |
| [implementation-status.md](implementation-status.md) | Status setup/implementasi, bukti dan batas pencapaian |
| [review-setup.md](review-setup.md) | Perbandingan fondasi repo dengan kebutuhan ABSA |

## Prinsip kerja

Setiap minggu dikerjakan berempat sesuai peran, tanpa PIC khusus.
Empat peran mengikuti pilihan pengguna; penempatan nama adalah usulan awal:

| Anggota | NRP | Peran |
|---|---|---|
| Bambang Herlambang | 5803024019 | Preprocessing dan anotasi |
| Efraim Melvyn Rafelino Lahai | 5803024009 | Pengumpulan dan eksplorasi data |
| Jap Robertus Kurniawan Setiabudi | 5803024004 | Pemodelan ABSA |
| Robertus Geraldyn Alexandro Gabeler | 5803024025 | Evaluasi dan analisis |

Week 10 disiapkan berempat: Efraim menangani sumber/data dan tujuan/BOD,
Bambang kebutuhan preprocessing/anotasi, Jap rencana model ABSA, serta
Geraldyn rancangan evaluasi. Coding week 11-12, laporan week 13, artikel
week 15 dan presentasi week 16 dibagi berempat sesuai peran. Semua ikut
latihan presentasi. Week 14 hanya jika diminta; tindak lanjut dibagi berempat.
Rincian dan alasan ada pada [rencana kolaborasi](collaboration-plan.md).
Kelas setiap Rabu; week 11 pada 4 November 2026 menjadi acuan.
Week 10 dipetakan mundur. Tanggal kelas bukan otomatis tenggat pengumpulan.

## Roadmap

| Week / kelas 2026 | Keluaran tugas |
|---|---|
| 10 / 28 Oktober | Dataset, karakteristik, BOD, algoritma; scraping disarankan |
| 11-12 / 4 dan 11 November | Preprocessing, mining, evaluation |
| 13 / 18 November | Laporan pertama |
| 14 / 25 November | Percobaan tambahan jika diminta |
| 15 / 2 Desember | Artikel bahasa Indonesia |
| 16 / 9 Desember | Presentasi |

Pemetaan tanggal kelas mengikuti perubahan jadwal dosen. Tenggat pengumpulan
dan format artikel mengikuti arahan dosen.

## Keputusan dan bukti

Catat pemilihan sumber, aspek, label, metode, pembagian data, dan metrik pada
dokumen tahap terkait. Hubungkan keputusan dengan sumber atau bukti.
Gunakan issue untuk tugas/masukan dosen dan PR untuk perubahan. Masing-masing
memperbarui status, kendala, serta tautan hasilnya.

Lihat [panduan kontribusi](../../CONTRIBUTING.md) dan
[review setup](review-setup.md).
