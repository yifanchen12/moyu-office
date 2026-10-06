param([string]$Compiler = 'ISCC.exe')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$python=Join-Path $root '.venv\Scripts\python.exe'
Push-Location $root
try {
    & $python -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) {throw 'Build dependency installation failed'}
    & $python -m PyInstaller --noconfirm --clean packaging/moyu-office.spec
    if ($LASTEXITCODE -ne 0) {throw 'PyInstaller failed'}
    & $Compiler packaging/installer.iss
    if ($LASTEXITCODE -ne 0) {throw 'Inno Setup failed'}
} finally {Pop-Location}
