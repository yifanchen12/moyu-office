from pathlib import Path
from importlib.util import find_spec
from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH).parent
data = [(str(root/'licenses'), 'licenses'), (str(root/'integrations'), 'integrations')]
for path in (root/'frontend').rglob('*'):
    if path.is_file() and path.name != 'electron-standalone.html' and '__pycache__' not in path.parts:
        data.append((str(path), str(path.relative_to(root).parent)))
for name in ('local-config.example.json', '.env.example', 'state.sample.json', 'asset-positions.json', 'asset-defaults.json', 'LICENSE', 'NOTICE.md', 'LICENSE-MOYU', 'README.md', 'README.en.md', 'SECURITY.md', 'SECURITY.zh-CN.md', 'PRIVACY.md', 'THIRD_PARTY_NOTICES.md', 'start-local.ps1', 'stop-local.ps1', 'start-fullscreen.ps1', 'scripts/read_music.ps1', 'scripts/report_training.py', '安装ComfyUI进度扩展.ps1'):
    data.append((str(root/name), str(Path(name).parent)))
for package in ('flask', 'werkzeug', 'jinja2', 'markupsafe', 'itsdangerous', 'click', 'blinker', 'pillow', 'psutil', 'websocket-client', 'pyyaml', 'setuptools', 'packaging'):
    data += copy_metadata(package)
# The Flask CLI fallback makes PyInstaller collect setuptools vendor modules.
# Keep their own metadata and licenses alongside the bundled code.
vendor = Path(find_spec('setuptools').origin).parent/'_vendor'
for path in vendor.glob('*.dist-info'):
    data.append((str(path), 'setuptools/_vendor/'+path.name))
a = Analysis([str(root/'desktop_launcher.py')], pathex=[str(root), str(root/'backend')], binaries=[], datas=data,
    hiddenimports=['app', 'security_utils', 'memo_utils', 'store_utils', 'compression.zstd'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MoyuOffice', debug=False,
    bootloader_ignore_signals=False, strip=False, upx=False, console=False, contents_directory='.')
collection = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='MoyuOffice')
