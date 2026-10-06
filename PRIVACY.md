# Privacy and data handling / 隐私与数据处理

## English

Moyu Office runs locally. Its collectors reduce observations to allowlisted status events and numeric metrics before displaying them. The project has no analytics, account registration, advertising SDK or telemetry upload endpoint.

| Source | Read | Displayed or retained |
| --- | --- | --- |
| Codex / DSH session logs | Log files are read locally to extract lifecycle markers | Event state/counts only; prompts, messages and tool arguments are not forwarded or copied |
| Game automation logs | Local log lines are matched against lifecycle markers | Generic state, log age, process count; no raw log text or account fields |
| Windows notifications | Notification IDs and application handler metadata, read-only | New-event timestamps and software identity; no notification content or chat databases |
| Cloud-drive processes | Process presence and disk I/O counters | Counts and write-rate metrics; no file lists, account data or download contents |
| Training files | Trainer JSON or explicitly supplied progress JSON | Allowlisted numbers and state; not arbitrary training descriptions or configuration |
| ComfyUI | Queue metadata and optional progress event metadata | Queue counts, node/prompt identifiers and numeric steps; no workflow, prompt, image or error text |
| Music | NetEase media title/artist or its window caption | Current title and artist; no audio, playlists, account data or playback control |
| System | OS counters and optional nvidia-smi output | CPU/RAM/GPU/temperature and aggregate network counters |

Local session logs may contain sensitive material even though only lifecycle metadata is displayed. The collector reads those files but does not upload or replicate their contents. Dashboard metadata itself can still reveal activity. `.env`, configuration, service logs, generated state and the dedicated Edge profile remain on the local machine and are excluded from publication.

The bridge normally contacts only configured ComfyUI and local HTTP/WebSocket endpoints. A user-selected remote ComfyUI URL causes communication with that server. The optional ComfyUI observer sends only its filtered metadata to `STAR_OFFICE_URL`; review that destination before changing it. Edge, Windows, driver utilities and monitored programs can have separate network behavior governed by their own settings.

The upstream memo and identity paths are redirected to this application's private `.local/` directory; the release does not read an adjacent personal memory folder or an unrelated OpenClaw identity file. Uninstall preserves user-generated settings and local runtime files. Back up and remove them manually if desired after stopping the service and closing the window.

## 简体中文

摸鱼事务所在本机运行，采集后只展示白名单状态与数值，不包含分析统计、账户注册、广告 SDK 或遥测上传接口。

Codex、DSH 与游戏工具的日志会在本地读取，用于提取生命周期标记；不复制或上传原始日志、提示词、消息及工具参数。Windows 通知只读取 ID 和应用标识，不读正文或聊天数据库。网盘只读取进程与 I/O 数值，不读文件列表或下载内容。训练只展示数字和状态；ComfyUI 不转发工作流、提示词、图像或错误正文。网易云只读取歌名、歌手或窗口标题，不读取账户、歌单或音频，也不控制播放。

这些来源文件本身可能含敏感内容，元数据也能透露活动，不能将“本地运行”等同于“数据不敏感”。私有配置、密钥、服务日志、运行状态及独立 Edge 配置目录保留在本机，不随源码或安装包发布。

桥接器通常只访问配置的 ComfyUI 和本机接口；配置远程地址后会与该服务器通信。ComfyUI 扩展仅向 `STAR_OFFICE_URL` 发送过滤后的元数据，修改地址前应检查目标。Edge、Windows、驱动工具及被监控软件自身的联网行为不由本项目控制。

发布版把上游记忆与身份文件读取范围限定到应用自己的 `.local/`，不读取相邻个人记忆目录或无关 OpenClaw 身份文件。卸载保留用户生成的本机配置及运行文件，需要清除时请先停止服务、关闭窗口并备份。
