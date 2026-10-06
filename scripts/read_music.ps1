$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$result = @{available=$false; title=''; artist=''; source='none'}
try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $managerType = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager,Windows,ContentType=WindowsRuntime]
    $propertiesType = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties,Windows,ContentType=WindowsRuntime]
    $asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    } | Select-Object -First 1
    $task = $asTask.MakeGenericMethod($managerType).Invoke($null, @($managerType::RequestAsync()))
    if ($task.Wait(2000)) {
        $sessions = @($task.Result.GetSessions() | Where-Object {$_.SourceAppUserModelId -match '(?i)cloudmusic|netease|网易云'})
        foreach ($session in $sessions) {
            $propertiesTask = $asTask.MakeGenericMethod($propertiesType).Invoke($null, @($session.TryGetMediaPropertiesAsync()))
            if (-not $propertiesTask.Wait(1500)) {continue}
            $media = $propertiesTask.Result
            if (-not [string]::IsNullOrWhiteSpace($media.Title)) {
                $result = @{available=$true; title=[string]$media.Title; artist=[string]$media.Artist;
                    source='smtc'}
                break
            }
        }
    }
} catch {}
if (-not $result.available) {
    $player = Get-Process -Name cloudmusic -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -and $_.MainWindowTitle -ne '网易云音乐'
    } | Select-Object -First 1
    if ($player) {
        $caption = $player.MainWindowTitle.Trim()
        $separator = $caption.LastIndexOf(' - ')
        if ($separator -gt 0 -and $separator -lt $caption.Length-3) {
            $result = @{available=$true; title=$caption.Substring(0,$separator); artist=$caption.Substring($separator+3);
                source='window-title'}
        }
    }
}
ConvertTo-Json -InputObject $result -Compress
