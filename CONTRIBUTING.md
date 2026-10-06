# Contributing / 贡献指南

Keep changes focused on local observation and display. State the source and limits of every collector; never infer task success from process presence or fabricate progress percentages. Use synthetic fixtures, not exported user logs.

Run `python -m unittest discover -s tests` and `python -m pip check` in the project virtual environment. For server changes, run the HTTP smoke test against a loopback instance. For Windows packaging changes, verify initialization, service ownership and install/uninstall behavior.

Do not commit `.env`, real local configuration, credentials, chat/session logs, screenshots of private work, API keys or binaries. Do not add network exposure, playback controls or game control as incidental changes. Respect [NOTICE.md](NOTICE.md); artwork contributions must include explicit provenance and license information.

Report vulnerabilities privately under [SECURITY.md](SECURITY.md). Ordinary issues and pull requests should include a concise problem statement, observable behavior and relevant validation.

请仅修改当前问题相关内容，说明采集数据来源及边界；使用虚构测试数据，不提交真实日志、密钥、本机配置、私密截图或二进制。安全问题按安全政策私下报告，素材提交须说明来源与许可。
