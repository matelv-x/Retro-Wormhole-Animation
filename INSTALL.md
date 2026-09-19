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
sudo ./install.sh --target /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Keep the original center crosshair

```bash
sudo ./install.sh --target /home/pi/sg1_v4 --keep-crosshair
sudo systemctl restart stargate.service
```

## Restore

```bash
sudo ./restore.sh --target /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

Restore reads the last v2 backup manifest and returns every installer-managed file to its exact pre-install state. Numbered media uploaded later are preserved intentionally.
