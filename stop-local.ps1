$ErrorActionPreference = 'Stop'
$recordPath=Join-Path $PSScriptRoot '.local\server.json'
if (-not (Test-Path -LiteralPath $recordPath)) {Write-Output '服务未启动 / Service is not running'; exit}
$record=Get-Content -LiteralPath $recordPath -Raw -Encoding UTF8 | ConvertFrom-Json
$process=Get-Process -Id $record.pid -ErrorAction SilentlyContinue
if ($process) {
    $native=Get-CimInstance Win32_Process -Filter ('ProcessId=' + $record.pid)
    $expected=Join-Path $PSScriptRoot $(if ($record.packaged) {'MoyuOffice.exe'} else {'local_server.py'})
    $sameCommand=$native.CommandLine.Contains($expected) -and (-not $record.packaged -or $native.CommandLine -match '(^|\s)--server(\s|$)')
    if ($record.script -ne $expected -or $process.StartTime.ToUniversalTime() -ne ([datetime]$record.started).ToUniversalTime() -or -not $sameCommand) {throw '进程身份已改变；未停止任何程序 / Process identity changed; nothing was stopped'}
    Stop-Process -Id $process.Id
}
Remove-Item -LiteralPath $recordPath
Write-Output '摸鱼事务所后台已停止 / Moyu Office service stopped'
