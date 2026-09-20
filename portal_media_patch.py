#!/usr/bin/env python3
"""Apply the small, marked source changes required by portal media v2."""

from pathlib import Path
import re
import sys


MARK = "RETRO WORMHOLE ANIMATION V2"


def write(path, text, dry_run=False):
    original = path.read_text(encoding="utf-8", errors="ignore")
    if text == original:
        print(f"unchanged: {path}")
        return
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def insert_before(text, marker, addition, label):
    if addition.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f"Cannot find {label} insertion point")
    return text.replace(marker, addition + marker, 1)


def patch_web_server(path, dry_run=False):
    text = path.read_text(encoding="utf-8", errors="ignore")
    get_block = '''            # RETRO WORMHOLE ANIMATION V2 GET START
            elif request_path == "/get/portal_media":
                from portal_media_manager import PortalMediaManager
                data = PortalMediaManager().get_config()
            # RETRO WORMHOLE ANIMATION V2 GET END

'''
    text = insert_before(
        text,
        '            elif request_path == "/get/config":',
        get_block,
        "GET route",
    )

    limit_block = '''            # RETRO WORMHOLE ANIMATION V2 UPLOAD LIMIT START
            if self.path.endswith('/update/portal_media_asset') and content_len > 110 * 1024 * 1024:
                self.send_json_response({"success": False, "message": "The upload request is larger than 110 MB."})
                return
            # RETRO WORMHOLE ANIMATION V2 UPLOAD LIMIT END
'''
    marker = "            body = self.rfile.read(content_len)"
    if "RETRO WORMHOLE ANIMATION V2 UPLOAD LIMIT START" not in text:
        if marker not in text:
            raise RuntimeError("Cannot find POST body insertion point")
        text = text.replace(marker, limit_block + "\n" + marker, 1)

    post_block = '''            # RETRO WORMHOLE ANIMATION V2 POST START
            elif self.path.endswith('/update/portal_media'):
                try:
                    from portal_media_manager import PortalMediaManager
                    data = PortalMediaManager().update(data)
                except (TypeError, ValueError, OSError) as ex:
                    data = {"success": False, "message": str(ex)}

            elif self.path.endswith('/update/portal_media_asset'):
                try:
                    from portal_media_manager import PortalMediaManager
                    data = PortalMediaManager().add(data)
                except (TypeError, ValueError, OSError) as ex:
                    data = {"success": False, "message": str(ex)}

            elif self.path.endswith('/update/delete_portal_media_asset'):
                try:
                    from portal_media_manager import PortalMediaManager
                    data = PortalMediaManager().delete(data)
                except (TypeError, ValueError, OSError) as ex:
                    data = {"success": False, "message": str(ex)}
            # RETRO WORMHOLE ANIMATION V2 POST END

'''
    text = insert_before(
        text,
        "            elif self.path == '/update/config':",
        post_block,
        "POST route",
    )
    compile(text, str(path), "exec")
    write(path, text, dry_run)


def patch_script_page(path, script, dry_run=False):
    text = path.read_text(encoding="utf-8", errors="ignore")
    tag = f'    <!-- {MARK} -->\n    <script src="{script}?v=2.0.2"></script>\n'
    pattern = re.compile(
        r'\s*<!-- ' + re.escape(MARK) + r' -->\s*<script src="'
        + re.escape(script) + r'\?v=[^"]+"></script>\s*'
    )
    if pattern.search(text):
        text = pattern.sub("\n" + tag, text, count=1)
    else:
        text = insert_before(text, "</body>", tag, f"script tag in {path}")
    write(path, text, dry_run)


