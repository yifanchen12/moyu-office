import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_launch import LocalLauncher, valid_target
import local_server as server


class LocalLaunchTest(unittest.TestCase):
    def test_existing_comfyui_opens_page_without_starting_a_second_service(self):
        with tempfile.TemporaryDirectory() as temporary:
            script=Path(temporary)/'run_nvidia_gpu.bat';script.touch()
            url='http://127.0.0.1:8198'
            launcher=LocalLauncher({'comfyui_url':url,'launch_targets':{'comfyui':str(script)}})
            with patch('local_launch.urlopen') as request, patch('local_launch.webbrowser.open',return_value=True) as browser, patch('local_launch.os.startfile',create=True) as open_file:
                request.return_value.__enter__.return_value=types.SimpleNamespace(status=200)
                self.assertEqual(launcher.launch('comfyui')[2],200)
                browser.assert_called_once_with(url)
                open_file.assert_not_called()

    def test_entry_points_are_local_and_request_cannot_supply_commands(self):
        for target in ('javascript:alert(1)','file:///C:/Windows/System32/cmd.exe','https://user:secret@example.test','cmd.exe /c anything','https://example.test\ncommand'):
            self.assertFalse(valid_target(target))
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'software.exe';path.touch()
            launcher=LocalLauncher({'launch_targets':{'sra':str(path)}})
            self.assertNotIn(str(path),json.dumps(launcher.info('sra')))
            with patch.object(launcher,'focus_existing',return_value=False), patch('local_launch.os.startfile',create=True) as open_file:
                self.assertEqual(launcher.launch('sra')[2],200)
                open_file.assert_called_once_with(str(path),cwd=str(path.parent))
                self.assertEqual(launcher.launch('sra')[2],429)
                self.assertEqual(launcher.launch('arbitrary-command')[2],400)

    def test_launch_api_requires_same_origin_and_known_id_only(self):
        with server.app.test_client() as client, patch.object(server.launcher,'launch',return_value=(True,'opened',200)) as launch:
            url=server.BASE_URL
            self.assertEqual(client.post('/local/launch',base_url=url,json={'id':'codex'}).status_code,403)
            self.assertEqual(client.post('/local/launch',base_url=url,headers={'Origin':'https://foreign.test'},json={'id':'codex'}).status_code,403)
            headers={'Origin':url}
            self.assertEqual(client.post('/local/launch',base_url=url,headers=headers,json={'id':'codex','command':'anything'}).status_code,400)
            self.assertEqual(client.post('/local/launch',base_url=url,headers=headers,json={'id':[]}).status_code,400)
            self.assertEqual(client.post('/local/launch',base_url=url,headers=headers,json={'id':'codex'}).status_code,200)
            launch.assert_called_once_with('codex')


if __name__=='__main__':unittest.main()
