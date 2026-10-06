# Attribution and licensing / 署名与许可

Moyu Office is a Windows desktop status dashboard derived from [Star Office UI](https://github.com/ringhyacinth/Star-Office-UI), created by **Ring Hyacinth and Simon Lee**. The imported baseline is commit `f29c107e9728a72f2635f10b4e8203b29b37221d`. Original copyright and usage conditions are preserved in [LICENSE](LICENSE).

摸鱼事务所基于 Star Office UI，原作者为 **Ring Hyacinth 与 Simon Lee**。本项目增加本机状态采集、信息卡片、网易云曲目横条、全屏启动、请求边界检查及 Windows 安装封装。发布版仅为冻结打包增加上游后端资源根目录适配；原前端场景逻辑继续复用。

| Component / 组成 | Terms / 条款 |
| --- | --- |
| Imported Star Office UI code / 上游代码 | MIT, copyright Ring Hyacinth & Simon Lee; see LICENSE |
| Original Moyu Office additions / 本项目新增代码 | MIT, copyright yifanchen12; see LICENSE-MOYU |
| Scene and artwork / 场景及美术素材 | **Non-commercial only / 仅限非商业用途**, as specified by upstream LICENSE |
| Guest animations / 访客动画 | LimeZu, [Animated Mini Characters 2 (Platformer) [FREE]](https://limezu.itch.io/animated-mini-characters-2-platform-free); retain attribution and original author terms |
| Ark Pixel fonts / 方舟像素字体 | SIL Open Font License 1.1; copyright TakWolf; see frontend/fonts/OFL.txt |
| Phaser | MIT; see licenses/Phaser-MIT.txt |

**The repository is not uniformly MIT-licensed.** MIT permissions for code do not grant commercial rights to the bundled artwork. Replace all restricted artwork with properly licensed original work before commercial use. No rights to third-party characters, posters, trademarks or music are granted by this repository.

**本仓库并非全部内容均为 MIT。** 代码许可不授予附带美术素材商业使用权。商业使用前应替换所有受限美术素材，并自行确认第三方角色、海报、商标及音乐的权利。项目不附带歌曲音频。

## Custom Codex and DSH characters / 自定义角色

The two local character sheets in `frontend/characters/` are AI-assisted pixel adaptations of the user's MV character references, generated with the built-in image tool. These fan characters are not official OpenAI/Codex or DeepSeek designs. This notice grants no trademark rights.

- **Codex silver dragon heroine** (`codex-dragon.png`): adapted from the user-authorized `MV/assets/gpt-character-fusion.png`. The MV source notice states that this artwork and its derivatives are outside the code's MIT license and carry no additional sublicense grant. Confirm reference-art permissions before redistribution.
- **DSH whale maid** (`dsh-whale-maid.png`): adapted from `MV/85190/remake-v2/assets/deepseek.png`; retain the MV source attribution chain: 溟月 © 上善无形 ([Pixiv](https://www.pixiv.net/users/62155430), [Bilibili](https://space.bilibili.com/4456176)); maid design ZipZipPipe ([Pixiv](https://www.pixiv.net/users/18604994), [Bilibili](https://space.bilibili.com/4168597)); standing art Small-tailqwq / dsh-deep-whale; expressions dsh-whale-galgame ([repository](https://github.com/JAdpp/dsh-whale-galgame)). This pixel-art adaptation retains **CC BY-NC-SA 4.0**, attribution and noncommercial/share-alike terms; see `licenses/CC-BY-NC-SA-4.0.txt`. Changes: chibi proportions, pixel rendering and idle/walking animation frames.

这两位角色来自用户 MV 的女性参考形象，经内置图片工具生成像素 Q 版及待机、行走帧。Codex 银龙角色沿用 MV 的素材权限说明，不纳入代码 MIT 许可；DSH 鲸鱼女仆的派生素材保留上述署名链及 CC BY-NC-SA 4.0。生成方式、提示词及动画规格见 `docs/character-art-prompts.md`。

## User-reference game characters / 游戏角色参考改编

`sra-aha.png`, `bettergi-furina.png` and `onedragon-chinatsu.png` are AI-assisted pixel fan-art adaptations of the three images supplied by the user: 阿哈（按参考图中的女性形象）、芙宁娜 / Furina and 千夏 / Chinatsu. The supplied images depict characters from Honkai: Star Rail, Genshin Impact and Zenless Zone Zero respectively, associated with HoYoverse / miHoYo. Reference-image authorship and redistribution permissions were not independently established. These adaptations are outside the code's MIT license; no third-party artwork, character or trademark rights are granted. They are not official game assets. Changes: pixel chibi rendering and idle/walking frames. Prompts and generation mode: `docs/game-character-art-prompts.md`.

三套素材按用户提供的参考形象制作，属于游戏角色的像素 Q 版同人改编，包含待机和行走帧。参考图作者及再分发许可未独立确认，不将这些素材纳入代码 MIT 许可，也不授予第三方美术、角色或商标权利。

## Original icon-inspired female mascots / 图标特色女性角色

The seven sheets `wechat-messenger.png`, `qq-penguin.png`, `training-researcher.png`, `baidu-cloud.png`, `quark-orbit.png`, `comfy-node-artist.png` and `system-engineer.png` were designed for this project with the built-in image tool. Speech bubbles, penguin colors, cloud-drive motifs and the installed ComfyUI yellow/dark-plum icon inspire their visual themes; training and performance use generic research and hardware motifs. Existing character sheets were used for pixel-style guidance only. These are original project fan mascots, not official Tencent, Baidu, Quark or Comfy Org characters. They are project artwork outside the code MIT license and follow the project's existing noncommercial artwork conditions; no brand or trademark rights are granted. Exact prompts and selected output metadata: `docs/remaining-character-art-prompts.md`.

七位角色为本项目设计的图标主题女性像素 Q 版：微信信使、QQ 企鹅围巾少女、论文研究员、百度云盘管理员、夸克星环少女、ComfyUI 节点工匠、硬件工程师。它们不是相应产品的官方人物；作为项目美术素材遵循现有非商业用途条件，不纳入代码 MIT 许可，也不授予品牌或商标权利。
