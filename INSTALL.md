# Installation

## Requirements

- Stargate SG1 v4 installed at `/home/pi/sg1_v4`
- Python 3 with Pillow available to the Stargate service
- `ffmpeg` available in `PATH` for MP4 and WebM conversion

## Compatibility check without writes

```bash
cd /home/pi/Retro-Wormhole-Animation
sudo ./install.sh --target /home/pi/sg1_v4 --dry-run
```

## Standard install

```bash
cd /home/pi/Retro-Wormhole-Animation
sudo ./install.sh --target /home/pi/sg1_v4 --install-dependencies
sudo systemctl restart stargate.service
```

The installer checks dependencies before modifying SG1 v4. With
`--install-dependencies`, missing Pillow is installed into the exact Python
environment used by `stargate.service`, and missing `ffmpeg` is installed
through APT. Without this option, missing dependencies stop installation with
an actionable error.

## Keep the original center crosshair

```bash
sudo ./install.sh --target /home/pi/sg1_v4 --install-dependencies --keep-crosshair
sudo systemctl restart stargate.service
```

## Restore

```bash
sudo ./restore.sh --target /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

Restore reads the last v2 backup manifest and returns every installer-managed file to its exact pre-install state. Numbered media uploaded later are preserved intentionally.

## Remove both the legacy v1 overlay and v2

```bash
sudo ./restore.sh --target /home/pi/sg1_v4 --remove-all
sudo systemctl restart stargate.service
```

This also deletes every numbered Wormhole and Black Hole media upload. It does not delete repository clone folders or timestamped backups.
