"""Windows application entry point for the packaged service and Edge display."""
import os
from pathlib import Path
import subprocess
import sys

from initialize_local import ROOT, initialize


def main():
    os.chdir(ROOT)
    if "--stop" not in sys.argv:
        initialize()
    if "--init-only" in sys.argv:
        return
    if "--server" in sys.argv:
        with (ROOT/".local/server.out.log").open("a", encoding="utf-8", buffering=1) as output, (ROOT/".local/server.err.log").open("a", encoding="utf-8", buffering=1) as errors:
            sys.stdout, sys.stderr = output, errors
            from local_server import main as serve
            serve()
        return
    script = "stop-local.ps1" if "--stop" in sys.argv else "start-local.ps1" if "--browser" in sys.argv else "start-fullscreen.ps1"
    command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(ROOT/script)]
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        # Keep detailed launcher diagnostics local; never display environment values.
        (ROOT/".local/launcher.err.log").write_text(result.stderr, encoding="utf-8")
        if getattr(sys, "frozen", False):
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, "启动失败。请检查 local-config.json 中的端口及 .local/launcher.err.log。\nFailed to start. Check the configured port and local launcher log.", "摸鱼事务所 / Moyu Office", 0x10)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
