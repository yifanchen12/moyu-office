# 摸鱼事务所 · Moyu Office

[English](README.en.md) · [安全政策](SECURITY.zh-CN.md) · [隐私说明](PRIVACY.md) · [许可与署名](NOTICE.md)

面向 Windows 副屏的像素风本机状态看板。把开发任务、生成进度、消息信号和电脑性能映射为房间中的角色与状态卡片，并在壁炉上方滚动显示网易云的当前歌名和歌手。

基于 [Star Office UI](https://github.com/ringhyacinth/Star-Office-UI) 构建。**代码采用 MIT；附带美术素材仅限非商业用途。** 完整条款见 [LICENSE](LICENSE)、[LICENSE-MOYU](LICENSE-MOYU) 和 [NOTICE.md](NOTICE.md)。

## 功能与边界

| 数据来源 | 显示内容 | 实际边界 |
| --- | --- | --- |
| Codex | task_started / task_complete 等本机生命周期 | 仅读会话事件；日志落盘存在延迟，30 分钟未更新的执行状态标待确认 |
| DeepSeek Harness（DSH） | 压缩会话中的 turn/start / turn/end | 不读取或配置模型 API 密钥，不安装 DSH；依赖 Python 3.14 的 zstd |
| 微信、QQ | Windows 新通知或任务栏闪烁信号 | 不读消息正文或聊天数据库；静音、托盘动画可能无法覆盖 |
| BetterGI、SRA、绝区零一条龙 | 日志中的运行、结束、异常；一条龙暂停/恢复 | 只观察，不控制游戏；关键词及版本变化会影响识别，无可靠总百分比 |
| ComfyUI | 队列与可选扩展转发的节点进度 | 节点百分比不是整个视频生成百分比；独立旁观 WebSocket 不保证收到定向事件 |
| 百度、夸克网盘 | 客户端存在与磁盘写入活动 | 磁盘写入不是下载速度，不能提供下载总百分比 |
| 训练任务 | Trainer 状态或自定义数值进度文件 | 更新超过 5 分钟标待确认；云端文件须由用户自行同步 |
| 电脑性能 | CPU、内存、GPU、显存、温度、网卡总收发 | GPU 数据需要 NVIDIA 驱动与 nvidia-smi；总网速不等于单程序速度 |
| 网易云音乐 | 当前歌名、歌手，循环滚动 | 每 5 秒刷新；不检测或展示播放/暂停，不播放歌曲 |

无数据时显示“未接入／离线”及具体原因，不用进程存在推断任务完成。

## 安装

### Windows 安装包（推荐）

从 [Releases](https://github.com/yifanchen12/moyu-office/releases) 下载 `MoyuOffice-Setup-0.1.0-windows-x64.exe`，核对同一版本 `SHA256SUMS.txt` 后运行。安装到当前用户目录，不需要管理员权限或单独安装 Python。

要求：Windows 10/11 x64、已安装 Microsoft Edge、Windows PowerShell 5.1。EXE 打包本机服务，窗口显示使用独立配置目录的 Edge 全屏模式；这不是独立浏览器内核。

开始菜单可打开事务所、普通浏览器视图、停止后台和卸载。默认优先副屏；按 **Alt+F4** 关闭全屏窗口。关闭窗口后后台继续采集，使用“Stop Moyu Office Service”停止。安装器默认不在安装结束时自动启动。

首次启动自动生成 `.env` 的随机本机密钥及 `local-config.json`，不会替换已有配置。卸载保留这些用户配置和 `.local/` 数据；若需要彻底清理，请在退出应用后自行备份并删除残留目录。版本 0.1.0 没有代码签名，哈希用于核对下载完整性，不等同于签名。

### 便携包

下载 `MoyuOffice-0.1.0-windows-x64.zip`，解压到可写目录，运行 `MoyuOffice.exe`。不要仅复制单个 EXE；同目录的 DLL、素材、脚本和许可证均是运行所需文件。

### 源码运行

安装 Python **3.14**，确认 `python --version`，然后：

```powershell
git clone https://github.com/yifanchen12/moyu-office.git
cd moyu-office
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\start-local.ps1
```

全屏运行 `.\start-fullscreen.ps1`，仅显示房间使用 `.\start-fullscreen.ps1 -RoomOnly`，停止服务使用 `.\stop-local.ps1`。如本机 PowerShell 策略阻止脚本，可双击附带的 `.cmd` 入口；其进程级策略只适用于该次启动，不修改系统策略。

默认页面为 `http://127.0.0.1:19100/dashboard`。若端口被其他应用占用，修改本机配置中的 `port` 后重启；不会结束其他占用端口的进程。

## 配置数据来源

编辑首次启动生成的 `local-config.json`，模板见 [local-config.example.json](local-config.example.json)。路径不配置时相应工具显示未接入。程序不会下载或启动被监控软件。

| 字段 | 用途 |
| --- | --- |
| `port` | 本机服务端口，1024–65535 |
| `comfyui_url` | 现有 ComfyUI 地址，模板为 `http://127.0.0.1:8188` |
| `paper_workspace` | 需要扫描 Trainer 进度文件的目录；留空不扫描工作区 |
| `training_files` | 数值进度文件列表；相对路径以应用目录为基准 |
| `bgi_log_dirs` | BetterGI 日志目录列表 |
| `sra_root` | SRA 安装根目录，自动发现版本子目录的日志 |
| `onedragon_root` | 绝区零一条龙根目录，读取 `.log/log.txt` |
| `dsh_homes` | DSH 会话目录所属的 home；默认 `~/.dsh` |

Codex、消息信号、音乐和性能从当前用户的本机元数据读取。应用不包含学校或其他提供商 API 配置，也不需要任何 LLM API 密钥。

### ComfyUI 扩展

```powershell
.\安装ComfyUI进度扩展.ps1 -ComfyRoot 'D:\Apps\ComfyUI'
```

指定包含 `server.py` 和 `custom_nodes` 的目录，再重启 ComfyUI。扩展保留原客户端发送，只异步转发白名单事件和数字；不发提示词、工作流、预览或错误正文。已有同名扩展不会被覆盖。若事务所端口改变，请在启动 ComfyUI 的环境中设置 `STAR_OFFICE_URL=http://127.0.0.1:新端口`。

### 本地或云端训练

将 [scripts/report_training.py](scripts/report_training.py) 放入需要的训练环境并调用：

```python
from report_training import report
report('/data/training-progress.json', current=120, total=1000, loss=0.32)
# 结束时上报 state='idle'
```

把进度文件同步到配置的本机目录。也支持本机 `POST /local/training`，字段为 `state`、`current`、`total`、`loss`、`epoch`、`learning_rate`。不自动创建云端任务、开通算力或开放隧道。

## 安全与隐私

服务仅监听 `127.0.0.1`，校验 Host／Origin，拒绝跨站 API 请求；本机密钥、配置、日志和运行状态均排除在版本控制与发布包之外。它仍信任同一台电脑上的用户与进程，**不是认证网关或多用户服务器**，不要直接公开端口或套用上游公网部署示例。详细威胁模型见 [安全政策](SECURITY.zh-CN.md)。

本项目不上传采集数据，也不读取聊天数据库。会话日志会在本地读取以提取生命周期；其中的提示词、消息和工具参数不展示、复制或转发。Edge 与被监控软件自身的网络行为不受本项目控制；读取已配置的远程 ComfyUI 地址会与该服务通信。详细数据范围见 [PRIVACY.md](PRIVACY.md)。

## 开发与构建

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/smoke_test.py --base-url http://127.0.0.1:19100
.\scripts\build-windows.ps1 -Compiler 'C:\Tools\Inno Setup 6\ISCC.exe'
```

构建需要 PyInstaller 与 Inno Setup 6。构建脚本和规范在 `packaging/`，产物位于 `dist/` 与 `release/`，不提交二进制到 Git。安全问题请使用仓库 Security → Report a vulnerability；普通问题可以提交脱敏 issue。参与贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 后续方向

自定义卡通角色及动画帧、按程序独立设计覆盖不同阶段的语录。当前版本不包含这些尚未制作的素材或语录。
