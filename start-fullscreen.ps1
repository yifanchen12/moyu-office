param([switch]$RoomOnly)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'start-local.ps1') -NoOpen | Out-Null
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'local-config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$page = if ($RoomOnly) {'/local/office'} else {'/dashboard'}
$url = 'http://127.0.0.1:' + $config.port + $page
$edge = @(
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),
    (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe')
) | Where-Object {Test-Path -LiteralPath $_} | Select-Object -First 1
if (-not $edge) {throw '未找到 Microsoft Edge，请先使用浏览器入口'}
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::AllScreens | Where-Object {-not $_.Primary} | Select-Object -First 1
if (-not $screen) {$screen = [System.Windows.Forms.Screen]::PrimaryScreen}
$bounds = $screen.Bounds
$profile = Join-Path $PSScriptRoot '.local\edge-room'
$arguments = @('--kiosk', $url, '--edge-kiosk-type=fullscreen', '--no-first-run', '--disable-extensions', '--kiosk-idle-timeout-minutes=0',
    ('--user-data-dir="' + $profile + '"'), ('--window-position=' + $bounds.X + ',' + $bounds.Y),
    ('--window-size=' + $bounds.Width + ',' + $bounds.Height))
# 用户要求显示全屏窗口；后台服务仍由 start-local 隐藏启动。
Start-Process -FilePath $edge -ArgumentList $arguments -WindowStyle Normal
Write-Output '摸鱼事务所已打开；Alt+F4 退出全屏窗口，后台采集会继续运行。'
