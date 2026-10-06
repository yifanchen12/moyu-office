# Third-party software notices

The Windows distribution bundles Python and Python libraries. Their copyright notices and license texts are distributed with the application; package metadata directories are preserved by the PyInstaller build.

| Software | License |
| --- | --- |
| Python | Python Software Foundation License; licenses/Python-LICENSE.txt |
| Flask, Werkzeug, Jinja, MarkupSafe, ItsDangerous, Click | BSD-3-Clause; respective bundled dist-info licenses |
| Blinker | MIT; bundled dist-info license |
| Pillow | HPND; bundled dist-info license |
| psutil, websocket-client, PyYAML | BSD-3-Clause, Apache-2.0, MIT respectively; bundled dist-info licenses |
| Phaser 3.80.1 | MIT; licenses/Phaser-MIT.txt |
| PyInstaller bootloader | GPL-2.0-or-later with bootloader distribution exception; licenses/PyInstaller-COPYING.txt |
| Setuptools and its vendor modules | MIT for Setuptools; each vendor's license is preserved under setuptools/_vendor/*.dist-info |
| Packaging | Apache-2.0 or BSD-2-Clause; bundled dist-info licenses |

Inno Setup is a build tool and is not included in the source or portable application. Microsoft Edge and Windows PowerShell are system prerequisites, not redistributed dependencies. Bundled scene art and fonts are covered separately by [NOTICE.md](NOTICE.md).

Windows 发布包保留 Python 与依赖库的许可证及版权声明。Inno Setup 仅用于构建；不捆绑 Microsoft Edge、PowerShell、DSH、ComfyUI、游戏工具或音乐客户端。素材许可与代码许可分别适用。
