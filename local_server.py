"""Loopback-only wrapper for the source and packaged Moyu Office application."""
import json
import os
from pathlib import Path
import secrets
import sys
import threading

from initialize_local import ROOT, initialize
config = initialize()
os.environ["MOYU_OFFICE_ROOT"] = str(ROOT)
sys.path.insert(0, str(ROOT/"backend"))
for line in (ROOT/".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)

from flask import g, jsonify, request, send_from_directory
import app as upstream
from local_bridge import Bridge, safe_training
from security_utils import is_strong_secret, is_strong_drawer_pass

app = upstream.app
if not is_strong_secret(upstream.app.secret_key) or not is_strong_drawer_pass(upstream.ASSET_DRAWER_PASS_DEFAULT):
    raise RuntimeError("Configure strong local secrets in .env; values are never logged")
upstream.MEMORY_DIR = str(ROOT/".local/memory")
upstream.IDENTITY_FILE = str(ROOT/".local/IDENTITY.md")
BASE_URL = f"http://127.0.0.1:{config['port']}"
ALLOWED_HOSTS = {f"127.0.0.1:{config['port']}", f"localhost:{config['port']}"}
ALLOWED_ORIGINS = {f"http://{host}" for host in ALLOWED_HOSTS}
mutation_lock = threading.RLock()
join_key = secrets.token_urlsafe(32)
agent_ids = {}


@app.before_request
def lock_state_files():
    if request.host not in ALLOWED_HOSTS:
        return jsonify({"error": "Invalid local Host"}), 403
    if not valid_origin():
        return jsonify({"error": "Foreign Origin is not allowed"}), 403
    if request.headers.get("Sec-Fetch-Site") == "cross-site" and request.path not in {"/", "/dashboard", "/local/office"}:
        return jsonify({"error": "Cross-site API access is not allowed"}), 403
    # ponytail: serialize upstream file writes; per-file locks if throughput matters.
    if request.path in {"/agents", "/status", "/set_state", "/join-agent", "/agent-push",
                        "/leave-agent", "/agent-approve", "/agent-reject", "/local/training"}:
        mutation_lock.acquire()
        g.local_state_lock = True


@app.teardown_request
def unlock_state_files(error):
    if g.pop("local_state_lock", False):
        mutation_lock.release()


def project(items):
    with mutation_lock:
        with app.test_client() as client:
            for item in items:
                if item["id"] == "system":
                    client.post("/set_state", json={"state": item["state"], "detail": item["detail"]}, base_url=BASE_URL)
                    continue
                name = item["name"]
                payload = {"name": name, "state": item["state"], "detail": item["detail"], "joinKey": join_key}
                if name in agent_ids:
                    payload["agentId"] = agent_ids[name]
                    result = client.post("/agent-push", json=payload, base_url=BASE_URL)
                    if result.status_code == 200: continue
                result = client.post("/join-agent", json=payload, base_url=BASE_URL)
                if result.status_code == 200: agent_ids[name] = result.json["agentId"]


bridge = Bridge(config, project)


@app.route("/dashboard")
def dashboard():
    return send_from_directory(upstream.FRONTEND_DIR, "local-dashboard.html")


@app.route("/local/office")
def office_view():
    response = upstream.index()
    # Display-only adaptation of the original scene; its source remains intact.
    css = '<style>body{padding:0!important;overflow:hidden!important;gap:0!important}#main-stage,#game-container{width:100vw!important;max-width:100vw!important}#game-container{height:100vh!important;max-height:none!important}#bottom-panels,#coords-toggle,#pan-toggle,#lang-toggle-group{display:none!important}</style>'
    html = response.get_data(as_text=True).replace('</head>', css+'</head>', 1)
    html = html.replace('海辛小龙虾的办公室', '摸鱼事务所').replace('Star 的像素办公室', '摸鱼事务所')
    music_version = (ROOT/'frontend/local-music.js').stat().st_mtime_ns
    response.set_data(html.replace('</body>', f'<script src="/static/local-music.js?v={music_version}"></script></body>', 1))
    return response


@app.route("/local/status")
def local_status():
    return jsonify({"application": "moyu-office", "version": "0.1.0", "items": bridge.snapshot(), "music": bridge.music_snapshot(), "port": config["port"]})


def valid_origin():
    origin = request.headers.get("Origin")
    return origin is None or origin in ALLOWED_ORIGINS


@app.route("/local/training", methods=["POST"])
def training_update():
    if not valid_origin(): return jsonify({"ok": False}), 403
    if request.content_length and request.content_length > 4096:
        return jsonify({"ok": False}), 413
    try:
        data = request.get_json()
        if not isinstance(data, dict): raise ValueError("invalid JSON")
        state, metrics = safe_training(data)
        clean = {"state": state, **{k:v for k,v in metrics.items() if k != "percent"}}
        folder = ROOT/".local"; folder.mkdir(exist_ok=True)
        temporary = folder/"training-progress.tmp"
        temporary.write_text(json.dumps(clean), encoding="utf-8")
        temporary.replace(folder/"training-progress.json")
        bridge.training()
        return jsonify({"ok": True})
    except (ValueError, TypeError, KeyError):
        return jsonify({"ok": False, "error": "需要有效 state、current/total 或数值指标"}), 400


@app.route("/local/comfy", methods=["POST"])
def comfy_update():
    if not valid_origin(): return jsonify({"ok": False}), 403
    if request.content_length and request.content_length > 4096: return jsonify({"ok": False}), 413
    try:
        message = request.get_json()
        kind = message["type"]
        if kind not in {"execution_start", "progress", "executing", "execution_error", "execution_interrupted"}:
            raise ValueError("unknown event")
        data = message.get("data", {})
        if not isinstance(data, dict): raise ValueError("invalid data")
        clean = {k: data[k] for k in ("value", "max", "node", "prompt_id") if k in data}
        for k in ("node", "prompt_id"):
            if k in clean and clean[k] is not None and (not isinstance(clean[k], str) or len(clean[k]) > 100):
                raise ValueError("invalid metadata")
        if kind == "progress":
            from local_bridge import progress
            progress(clean["value"], clean["max"])
        bridge.comfy_event({"type": kind, "data": clean})
        import time
        bridge.comfy_forwarded_at = time.time()
        return jsonify({"ok": True})
    except (ValueError, TypeError, KeyError):
        return jsonify({"ok": False}), 400


def main():
    keys = upstream.load_join_keys()
    # Reusable private bridge key; no need to display it or configure upstream manually.
    keys["keys"] = [k for k in keys.get("keys", []) if k.get("label") != "local-status-bridge"]
    keys["keys"].append({"key": join_key, "label": "local-status-bridge", "maxConcurrent": 16, "reusable": True})
    upstream.save_join_keys(keys)
    bridge.start()
    app.run(host="127.0.0.1", port=config["port"], threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
