"""Initialize private runtime files without replacing existing user settings."""
import json
from pathlib import Path
import secrets
import sys
from urllib.parse import urlparse

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def initialize(root=ROOT):
    root = Path(root)
    (root/".local").mkdir(exist_ok=True)
    for filename, sample in (("local-config.json", "local-config.example.json"), ("state.json", "state.sample.json")):
        target = root/filename
        if not target.exists():
            with target.open("x", encoding="utf-8") as handle:
                handle.write((root/sample).read_text(encoding="utf-8"))
    target = root/".env"
    if not target.exists():
        with target.open("x", encoding="utf-8") as handle:
            handle.write(f"FLASK_SECRET_KEY={secrets.token_urlsafe(48)}\nASSET_DRAWER_PASS={secrets.token_urlsafe(24)}\nSTAR_OFFICE_ENV=local\n")
    config = json.loads((root/"local-config.json").read_text(encoding="utf-8"))
    port = config.get("port")
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("port must be an integer between 1024 and 65535")
    address = urlparse(config.get("comfyui_url", ""))
    if address.scheme not in {"http", "https"} or not address.hostname or address.username or address.password:
        raise ValueError("comfyui_url must be HTTP(S) without embedded credentials")
    return config


if __name__ == "__main__":
    initialize()
    print("Local configuration initialized; existing files preserved.")
