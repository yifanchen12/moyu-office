# Moyu Office · 摸鱼事务所

[简体中文](README.md) · [Security policy](SECURITY.md) · [Privacy](PRIVACY.md) · [Attribution](NOTICE.md)

A pixel-art local status dashboard for a Windows secondary display. Development tasks, generation progress, notification signals and system metrics appear as room characters and status cards. A strip above the fireplace scrolls the current NetEase Cloud Music title and artist.

Built on [Star Office UI](https://github.com/ringhyacinth/Star-Office-UI). **Code is MIT-licensed; bundled artwork is non-commercial only.** See [LICENSE](LICENSE), [LICENSE-MOYU](LICENSE-MOYU) and [NOTICE.md](NOTICE.md) for separate terms.

## Capabilities and limits

| Source | Display | Limits |
| --- | --- | --- |
| Codex | Local task lifecycle events | Reads event metadata only; delayed log writes affect freshness; unfinished execution events older than 30 minutes are uncertain |
| DeepSeek Harness (DSH) | turn/start and turn/end in compressed sessions | Does not install DSH or read/configure API credentials; requires Python 3.14 zstd support |
| WeChat and QQ | New Windows notifications or taskbar flashing | No chat text or chat database access; muted messages and tray animations may not be observed |
| BetterGI, SRA, ZZZ OneDragon | Log-based execution, termination and failures; OneDragon pause/resume | Observation only; version-specific markers may change; no reliable overall percentage |
| ComfyUI | Queue and optional forwarded node progress | Node percentage is not total video progress; observer sockets may miss client-targeted events |
| Baidu and Quark cloud drives | Process presence and disk-write activity | Disk writes are not download speed; overall download percentage is unavailable |
| Training | Trainer state or explicit numeric progress files | Execution data older than five minutes is uncertain; cloud files must be synchronized by the user |
| System | CPU, RAM, GPU, VRAM, temperature and total network traffic | NVIDIA metrics require nvidia-smi; aggregate traffic is not per-application speed |
| NetEase Cloud Music | Current song title and artist | Refreshes every five seconds; no playback/pause detection or playback controls |

Missing data is explicitly marked unavailable. Process presence never implies successful task completion.

## Installation

### Windows installer

Download `MoyuOffice-Setup-0.1.0-windows-x64.exe` from [Releases](https://github.com/yifanchen12/moyu-office/releases) and compare its SHA-256 with the same release's `SHA256SUMS.txt`. It installs for the current user without administrator privileges or a separate Python installation.

Requirements: Windows 10/11 x64, Microsoft Edge and Windows PowerShell 5.1. The EXE bundles the local service; the fullscreen display uses a dedicated Edge profile. It does not bundle a browser engine.

Start-menu entries open fullscreen or browser views, stop the service, and uninstall. The first non-primary display is preferred. Press **Alt+F4** to close the fullscreen window; the background service continues until stopped separately. Automatic launch after installation is unchecked by default.

First launch generates private `local-config.json` and random secrets in `.env`, preserving existing settings. Uninstallation preserves user-generated configuration and `.local/` files. Back up and remove the remaining installation directory manually if you want to remove these too. Version 0.1.0 is unsigned; checksums verify integrity and are not a signing identity.

### Portable distribution

Extract `MoyuOffice-0.1.0-windows-x64.zip` to a writable directory and run `MoyuOffice.exe`. Keep the EXE together with its DLLs, assets, scripts and licenses.

### From source

Install Python **3.14** and confirm `python --version`:

```powershell
git clone https://github.com/yifanchen12/moyu-office.git
cd moyu-office
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\start-local.ps1
```

Use `start-fullscreen.ps1` for fullscreen, `start-fullscreen.ps1 -RoomOnly` for the room alone, and `stop-local.ps1` to stop the service. The included `.cmd` entry points apply a process-only execution policy; they do not alter system policy.

Default URL: `http://127.0.0.1:19100/dashboard`. Change `port` in the local configuration if another application occupies it. The launcher does not terminate other applications using the port.

## Configuration

Edit the generated `local-config.json`; see [local-config.example.json](local-config.example.json). Unconfigured installation/log paths leave those tools unavailable. Monitored software is never downloaded or started automatically.

| Field | Purpose |
| --- | --- |
| `port` | Local service port, 1024–65535 |
| `comfyui_url` | Existing ComfyUI address; template uses `http://127.0.0.1:8188` |
| `paper_workspace` | Directory to scan for Trainer progress; empty disables workspace scanning |
| `training_files` | Numeric progress files; relative paths are relative to the application directory |
| `bgi_log_dirs` | BetterGI log directories |
| `sra_root` | SRA installation root; version-directory logs are discovered automatically |
| `onedragon_root` | ZZZ OneDragon root; reads `.log/log.txt` |
| `dsh_homes` | DSH home directories; default `~/.dsh` |

Codex, notifications, music and system metrics use current-user local metadata. No university/provider API configuration is shipped; no LLM API key is required.

### ComfyUI node progress

```powershell
.\安装ComfyUI进度扩展.ps1 -ComfyRoot 'D:\Apps\ComfyUI'
```

Choose the directory containing `server.py` and `custom_nodes`, then restart ComfyUI. The extension preserves original client delivery and asynchronously forwards allowlisted events and numbers without prompts, workflows, previews or error text. Existing extension directories are not overwritten. If the dashboard port changes, set `STAR_OFFICE_URL=http://127.0.0.1:YOUR_PORT` in the ComfyUI launch environment.

### Training

Use [scripts/report_training.py](scripts/report_training.py) in the training environment:

```python
from report_training import report
report('/data/training-progress.json', current=120, total=1000, loss=0.32)
# Report state='idle' after completion.
```

Synchronize this file to a configured local path. Local `POST /local/training` accepts `state`, `current`, `total`, `loss`, `epoch` and `learning_rate`. The project does not create cloud jobs, provision compute or open tunnels.

## Security and privacy

The service binds only to `127.0.0.1`, validates Host and Origin, and rejects cross-site API requests. Private secrets, settings, logs and runtime state are excluded from version control and release packages. Same-machine users and processes remain trusted. **This is not an authenticated gateway or multi-user server.** Do not expose its port or apply upstream public-tunnel examples. See [SECURITY.md](SECURITY.md) for the threat model.

Collected data is not uploaded and chat databases are not read. Session logs are read locally to extract lifecycle markers; prompts, messages and tool arguments are not displayed, copied or forwarded. Edge and monitored applications may have their own network behavior. A configured remote ComfyUI address communicates with that service. See [PRIVACY.md](PRIVACY.md).

## Development and packaging

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/smoke_test.py --base-url http://127.0.0.1:19100
.\scripts\build-windows.ps1 -Compiler 'C:\Tools\Inno Setup 6\ISCC.exe'
```

Windows packaging uses PyInstaller and Inno Setup 6. Build specifications are in `packaging/`; generated binaries stay in ignored `dist/` and `release/` directories. Report vulnerabilities through Security → Report a vulnerability; use sanitized public issues for ordinary bugs. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Future work

Custom cartoon character sheets and animations, and distinct program-specific quotes across task phases. These assets and quotes are not included in this version.
