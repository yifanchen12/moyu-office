# Security policy

[简体中文](SECURITY.zh-CN.md)

## Supported versions

Security fixes target the latest published 0.1.x release and `main`. Older binaries should be updated before a report is reproduced. This is a personal open-source project with no guaranteed response or remediation deadline.

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/yifanchen12/moyu-office/security/advisories/new). Include the affected version, a minimal reproduction using synthetic data, expected and observed behavior, and the potential impact. Do not include real keys, raw chat logs, LLM prompts or private machine configuration.

If private reporting is unavailable, open a public issue **only asking for a private contact channel**; do not post exploit details, sensitive screenshots or proof-of-concept credentials. Public bug reports are appropriate for ordinary layout or compatibility problems.

## Threat model and boundaries

- The supported service entry point is `local_server.py` or `MoyuOffice.exe`. It binds to `127.0.0.1`; the raw upstream `backend/app.py` entry point is not covered by this local deployment model.
- Host values are restricted to `127.0.0.1:configured-port` and `localhost:configured-port`. Foreign Origin headers and cross-site API requests are rejected. No permissive CORS policy is added.
- Origin-free HTTP calls from local processes, including the ComfyUI extension, are supported. They are not authenticated. This design trusts the local Windows user and other local processes; it does not defend against a compromised local account or malware.
- Initial session and asset-drawer secrets are generated per installation. Defaults and weak configured secrets are refused. Secrets are never part of a release archive. These secrets do not turn all dashboard APIs into an authenticated gateway.
- The two local event endpoints limit request size to 4 KiB and validate allowlisted fields. They do not accept arbitrary prompts, workflows, log text or shell commands.
- The application does not run tasks in monitored software, submit generation jobs, send messages or install API/provider credentials. ComfyUI's optional observer preserves original delivery and drops queued observations if the bounded queue is full.
- Live metadata can reveal software activity, system performance and song titles. Protect the local account and avoid displaying private work on a shared screen.

## Deployment rules

Do not bind the service to `0.0.0.0`, publish it through a tunnel, disable request guards, or expose it as a multi-user service. Remote exposure requires a separately reviewed authenticated gateway, TLS and authorization model; these are not implemented here.

The launcher uses an isolated Edge profile with extensions disabled to avoid unrelated extension windows. It does not disable Windows Defender, SmartScreen, certificate verification, firewall rules or browser sandboxing. No remote-debugging port is enabled. Temporary script execution policy applies only to the launcher process.

Install and edit configuration only in directories owned by your user. Review the optional ComfyUI extension before installing it. Keep Windows, Edge, Python and dependencies updated. Never put authentication credentials in configured URLs.

## Release hygiene

`.env`, `local-config.json`, runtime state, join keys, sessions, logs, virtual environments and generated binaries are excluded from Git. Source archives are generated from tracked files; portable archives contain a clean PyInstaller output. Releases provide SHA-256 checksums. Current executables are unsigned; a checksum is not a publisher certificate or an antivirus certification.

If a credential is accidentally published, revoke or rotate it promptly and remove it from repository history and release artifacts. Deleting the visible file alone is insufficient.

## License distinction

This security policy is not a license, contractual service-level agreement or warranty. Code licensing and artwork restrictions are documented in [NOTICE.md](NOTICE.md) and the license files.
