import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import qwen_inference as q


def answer(keys):
    return json.dumps({"hasil": [{"id": key, "aspek": [{"kata": "login", "seragam": "login",
          "kategori": "akun login", "label": "negatif", "bukti": "gagal login"}]} for key in keys]})


class QwenTests(unittest.TestCase):
    def test_chat_uses_same_schema_and_records_metadata(self):
        calls = []
        def urlopen(request, timeout):
            calls.append(json.loads(request.data))
            return io.BytesIO(json.dumps({"done": True, "done_reason": "stop", "model": "qwen3.5:4b",
                            "message": {"content": answer(["r1"])}, "prompt_eval_count": 300}).encode())
        with patch.object(q.urllib.request, "urlopen", urlopen):
            text, meta = q.chat("http://localhost:11435", "qwen3.5:4b", "system", "user", {"num_ctx": 8192})
        self.assertFalse(calls[0]["think"])
        self.assertEqual(calls[0]["format"]["type"], "object")
        self.assertEqual(calls[0]["messages"][0]["content"], "system")
        self.assertEqual(meta["prompt_eval_count"], 300)
        self.assertEqual(set(q.parse_response(text, {"r1": "id1"})), {"id1"})

    def test_rejects_truncated_output_and_context_exhaustion(self):
        for response in [{"done": True, "done_reason": "length"},
                         {"done": True, "done_reason": "stop", "prompt_eval_count": 8192}]:
            with patch.object(q, "api_json", return_value=response):
                with self.assertRaises(ValueError):
                    q.chat("local", "qwen", "s", "u", {"num_ctx": 8192})

    def test_rejects_missing_duplicate_ids_and_invalid_labels(self):
        cases = [{"hasil": []}, {"hasil": [{"id": "r1", "aspek": []}]*2},
                 {"hasil": [{"id": "other", "aspek": []}]},
                 {"hasil": [{"id": "r1"}]}, json.loads(answer(["r1"]))]
        cases[-1]["hasil"][0]["aspek"][0]["label"] = "campuran"
        for value in cases:
            with self.assertRaises(ValueError):q.parse_response(json.dumps(value), {"r1": "id1"})

    def test_empty_mentions_are_valid_no_aspect(self):
        self.assertEqual(q.parse_response('{"hasil":[{"id":"r1","aspek":[]}]}', {"r1":"x"}), {"x":[]})

    def test_failed_batch_resumes_only_remaining_ids_and_refuses_changed_model(self):
        items=[(str(i),"gagal login") for i in range(4)];originals=dict(items)
        def fake(*args):return answer(["r1","r2"]), {"done_reason":"stop"}
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(q,"chat",side_effect=[fake(), TimeoutError("uji putus")]):
                with self.assertRaises(RuntimeError):
                    q.infer(items,originals,tmp,{"model_digest":"abc"},max_retries=0,log=lambda *_args,**_kw:None)
            state=json.loads((Path(tmp)/'checkpoint.json').read_text())
            self.assertEqual(set(state['result']),{'0','1'})
            with patch.object(q,"chat",side_effect=fake) as call:
                labels=q.infer(items,originals,tmp,{"model_digest":"abc"},log=lambda *_args,**_kw:None)
                self.assertEqual(call.call_count,1)
                self.assertEqual(len(labels),4)
                self.assertTrue(all(v['akun_login']=='negatif' for v in labels.values()))
            with patch.object(q,"chat",side_effect=AssertionError("tidak boleh meminta ulang")):
                q.infer(items,originals,tmp,{"model_digest":"abc"},log=lambda *_args,**_kw:None)
            with self.assertRaisesRegex(ValueError,'Checkpoint berbeda'):
                q.infer(items,originals,tmp,{"model_digest":"new"})
            changed=items[:-1]+[('3','teks berbeda')]
            with self.assertRaisesRegex(ValueError,'Checkpoint berbeda'):
                q.infer(changed,originals,tmp,{"model_digest":"abc"})

    def test_malformed_response_retries_without_creating_empty_prediction(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(q.time,'sleep'), \
             patch.object(q,'chat',side_effect=[('{"hasil":[]}',{}),(answer(['r1']),{})]) as call:
            labels=q.infer([('a','gagal login')],{'a':'gagal login'},tmp,{'model_digest':'abc'},
                           log=lambda *_args,**_kw:None)
            self.assertEqual(call.call_count,2)
            self.assertEqual(labels['a']['akun_login'],'negatif')
            self.assertEqual(json.loads((Path(tmp)/'checkpoint.json').read_text())['batches'][0]['attempt'],2)
