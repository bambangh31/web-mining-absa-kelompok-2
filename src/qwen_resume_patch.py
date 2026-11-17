"""Patch transport untuk melanjutkan notebook Qwen versi 574fddc tanpa mengulang ID.

Dijalankan di runtime notebook lama setelah sel data/server tersedia.
Checkpoint, prompt, model, opsi inferensi, dan ukuran batch tidak diubah.
Audit patch disimpan bersama hasil agar respons versi lama/baru dapat dibedakan.
"""
import hashlib
import importlib
import json
import os
import re
from pathlib import Path

LEGACY_SHA256 = "33b30a3b5f60a8a9df2b7dfb848e1023a6ba8cad3573e92c1887257e489a1b36"
REVISION = "ids-count-v2"


def activate(out=None):
    q = importlib.import_module("src.qwen_inference")
    if getattr(q, "transport_revision", None) == REVISION:
        print("Perbaikan ID sudah aktif. Jalankan ulang sel prediksi tahap 4.")
        return
    source_hash = hashlib.sha256(Path(q.__file__).read_bytes()).hexdigest()
    if source_hash != LEGACY_SHA256:
        raise RuntimeError("Patch ini khusus notebook Qwen lama 574fddc; kode runtime berbeda.")
    out = Path(out or os.environ.get("QWEN_RESULTS_DIR", "/content/hasil_qwen"))
    checkpoint = out / "checkpoint.json"
    before = checkpoint.read_bytes()
    state = json.loads(before)
    if state["protocol"]["identity"]["source_commit"] != "574fddc5084ff07b6bafe9152b0a029440316157":
        raise RuntimeError("Versi checkpoint berbeda dari notebook lama.")
    q.save_json(out / "transport_patch.json", {
        "revision": REVISION, "legacy_source_sha256": source_hash,
        "patch_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checkpoint_before_sha256": hashlib.sha256(before).hexdigest(),
        "n_preserved": len(state["result"]),
        "change": "ID enum dan jumlah objek respons diperketat; prompt/model/opsi/batch tetap",
    })
    original_api, original_chat, original_parse = q.api_json, q.chat, q.parse_response

    def api(host, path, payload=None, timeout=30):
        if path == "/api/chat" and payload and isinstance(payload.get("format"), dict):
            keys = re.findall(r"^(r[0-9]+): ", payload["messages"][-1]["content"], flags=re.MULTILINE)
            if keys:
                if len(set(keys)) != len(keys):
                    raise ValueError("ID masukan batch duplikat")
                array = payload["format"]["properties"]["hasil"]
                array.update(minItems=len(keys), maxItems=len(keys))
                array["items"]["properties"]["id"]["enum"] = keys
        return original_api(host, path, payload, timeout)

    def chat(host, model, system, user, options, timeout=300):
        text, meta = original_chat(host, model, system, user, options, timeout)
        meta["response_schema"] = {"revision": REVISION,
                                   "expected_ids": re.findall(r"^(r[0-9]+): ", user, flags=re.MULTILINE)}
        return text, meta

    def parse(text, keys):
        try:
            return original_parse(text, keys)
        except ValueError as exc:
            with (out / "rejected_responses.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"expected_ids": keys, "response": text, "error": str(exc)},
                                         ensure_ascii=False) + "\n")
            raise

    q.api_json, q.chat, q.parse_response = api, chat, parse
    q.transport_revision = REVISION
    assert checkpoint.read_bytes() == before
    print(f"Perbaikan aktif; {len(state['result'])} ulasan tersimpan tetap dipertahankan.")
    print("Jalankan ulang sel prediksi tahap 4, lalu sel evaluasi tahap 5.")


if __name__ == "__main__":
    activate()
