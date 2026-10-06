"""Forward only task lifecycle and numeric node progress, without workflow/prompt data."""
import json
import os
import queue
import threading
from urllib.request import Request, urlopen

from server import PromptServer

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
EVENTS = {'execution_start', 'progress', 'executing', 'execution_error', 'execution_interrupted'}
events = queue.Queue(maxsize=64)
endpoint = os.environ.get('STAR_OFFICE_URL', 'http://127.0.0.1:19100').rstrip('/')+'/local/comfy'


def forward():
    while True:
        message = events.get()
        try:
            req = Request(endpoint, json.dumps(message).encode(), {'Content-Type': 'application/json'})
            with urlopen(req, timeout=1) as reply: reply.read(64)
        except (OSError, ValueError, TypeError):
            pass  # An offline dashboard must never interrupt generation.
        finally: events.task_done()


server = PromptServer.instance
if not getattr(server, '_star_office_observer', False):
    original_send = server.send_sync

    def observe(event, data, sid=None):
        # Preserve ComfyUI's original client-targeted delivery.
        result = original_send(event, data, sid)
        if event in EVENTS and isinstance(data, dict):
            clean = {k: data[k] for k in ('value', 'max', 'node', 'prompt_id') if k in data}
            try: events.put_nowait({'type': event, 'data': clean})
            except queue.Full: pass
        return result

    server.send_sync = observe
    server._star_office_observer = True
    threading.Thread(target=forward, daemon=True, name='star-office-progress').start()
