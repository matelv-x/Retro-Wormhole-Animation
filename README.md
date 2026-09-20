# Retro Wormhole Animation

[![Downloads](https://img.shields.io/github/downloads/matelv-x/Retro-Wormhole-Animation/total?label=downloads)](https://github.com/matelv-x/Retro-Wormhole-Animation/releases)
[![Latest release](https://img.shields.io/github/v/release/matelv-x/Retro-Wormhole-Animation)](https://github.com/matelv-x/Retro-Wormhole-Animation/releases/latest)

Animated, user-selectable Wormhole and Black Hole media for the Stargate SG1 v4 Retro web interface.

<img width="232" height="216" alt="Original Wormhole" src="./images/original-wormhole.png" />
<img width="232" height="216" alt="Animated Wormhole" src="./images/animated-wormhole.png" />
<img width="232" height="235" alt="Select Wormhole" src="./images/select-wormhole.png" />
<img width="232" height="235" alt="Select Black Hole" src="./images/select-black-hole.png" />
<img width="1060" height="159" alt="New Select Wormhole button" src="./images/select-wormhole-button.png" />

## Version 2 features

- Adds **Select Wormhole** to `debug.htm` without replacing the page.
- Opens one picker with separate **Wormhole** and **Black Hole** tabs.
- Accepts GIF, PNG, JPG/JPEG, MP4, and WebM files.
- Converts MP4 and WebM uploads to MP4/H.264 with `yuv420p` and fast-start metadata for Safari compatibility.
- Automatically assigns sequential names such as `wormhole1.gif`, `wormhole2.mp4`, `blackhole1.png`, and `blackhole2.mp4`; after deletion, the smallest available number is reused.
- Provides thumbnail previews, selection, upload, right-click or checkbox deletion, and an individual 50–250% scale for every file.
- Centers and crops media into the inner Stargate ring with a circular mask and `object-fit: cover`.
- Supports Safari, Firefox, Chrome, and Chromium-based kiosk browsers.
- Protects the original `wormhole.gif` and `blackhole.gif` from deletion.

## Install

Requirements:

- Stargate SG1 v4 in `/home/pi/sg1_v4`
- Python 3 and Pillow in the Stargate runtime
- `ffmpeg` for MP4 or WebM uploads

```bash
cd /home/pi
rm -rf Retro-Wormhole-Animation
git clone https://github.com/matelv-x/Retro-Wormhole-Animation.git
cd Retro-Wormhole-Animation
chmod +x install.sh restore.sh
sudo ./install.sh --target /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

The installer creates a timestamped backup before changing anything. Run a read-only compatibility check first if desired:

```bash
sudo ./install.sh --target /home/pi/sg1_v4 --dry-run
```

## Restore the state from before installation

```bash
cd /home/pi/Retro-Wormhole-Animation
sudo ./restore.sh --target /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

The v2 restore uses the exact manifest and backup made by the most recent install. Uploaded numbered media are left intact so personal files are not destroyed accidentally.

## Completely remove v1 and v2

```bash
sudo ./restore.sh --target /home/pi/sg1_v4 --remove-all
sudo systemctl restart stargate.service
```

`--remove-all` first restores the pre-v2 backup, then removes the original GIF-only v1 overlay, all v2 integration files and configuration, and every numbered Wormhole/Black Hole upload. Repository clone folders and timestamped backups are retained.

## Previous GIF-only version

The original GIF-only edition remains available as the [`v1.0.0` release](https://github.com/matelv-x/Retro-Wormhole-Animation/releases/tag/v1.0.0). Each GitHub release also provides source ZIP and TAR archives.

## Surgical installation boundaries

The installer:

- patches only marked route blocks in `classes/web_server.py`;
- adds isolated `portal_media_manager.py`, `portal_media_debug.js`, `portal_media.js`, and `portal_media.css` files;
- inserts only marked script/style tags and the two circular SVG media layers;
- preserves Ring Symbols and unrelated Stargate customizations;
- never changes `web/fan113`;
- supports `--keep-crosshair` and `--dry-run`.

## Attribution and originality

Original base project: https://github.com/polklabs/stargate-retro

The Retro pages being patched come from the Polklabs Retro UI project. This repository contains the matelv-x SG1 v4 add-on, installer, media-management code, and Wormhole/Black Hole overlay behavior.
