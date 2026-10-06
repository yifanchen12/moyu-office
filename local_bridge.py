"""Read-only collectors. Only lifecycle metadata and numeric progress reach the UI."""
from __future__ import annotations

import copy
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

import psutil
import websocket

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
NAMES = {"codex": "Codex", "dsh": "DSH", "wechat": "微信", "qq": "QQ",
         "training": "论文任务", "baidu": "百度网盘", "quark": "夸克网盘",
         "bgi": "BetterGI", "sra": "SRA", "onedragon": "绝区零一条龙",
         "comfyui": "ComfyUI", "system": "电脑性能"}
PROC_NAMES = {"wechat": {"weixin.exe", "wechat.exe"}, "qq": {"qq.exe"},
              "baidu": {"baidunetdisk.exe"}, "quark": {"quarkclouddrive.exe", "quark.exe"},
              "bgi": {"bettergi.exe"}, "sra": {"sra.exe", "sra-cli.exe", "sra-server.exe"},
              "onedragon": {"onedragon-launcher.exe", "onedragon.exe"}}
VALID_STATES = {"idle", "writing", "researching", "executing", "syncing", "error"}


def progress(current, total):
    if isinstance(current, bool) or isinstance(total, bool):
        raise ValueError("progress must be numeric")
    current, total = float(current), float(total)
    if not (0 <= current <= total and total > 0):
        raise ValueError("invalid progress bounds")
    return round(current / total * 100, 1)


def lifecycle(row, previous="idle", dsh=False):
    if dsh:
        event = row.get("type")
    else:
        if row.get("type") != "event_msg":
            return previous
        event = row.get("payload", {}).get("type")
    if event in {"task_started", "turn/start"}:
        return "executing"
    if event in {"task_complete", "turn/end", "turn_aborted"}:
        return "idle"
    if event in {"turn/error", "task_failed"}:
        return "error"
    return previous


def safe_training(data):
    # Allowlisted numeric fields only: never forward an arbitrary log or task description.
    state = data.get("state", "executing")
    if state not in VALID_STATES:
        raise ValueError("invalid training state")
    metrics = {}
    if "current" in data or "total" in data:
        metrics["percent"] = progress(data["current"], data["total"])
        metrics["current"], metrics["total"] = float(data["current"]), float(data["total"])
    for key in ("loss", "epoch", "learning_rate"):
        if key in data:
            value = float(data[key])
            if not (-1e20 < value < 1e20):
                raise ValueError("invalid metric")
            metrics[key] = value
    return state, metrics


def read_tail(path, size=262144):
    with path.open("rb") as handle:
        length = path.stat().st_size
        handle.seek(max(0, length-size))
        if length > size:
            handle.readline()
        return handle.read().decode("utf-8", errors="replace")


def automation_event(line, key, phase="unknown"):
    """Recognize observed lifecycle markers, never return raw log contents."""
    if key == "sra":
        if "TaskManager thread started" in line or "重新开始执行" in line:
            return "running"
        if re.search(r"任务 .*失败。停止进一步执行", line):
            return "error"
        if "TaskManager thread stopped" in line or "event listener stopped" in line:
            return "error" if phase == "error" else "finished"
    else:
        root = re.search(r"指令\[\s*(一条龙|执行应用组 [^\]]+)\s*\]\s+执行(成功|失败)", line)
        if root:
            return "finished" if root[2] == "成功" or "人工结束" in line else "error"
        if "恢复运行" in line:
            return "running"
        if "暂停运行" in line:
            return phase if phase in {"finished", "error"} else "paused"
        if re.search(r"(运行应用 .*失败|运行前初始化失败|创建应用 .*失败)", line):
            return "error"
        if "[operation.py " in line and " 节点 " in line and " 返回状态 " in line:
            return "paused" if phase == "paused" else "running"
    return phase


