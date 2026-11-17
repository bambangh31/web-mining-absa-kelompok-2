# Melanjutkan Qwen setelah respons kehilangan ID

Pada notebook lama bersumber commit 574fddc, schema hasil belum mewajibkan
jumlah objek dan ID sesuai batch. Model dapat mengembalikan JSON sah yang
kurang dari dua ulasan. Validator menghentikan proses; ulasan yang belum
terjawab tidak diisi label kosong.

Untuk notebook lama yang berhenti pada 6/150, tetap gunakan runtime dan
notebook yang sekarang. Simpan ZIP parsial sebelum melanjutkan. Tambahkan
satu sel kode, jalankan kode berikut, lalu jalankan ulang **sel prediksi
tahap 4** dan **sel evaluasi tahap 5**. Tidak perlu memasang/mengunduh model ulang.

```python
from pathlib import Path
import hashlib, urllib.request, runpy
url = "https://raw.githubusercontent.com/bambangh31/web-mining-absa-kelompok-2/30fdae6931f251d174fd4af314722cb3973eced5/src/qwen_resume_patch.py"
data = urllib.request.urlopen(url).read()
assert hashlib.sha256(data).hexdigest() == "55a2e617cff78a4349febfe64f03c8a33391520fbcac4a849a932f176cc45df5"
patch = Path("/content/hasil_qwen/qwen_resume_patch.py")
patch.write_bytes(data)
runpy.run_path(str(patch), run_name="__main__")
```

Pesan yang diharapkan: `Perbaikan aktif; 6 ulasan tersimpan tetap dipertahankan.`
Prediksi berikutnya mulai dari enam hasil tersimpan dan hanya memproses 144 ID
tersisa. Patch menambah enum ID serta batas jumlah respons. Prompt, model,
seed, temperature, batch, dan checkpoint tidak diubah. Audit hash patch,
checkpoint sebelum perbaikan, dan revisi schema disertakan dalam folder hasil.
Jika masih gagal, respons yang ditolak disimpan di `rejected_responses.jsonl`.

Sumber patch dan SHA dikunci ke commit yang telah diuji. Patch menolak versi
runtime lain. Jika runtime lama terhapus, buka salinan notebook lama di Drive,
pulihkan ZIP parsial menggunakan `RESTORE_ZIP = True`, jalankan sampai server
siap, lalu pasang patch ini sebelum sel prediksi. Notebook terbaru memakai
sumber yang telah diperbaiki; ZIP lama tidak dicampur otomatis dengan konfigurasi baru.

Pemeriksaan: sembilan tes Qwen lulus. Replay checkpoint asli enam ulasan
mempertahankan tiga batch awal dan menyelesaikan 144 ID tersisa menggunakan
API tiruan. Inferensi GPU sesungguhnya belum diuji untuk perbaikan ini.
