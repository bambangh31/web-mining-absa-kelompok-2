import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import qwen_inference as q, qwen_resume_patch as recovery


class RecoveryTests(unittest.TestCase):
    def test_keeps_checkpoint_and_constrains_legacy_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);source=out/'legacy.py';source.write_text('legacy fixture')
            checkpoint=out/'checkpoint.json'
            checkpoint.write_text(json.dumps({'protocol':{'identity':{'source_commit':
                '574fddc5084ff07b6bafe9152b0a029440316157'}},'result':{'saved':[]}}))
            before=checkpoint.read_bytes();calls=[]
            legacy=SimpleNamespace(__file__=str(source),save_json=q.save_json,parse_response=q.parse_response)
            def api(host,path,payload,timeout):calls.append(payload);return {}
            legacy.api_json=api
            def chat(host,model,system,user,options,timeout):
                legacy.api_json(host,'/api/chat',{'format':q.schema_json(q.llm_label.RESPONSE_SCHEMA),
                    'messages':[{'role':'user','content':user}]},timeout)
                return '{"hasil":[]}',{}
            legacy.chat=chat
            with patch.dict('sys.modules',{'src.qwen_inference':legacy}), \
                 patch.object(recovery,'LEGACY_SHA256',hashlib.sha256(source.read_bytes()).hexdigest()):
                recovery.activate(out)
                text,meta=legacy.chat('host','model','system','r1: a\nr2: b',{},300)
                self.assertEqual(meta['response_schema']['revision'],'ids-count-v2')
                array=calls[0]['format']['properties']['hasil']
                self.assertEqual((array['minItems'],array['maxItems']),(2,2))
                self.assertEqual(array['items']['properties']['id']['enum'],['r1','r2'])
                with self.assertRaises(ValueError):legacy.parse_response(text,{'r1':'a','r2':'b'})
                self.assertTrue((out/'rejected_responses.jsonl').exists())
                self.assertEqual(checkpoint.read_bytes(),before)
                recovery.activate(out)
                self.assertEqual(checkpoint.read_bytes(),before)

    def test_refuses_different_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'other.py';p.write_text('different source')
            with patch.dict('sys.modules',{'src.qwen_inference':SimpleNamespace(__file__=str(p))}):
                with self.assertRaisesRegex(RuntimeError,'kode runtime berbeda'):
                    recovery.activate(tmp)
