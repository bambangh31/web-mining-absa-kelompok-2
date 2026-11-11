"""Pelabelan ABSA dengan LLM (Gemini API atau Ollama lokal), prompt v1.

LLM membaca `text_llm` dan mengeluarkan daftar penyebutan aspek per ulasan
(kata aspek persis, aspek seragam, kategori, label, bukti) dalam JSON yang
dibatasi skema. Label per ulasan (ACSA) diturunkan dengan aturan yang sama
seperti lembar manual (`absa_schema.aggregate_mentions`).

Contoh:

  # 800 ulasan berlabel: pra-label latih/validasi dan prediksi pembanding uji
  python src/llm_label.py --set split

  # Ulasan pada lembar manual -> lembar versi LLM untuk dibandingkan
  python src/llm_label.py --set manual \
      --manual-excel "Label Manual Sentimen Komentar Satu Sehat.xlsx" \
      --excel-out "Label LLM Sentimen Komentar Satu Sehat.xlsx"

Kunci API dibaca dari `.env` (GEMINI_API_KEY). Respons mentah disimpan per
batch sehingga pekerjaan yang terhenti bisa dilanjutkan tanpa mengulang.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.absa_schema import ASPECT_DESCRIPTIONS, ASPECT_NAMES, ASPECTS, aggregate_mentions  # noqa: E402
from src import label_excel  # noqa: E402

PROMPT_VERSION = "v1"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
WORKSPACE = Path("data/annotation_workspace/llm")
CATEGORY_NAMES = [ASPECT_NAMES[a] for a in ASPECTS]

GUIDE = f"""Kamu anotator aspect-based sentiment analysis (ABSA) untuk ulasan Google Play
aplikasi SATUSEHAT Mobile (dulu PeduliLindungi) dari Kementerian Kesehatan RI.

Untuk setiap ulasan, temukan SEMUA penyebutan aspek beserta sentimennya.
Satu ulasan bisa memuat beberapa aspek dengan sentimen berbeda (multi-aspek).

Kategori aspek:
{chr(10).join(f"- {ASPECT_NAMES[a]}: {ASPECT_DESCRIPTIONS[a]}" for a in ASPECTS)}

Label sentimen:
- positif: pengguna puas atau memuji aspek itu
- negatif: pengguna mengeluh atau melaporkan masalah pada aspek itu
- netral: aspek disebut tanpa penilaian, misalnya pertanyaan cara, saran, atau permintaan fitur

Aturan:
1. Sentimen dinilai dari teks, bukan dari rating bintang (rating tidak diberikan).
2. "umum" hanya dipakai bila ulasan menilai aplikasi secara keseluruhan dan TIDAK
   menyebut aspek khusus apa pun. Jika ada aspek khusus, jangan isi umum.
3. "performa" hanya bila ada kegagalan atau kualitas teknis yang disebut: tidak bisa
   dibuka, error, force close, keluar sendiri, stuck di logo, lambat, loading, server, bug,
   atau sebaliknya pujian cepat/lancar. "Susah login" atau "PIN salah terus" saja adalah
   akun login, bukan performa. "Login langsung error" adalah akun login DAN performa.
4. "kemudahan penggunaan" hanya bila pengguna menilai alur atau tampilan (ribet, bingung,
   susah dipakai, mudah, simpel), bukan setiap kali ada fitur yang gagal.
5. "pembaruan aplikasi" untuk update/pembaruan/versi, diminta update terus, gagal update,
   perubahan atau ganti nama dari PeduliLindungi ke SATUSEHAT, dan perbandingan dengan
   aplikasi lama. "Setelah update tidak bisa dibuka" = pembaruan aplikasi negatif DAN
   performa negatif.
6. "layanan pelanggan" untuk CS, helpdesk, aduan lewat email/WA, dan tanggapan atau
   respons pihak pengembang terhadap keluhan.
7. Jangan menambah aspek yang tidak disebut. Kata kasar tidak mengubah kategori.
8. Ulasan tanpa aspek yang bisa dinilai boleh berisi daftar aspek kosong.

