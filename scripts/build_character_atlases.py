"""Write Phaser frame/foot-pivot metadata without changing the generated PNGs."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'frontend' / 'characters'

def build(path):
    with Image.open(path) as image:
        assert image.mode == 'RGBA', f'{path.name}: expected transparent RGBA'
        width, height = image.size
        cell_w, cell_h = width // 4, height // 2
        frames = []
        for index in range(8):
            x, y = index % 4 * cell_w, index // 4 * cell_h
            alpha = image.getchannel('A').crop((x, y, x + cell_w, y + cell_h))
            opaque = alpha.point(lambda value: 255 if value >= 128 else 0)
            bounds = opaque.getbbox()
            assert bounds and min(bounds[0], bounds[1], cell_w-bounds[2], cell_h-bounds[3]) >= 5, f'{path.name} frame {index}: clipped'
            bottom = bounds[3]
            feet = opaque.crop((0, bottom-20, cell_w, bottom)).getbbox()
            frames.append({'filename': str(index), 'frame': {'x':x, 'y':y, 'w':cell_w, 'h':cell_h},
                'rotated': False, 'trimmed': False,
                'spriteSourceSize': {'x':0, 'y':0, 'w':cell_w, 'h':cell_h},
                'sourceSize': {'w':cell_w, 'h':cell_h},
                'pivot': {'x': (feet[0]+feet[2])/2/cell_w, 'y':bottom/cell_h}})
    result = {'frames': frames, 'meta': {'image':path.name, 'size':{'w':width, 'h':height}, 'scale':'1'}}
    path.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'{path.name}: 8 complete frames with aligned foot pivots')

if __name__ == '__main__':
    for filename in ['codex-dragon.png', 'dsh-whale-maid.png', 'sra-aha.png', 'bettergi-furina.png', 'onedragon-chinatsu.png',
                     'wechat-messenger.png', 'qq-penguin.png', 'training-researcher.png', 'baidu-cloud.png',
                     'quark-orbit.png', 'comfy-node-artist.png', 'system-engineer.png']:
        build(ROOT / filename)
