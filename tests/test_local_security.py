import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from initialize_local import ROOT, initialize
import local_server as server


class LocalSecurityTest(unittest.TestCase):
    def test_bootstrap_preserves_private_config_and_uses_distinct_secrets(self):
        with tempfile.TemporaryDirectory() as temporary:
            first=Path(temporary)/'first';second=Path(temporary)/'second'
            for root in (first,second):
                root.mkdir()
                for filename in ('state.sample.json','local-config.example.json'):
                    shutil.copyfile(ROOT/filename,root/filename)
                initialize(root)
            secret_file=(first/'.env').read_bytes()
            self.assertNotEqual(secret_file,(second/'.env').read_bytes())
            config=json.loads((first/'local-config.json').read_text())
            config['port']=19102
            (first/'local-config.json').write_text(json.dumps(config))
            self.assertEqual(initialize(first)['port'],19102)
            self.assertEqual((first/'.env').read_bytes(),secret_file)

    def test_local_host_origin_and_cross_site_guards(self):
        with server.app.test_client() as client:
            self.assertEqual(client.get('/local/status',base_url=server.BASE_URL).status_code,200)
            self.assertEqual(client.get('/local/status',base_url='http://attacker.invalid:19100').status_code,403)
            self.assertEqual(client.get('/local/status',base_url=server.BASE_URL,headers={'Origin':'https://attacker.invalid'}).status_code,403)
            self.assertEqual(client.get('/local/status',base_url=server.BASE_URL,headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
            self.assertEqual(client.get('/local/status',base_url=server.BASE_URL,headers={'Origin':server.BASE_URL}).status_code,200)

    def test_event_body_limit_and_training_field_filter(self):
        with tempfile.TemporaryDirectory() as temporary, server.app.test_client() as client:
            with patch.object(server,'ROOT',Path(temporary)), patch.object(server.bridge,'training'):
                self.assertEqual(client.post('/local/training',base_url=server.BASE_URL,data='x'*4097,content_type='application/json').status_code,413)
                result=client.post('/local/training',base_url=server.BASE_URL,json={'current':2,'total':4,'detail':'private','api_key':'DO_NOT_FORWARD'})
                self.assertEqual(result.status_code,200)
                data=json.loads((Path(temporary)/'.local/training-progress.json').read_text())
                self.assertEqual(set(data),{'state','current','total'})
                self.assertEqual(client.post('/local/comfy',base_url=server.BASE_URL,json={'type':'progress','data':{'value':5,'max':2}}).status_code,400)


if __name__=='__main__':unittest.main()
