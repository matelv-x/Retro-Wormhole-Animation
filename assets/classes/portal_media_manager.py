"""Wormhole and Black Hole media library for the SG1 v4 web interface."""

import base64
import binascii
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


class PortalMediaManager:
    MEDIA_TYPES = ("wormhole", "blackhole")
    IMAGE_FORMATS = {"GIF": ".gif", "JPEG": ".jpg", "PNG": ".png"}
    FILE_PATTERN = r"(?:gif|png|jpe?g|mp4|webm)"
    MAX_UPLOAD_BYTES = 80 * 1024 * 1024

    def __init__(self):
        self.app_dir = Path(__file__).resolve().parent.parent
        self.web_dir = self.app_dir / "web"
        self.config_path = self.app_dir / "config" / "portal-media.json"

    def _image_dirs(self):
        directories = [self.web_dir / "retro" / "images"]
        guest = self.web_dir / "guest113" / "retro" / "images"
        if guest.parent.is_dir():
            directories.append(guest)
        return directories

    @staticmethod
    def _atomic_json(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)

    def _read_stored(self):
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, ValueError):
            data = {}
        return data if isinstance(data, dict) else {}

    def _files(self, media_type):
        pattern = re.compile(
            rf"^{re.escape(media_type)}(\d*)\.{self.FILE_PATTERN}$", re.IGNORECASE
        )
        names = set()
        for folder in self._image_dirs():
            if folder.is_dir():
                names.update(path.name for path in folder.iterdir() if path.is_file() and pattern.fullmatch(path.name))

        def sort_key(name):
            match = pattern.fullmatch(name)
            number = int(match.group(1)) if match and match.group(1) else 0
            return number, name.lower()

        return sorted(names, key=sort_key)

    def get_config(self):
        stored = self._read_stored()
        result = {"success": True, "min_scale": 50, "max_scale": 250}
        for media_type in self.MEDIA_TYPES:
            files = self._files(media_type)
            base = f"{media_type}.gif"
            selected = stored.get(f"{media_type}_selected", base)
            if selected not in files:
                selected = base if base in files else (files[0] if files else base)
            raw_scales = stored.get(f"{media_type}_scales", {})
            if not isinstance(raw_scales, dict):
                raw_scales = {}
            scales = {}
            for filename in files:
                try:
                    scales[filename] = max(50, min(250, int(raw_scales.get(filename, 100))))
                except (TypeError, ValueError):
                    scales[filename] = 100
            result[media_type] = {
                "selected": selected,
                "files": files,
                "scales": scales,
                "scale": scales.get(selected, 100),
            }
        return result

    def update(self, request):
        if not isinstance(request, dict):
            raise ValueError("Invalid portal-media request.")
        media_type = str(request.get("media_type", "")).lower()
        if media_type not in self.MEDIA_TYPES:
            raise ValueError("Invalid portal-media type.")
        current = self.get_config()[media_type]
        filename = str(request.get("filename", current["selected"]))
        if filename not in current["files"]:
            raise ValueError("The selected media file does not exist.")
        try:
            scale = int(request.get("scale", current["scales"].get(filename, 100)))
        except (TypeError, ValueError) as ex:
            raise ValueError("Scale must be a number from 50 to 250.") from ex
        if scale < 50 or scale > 250:
            raise ValueError("Scale must be a number from 50 to 250.")

        stored = self._read_stored()
        scales = stored.get(f"{media_type}_scales", {})
        if not isinstance(scales, dict):
            scales = {}
        scales[filename] = scale
        stored[f"{media_type}_selected"] = filename
        stored[f"{media_type}_scales"] = scales
        self._atomic_json(self.config_path, stored)
        return self.get_config()

    @staticmethod
    def _decode_upload(request):
        encoded = request.get("content", "")
        if not isinstance(encoded, str) or "," not in encoded:
            raise ValueError("The uploaded media data is missing.")
        try:
            raw = base64.b64decode(encoded.split(",", 1)[1], validate=True)
        except (ValueError, binascii.Error) as ex:
            raise ValueError("Unable to decode the uploaded media.") from ex
        if not raw or len(raw) > PortalMediaManager.MAX_UPLOAD_BYTES:
            raise ValueError("The media file must be between 1 byte and 80 MB.")
        return raw

    def _prepare_image(self, raw):
        try:
            from PIL import Image
            with Image.open(io.BytesIO(raw)) as image:
                image_format = image.format
                image.verify()
        except Exception as ex:
            raise ValueError("The selected file is not a valid GIF, JPG, or PNG image.") from ex
        extension = self.IMAGE_FORMATS.get(image_format)
        if not extension:
            raise ValueError("Only GIF, JPG/JPEG, and PNG images are supported.")
        return raw, extension

    @staticmethod
    def _prepare_video(raw, source_extension):
        if not shutil.which("ffmpeg"):
            raise ValueError("ffmpeg is required to install MP4 or WebM video.")
        source_path = None
        output_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=source_extension, delete=False) as source:
                source.write(raw)
                source_path = Path(source.name)
            output_fd, output_name = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            output_path = Path(output_name)
            stream_copy = False
            if source_extension == ".mp4" and shutil.which("ffprobe"):
                probe = subprocess.run(
                    [
                        "ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=codec_name,pix_fmt",
                        "-of", "json", str(source_path),
                    ],
                    capture_output=True, text=True, timeout=60, check=False,
                )
                if probe.returncode == 0:
                    try:
                        streams = json.loads(probe.stdout).get("streams", [])
                        stream = streams[0] if streams else {}
                        stream_copy = (
                            stream.get("codec_name") == "h264"
                            and stream.get("pix_fmt") in ("yuv420p", "yuvj420p")
                        )
                    except (TypeError, ValueError, json.JSONDecodeError):
                        stream_copy = False

            if stream_copy:
                # Do not re-encode an already Safari-compatible MP4. Re-encoding
                # changed its frame cadence and caused visible judder in Safari.
                command = [
                    "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source_path),
                    "-map", "0:v:0", "-an", "-c:v", "copy",
                    "-movflags", "+faststart", str(output_path),
                ]
            else:
                command = [
                    "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source_path),
                    "-map", "0:v:0", "-an", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-profile:v", "main", "-pix_fmt", "yuv420p",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    "-movflags", "+faststart", str(output_path),
                ]
            try:
                converted = subprocess.run(command, capture_output=True, text=True, timeout=900, check=False)
            except (OSError, subprocess.TimeoutExpired) as ex:
                raise ValueError("Video conversion failed or exceeded the 15-minute limit.") from ex
            if converted.returncode != 0 or not output_path.is_file() or output_path.stat().st_size == 0:
                detail = converted.stderr.strip().splitlines()[-1] if converted.stderr.strip() else "unknown ffmpeg error"
                raise ValueError(f"Unable to convert video to Safari-compatible MP4: {detail}")
            return output_path.read_bytes(), ".mp4"
        finally:
            for path in (source_path, output_path):
                if path:
                    try:
                        path.unlink(missing_ok=True)
                    except OSError:
                        pass

    def add(self, request):
        if not isinstance(request, dict):
            raise ValueError("Invalid upload request.")
        media_type = str(request.get("media_type", "")).lower()
        if media_type not in self.MEDIA_TYPES:
            raise ValueError("Invalid portal-media type.")
        original_name = str(request.get("filename", ""))
        extension_match = re.search(r"\.(gif|png|jpe?g|mp4|webm)$", original_name, re.IGNORECASE)
        if not extension_match:
            raise ValueError("Only GIF, PNG, JPG/JPEG, MP4, and WebM files are supported.")
        raw = self._decode_upload(request)
        source_extension = "." + extension_match.group(1).lower()
        if source_extension in (".mp4", ".webm"):
            raw, extension = self._prepare_video(raw, source_extension)
        else:
            raw, extension = self._prepare_image(raw)

        used_numbers = set()
        number_pattern = re.compile(
            rf"^{re.escape(media_type)}(\d*)\.{self.FILE_PATTERN}$", re.IGNORECASE
        )
        for filename in self._files(media_type):
            match = number_pattern.fullmatch(filename)
            if match:
                used_numbers.add(int(match.group(1)) if match.group(1) else 0)
        next_number = 1
        while next_number in used_numbers:
            next_number += 1
        filename = f"{media_type}{next_number}{extension}"

        temporary_paths = []
        directories = self._image_dirs()
        try:
            for folder in directories:
                folder.mkdir(parents=True, exist_ok=True)
                temporary = folder / f".{filename}.upload"
                temporary.write_bytes(raw)
                temporary_paths.append(temporary)
            for temporary, folder in zip(temporary_paths, directories):
                os.replace(temporary, folder / filename)
        finally:
            for temporary in temporary_paths:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

        result = self.get_config()
        result.update({"success": True, "filename": filename, "media_type": media_type})
        return result

    def delete(self, request):
        if not isinstance(request, dict):
            raise ValueError("Invalid delete request.")
        media_type = str(request.get("media_type", "")).lower()
        if media_type not in self.MEDIA_TYPES:
            raise ValueError("Invalid portal-media type.")
        filename = str(request.get("filename", ""))
        protected = f"{media_type}.gif"
        if filename == protected:
            raise ValueError(f"The original {protected} is protected and cannot be deleted.")
        if not re.fullmatch(
            rf"{re.escape(media_type)}\d+\.{self.FILE_PATTERN}", filename, re.IGNORECASE
        ):
            raise ValueError("Invalid portal-media filename.")
        targets = [folder / filename for folder in self._image_dirs()]
        if not any(path.is_file() for path in targets):
            raise ValueError("The selected media file does not exist.")
        for target in targets:
            if target.is_file():
                target.unlink()

        stored = self._read_stored()
        scales_key = f"{media_type}_scales"
        scales = stored.get(scales_key, {})
        if isinstance(scales, dict):
            scales.pop(filename, None)
            stored[scales_key] = scales
        if stored.get(f"{media_type}_selected") == filename:
            stored[f"{media_type}_selected"] = protected
        self._atomic_json(self.config_path, stored)
        result = self.get_config()
        result.update({"success": True, "deleted": filename, "media_type": media_type})
        return result