class Bridge:
    def __init__(self, config, publish):
        self.config, self.publish = config, publish
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.items = {}
        self.codex_cache, self.dsh_cache = {}, {}
        self.proc = {}
        self.proc_io = {}
        self.automation_cache = {}
        self.music_info = {"available": False, "title": "", "artist": "", "source": "正在检查"}
        self.notifications = {}
        self.notification_ids = None
        self.shell_hook = False
        self.comfy_step = {}
        self.comfy_prompt = None
        self.comfy_error = False
        self.comfy_ws_online = False
        self.comfy_forwarded_at = 0
        self.last_net = (time.monotonic(), psutil.net_io_counters())
        for key in NAMES:
            self.set(key, "idle", "正在检查数据来源", "初始化", available=False)

    def set(self, key, state, detail, source, metrics=None, available=True):
        item = {"id": key, "name": NAMES[key], "state": state, "detail": detail,
                "source": source, "metrics": metrics or {}, "available": available,
                "updated_at": datetime.now().astimezone().isoformat()}
        with self.lock:
            self.items[key] = item

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(list(self.items.values()))

    def music_snapshot(self):
        with self.lock:
            return copy.deepcopy(self.music_info)

    def loop(self, collector, delay):
        while not self.stop.is_set():
            try:
                collector()
            except Exception as error:
                # Exception strings may contain URLs or tokens. Log only the class.
                print(f"Collector {collector.__name__}: {type(error).__name__}", flush=True)
                key = "system" if collector.__name__ == "performance" else collector.__name__
                if key in NAMES:
                    self.set(key, "idle", "读取失败；当前状态待确认", type(error).__name__, available=False)
            self.stop.wait(delay)

    def start(self):
        for fn, delay in [(self.performance, 3), (self.processes, 5), (self.codex, 3),
                          (self.dsh, 5), (self.bgi, 5), (self.sra, 5), (self.onedragon, 5),
                          (self.music, 5), (self.training, 8),
                          (self.comfy, 4), (self.notification_poll, 3), (self.project, 5)]:
            threading.Thread(target=self.loop, args=(fn, delay), daemon=True).start()
        threading.Thread(target=self.comfy_socket, daemon=True).start()
        if os.name == "nt":
            threading.Thread(target=self.windows_flash, daemon=True).start()

    def project(self):
        self.publish(self.snapshot())

    def performance(self):
        cpu = psutil.cpu_percent(interval=0.25)
        ram = psutil.virtual_memory()
        now, net = time.monotonic(), psutil.net_io_counters()
        previous_time, previous = self.last_net
        seconds = max(now-previous_time, 0.1)
        metrics = {"cpu_percent": cpu, "ram_percent": ram.percent,
                   "ram_used_gb": round(ram.used/2**30, 1), "ram_total_gb": round(ram.total/2**30, 1),
                   "rx_kbps": round(max(0, net.bytes_recv-previous.bytes_recv)/seconds/1024, 1),
                   "tx_kbps": round(max(0, net.bytes_sent-previous.bytes_sent)/seconds/1024, 1)}
        self.last_net = (now, net)
        try:
            gpu = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                                  "--format=csv,noheader,nounits"], capture_output=True, text=True,
                                 timeout=3, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            values = [int(x.strip()) for x in gpu.stdout.splitlines()[0].split(",")]
            metrics.update(dict(zip(("gpu_percent", "vram_used_mb", "vram_total_mb", "gpu_temp_c"), values)))
        except (OSError, subprocess.SubprocessError, ValueError, IndexError):
            pass
        self.set("system", "executing" if cpu > 80 else "idle",
                 f"CPU {cpu:.0f}% · 内存 {ram.percent:.0f}%", "psutil / NVIDIA 驱动", metrics)

    def processes(self):
        groups = {key: [] for key in PROC_NAMES}
        for p in psutil.process_iter(["name", "pid"]):
            for key, names in PROC_NAMES.items():
                if (p.info["name"] or "").lower() in names:
                    groups[key].append(p)
            if (p.info["name"] or "").lower() in {"python.exe", "pythonw.exe"}:
                try:
                    root = self.config.get("onedragon_root", "")
                    if root and any(root.lower() in arg.lower().replace("/", "\\") for arg in [p.exe(), *p.cmdline()]):
                        groups["onedragon"].append(p)
                except psutil.Error:
                    pass
        self.proc = groups
        for key in ("baidu", "quark"):
            procs = groups[key]
            if not procs:
                self.set(key, "idle", "客户端未运行", "Windows 进程检测", available=False)
                continue
            total = 0
            readable = False
            for p in procs:
                try:
                    io = p.io_counters()
                    total += io.write_bytes
                    readable = True
                except psutil.Error:
                    pass
            previous = self.proc_io.get(key)
            now = time.monotonic()
            rate = max(0, total-previous[1]) / max(.1, now-previous[0]) / 1024 if previous else 0
            self.proc_io[key] = (now, total)
            self.set(key, "syncing" if rate > 64 else "idle",
                     "客户端运行中；下载百分比尚不可读", "进程 / 磁盘写入（不等于下载速度）",
                     {"processes": len(procs), "disk_write_kbps": round(rate, 1)} if readable else {})
        for key in ("wechat", "qq"):
            procs = groups[key]
            stamp = self.notifications.get(key, 0)
            recent = stamp > time.time()-60
            self.set(key, "syncing" if recent else "idle",
                     "收到新消息提醒" if recent else ("运行中；等待新消息信号" if procs else "客户端未运行"),
                     "系统通知元数据 / 任务栏闪烁（不读取正文）",
                     {"last_alert_at": datetime.fromtimestamp(stamp).astimezone().isoformat() if stamp else None,
                      "shell_hook": self.shell_hook,
                      "limit": "仅覆盖系统通知和任务栏闪烁；托盘动画/静音消息未覆盖"}, bool(procs))

    def codex(self):
        folder = Path.home()/".codex/sessions"
        today = datetime.now()
        days = [today, datetime.fromtimestamp(time.time()-86400)]
        files = []
        for day in days:
            directory = folder / day.strftime("%Y/%m/%d")
            files.extend(directory.glob("*.jsonl"))
        files = sorted(set(files), key=lambda p: p.stat().st_mtime, reverse=True)[:48]
        active, errors, stale = 0, 0, 0
        for path in files:
            stat = path.stat()
            cached = self.codex_cache.get(str(path), (0, "idle"))
            state = cached[1]
            if stat.st_size != cached[0]:
                with path.open("rb") as h:
                    start = cached[0] if cached[0] <= stat.st_size else 0
                    h.seek(start)
                    # Initial scan needs the start of long turns; a bounded tail
                    # can miss task_started and incorrectly show an active task idle.
                    offset = start
                    for line in h:
                        if not line.endswith(b'\n'): break
                        if b'"event_msg"' in line:
                            try: state = lifecycle(json.loads(line), state)
                            except (ValueError, TypeError, AttributeError): pass
                        offset = h.tell()
                self.codex_cache[str(path)] = (offset, state)
            if time.time()-stat.st_mtime > 1800 and state == "executing":
                stale += 1
            elif state == "executing":
                active += 1
            elif state == "error":
                errors += 1
        detail = f"{active} 个会话正在执行" if active else ("存在尚未收到结束事件的会话" if stale else "已观察会话暂无执行事件")
        if stale: detail += f"；{stale} 个旧会话状态待确认"
        self.set("codex", "executing" if active else ("error" if errors else "idle"), detail,
                 "本机任务生命周期 JSONL（桌面 / CLI）",
                 {"active_sessions": active, "uncertain_sessions": stale, "observed_sessions": len(files)}, bool(files))

    def dsh(self):
        from compression import zstd
        active, recent, uncertain = 0, 0, 0
        for home in self.config["dsh_homes"]:
            folder = Path(home).expanduser()/"sessions"
            files = sorted(folder.rglob("*.jsonl.zstd"), key=lambda p:p.stat().st_mtime, reverse=True)[:24]
            for path in files:
                stat = path.stat()
                if time.time()-stat.st_mtime > 86400: continue
                recent += 1
                cached = self.dsh_cache.get(str(path), (0, "idle"))
                state = cached[1]
                if cached[0] != stat.st_size:
                    try:
                        state = "idle"
                        with zstd.open(path, "rt", encoding="utf-8") as h:
                            for line in h:
                                try: state = lifecycle(json.loads(line), state, dsh=True)
                                except ValueError: pass
                    except (OSError, EOFError, zstd.ZstdError):
                        # An active writer may leave a partial final frame.
                        pass
                    self.dsh_cache[str(path)] = (stat.st_size, state)
                if state == "executing":
                    if time.time()-stat.st_mtime > 1800: uncertain += 1
                    else: active += 1
        self.set("dsh", "executing" if active else "idle",
                 f"{active} 个会话正在执行" if active else "没有正在执行的已观察会话",
                 "DSH 本地 turn/start、turn/end 元数据",
                 {"active_sessions": active, "observed_sessions": recent, "uncertain_sessions": uncertain}, bool(recent))

    def bgi(self):
        files = []
        for directory in self.config["bgi_log_dirs"]:
            files.extend(Path(directory).glob("*.log"))
        if not files:
            self.set("bgi", "idle", "未找到 BetterGI 日志", "日志目录", available=False)
            return
        latest = max(files, key=lambda p:p.stat().st_mtime)
        age = time.time()-latest.stat().st_mtime
        lines = read_tail(latest).splitlines()
        state, event = "idle", "近期没有任务事件"
        # Read only task-lifecycle lines. Ordinary log chatter is not task completion.
        for line in lines:
            if re.search(r"(任务|脚本|调度|一条龙).*(开始|启动)|开始.*(任务|脚本|调度|一条龙)", line):
                state, event = "executing", "任务开始"
            if re.search(r"(任务|脚本|调度|一条龙).*(完成|结束|停止)|结束.*(任务|脚本)", line):
                state, event = "idle", "任务已结束"
            if re.search(r"(任务|脚本|调度).*(异常|失败)", line):
                state, event = "error", "任务异常"
        if age > 1800:
            state, event = "idle", "日志较旧；当前任务状态待确认"
        self.set("bgi", state, event, "BetterGI 任务日志（主桌面 / 分身）",
                 {"log_age_seconds": round(age), "log_file": latest.name,
                  "processes": len(self.proc.get("bgi", [])), "limit": "日志关键字识别；日志未落盘期间状态可能延迟"})

    def sra(self):
        self.automation("sra")

    def onedragon(self):
        self.automation("onedragon")

    def automation(self, key):
        files = []
        if key == "sra":
            location = self.config.get("sra_root")
            if not location:
                self.set(key, "idle", "请配置 SRA 安装目录", "本机配置", available=False)
                return
            root = Path(location)
            folders = [root/"log", *root.glob("*/log")]
            for folder in folders:
                files.extend(folder.glob("SRA*.log"))
        else:
            location = self.config.get("onedragon_root")
            if not location:
                self.set(key, "idle", "请配置绝区零一条龙安装目录", "本机配置", available=False)
                return
            root = Path(location)
            files = list((root/".log").glob("log.txt*"))
        if not files:
            self.set(key, "idle", "未找到任务日志", "本地任务日志", available=False)
            return
        latest = max(files, key=lambda p: p.stat().st_mtime)
        stat = latest.stat()
        offset, phase = self.automation_cache.get(str(latest), (0, "unknown"))
        if stat.st_size < offset:
            offset, phase = 0, "unknown"
        with latest.open("rb") as handle:
            handle.seek(offset)
            for line in handle:
                if not line.endswith(b"\n"):
                    break
                phase = automation_event(line.decode("utf-8", errors="replace"), key, phase)
                offset = handle.tell()
        self.automation_cache[str(latest)] = (offset, phase)
        age = time.time()-stat.st_mtime
        running = bool(self.proc.get(key))
        if phase in {"running", "paused", "error"} and age > 1800:
            phase = "unknown"
        if not running:
            phase = "closed"
        detail = {"running": "正在执行任务", "paused": "任务已暂停", "finished": "最近任务已结束",
                  "error": "任务异常", "unknown": "程序运行中；任务状态待确认", "closed": "程序未运行"}[phase]
        state = "executing" if phase == "running" else "error" if phase == "error" else "idle"
        self.set(key, state, detail, f"{NAMES[key]} 本机 / 分身任务日志",
                 {"phase": phase, "log_age_seconds": round(age), "processes": len(self.proc.get(key, []))}, running)

    def music(self):
        info = {"available": False, "title": "", "artist": "", "source": "网易云尚无歌曲信息"}
        try:
            powershell = Path(os.environ.get("SystemRoot", "C:/Windows"))/"System32/WindowsPowerShell/v1.0/powershell.exe"
            result = subprocess.run([str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                     "-File", str(ROOT/"scripts/read_music.ps1")], capture_output=True,
                                    encoding="utf-8-sig", timeout=8,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            data = json.loads(result.stdout) if result.returncode == 0 else {}
            if data.get("available") and isinstance(data.get("title"), str) and data["title"].strip():
                info = {"available": True, "title": data["title"][:256], "artist": str(data.get("artist", ""))[:256],
                        "source": "Windows 媒体会话" if data.get("source") == "smtc" else "网易云窗口标题"}
        except (OSError, subprocess.SubprocessError, ValueError, TypeError, AttributeError):
            pass
        with self.lock:
            self.music_info = info

    def training(self):
        paths = [ROOT/Path(f) if not Path(f).is_absolute() else Path(f) for f in self.config["training_files"]]
        paper = Path(self.config["paper_workspace"]) if self.config.get("paper_workspace") else None
        if paper:
            paths.extend(paper.rglob("trainer_state.json"))
            paths.extend(paper.rglob("training-progress.json"))
        existing = [p for p in paths if p.is_file()]
        if existing:
            path = max(existing, key=lambda p:p.stat().st_mtime)
            data = json.loads(path.read_text(encoding="utf-8"))
            if path.name == "trainer_state.json":
                data = {"state": "idle" if data["global_step"] >= data["max_steps"] else "executing", "current": data["global_step"], "total": data["max_steps"],
                        **({"loss": data["log_history"][-1]["loss"]} if data.get("log_history") and "loss" in data["log_history"][-1] else {})}
            state, metrics = safe_training(data)
            age = time.time()-path.stat().st_mtime
            if age > 300 and state in {"executing", "writing"}:
                self.set("training", "idle", "进度超过 5 分钟未更新；任务状态待确认", "训练进度文件", metrics, False)
                return
            self.set("training", state, f"训练进度 {metrics['percent']}%" if "percent" in metrics else "训练状态已更新",
                     "训练进度文件 / Hugging Face Trainer", metrics)
            return
        self.set("training", "idle", "尚未连接训练进度", "训练进度文件检查", available=False)

    def comfy_event(self, message):
        kind, data = message.get("type"), message.get("data", {})
        with self.lock:
            prompt = data.get("prompt_id")
            if kind == "execution_start":
                self.comfy_prompt, self.comfy_step, self.comfy_error = prompt, {}, False
                self.comfy_forwarded_at = time.time()
            elif kind == "progress":
                if prompt and self.comfy_prompt and prompt != self.comfy_prompt: return
                try:
                    self.comfy_step = {"current": data["value"], "total": data["max"],
                                       "percent": progress(data["value"], data["max"]), "scope": "当前节点 / 采样步骤"}
                    self.comfy_forwarded_at = time.time()
                except (ValueError, KeyError, TypeError): pass
            elif kind == "executing":
                if prompt and self.comfy_prompt and prompt != self.comfy_prompt: return
                if data.get("node") is None:
                    self.comfy_step, self.comfy_prompt = {}, None
                else:
                    self.comfy_step = {"node": str(data["node"]), "scope": "当前节点"}
            elif kind in {"execution_error", "execution_interrupted"}:
                if prompt and self.comfy_prompt and prompt != self.comfy_prompt: return
                self.comfy_error, self.comfy_step = True, {}

    def comfy_socket(self):
        while not self.stop.is_set():
            socket = None
            try:
                url = self.config["comfyui_url"].replace("http://", "ws://").replace("https://", "wss://")+"/ws"
                socket = websocket.create_connection(url, timeout=5, http_proxy_host=None)
                self.comfy_ws_online = True
                while not self.stop.is_set():
                    try: data = socket.recv()
                    except websocket.WebSocketTimeoutException: continue
                    if not data: break
                    if isinstance(data, str):
                        self.comfy_event(json.loads(data))
            except (OSError, ValueError, websocket.WebSocketException):
                pass
            finally:
                self.comfy_ws_online = False
                if socket: socket.close()
            self.stop.wait(5)

    def comfy(self):
        try:
            with urlopen(self.config["comfyui_url"]+"/queue", timeout=2) as r:
                queue = json.load(r)
            running, pending = len(queue.get("queue_running", [])), len(queue.get("queue_pending", []))
            with self.lock: metrics = dict(self.comfy_step)
            if metrics and time.time()-self.comfy_forwarded_at > 120:
                metrics = {}
            if not running: metrics = {}
            metrics.update({"running": running, "pending": pending, "websocket": self.comfy_ws_online})
            state = "executing" if running else ("error" if self.comfy_error else "idle")
            detail = f"执行 {running} · 排队 {pending}"
            if "percent" in metrics: detail += f" · 当前节点 {metrics['percent']}%"
            elif running: detail += " · 节点进度尚未接入"
            self.set("comfyui", state, detail, "ComfyUI /queue + /ws（节点进度）", metrics)
        except (OSError, ValueError):
            with self.lock: self.comfy_step = {}
            self.set("comfyui", "idle", "ComfyUI 未启动或地址不可连接", self.config["comfyui_url"], available=False)

    def notification_poll(self):
        database = Path.home()/"AppData/Local/Microsoft/Windows/Notifications/wpndatabase.db"
        if not database.exists(): return
        try:
            with sqlite3.connect(database.as_uri()+"?mode=ro", uri=True, timeout=.5) as con:
                handlers = dict(con.execute("select RecordId, PrimaryId from NotificationHandler"))
                rows = list(con.execute("select Id, HandlerId from Notification"))
            ids = {row[0] for row in rows}
            if self.notification_ids is not None:
                for ident, handler in rows:
                    if ident in self.notification_ids: continue
                    appid = str(handlers.get(handler, "")).lower()
                    for key, patterns in (("wechat", ("weixin", "wechat")), ("qq", ("tencent.qq", "qq.exe"))):
                        if any(x in appid for x in patterns): self.notifications[key] = time.time()
            self.notification_ids = ids
        except (sqlite3.Error, OSError):
            pass

    def windows_flash(self):
        # Shell events expose only an HWND, never message text or a chat database.
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        result_type = ctypes.c_ssize_t
        callback_type = ctypes.WINFUNCTYPE(result_type, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32.DefWindowProcW.restype = result_type
        user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.CreateWindowExW.restype = wintypes.HWND
        user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                         wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        hookmsg = user32.RegisterWindowMessageW("SHELLHOOK")
        def callback(hwnd, msg, wparam, lparam):
            if msg == hookmsg and wparam == 0x8006:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(wintypes.HWND(lparam), ctypes.byref(pid))
                try:
                    name = psutil.Process(pid.value).name().lower()
                    for key in ("wechat", "qq"):
                        if name in PROC_NAMES[key]: self.notifications[key] = time.time()
                except psutil.Error: pass
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        callback_fn = callback_type(callback)
        class WNDCLASS(ctypes.Structure):
            _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", callback_type),
                        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                        ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                        ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]
        instance = kernel32.GetModuleHandleW(None)
        cls = WNDCLASS(0, callback_fn, 0, 0, instance, None, None, None, None, "StarOfficeNotificationObserver")
        if not user32.RegisterClassW(ctypes.byref(cls)): return
        hwnd = user32.CreateWindowExW(0x80, cls.lpszClassName, "", 0, 0, 0, 0, 0, None, None, instance, None)
        if not hwnd: return
        self.shell_hook = bool(user32.RegisterShellHookWindow(wintypes.HWND(hwnd)))
        msg = wintypes.MSG()
        while not self.stop.is_set():
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(msg)); user32.DispatchMessageW(ctypes.byref(msg))
            self.stop.wait(.2)
        user32.DeregisterShellHookWindow(wintypes.HWND(hwnd)); user32.DestroyWindow(wintypes.HWND(hwnd))
