"""Inferensi Qwen via Ollama dengan prompt proyek dan checkpoint per batch.

Tidak membaca label uji. Pemanggil memberikan pasangan ID/teks serta teks
asli untuk audit kutipan. Evaluasi dilakukan setelah seluruh prediksi selesai.
"""
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from src import llm_label
from src.absa_schema import aggregate_mentions
from src.model_data import write_predictions


def json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def schema_json(value):
    """Skema yang sama dengan Gemini, dalam format JSON Schema Ollama."""
    if isinstance(value, dict):
        return {k: v.lower() if k == "type" else schema_json(v)
                for k, v in value.items() if k != "propertyOrdering"}
    if isinstance(value, list):
        return [schema_json(v) for v in value]
    return value


def api_json(host, path, payload=None, timeout=30):
    request = urllib.request.Request(host.rstrip("/") + path,
                                     data=None if payload is None else json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def chat(host, model, system, user, options, timeout=300):
    # Prompt lama dan checkpoint tetap berlaku. Perubahan ini hanya
    # membatasi format ID/jumlah objek, bukan memilih label sentimen.
    keys = re.findall(r"^(r[0-9]+): ", user, flags=re.MULTILINE)
    schema = schema_json(llm_label.RESPONSE_SCHEMA)
    if keys:
        if len(set(keys)) != len(keys):
            raise ValueError("ID masukan batch duplikat")
        array = schema["properties"]["hasil"]
        array.update(minItems=len(keys), maxItems=len(keys))
        array["items"]["properties"]["id"]["enum"] = keys
    data = api_json(host, "/api/chat", {"model": model, "stream": False, "think": False,
                    "keep_alive": "30m", "format": schema,
                    "options": options, "messages": [{"role": "system", "content": system},
                                                        {"role": "user", "content": user}]}, timeout)
    if data.get("done") is not True or data.get("done_reason") != "stop":
        raise ValueError(f"Respons Ollama belum lengkap: {data.get('done_reason')}")
    if data.get("prompt_eval_count", 0) >= options["num_ctx"]:
        raise ValueError("Prompt mencapai batas konteks; hentikan untuk memeriksa pemotongan input")
    text = data.get("message", {}).get("content")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Respons Ollama tidak memiliki jawaban akhir")
    meta = {k: data.get(k) for k in ["model", "created_at", "done_reason", "prompt_eval_count",
                                    "eval_count", "total_duration", "load_duration",
                                    "prompt_eval_duration", "eval_duration"]}
    meta["response_schema"] = {"revision": "ids-count-v2", "expected_ids": keys}
    return text, meta


def parse_response(text, keys):
    data = json.loads(text)
    if not isinstance(data, dict) or not isinstance(data.get("hasil"), list):
        raise ValueError("Respons harus memuat daftar hasil")
    result = {}
    required = ["kata", "seragam", "kategori", "label", "bukti"]
    for row in data["hasil"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("ID respons tidak valid")
        key = row["id"]
        if key not in keys or key in result or not isinstance(row.get("aspek"), list):
            raise ValueError("ID duplikat/tidak dikenal atau daftar aspek tidak valid")
        for mention in row["aspek"]:
            if not isinstance(mention, dict) or not all(isinstance(mention.get(k), str) for k in required):
                raise ValueError("Kolom penyebutan tidak lengkap")
            if mention["kategori"] not in llm_label.CATEGORY_NAMES or mention["label"] not in ("positif", "negatif", "netral"):
                raise ValueError("Kategori atau label sentimen tidak valid")
        result[key] = row["aspek"]
    if set(result) != set(keys):
        raise ValueError(f"ID respons belum lengkap: hilang {sorted(set(keys)-set(result))}")
    return {keys[k]: result[k] for k in keys}


def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def snapshot(out, done, originals):
    mentions, issues, labels = [], [], {}
    for rid, raw in sorted(done.items()):
        found, problems = llm_label.clean_mentions(rid, raw, originals[rid])
        mentions.extend(found)
        issues.extend({"reviewId": rid, "masalah": problem} for problem in problems)
        labels[rid] = aggregate_mentions([(m["aspek"], m["label"]) for m in found])
    write_predictions(out / "predictions/B3-Qwen_42.csv", "B3-Qwen", 42, labels)
    for name, rows, columns in [
            ("mentions.csv", mentions, ["reviewId", "kata", "seragam", "aspek", "label", "bukti"]),
            ("issues.csv", issues, ["reviewId", "masalah"])]:
        with (out / name).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    return labels


def infer(items, originals, out, identity, host="http://127.0.0.1:11435", model="qwen3.5:4b",
          batch_size=2, max_retries=2, timeout=300, log=print, on_progress=None):
    """Checkpoint hanya dilanjutkan bila input, model, prompt, dan opsi identik.

    `identity` mencatat commit/hash sumber, versi Ollama, dan digest model.
    Kutipan yang tidak cocok dicatat dengan aturan yang sama dengan Gemini;
    masalah kutipan tidak diam-diam mengubah sentimen atau menghapus prediksi.
    """
    items = list(items)
    ids = [rid for rid, _ in items]
    if not items or len(set(ids)) != len(ids) or any(r not in originals for r in ids):
        raise ValueError("ID kosong/duplikat atau teks asli tidak tersedia")
    if batch_size < 1 or max_retries < 0:
        raise ValueError("batch_size/max_retries tidak valid")
    if not identity.get("model_digest"):
        raise ValueError("Digest model Ollama wajib dicatat")
    options = {"temperature": 0.0, "seed": 42, "num_ctx": 8192, "num_predict": 4096}
    protocol = {"identity": identity, "model": model, "prompt_version": llm_label.PROMPT_VERSION,
                "prompt_sha256": json_hash(llm_label.system_prompt()), "items_sha256": json_hash(items),
                "originals_sha256": json_hash({r: originals[r] for r in ids}),
                "batch_size": batch_size, "think": False, "options": options}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "checkpoint.json"
    state = {"protocol": protocol, "result": {}, "batches": []}
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
        if state["protocol"] != protocol or not set(state["result"]).issubset(ids):
            raise ValueError("Checkpoint berbeda: gunakan folder hasil baru")
        for rid, mentions in state["result"].items():
            parse_response(json.dumps({"hasil": [{"id": "r1", "aspek": mentions}]}), {"r1": rid})
    else:
        save_json(path, state)
    done = state["result"]
    todo = [(rid, text) for rid, text in items if rid not in done]
    log(f"Qwen: {len(done)}/{len(ids)} ulasan tersimpan; {len(todo)} menunggu", flush=True)
    for start in range(0, len(todo), batch_size):
        chunk = todo[start:start + batch_size]
        keys = {f"r{i+1}": rid for i, (rid, _) in enumerate(chunk)}
        user = llm_label.batch_prompt([(f"r{i+1}", text) for i, (_, text) in enumerate(chunk)])
        for attempt in range(max_retries + 1):
            began = time.perf_counter()
            text = None
            try:
                text, meta = chat(host, model, llm_label.system_prompt(), user, options, timeout)
                parsed = parse_response(text, keys)
            except (ValueError, KeyError, TypeError, urllib.error.URLError, TimeoutError) as exc:
                with (out / "errors.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps({"ids": list(keys.values()), "attempt": attempt + 1,
                                             "error": str(exc), "response": text}, ensure_ascii=False) + "\n")
                if attempt == max_retries:
                    raise RuntimeError("Batch Qwen gagal; progres sebelumnya tersimpan") from exc
                log(f"Batch gagal, mencoba ulang ({attempt+1}/{max_retries}): {exc}", flush=True)
                time.sleep(2)
                continue
            done.update(parsed)
            state["batches"].append({"ids": list(keys.values()), "attempt": attempt + 1,
                                     "seconds": time.perf_counter()-began, "response": text, "meta": meta})
            save_json(path, state)
            snapshot(out, done, originals)
            log(f"Qwen: {len(done)}/{len(ids)} ulasan selesai", flush=True)
            if on_progress:
                on_progress(len(done), len(ids))
            break
    labels = snapshot(out, done, originals)
    save_json(out / "inference.json", {"status": "predictions_completed", "n_ulasan": len(labels),
                                      "protocol": protocol, "n_batches": len(state["batches"])})
    return labels