def ensure_gate_layers(text):
    clip = '''<clipPath id="wormholeClip">
  <circle cx="337" cy="335" r="237" />
</clipPath>
'''
    layers = '''<!-- WORMHOLE BLACKHOLE GIF UNIVERSAL PATCH -->
<image class="wormhole-gif" href="images/wormhole.gif" x="29" y="27" width="616" height="616" preserveAspectRatio="xMidYMid slice" clip-path="url(#wormholeClip)"/>
<image class="blackhole-gif" href="images/blackhole.gif" x="29" y="27" width="616" height="616" preserveAspectRatio="xMidYMid slice" clip-path="url(#wormholeClip)"/>
'''
    if 'id="wormholeClip"' not in text:
        text, count = re.subn(
            r'(<radialGradient\b[^>]*id=["\']radialGradient["\'])',
            clip + r'\n\1', text, count=1, flags=re.I,
        )
        if count != 1:
            raise RuntimeError("Cannot find radialGradient for circular media clip")
    if 'class="wormhole-gif"' not in text or 'class="blackhole-gif"' not in text:
        pattern = re.compile(
            r'(<circle\b(?=[^>]*\bcx=["\']337["\'])(?=[^>]*\bcy=["\']335["\'])(?=[^>]*\br=["\']237["\'])(?=[^>]*fill=["\']url\(#radialGradient\)["\'])[^>]*/?>)',
            re.I,
        )
        match = pattern.search(text)
        if not match:
            raise RuntimeError("Cannot find the original wormhole circle")
        circle = re.sub(
            r'fill=["\']url\(#radialGradient\)["\']', 'fill="transparent"', match.group(1), count=1, flags=re.I
        )
        text = text[:match.start()] + layers + circle + text[match.end():]
    return text


def patch_dial_page(path, dry_run=False):
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = ensure_gate_layers(text)
    css = f'    <!-- {MARK} -->\n    <link rel="stylesheet" href="css/portal_media.css?v=2.0.2-safari-smooth-video">\n'
    js = f'    <!-- {MARK} -->\n    <script src="js/portal_media.js?v=2.0.2-safari-smooth-video"></script>\n'
    css_pattern = re.compile(
        r'\s*<!-- ' + re.escape(MARK)
        + r' -->\s*<link rel="stylesheet" href="css/portal_media\.css\?v=[^"]+">\s*'
    )
    js_pattern = re.compile(
        r'\s*<!-- ' + re.escape(MARK)
        + r' -->\s*<script src="js/portal_media\.js\?v=[^"]+"></script>\s*'
    )
    if css_pattern.search(text):
        text = css_pattern.sub("\n" + css, text, count=1)
    else:
        text = insert_before(text, "</head>", css, f"CSS tag in {path}")
    if js_pattern.search(text):
        text = js_pattern.sub("\n" + js, text, count=1)
    else:
        text = insert_before(text, "</body>", js, f"JS tag in {path}")
    write(path, text, dry_run)


def patch_dial_js(path, dry_run=False):
    if not path.is_file():
        print(f"optional file missing: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "const CLASS_BLACK_HOLE = 'black-hole-active';" not in text:
        marker = "const STATE_DIAL_IN = 'dialing_in';"
        if marker not in text:
            raise RuntimeError(f"Cannot find state constants in {path}")
        text = text.replace(marker, marker + "\nconst CLASS_BLACK_HOLE = 'black-hole-active';", 1)
    if "function updateBlackHoleGifState()" not in text:
        marker = "function updateDestination(lastXGlyphs) {"
        if marker not in text:
            raise RuntimeError(f"Cannot find updateDestination in {path}")
        function = '''function updateBlackHoleGifState() {
  border.classList.toggle(
    CLASS_BLACK_HOLE,
    state === STATE_ACTIVE && gateStatus.wormhole_active && gateStatus.black_hole_connected,
  );
}

'''
        text = text.replace(marker, function + marker, 1)
    if "updateBlackHoleGifState();" not in text:
        marker = "  if (gdo.state === 'recognized' || gdo.state === 'complete') {"
        if marker not in text:
            raise RuntimeError(f"Cannot find GDO status block in {path}")
        text = text.replace(marker, "  updateBlackHoleGifState();\n\n" + marker, 1)
    write(path, text, dry_run)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: portal_media_patch.py TARGET [--dry-run]")
    root = Path(sys.argv[1]).resolve()
    dry_run = "--dry-run" in sys.argv[2:]
    web = root / "web" if (root / "web/retro").is_dir() else root
    app = web.parent
    if not (web / "retro").is_dir() or not (app / "classes/web_server.py").is_file():
        raise SystemExit(f"ERROR: SG1 v4 target not found: {root}")

    patch_web_server(app / "classes/web_server.py", dry_run)
    patch_script_page(web / "debug.htm", "/js/portal_media_debug.js", dry_run)
    interfaces = [web / "retro"]
    guest = web / "guest113" / "retro"
    if guest.is_dir():
        interfaces.append(guest)
    for interface in interfaces:
        for page in ("dial.html", "dial9.html"):
            patch_dial_page(interface / page, dry_run)
        patch_dial_js(interface / "js/dial.js", dry_run)


if __name__ == "__main__":
    main()
