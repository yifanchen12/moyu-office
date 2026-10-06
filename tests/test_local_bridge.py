import json
from pathlib import Path
import sys
import unittest
import tempfile
from datetime import datetime
import importlib.util
import types
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_bridge import Bridge, automation_event, lifecycle, progress, safe_training, codex_desktop_event


class LocalBridgeTest(unittest.TestCase):
    def test_desktop_activity_overrides_delayed_rollout_and_completes(self):
        thread = '00000000-0000-0000-0000-000000000001'
        turn = '00000000-0000-0000-0000-000000000002'
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            day = datetime.now().strftime('%Y/%m/%d')
            logs = home/'AppData/Local/Codex/Logs'/day
            sessions = home/'.codex/sessions'/day
            logs.mkdir(parents=True); sessions.mkdir(parents=True)
            from datetime import timezone, timedelta
            started = datetime.now(timezone.utc)
            old = (started-timedelta(seconds=60)).isoformat()
            (sessions/'delayed.jsonl').write_text(json.dumps({'type':'session_meta','payload':{'id':thread}})+'\n'+
                json.dumps({'type':'event_msg','timestamp':old,'payload':{'type':'task_complete'}})+'\n',encoding='utf-8')
            def line(seconds, message):
                stamp=(started+timedelta(seconds=seconds)).isoformat().replace('+00:00','Z')
                return f'{stamp} info {message}\n'
            path=logs/'codex-desktop-test.log'
            path.write_text(line(0,f'[electron-message-handler] Reasoning summary item completed summary="PRIVATE_PROMPT" threadId={thread} turnId={turn}'),encoding='utf-8')
            bridge=Bridge({},lambda items:None)
            with patch('local_bridge.Path.home',return_value=home):
                bridge.codex()
                self.assertEqual(bridge.items['codex']['state'],'executing')
                self.assertEqual(bridge.items['codex']['metrics']['active_sessions'],1)
                self.assertNotIn('PRIVATE_PROMPT',json.dumps(bridge.snapshot()))
                completion = 'turn-'+json.dumps(['account','agent-turn-complete','local',thread,turn],separators=(',',':'))
                self.assertEqual(codex_desktop_event(line(1,f'[notifications-service] show notification kind=turn-complete notificationId={completion}'))[1],'idle')
                with path.open('a',encoding='utf-8') as handle:
                    handle.write(line(1,f'[desktop-notifications] show notification kind=turn-complete notificationId={completion}'))
                    handle.write(line(2,f'[electron-message-handler] Reasoning summary item completed threadId={thread} turnId={turn}'))
                bridge.codex()
                self.assertEqual(bridge.items['codex']['state'],'idle')
                with path.open('a',encoding='utf-8') as handle:
                    handle.write(line(3,f'[electron-message-handler] Received turn/started for unknown conversation conversationId={thread}'))
                bridge.codex()
                self.assertEqual(bridge.items['codex']['state'],'executing')

    def test_desktop_parser_does_not_confuse_completed_reasoning_with_task_end(self):
        thread='00000000-0000-0000-0000-000000000001'
        event=codex_desktop_event(f'2026-10-06T12:00:00.000Z info [electron-message-handler] Reasoning summary item completed threadId={thread}')
        self.assertEqual(event[1],'executing')
        self.assertIsNone(codex_desktop_event('private text task_started'))
        self.assertEqual(lifecycle({'type':'event_msg','payload':{'type':'turn_aborted'}},'executing'),'idle')
        accepted=f'2026-10-06T12:00:01.000Z info [AppServerConnection] response_routed conversationId={thread} errorCode=null method=turn/start'
        self.assertEqual(codex_desktop_event(accepted)[1],'executing')
        self.assertIsNone(codex_desktop_event(accepted.replace('errorCode=null','errorCode=RATE_LIMIT')))
        self.assertEqual(codex_desktop_event(accepted.replace('turn/start','turn/interrupt'))[1],'idle')
        spoof='00000000-0000-0000-0000-000000000009'
        summary=f'2026-10-06T12:00:01.000Z info [electron-message-handler] Reasoning summary item completed summary="threadId={spoof}" threadId={thread}'
        self.assertEqual(codex_desktop_event(summary)[0],thread)

    def test_automation_lifecycle_and_child_success(self):
        phase=automation_event('INFO | TaskManager thread started','sra')
        self.assertEqual(phase,'running')
        phase=automation_event("ERROR | 任务 'StartGameTask' 失败。停止进一步执行。",'sra',phase)
        self.assertEqual(automation_event('INFO | TaskManager thread stopped','sra',phase),'error')
        self.assertEqual(automation_event('INFO | TaskManager thread stopped','sra','running'),'finished')
        phase=automation_event('[operation.py 451] [INFO]: 指令[ 一条龙 ] 节点 初始化 返回状态 成功','onedragon')
        self.assertEqual(phase,'running')
        self.assertEqual(automation_event('指令[ 返回大世界 ] 执行成功 返回状态 成功','onedragon',phase),'running')
        phase=automation_event('[INFO]: 暂停运行','onedragon',phase)
        self.assertEqual(automation_event('[operation.py 451] 指令[ 一条龙 ] 节点 初始化 返回状态 成功','onedragon',phase),'paused')
        self.assertEqual(automation_event('恢复运行','onedragon',phase),'running')
        self.assertEqual(automation_event('指令[ 一条龙 ] 执行失败 返回状态 人工结束','onedragon','paused'),'finished')
        self.assertEqual(automation_event('指令[ 一条龙 ] 执行失败 返回状态 异常','onedragon','running'),'error')

    def test_music_ignores_private_fields_and_clears_old_song(self):
        bridge=Bridge({},lambda items:None)
        data={'available':True,'title':'示例歌名','artist':'示例歌手','playback':'paused','source':'smtc','api_key':'DO_NOT_FORWARD'}
        result=types.SimpleNamespace(returncode=0,stdout=json.dumps(data))
        with patch('local_bridge.subprocess.run',return_value=result):bridge.music()
        self.assertEqual(bridge.music_snapshot()['title'],'示例歌名')
        self.assertEqual(bridge.music_snapshot()['artist'],'示例歌手')
        self.assertNotIn('playback',bridge.music_snapshot())
        self.assertNotIn('api_key',bridge.music_snapshot())
        with patch('local_bridge.subprocess.run',side_effect=OSError):bridge.music()
        self.assertFalse(bridge.music_snapshot()['available'])
        self.assertEqual(bridge.music_snapshot()['title'],'')

    def test_task_lifecycle_ignores_chat_content(self):
        self.assertEqual(lifecycle({'type':'event_msg','payload':{'type':'task_started'}}), 'executing')
        self.assertEqual(lifecycle({'type':'event_msg','payload':{'type':'task_complete'}}, 'executing'), 'idle')
        self.assertEqual(lifecycle({'type':'assistant','payload':{'type':'task_complete'}}, 'executing'), 'executing')
        self.assertEqual(lifecycle({'type':'turn/start'}, dsh=True), 'executing')
        self.assertEqual(lifecycle({'type':'turn/end'}, 'executing', dsh=True), 'idle')

    def test_training_bounds_and_private_fields(self):
        self.assertEqual(progress(3, 8), 37.5)
        for current,total in [(1,0),(9,8),(-1,8),(True,8),(float('nan'),8)]:
            with self.assertRaises(ValueError): progress(current,total)
        state, metrics=safe_training({'current':3,'total':8,'loss':.2,'api_key':'DO_NOT_FORWARD','detail':'private'})
        self.assertEqual(state,'executing')
        self.assertEqual(set(metrics),{'percent','current','total','loss'})

    def test_comfy_node_reset_and_disconnect(self):
        bridge=Bridge({'comfyui_url':'http://127.0.0.1:8188'},lambda items:None)
        bridge.comfy_event({'type':'execution_start','data':{'prompt_id':'one'}})
        bridge.comfy_event({'type':'progress','data':{'prompt_id':'one','value':2,'max':4}})
        self.assertEqual(bridge.comfy_step['percent'],50)
        bridge.comfy_event({'type':'progress','data':{'prompt_id':'other','value':4,'max':4}})
        self.assertEqual(bridge.comfy_step['percent'],50)
        bridge.comfy_event({'type':'executing','data':{'prompt_id':'one','node':None}})
        self.assertEqual(bridge.comfy_step,{})
        with patch('local_bridge.urlopen',side_effect=OSError): bridge.comfy()
        self.assertFalse(next(i for i in bridge.snapshot() if i['id']=='comfyui')['available'])

    def test_partial_codex_event_and_finished_training(self):
        with tempfile.TemporaryDirectory() as temporary:
            home=Path(temporary); folder=home/'.codex/sessions'/datetime.now().strftime('%Y/%m/%d')
            folder.mkdir(parents=True); path=folder/'test.jsonl'
            row=json.dumps({'type':'event_msg','payload':{'type':'task_started'}})
            path.write_text(row[:20],encoding='utf-8')
            bridge=Bridge({'training_files':[],'paper_workspace':str(home)},lambda items:None)
            with patch('local_bridge.Path.home',return_value=home):
                bridge.codex()
                with path.open('a',encoding='utf-8') as h:h.write(row[20:]+'\n')
                bridge.codex()
            self.assertEqual(bridge.items['codex']['metrics']['active_sessions'],1)
            (home/'trainer_state.json').write_text(json.dumps({'global_step':4,'max_steps':4}),encoding='utf-8')
            bridge.training()
            self.assertEqual(bridge.items['training']['state'],'idle')
            self.assertEqual(bridge.items['training']['metrics']['percent'],100)

    def test_comfy_extension_keeps_original_delivery_and_filters_data(self):
        sent=[]
        fake=types.SimpleNamespace(send_sync=lambda event,data,sid=None:sent.append((event,data,sid)))
        module=types.ModuleType('server'); module.PromptServer=types.SimpleNamespace(instance=fake)
        path=Path(__file__).resolve().parents[1]/'integrations/comfyui_star_office/__init__.py'
        spec=importlib.util.spec_from_file_location('comfy_test',path); plugin=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'server':module}), patch('threading.Thread.start'):
            spec.loader.exec_module(plugin)
        payload={'value':1,'max':4,'prompt_id':'test','prompt':'private','api_key':'DO_NOT_FORWARD'}
        fake.send_sync('progress',payload,'original-client')
        self.assertIs(sent[0][1],payload)
        self.assertEqual(sent[0][2],'original-client')
        self.assertEqual(plugin.events.get_nowait()['data'],{'value':1,'max':4,'prompt_id':'test'})

    def test_long_active_codex_turn_survives_bridge_restart(self):
        with tempfile.TemporaryDirectory() as temporary:
            home=Path(temporary);folder=home/'.codex/sessions'/datetime.now().strftime('%Y/%m/%d')
            folder.mkdir(parents=True);path=folder/'long.jsonl'
            path.write_text(json.dumps({'type':'event_msg','payload':{'type':'task_started'}})+'\n'+json.dumps({'type':'response_item','payload':'x'*(4*1024*1024+1)})+'\n',encoding='utf-8')
            bridge=Bridge({},lambda items:None)
            with patch('local_bridge.Path.home',return_value=home):bridge.codex()
            self.assertEqual(bridge.items['codex']['metrics']['active_sessions'],1)


if __name__=='__main__': unittest.main()
