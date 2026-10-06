param([switch]$NoOpen)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
$application = Join-Path $root 'MoyuOffice.exe'
$packaged = Test-Path -LiteralPath $application
if ($packaged) {
    $initialized = Start-Process -FilePath $application -ArgumentList '--init-only' -WindowStyle Hidden -Wait -PassThru
    if ($initialized.ExitCode -ne 0) {throw '初始化失败 / Initialization failed'}
} else {
    if (-not (Test-Path -LiteralPath $python)) {throw '请先安装源码依赖，或使用 EXE 安装包 / Install source dependencies or use the EXE installer'}
    & $python (Join-Path $root 'initialize_local.py') | Out-Null
    if ($LASTEXITCODE -ne 0) {throw '初始化失败 / Initialization failed'}
}
$config = Get-Content -LiteralPath (Join-Path $root 'local-config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$url = 'http://127.0.0.1:' + $config.port
$reply = $null
try {$reply = Invoke-RestMethod -Uri ($url + '/local/status') -TimeoutSec 2} catch {}
if ($reply -and $reply.application -ne 'moyu-office') {throw '端口被其他应用占用，请修改 local-config.json 中的 port / Port is used by another application'}
$running = $null -ne $reply
if (-not $running) {
    $folder = Join-Path $root '.local'
    if ($packaged) {
        $server = $application
        $process = Start-Process -FilePath $application -ArgumentList '--server' -WorkingDirectory $root -WindowStyle Hidden -PassThru
    } else {
        $server = Join-Path $root 'local_server.py'
        $process = Start-Process -FilePath $python -ArgumentList ('"' + $server + '"') -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $folder 'server.out.log') -RedirectStandardError (Join-Path $folder 'server.err.log')
    }
    @{pid=$process.Id; started=$process.StartTime.ToUniversalTime().ToString('o'); script=$server; packaged=$packaged} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'server.json') -Encoding UTF8
    for ($attempt=0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 500
        $process.Refresh()
        if ($process.HasExited) {throw '服务启动失败，请查看 .local/server.err.log / Service failed to start'}
        try {$reply=Invoke-RestMethod -Uri ($url+'/local/status') -TimeoutSec 1; $running=$reply.application -eq 'moyu-office' -and $reply.port -eq $config.port} catch {}
        if ($running) {break}
    }
    if (-not $running) {throw '服务未响应，请查看 .local/server.err.log / Service did not respond'}
}
if (-not $NoOpen) {Start-Process ($url + '/dashboard')}
Write-Output ($url + '/dashboard')
