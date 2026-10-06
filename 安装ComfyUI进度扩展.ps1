param([Parameter(Mandatory=$true)][string]$ComfyRoot)
$ErrorActionPreference='Stop'
$resolved=(Resolve-Path -LiteralPath $ComfyRoot).Path
if (-not (Test-Path -LiteralPath (Join-Path $resolved 'server.py')) -or -not (Test-Path -LiteralPath (Join-Path $resolved 'custom_nodes') -PathType Container)) {throw '请指定包含 server.py 和 custom_nodes 的 ComfyUI 目录'}
$destination=Join-Path $resolved 'custom_nodes\comfyui_star_office'
if (Test-Path -LiteralPath $destination) {throw '目标扩展已存在，请先检查，未覆盖任何文件'}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'integrations\comfyui_star_office') -Destination $destination -Recurse
Write-Output '扩展已安装；重启 ComfyUI 后从原界面生成，即可转发节点进度。'
