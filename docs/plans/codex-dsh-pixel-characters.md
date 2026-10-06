# Codex and DSH pixel characters

Approved on 2026-10-06: adapt the two identified MV heroines into pixel chibi characters and replace the local Codex/DSH guests.

## Sources and scope

- Codex: MV/assets/gpt-character-fusion.png, the user-authorized silver-haired dragon heroine with white horns, pointed ears, white dress and dragon tail.
- DSH: MV/85190/remake-v2/assets/deepseek.png, the blue-haired whale maid with whale fins/tail, navy dress, white apron and maid headband. Preserve the existing MV attribution chain and CC BY-NC-SA 4.0 notice for this adaptation.
- Reuse built-in image generation, shipped Phaser sprite loading/animation, existing source IDs, movement tweens and character selection. No runtime dependency is added.
- Change frontend character assets and frontend/index.html only for local character rendering; retain all collector, detail, launch, scene furniture, music and other guest behavior.
- Add generation prompts/provenance and artwork attribution. Synchronize final assets/code into the active Star-Office-UI tree. Publishing/rebuilding installers is outside this request.

## Asset interface

Each transparent PNG is a regular 4-column, 2-row sheet with eight equal cells: four idle frames in the first row, four walking frames in the second. All cells use the same scale, foot baseline, costume and three-quarter-right facing; mirror horizontally for leftward movement. Keep horns, tails, hands and feet inside each cell. Use a matching outlined pixel chibi style suitable for the room and render at approximately the existing guest height.

If the generated geometry does not match the intended grid, inspect and repair the generated art before integration rather than silently accepting clipped characters.

## Integration

- Load the two sheets for the local office, create idle/walk animation keys and select them only for source IDs codex/dsh.
- Switch between idle and walk using the existing movement lifecycle. Preserve animation and position across status polls.
- Keep a fallback to the current guest asset when a custom sheet is unavailable; keep existing click handlers and accessible labels.
- Validate transparency/grid dimensions visually, check both sprite identities and animation changes with focused scene checks, and inspect real moving characters in the browser. Restart the active window-reading backend on the normal desktop, so music collection remains functional.


## Asset geometry refinement

The selected PNGs are 1774×887 with eight 443×443 usable cells. Generation did not produce identical idle/walk foot offsets, so the loader consumes accompanying Phaser atlas JSON. The existing Pillow dependency is used only to read alpha and generate per-frame foot pivot metadata; artwork is not edited by the script. This keeps frames anchored without changing the movement/detail/launch contract. Both selected sheets passed clipping/margin checks.

## Verification result (2026-10-07)

Both selected PNG/JSON atlases are served successfully and the normal-desktop backend continues to read real music metadata. Live room inspection confirmed the silver dragon Codex and blue whale-maid DSH at the intended scale, walking poses, complete horns/tails/shoes, attached names and the restored decorative cats. Both character detail identities were verified; DSH retains its existing launch button. The atlas builder passed eight complete-frame checks per character; JavaScript checks cover custom sprite identity, idle/walk switching and poll stability as well as the previous scene regressions. Existing 20 Python tests passed. Source/assets/attribution are synchronized to the active tree; no installer rebuilding or public push was performed.
