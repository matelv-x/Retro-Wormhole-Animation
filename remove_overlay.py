#!/usr/bin/env python3
from pathlib import Path
import re
import sys


def write_if_changed(path, text):
    original = path.read_text(encoding="utf-8", errors="ignore")
    if text == original:
        print(f"Already clean: {path}")
        return
    path.write_text(text, encoding="utf-8")
    print(f"Updated: {path}")


arguments = sys.argv[1:]
remove_all_media = "--remove-all-media" in arguments
paths = [argument for argument in arguments if not argument.startswith("--")]
target = Path(paths[0] if paths else "/home/pi/sg1_v4/web")
if (target / "web/retro").is_dir():
    target = target / "web"
if not (target / "retro").is_dir():
    raise SystemExit(f"ERROR: target web folder not found: {target}")

app_root = target.parent

server = app_root / "classes/web_server.py"
if server.is_file():
    text = server.read_text(encoding="utf-8", errors="ignore")
    for start, end in (
        ("            # RETRO WORMHOLE ANIMATION V2 GET START", "            # RETRO WORMHOLE ANIMATION V2 GET END"),
        ("            # RETRO WORMHOLE ANIMATION V2 UPLOAD LIMIT START", "            # RETRO WORMHOLE ANIMATION V2 UPLOAD LIMIT END"),
        ("            # RETRO WORMHOLE ANIMATION V2 POST START", "            # RETRO WORMHOLE ANIMATION V2 POST END"),
    ):
        text = re.sub(
            r"\n[ \t]*" + re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"[ \t]*\n+",
            "\n",
            text,
        )
    write_if_changed(server, text)

debug = target / "debug.htm"
if debug.is_file():
    text = debug.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(
        r'^[ \t]*<!-- RETRO WORMHOLE ANIMATION V2 -->[ \t]*\r?\n'
        r'[ \t]*<script src="/js/portal_media_debug\.js\?v=[^"]+"></script>[ \t]*(?:\r?\n)?',
        "", text, flags=re.MULTILINE,
    )
    write_if_changed(debug, text)

interfaces = [target / "retro"]

for interface in interfaces:
  for name in ("dial.html", "dial9.html"):
    path = interface / name
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(
        r'^[ \t]*<!-- RETRO WORMHOLE ANIMATION V2 -->[ \t]*\r?\n'
        r'[ \t]*<(?:link rel="stylesheet" href="css/portal_media\.css\?v=[^"]+"|script src="js/portal_media\.js\?v=[^"]+"></script)>[ \t]*(?:\r?\n)?',
        "", text, flags=re.MULTILINE,
    )
    text = re.sub(r"\s*<!-- WORMHOLE BLACKHOLE GIF UNIVERSAL PATCH -->\s*", "\n", text)
    text = re.sub(r'\s*<image class="wormhole-gif"[^>]*/>\s*', "\n", text)
    text = re.sub(r'\s*<image class="blackhole-gif"[^>]*/>\s*', "\n", text)
    text = re.sub(
        r'\s*<clipPath id="wormholeClip">\s*<circle cx="337" cy="335" r="237" />\s*</clipPath>\s*',
        "\n",
        text,
    )
    text = text.replace('fill="transparent" stroke-width="4.96px"', 'fill="url(#radialGradient)" stroke-width="4.96px"')
    write_if_changed(path, text)

for rel in ("retro/css/dial.css", "retro/css/dial9.css"):
    path = target / rel
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(
        r"\n*/\* WORMHOLE BLACKHOLE GIF UNIVERSAL PATCH START \*/[\s\S]*?/\* WORMHOLE BLACKHOLE GIF UNIVERSAL PATCH END \*/\s*\Z",
        "\n",
        text,
    )
    write_if_changed(path, text)

for interface in interfaces:
    path = interface / "js/dial.js"
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = text.replace("\nconst CLASS_BLACK_HOLE = 'black-hole-active';", "")
        text = re.sub(
            r"\nfunction updateBlackHoleGifState\(\) \{[\s\S]*?\n\}\n\n(?=function updateDestination)",
            "\n", text, count=1,
        )
        text = text.replace("  updateBlackHoleGifState();\n\n", "")
        write_if_changed(path, text)

numbered_media = re.compile(
    r"^(?:wormhole|blackhole)\d+\.(?:gif|png|jpe?g|mp4|webm)$",
    re.IGNORECASE,
)
for interface in interfaces:
    image_dir = interface / "images"
    for name in ("wormhole.gif", "blackhole.gif"):
        path = image_dir / name
        if path.is_file():
            path.unlink()
            print(f"Removed: {path}")
    if remove_all_media and image_dir.is_dir():
        for path in image_dir.iterdir():
            if path.is_file() and numbered_media.fullmatch(path.name):
                path.unlink()
                print(f"Removed uploaded media: {path}")

for path in (
    app_root / "classes/portal_media_manager.py",
    target / "js/portal_media_debug.js",
    target / "retro/js/portal_media.js",
    target / "retro/css/portal_media.css",
    app_root / "config/portal-media.json",
):
    if path.is_file():
        path.unlink()
        print(f"Removed: {path}")

print("Retro Wormhole Animation overlay removed.")
