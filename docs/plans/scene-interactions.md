# Scene activity and character interactions

Approved on 2026-10-06: correct Codex task activity, let characters wander in their assigned areas, and show live details when a character is selected. Installer troubleshooting is paused.

Approved addition: the detail dialog has a separate "Launch software" button. Training opens its workspace/platform; automation opens the application without starting a job. Only locally configured or discovered program targets may be launched. A browser request supplies a known program ID, never a command or path.

## Requirement reading

An executing Codex task must appear in the work area; task completion returns it to the lounge. Characters should walk and pause inside the area belonging to their current state. Selecting a character opens read-only information about the corresponding program.

## Reuse survey

- Reuse `local_bridge.py` collectors, lifecycle parser and allowlisted snapshots; preserve CLI JSONL support. Observed desktop task events may precede rollout writes. Inspect desktop lifecycle metadata and verify its source before enabling it.
- Reuse `frontend/index.html` Phaser sprites, area rectangles, tweens and bubble following. Actual characters currently snap to fixed points on each poll; only demo characters move.
- Reuse `/local/status` for local scene status and details, matching by stable program ID. Do not expose upstream agent join keys through the new details UI.
- Existing dependencies in `requirements-local.txt` cover collectors; Phaser is already shipped. No new runtime dependency is required.
- Existing checks: `tests/test_local_bridge.py`, `tests/test_local_security.py`; run `.venv/Scripts/python.exe -m unittest discover -s tests -v`. Add the smallest focused checks for the changed lifecycle and scene behavior.

## Capability and file boundaries

- `local_bridge.py`: merge observed desktop lifecycle metadata with existing CLI task events; never treat a running application process as proof of an active task. Forward only state and aggregate counts.
- `frontend/index.html`: local snapshot mapping, state-driven areas, bounded wandering independent of polling, character selection and a live detail dialog. Include the main performance character when visible.
- `local_server.py`: change only if a small scene integration hook is required; preserve existing local access protections and routes.
- `local_launch.py`: resolve known desktop entry points or locally configured targets, expose safe availability labels, and launch only after a same-origin POST with a known program ID. Use existing Python/Windows features. No remote download or command endpoint.
- `local-config.example.json`: document optional per-program local launch targets; retain automatic discovery when available.
- Focused tests: lifecycle start/end/abort, conflicting state/area, movement bounds and polling stability, safe detail selection.
- Sync verified changes to the active `Star-Office-UI` tree and the public `moyu-office` source tree. Do not change credentials, local settings, music behavior, artwork or unrelated installer work.

## Interfaces and invariants

- Collector input is the observed lifecycle record; output is executing, idle or error plus aggregate freshness/count metrics. Missing, stale or unsupported data is identified explicitly.
- Local scene input is the allowlisted `/local/status` snapshot. Each item ID has one stable character identity. State determines its area; stale area metadata cannot override a fresh executing state.
- Character movement persists between polls. A changed area replaces the old movement target. Name and bubbles follow the character. Walk endpoints stay within the assigned area; transit is distinct from wandering.
- Use clickable DOM name labels alongside sprite hit targets so keyboard users can select a character. Labels follow the rendered camera/scale and stay inside the canvas viewport. Floor bounds avoid the actual table and sofa identified during visual verification.
- Selected details include name, state, availability, source, updated time and available metrics. Use text nodes, not untrusted HTML. Refresh while open; close by button or Escape. Do not include message contents, prompts, credentials or raw logs.
- `/local/launch` accepts `{id: <known program id>}` after Host/Origin validation, returns a safe success/error reason, and cannot receive executable arguments or user-controlled shell commands. The status snapshot exposes launch availability without local paths. Targets are desktop entry points, folders or validated HTTP(S) URLs from local configuration.

## Build order

1. Verify collector parsing using observed metadata and focused fixtures.
2. Verify movement/selection logic independently, then assemble it with the scene and allowlisted snapshots.
3. Exercise local scene integration and synchronize the source trees.

## Validation

- Codex active -> work area; complete/aborted -> lounge; errors -> error area; old/missing records do not silently claim an active task.
- Real characters walk, pause and remain bounded without being repositioned on every fetch. Status changes take them to the new area.
- Clicking each program shows the correct safe fields, updates while open and closes correctly.
- Run existing local tests and JavaScript syntax checks; inspect the real scene when runtime permissions permit. Report any unverified live behavior.

## Facts versus assumptions

- Verified: current JSONL files did not receive fresh task lifecycle records during desktop work; the active bridge consequently reported Codex idle.
- Verified: real characters are fixed in place, have no selection handler, and some predefined coordinates fall outside their declared area.
- Verified: desktop logs contain `turn/started` and `turn/completed` markers with conversation identifiers. Their applicability and freshness must be checked; do not assume those sparse diagnostic markers cover all tasks.
- Assumed: brief pauses and directional facing with existing sprite frames satisfy the requested walking behavior. New character art is outside this task.

## Verification result

- Local collection and the live detail dialog both identified the current Codex task as executing; its character occupied the work area.
- All 12 moving labels changed position across real scene observations. The actual table/sofa layout was used to constrain floor bounds.
- Live detail fields refreshed, Escape closed the dialog and the known-ID launch request for Task Manager returned success.
- 20 Python checks and the Node scene check cover desktop lifecycle/late completion, CLI compatibility, source privacy, local API guards, ComfyUI service reuse, movement bounds/poll stability and stable click identity.
- Eleven local launch entry points were found/configured. Codex desktop launch remains unavailable until the user supplies a reliable desktop entry point; its activity and detail functions work.
- Source updates are synchronized between the active tree and public source directory. Installer rebuilding/publication is outside this scene update and remains paused.

## Display regression repair (2026-10-06)

- Local room views now always use FIT, including touch-capable Windows displays; local canvas CSS preserves the room aspect ratio instead of stretching both dimensions.
- Accessible moving labels use Phaser's render matrix, including camera-origin offsets. The local plaque keeps its configured product name across status polls and language refreshes.
- Verified canvas bounds at 3200x2000 (3200x1800 centered), visual results at 1600x1000 and 1280x720, the restored cat, all 12 moving labels, and detail-dialog open/Escape close. Added focused FIT/projection regression checks; the 20 Python checks still pass.

## Approved movement scope refinement (2026-10-06)

The user requested a larger roaming range beyond the bottom floor. Reuse the existing point selection and tween queue, expand local floor bounds into connected strips above/beside the work desk and beside the lounge furniture, and route through the clear side corridors when switching strips. Keep the same state/selection interfaces and retain furniture/wall exclusions. Restore the original sofa cat as decorative idle animation, independent of all program states. Check generated endpoints/routes against the floor strips and confirm the animated cat and expanded roaming visually.

Music startup diagnosis: the backend restarted from a sandbox desktop could not see the actual player windows. Running the existing reader on the normal desktop returned current title/artist via its window-title fallback. Restart this window-reading backend on the normal desktop; no new music data source or operating-system setting change is needed.

Verification: the normal-desktop backend returned real current song/artist metadata and the music strip updated across observed song changes. The sofa cat is visible and animated alongside all 12 program characters. Live scene observations showed characters above the previous bottom-only floor. Focused JavaScript checks validate sampled endpoints and every route segment within each floor union, and cat visibility through idle/work/error/sync states; all 20 Python checks pass. Future restarts of this backend must run on the normal user desktop (approved non-sandbox execution or user-started launcher), so existing window-based collectors can see the applications.
