# Character art generation

Built-in image generation; transparent RGBA outputs. Reference images remain in the user's MV project. No API key or fallback CLI was used. Only the selected sheets are bundled.

## Codex selected refinement prompt

Revise image 1 ONLY into an actual LOW-RESOLUTION PIXEL GAME SPRITESHEET matching the pixel lodge furniture style in image 2. Preserve the same single female silver dragon heroine: silver/lilac long hair, two white horns, pointed ears, lilac eyes, white high-neck dress, small silver knot ornament, white shoes, curled white dragon tail. No room/background from image 2. Use extremely simple chunky 16-bit RPG sprite pixel clusters, flat limited colors, 1 logical pixel dark outline. Each sprite is drawn as if on a 48x64 logical-pixel canvas then nearest-neighbor enlarged; NO smooth anime rendering, fine individual strands, soft gradients, detailed embroidery, or anti-aliasing. Modest compact fully covering white dress. Keep her cute and recognizable. Exactly eight full-body sprites in a strict 4 columns x 2 rows regular grid; sheet ideally 1024x512. EACH sprite must be the same size with the same foot baseline and occupy only the central 70% of its square cell. Leave a wide transparent moat of 15% on ALL sides of every cell; horns/tails/feet never approach cell edges. All face three-quarter screen-right. Top row: four subtle idle poses with a blink in third frame and tiny breathing/hair/tail motion. Bottom row: four WALK CYCLE poses, alternating right/left feet and arms, same head/body size as the idle row. Real alpha background. No checkerboard painted into pixels, no floor, no text/numbers/grid lines. The final result must read as hand-pixelled tiny game NPCs, not miniature detailed anime illustrations.

References: the first generated dragon sheet and the verified local office screenshot; identity initially derives from `MV/assets/gpt-character-fusion.png`.

Selected Codex output: `frontend/characters/codex-dragon.png`, 1774×887 RGBA. Eight 443×443 cells, with the final two columns and last row outside the cell grid unused. Opaque character bounds were inspected: every cell has clear margins; feet end at y=435–436. Runtime display canvas height: 78 world pixels, four idle frames at 4 fps and four walk frames at 8 fps.

## DSH successful generation prompt

A production game sprite sheet: ONE cute adult blue-haired whale-maid woman, eight low-resolution pixel-art animation frames on true transparent background. Character identity: navy blue long hair fading to blue tips, big blue eyes, small whale-fin-shaped ears, white frilled maid headband with blue ribbon, modest navy blue maid dress, white apron with tiny blue whale motif, dark blue shoes and compact blue whale tail with split fluke. Chibi 2.5 heads tall, readable chunky hand-placed 16-bit RPG pixels, thick dark outline, flat limited colors. FOUR COLUMNS x TWO ROWS, equally sized square cells, landscape 2:1. Same body size, camera and foot baseline, generous alpha padding around every figure. Top row: four idle frames (relaxed, breathe, blink, breathe). Bottom row: four walking gait frames with alternating foot steps and arm swing. Three-quarter facing right in every cell. Consistent costume and hairstyle. Designed as a tiny cozy pixel-lodge NPC; logical resolution 48x64 pixels per figure, enlarged with nearest-neighbor. No text, labels, grid lines, floor, background, painted checkerboard, smooth anime rendering or other characters.

The final DSH generation used this description after inspecting the MV whale maid; two earlier reference-image requests did not return usable results. The successful first sheet was then used for the following spacing edit.

## DSH selected spacing edit prompt

Adjust ONLY the spacing and alignment of this pixel-art sprite sheet. Keep this exact same blue-haired whale maid, all eight poses, pixel style, colors, costume, facial expressions, whale-fin ears and tail. Preserve a regular 4-columns x 2-rows grid. Make every sprite 15% smaller inside its cell, leaving a clear wide transparent margin on ALL four sides of EACH cell. In EVERY cell: top of maid headband at 10% cell height, soles at 90% cell height, character centered horizontally. Both idle and walk rows must have the same body/head scale and exact common foot baseline. The currently touching row boundary must become a generous transparent gap. No sprite pixel may touch an outer edge or neighboring cell. Actual transparent background; no checkerboard, text, cell lines or ground. Do not introduce any new artistic detail or different character. Eight equally sized square cells, four idle poses above and four walking poses below.

Selected DSH output: `frontend/characters/dsh-whale-maid.png`, 1774×887 RGBA, eight 443×443 cells. Its transparent padding differs between idle/walk rows. `scripts/build_character_atlases.py` reads the PNG alpha and writes eight named frames with individual foot pivots; it never changes the generated PNG. Phaser uses these pivots to align feet at the character world position on every frame. Visible character height is approximately 72 world pixels for both characters. The runtime uses four idle frames at 4 fps and four walk frames at 8 fps.

Rebuild metadata after replacing a generated sheet:

```powershell
.venv/Scripts/python.exe scripts/build_character_atlases.py
```
