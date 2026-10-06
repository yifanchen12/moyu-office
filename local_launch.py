"""Launch known local desktop entry points; browser input is a program ID only."""
import ctypes
import os
from pathlib import Path
import re
import threading
import time
from urllib.parse import urlsplit
from urllib.request import urlopen
import webbrowser

import psutil
from local_bridge import NAMES, PROC_NAMES

SHORTCUT_NAMES = {
    "codex":("codex",), "dsh":("dsh","dshdesktop","dsh桌面版","deepseekdsh"), "wechat":("微信","wechat","weixin"), "qq":("qq",),
    "baidu":("百度网盘","baidunetdisk"), "quark":("夸克","夸克网盘","quark"), "bgi":("bettergi",),
    "sra":("sra","starrailassistant"), "onedragon":("绝区零一条龙","zenlesszonezero-onedragon"),
    "comfyui":("comfyui",),
}


def valid_target(value):
    if not isinstance(value, str) or not value or len(value) > 2048:
        return False
    if any(c in value for c in "\r\n\x00"):
        return False
    if value.startswith("shell:AppsFolder\\"):
        return bool(re.fullmatch(r"shell:AppsFolder\\[A-Za-z0-9_.-]+![A-Za-z0-9_.-]+", value))
    try: url = urlsplit(value)
    except ValueError: return False
    if url.scheme in {"http", "https"}:
        return bool(url.hostname) and not url.username and not url.password
    path = Path(value).expanduser()
    return path.is_absolute() and path.exists() and (path.is_dir() or path.suffix.lower() in {".exe", ".lnk", ".bat", ".cmd"})


class LocalLauncher:
    def __init__(self, config):
        self.config = config
        self.targets = {}
        self.lock = threading.Lock()
        self.last_launch = {}
        self.discover()

    def discover(self):
        home = Path.home()
        shortcut_roots = [home/"Desktop", home/"AppData/Roaming/Microsoft/Windows/Start Menu/Programs",
                          Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))/"Microsoft/Windows/Start Menu/Programs"]
        if os.name == "nt":
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as registry:
                    desktop, _ = winreg.QueryValueEx(registry, "Desktop")
                    shortcut_roots.append(Path(os.path.expandvars(desktop)))
            except OSError: pass
        for root in shortcut_roots:
            for path in sorted(root.rglob("*.lnk")):
                name = path.stem.lower().replace(" ", "")
                for key, names in SHORTCUT_NAMES.items():
                    if name in names:
                        self.targets.setdefault(key, str(path))
        for key, field, filenames in (
            ("sra", "sra_root", ("SRA.exe", "StarRailAssistant.exe")),
            ("onedragon", "onedragon_root", ("OneDragon Launcher.exe", "OneDragon-Launcher.exe", "一条龙启动器.exe")),
        ):
            folder = self.config.get(field)
            if folder:
                for filename in filenames:
                    path = Path(folder)/filename
                    if path.is_file(): self.targets.setdefault(key, str(path))
                if key == "sra":
                    versions = sorted(Path(folder).glob("v*/SRA.exe"), key=lambda p:p.stat().st_mtime, reverse=True)
                    if versions: self.targets.setdefault(key, str(versions[0]))
        for log_dir in self.config.get("bgi_log_dirs", []):
            path = Path(log_dir).parent/"BetterGI.exe"
            if path.is_file(): self.targets.setdefault("bgi", str(path))
        workspace = self.config.get("paper_workspace")
        self.targets["training"] = workspace if workspace and Path(workspace).is_dir() else "https://discovery.intern-ai.org.cn"
        self.targets.setdefault("comfyui", self.config.get("comfyui_url", "http://127.0.0.1:8188"))
        taskmgr = Path(os.environ.get("WINDIR", r"C:\Windows"))/"System32/Taskmgr.exe"
        if taskmgr.is_file(): self.targets["system"] = str(taskmgr)
        # Explicit local settings win. An invalid entry disables that button.
        for key, value in self.config.get("launch_targets", {}).items():
            if key in NAMES: self.targets[key] = value

    def info(self, key):
        target = self.targets.get(key)
        available = valid_target(target)
        label = "打开训练入口" if key == "training" else "打开任务管理器" if key == "system" else "启动软件"
        if key == "comfyui" and isinstance(target, str) and target.startswith(("http://", "https://")):
            label = "打开 ComfyUI"
        return {"available":available, "label":label,
                "reason":"" if available else "未找到软件入口，请在 local-config.json 的 launch_targets 中填写本机路径"}

    def focus_existing(self, key):
        if os.name != "nt": return False
        names = set(PROC_NAMES.get(key, set()))
        names.update({"codex.exe"} if key == "codex" else {"dsh.exe", "deepseek harness.exe"} if key == "dsh" else set())
        if not names: return False
        pids = {p.info["pid"] for p in psutil.process_iter(["name", "pid"]) if (p.info["name"] or "").lower() in names}
        if not pids: return False
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.IsWindowVisible.argtypes = [wintypes.HWND]
        user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
        user32.GetWindow.restype = wintypes.HWND
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        found = []
        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        @callback_type
        def visit(window, unused):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(window, ctypes.byref(pid))
            if pid.value in pids and user32.IsWindowVisible(window) and not user32.GetWindow(window, 4):
                found.append(window)
                return False
            return True
        user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
        user32.EnumWindows(visit, 0)
        if not found: return False
        user32.ShowWindow(found[0], 9)
        user32.SetForegroundWindow(found[0])
        return True

    def launch(self, key):
        if key not in NAMES: return False, "未知软件", 400
        info = self.info(key)
        if not info["available"]: return False, info["reason"], 409
        with self.lock:
            if time.monotonic()-self.last_launch.get(key, -10) < 2:
                return False, "请稍候再点击", 429
            target = self.targets[key]
            try:
                if key == "comfyui":
                    url = self.config.get("comfyui_url", "http://127.0.0.1:8188").rstrip("/")
                    if valid_target(url):
                        try:
                            with urlopen(url+'/system_stats', timeout=1) as response:
                                if response.status == 200: target = url
                        except (OSError, ValueError): pass
                if not self.focus_existing(key):
                    if target.startswith(("http://", "https://")):
                        if not webbrowser.open(target): raise OSError()
                    else:
                        # ShellExecute opens a configured entry point; no shell command is assembled.
                        target = target if target.startswith("shell:") else str(Path(target).expanduser())
                        os.startfile(target, cwd=str(Path(target).parent) if not target.startswith("shell:") else None)
                self.last_launch[key] = time.monotonic()
                return True, "已发送打开请求；自动化与训练任务需在软件内启动", 200
            except (OSError, ValueError, psutil.Error, webbrowser.Error):
                return False, "无法打开软件，请检查本机路径或快捷方式", 503