Isi setiap penyebutan:
- kata: kata atau frasa aspek, disalin PERSIS dari ulasan (huruf, ejaan, dan spasi sama)
- seragam: bentuk baku huruf kecil dari kata aspek, misalnya login, kode verifikasi, OTP,
  PIN, pendaftaran, NIK, data diri, nomor telepon, sertifikat, vaksin, booster, cek
  kesehatan, buka aplikasi, error, lemot, loading, logo, stuck, bug, ribet, mudah, update,
  PeduliLindungi, customer service, respon, bagus, aplikasi
- kategori: salah satu kategori di atas
- label: positif, negatif, atau netral
- bukti: potongan kalimat PERSIS dari ulasan yang menunjukkan sentimen; bila lebih dari
  satu potongan, pisahkan dengan "; "
Satu kata aspek yang muncul berulang cukup ditulis sekali."""

# Contoh buatan tim berdasarkan panduan, bukan ulasan dari dataset.
FEW_SHOT = [
    ("Setelah update malah ga bisa dibuka, cuma muncul logo doang. Padahal mau lihat sertifikat vaksin", [
        ("update", "update", "pembaruan aplikasi", "negatif", "Setelah update malah ga bisa dibuka"),
        ("dibuka", "buka aplikasi", "performa", "negatif", "ga bisa dibuka, cuma muncul logo doang"),
        ("sertifikat vaksin", "sertifikat", "fitur kesehatan", "negatif", "Padahal mau lihat sertifikat vaksin")]),
    ("Susah login, PIN salah terus padahal udah bener", [
        ("login", "login", "akun login", "negatif", "Susah login"),
        ("PIN", "PIN", "akun login", "negatif", "PIN salah terus padahal udah bener")]),
    ("Tiap login langsung error terus keluar sendiri", [
        ("login", "login", "akun login", "negatif", "Tiap login langsung error"),
        ("error", "error", "performa", "negatif", "langsung error terus keluar sendiri")]),
    ("Aplikasinya bagus banget, sangat membantu", [
        ("Aplikasinya", "aplikasi", "umum", "positif", "Aplikasinya bagus banget, sangat membantu")]),
    ("Daftar pakai NIK katanya sudah terdaftar, padahal belum pernah daftar. Lapor lewat email juga ga dibalas", [
        ("NIK", "NIK", "registrasi data", "negatif", "Daftar pakai NIK katanya sudah terdaftar"),
        ("email", "respon", "layanan pelanggan", "negatif", "Lapor lewat email juga ga dibalas")]),
    ("Tampilannya simpel, mudah dipakai orang tua. Cek kesehatan gratis juga lancar", [
        ("Tampilannya", "tampilan", "kemudahan penggunaan", "positif", "Tampilannya simpel, mudah dipakai orang tua"),
        ("Cek kesehatan gratis", "cek kesehatan", "fitur kesehatan", "positif", "Cek kesehatan gratis juga lancar")]),
    ("Tolong tambahkan fitur mode gelap min", [
        ("mode gelap", "mode gelap", "kemudahan penggunaan", "netral", "Tolong tambahkan fitur mode gelap")]),
    ("Enakan PeduliLindungi yang dulu, sekarang ribet banget", [
        ("PeduliLindungi", "PeduliLindungi", "pembaruan aplikasi", "negatif", "Enakan PeduliLindungi yang dulu"),
        ("ribet", "ribet", "kemudahan penggunaan", "negatif", "sekarang ribet banget")]),
    ("Kode OTP ga masuk masuk udah nunggu sejam", [
        ("Kode OTP", "OTP", "akun login", "negatif", "Kode OTP ga masuk masuk udah nunggu sejam")]),
    ("Cara ganti nomor HP gimana ya?", [
        ("nomor HP", "nomor telepon", "registrasi data", "netral", "Cara ganti nomor HP gimana ya?")]),
    ("Apk ga guna sama sekali", [
        ("Apk", "aplikasi", "umum", "negatif", "Apk ga guna sama sekali")]),
    ("Kemarin error tapi sekarang sudah lancar lagi, makasih CS yang cepat tanggap", [
        ("lancar", "lancar", "performa", "positif", "sekarang sudah lancar lagi"),
        ("CS", "customer service", "layanan pelanggan", "positif", "makasih CS yang cepat tanggap")]),
]

MENTION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "kata": {"type": "STRING"},
        "seragam": {"type": "STRING"},
        "kategori": {"type": "STRING", "enum": CATEGORY_NAMES},
        "label": {"type": "STRING", "enum": ["positif", "negatif", "netral"]},
        "bukti": {"type": "STRING"},
    },
    "required": ["kata", "seragam", "kategori", "label", "bukti"],
    "propertyOrdering": ["kata", "seragam", "kategori", "label", "bukti"],
}
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {"hasil": {"type": "ARRAY", "items": {
        "type": "OBJECT",
        "properties": {"id": {"type": "STRING"}, "aspek": {"type": "ARRAY", "items": MENTION_SCHEMA}},
        "required": ["id", "aspek"], "propertyOrdering": ["id", "aspek"]}}},
    "required": ["hasil"],
}


def few_shot_text():
    lines = ["Contoh (dibuat dari panduan, bukan dari data):"]
    for i, (text, mentions) in enumerate(FEW_SHOT, start=1):
        out = {"id": f"c{i}", "aspek": [dict(zip(("kata", "seragam", "kategori", "label", "bukti"), m))
                                         for m in mentions]}
        lines.append(f"Ulasan c{i}: {text}\nJawaban: {json.dumps(out, ensure_ascii=False)}")
    return "\n\n".join(lines)


def system_prompt():
    return GUIDE + "\n\n" + few_shot_text()


def batch_prompt(items):
    body = "\n".join(f"{key}: {text}" for key, text in items)
    return ("Labeli setiap ulasan berikut. Kembalikan satu objek per id, urut sesuai masukan.\n\n" + body)


def load_env(path=".env"):
    path = Path(path)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def call_gemini(model, system, user, temperature, api_key, timeout=300):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature, "responseMimeType": "application/json",
                             "responseSchema": RESPONSE_SCHEMA},
    }
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    parts = data["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    return text, {"usage": data.get("usageMetadata"), "modelVersion": data.get("modelVersion")}


def call_ollama(model, system, user, temperature, host="http://localhost:11434", timeout=300):
    schema = {"type": "object", "properties": {"hasil": {"type": "array", "items": {
        "type": "object", "properties": {"id": {"type": "string"}, "aspek": {"type": "array", "items": {
            "type": "object", "properties": {
                "kata": {"type": "string"}, "seragam": {"type": "string"},
                "kategori": {"type": "string", "enum": CATEGORY_NAMES},
                "label": {"type": "string", "enum": ["positif", "negatif", "netral"]},
                "bukti": {"type": "string"}},
            "required": ["kata", "seragam", "kategori", "label", "bukti"]}}},
        "required": ["id", "aspek"]}}}, "required": ["hasil"]}
    payload = {"model": model, "stream": False, "think": False, "format": schema,
               "options": {"temperature": temperature, "num_ctx": 8192},
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    request = urllib.request.Request(f"{host}/api/chat", data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    return data["message"]["content"], {"usage": {k: data.get(k) for k in ("prompt_eval_count", "eval_count")}}


def locate(fragment, original):
    """Cari `fragment` di teks asli; spasi/baris baru boleh berbeda. Kembalikan potongan asli."""
    fragment = str(fragment).strip()
    if not fragment:
        return None
    if fragment in original:
        return fragment
    words = fragment.split()
    pattern = r"\s+".join(re.escape(w) for w in words)
    for flags in (0, re.IGNORECASE):
        match = re.search(pattern, original, flags)
        if match:
            return match.group(0)
    return None


def clean_mentions(rid, raw_mentions, original):
    """Validasi keluaran LLM; kata/bukti disejajarkan ke teks asli bila bisa."""
    mentions, issues = [], []
    seen = set()
    for m in raw_mentions:
        try:
            aspect = ASPECTS[CATEGORY_NAMES.index(m["kategori"])]
        except (KeyError, ValueError):
            issues.append(f"kategori tidak sah: {m.get('kategori')!r}")
            continue
        if m.get("label") not in ("positif", "negatif", "netral"):
            issues.append(f"label tidak sah: {m.get('label')!r}")
            continue
        kata = locate(m.get("kata", ""), original)
        if kata is None:
            issues.append(f"kata tidak ditemukan persis: {m.get('kata')!r}")
            kata = str(m.get("kata", "")).strip()
        pieces = []
        # LLM kadang menggabungkan potongan dengan "..."; cari tiap potongan di teks asli.
        for piece in re.split(r";|\.\.\.+|…", str(m.get("bukti", ""))):
            found = locate(piece, original)
            if found:
                pieces.append(found)
            elif piece.strip():
                issues.append(f"bukti tidak ditemukan persis: {piece.strip()!r}")
        key = (kata.lower(), aspect, m["label"])
        if key in seen:
            continue
        seen.add(key)
        mentions.append({"reviewId": rid, "kata": kata, "seragam": str(m.get("seragam", "")).strip(),
                         "aspek": aspect, "label": m["label"], "bukti": "; ".join(pieces)})
    return mentions, issues


def read_done(raw_path):
    done = {}
    if raw_path.exists():
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("ok"):
                done.update(record["result"])
    return done


def label_reviews(items, originals, backend, model, run_dir, batch_size=20, temperature=0.0,
                  max_retries=4, pause=4.0, log=print):
    """items: [(reviewId, text_llm)]. Hasil: {reviewId: daftar penyebutan mentah}."""
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw.jsonl"
    done = read_done(raw_path)
    todo = [(rid, text) for rid, text in items if rid not in done]
    system = system_prompt()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if backend == "gemini" and not api_key and todo:
        raise SystemExit("GEMINI_API_KEY belum diisi di .env")
    log(f"{len(done)} ulasan sudah ada, {len(todo)} ulasan akan dikirim ({backend}:{model})")
    for start in range(0, len(todo), batch_size):
        chunk = todo[start:start + batch_size]
        keys = {f"r{i + 1}": rid for i, (rid, _) in enumerate(chunk)}
        user = batch_prompt([(f"r{i + 1}", text) for i, (_, text) in enumerate(chunk)])
        for attempt in range(1, max_retries + 2):
            began = time.time()
            record = {"time": datetime.now(timezone.utc).isoformat(), "backend": backend, "model": model,
                      "prompt_version": PROMPT_VERSION, "temperature": temperature, "ids": keys,
                      "attempt": attempt}
            try:
                if backend == "gemini":
                    text, meta = call_gemini(model, system, user, temperature, api_key)
                else:
                    text, meta = call_ollama(model, system, user, temperature)
                parsed = json.loads(text)
                by_key = {h["id"]: h.get("aspek", []) for h in parsed["hasil"]}
                missing = set(keys) - set(by_key)
                if missing:
                    raise ValueError(f"id hilang pada respons: {sorted(missing)}")
                record.update(ok=True, seconds=round(time.time() - began, 2), response=text, **meta,
                              result={keys[k]: by_key[k] for k in keys})
                with raw_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                done.update(record["result"])
                log(f"  batch {start // batch_size + 1}: {len(chunk)} ulasan, {record['seconds']} detik")
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError,
                    KeyError, json.JSONDecodeError) as error:
                detail = error.read().decode("utf-8", "replace")[:1500] if isinstance(error, urllib.error.HTTPError) else ""
                record.update(ok=False, error=f"{type(error).__name__}: {error} {detail}".strip())
                with raw_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                if "PerDay" in record["error"] or "per day" in record["error"]:
                    raise SystemExit("Kuota harian model ini habis (free tier 20 permintaan/hari). "
                                     "Jalankan lagi besok; batch yang sudah berhasil tidak dikirim ulang.")
                wait = 60 * attempt if ("429" in record["error"] or "503" in record["error"]) else pause * attempt
                log(f"  gagal (percobaan {attempt}): {record['error'][:160]}; tunggu {wait} detik")
                if attempt > max_retries:
                    raise SystemExit("Batch gagal setelah beberapa percobaan; jalankan ulang untuk melanjutkan")
                time.sleep(wait)
        time.sleep(pause)
    return {rid: done[rid] for rid, _ in items}


def read_clean(path="data/processed/reviews_clean.csv"):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return {row["reviewId"]: row for row in csv.DictReader(stream)}


def read_split(path="data/annotations/split.csv"):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return {row["reviewId"]: row["split"] for row in csv.DictReader(stream)}


def safe_name(model):
    return re.sub(r"[^a-z0-9.]+", "-", model.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", choices=("gemini", "ollama"), default="gemini")
    parser.add_argument("--model", default=None, help=f"default gemini: {DEFAULT_MODEL}, ollama: qwen3.5:4b")
    parser.add_argument("--set", choices=("split", "manual"), required=True)
    parser.add_argument("--splits", default="gold_train,gold_val,gold_test",
                        help="split yang dilabeli untuk --set split (kalibrasi tidak, karena sumber contoh)")
    parser.add_argument("--manual-excel", type=Path, default=Path("Label Manual Sentimen Komentar Satu Sehat.xlsx"))
    parser.add_argument("--excel-out", type=Path, default=None)
    parser.add_argument("--clean", type=Path, default=Path("data/processed/reviews_clean.csv"))
    parser.add_argument("--split-file", type=Path, default=Path("data/annotations/split.csv"))
    parser.add_argument("--raw", type=Path, default=Path("data/raw/com.telkom.tracencare_reviews.csv"))
    parser.add_argument("--batch-size", type=int, default=60)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None, help="uji coba: batasi jumlah ulasan")
    args = parser.parse_args()
    load_env()
    model = args.model or (DEFAULT_MODEL if args.backend == "gemini" else "qwen3.5:4b")
    clean, split, raw = read_clean(args.clean), read_split(args.split_file), label_excel.read_raw(args.raw)

    if args.set == "split":
        wanted = set(args.splits.split(","))
        if "kalibrasi" in wanted:
            raise SystemExit("Kalibrasi tidak dilabeli LLM karena menjadi sumber contoh few-shot")
        ids = sorted(rid for rid, name in split.items() if name in wanted)
        reviews = {rid: {"No": i + 1, "reviewId": rid, "Tanggal": raw[rid]["at"],
                         "Versi Aplikasi": raw[rid]["reviewCreatedVersion"], "Rating": int(raw[rid]["score"]),
                         "Komentar": raw[rid]["content"]} for i, rid in enumerate(ids)}
    else:
        reviews, _ = label_excel.read_mentions(args.manual_excel)
        ids = list(reviews)
    if args.limit:
        ids = ids[:args.limit]
    missing = [rid for rid in ids if rid not in clean]
    if missing:
        raise SystemExit(f"{len(missing)} reviewId tidak ada di reviews_clean.csv")
    items = [(rid, clean[rid]["text_llm"]) for rid in ids]
    run_dir = WORKSPACE / safe_name(model) / f"{args.set}_{PROMPT_VERSION}"
    result = label_reviews(items, raw, args.backend, model, run_dir, args.batch_size, args.temperature)

    mentions, issues = [], []
    for rid in ids:
        found, problems = clean_mentions(rid, result[rid], raw[rid]["content"])
        mentions.extend(found)
        issues.extend({"reviewId": rid, "masalah": p} for p in problems)
    labels = {rid: aggregate_mentions([(m["aspek"], m["label"]) for m in mentions if m["reviewId"] == rid])
              for rid in ids}
    tag = safe_name(model)
    with (run_dir / "mentions.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["reviewId", "kata", "seragam", "aspek", "label", "bukti"])
        writer.writeheader()
        writer.writerows(mentions)
    with (run_dir / "issues.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["reviewId", "masalah"])
        writer.writeheader()
        writer.writerows(issues)
    extra = {"model": model, "prompt_version": PROMPT_VERSION}
    if args.set == "split":
        out = Path("data/annotations") / f"llm_{tag}.csv"
    else:
        out = run_dir / f"llm_{tag}_manual.csv"
    label_excel.write_label_csv(out, labels, extra)
    if args.excel_out:
        sub = {rid: reviews[rid] for rid in ids}
        label_excel.write_mentions(args.excel_out, sub, mentions)
    print(json.dumps({"ulasan": len(ids), "penyebutan": len(mentions), "masalah_validasi": len(issues),
                      "label_csv": str(out), "excel": str(args.excel_out) if args.excel_out else None,
                      "raw": str(run_dir / "raw.jsonl")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
