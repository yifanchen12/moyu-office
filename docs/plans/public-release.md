# Public release implementation plan

The user approved public publication, bilingual documentation, security policies and packaging on 2026-10-06, and explicitly requested an independent Windows EXE installer.

## Reuse and boundaries

The release tree is separate from the active Star-Office-UI installation. Reuse the existing bridge, local dashboard, music strip, upstream backend and required scene assets. Preserve upstream LICENSE and font licenses. Do not export working configuration, environments, user sessions, logs, installers for other applications, cloud credentials or development history.

## Files and responsibilities

- local-config.example.json, .env.example, initialize_local.py: portable configuration templates and per-install random secrets; preserve user edits.
- local_server.py, local_bridge.py: resolve bundled resources, protect Host/Origin boundaries, avoid unrelated parent-directory memo/identity reads and remove personal default paths. Existing collector contracts and music-only metadata remain.
- backend/app.py: release-only resource root override so its existing routes work in a frozen bundle; original installation stays unchanged.
- desktop_launcher.py, start-local.ps1, stop-local.ps1, start-fullscreen.ps1: packaged and source launch/stop paths, background service ownership checks and existing Edge fullscreen display.
- packaging/moyu-office.spec, packaging/installer.iss, scripts/build-windows.ps1: PyInstaller distribution and per-user Inno Setup installer without bundling other applications.
- README.md, README.en.md, SECURITY.md, SECURITY.zh-CN.md, PRIVACY.md, CHANGELOG.md, NOTICE.md: installation, capability limits, privacy model, responsible disclosure, license attribution and release notes.
- tests and GitHub workflow: bridge regression and request-boundary checks; standard-library runtime tests, read-only workflow permissions.

## Contracts and build order

1. Bootstrap produces ignored local-config.json and .env; no existing local files are replaced. Bind only to 127.0.0.1.
2. Status exposes application/version identity and existing allowlisted metadata. Wrong Host, foreign Origin and cross-site API requests are rejected; same-origin browser and origin-free local extension calls remain supported.
3. Verify independent initialization and request guards, then assemble a clean source install. Build and verify frozen EXE before building installer.
4. EXE runs the local service and opens Edge; --server starts only the service, --stop stops only its recorded instance. Installer uses current-user installation and standard uninstall; persistent settings stay in user-owned storage.
5. Audit final Git index and archives, preserve copyright/notices, create yifanchen12/moyu-office as a public repository, push and publish v0.1.0 assets with SHA-256 checksums.

## Validation

Run focused unittest checks, pip dependency check, clean-source HTTP smoke, Host/Origin rejection, music payload filtering, PyInstaller EXE HTTP smoke and installer install/uninstall in an isolated workspace directory. No game jobs or music actions are triggered. Public preview data, if included, must be synthetic.

## Known facts and limits

GitHub account and repository name verified. Artwork has non-commercial restrictions distinct from MIT code. Python 3.14 is the verified runtime. The Windows application depends on installed Edge; it is not a replacement browser. Executables will be unsigned unless a signing identity is supplied; none is assumed. Packaging will not publish the original machine's private configuration or API credentials.
