# Changelog

## 2.0.2 - 2026-09-19

- Removed all `guest113` installation, patching, media synchronization, backup,
  and removal behavior. The installer now manages only the main `web/retro`
  interface.
- Made repeated installation byte-stable and made `--remove-all` restore the
  original HTML, CSS, and server formatting without accumulating whitespace.
- Fixed Chrome and Brave MP4 visibility by keeping video filenames out of SVG
  image elements and hiding the corresponding SVG media layer during playback.
- Fixed Chrome Black Hole video visibility by suppressing the legacy SVG
  danger-gradient fill only while a Black Hole video is selected.
- Corrected README image aspect ratios while keeping repository-hosted assets.
- Replaced CSS `clip-path` video cropping with compositor-friendly circular
  `border-radius` overflow clipping, avoiding Safari per-frame repaint judder.
- Removed paint containment from the live video layer while retaining GPU-backed
  scaling and exact circular cropping.
- Preserved compatible MP4/H.264 video streams instead of re-encoding them,
  preventing Safari frame-cadence judder while still removing audio and moving
  MP4 metadata to the beginning of the file.
- Restored the Safari-specific video compositing fix: WebKit circular clipping,
  GPU-backed layers, hidden backfaces, and explicit inline playback attributes.
- Refreshed both portal media asset cache keys so Safari does not reuse the old
  CSS or JavaScript.
- Kept the SG1 Iris canvas above Wormhole and Black Hole GIF, image, and video layers.
- Refreshed the media stylesheet cache key so browsers load the Iris stacking fix immediately.
- Fixed placement of **Select Wormhole** so it appears directly after **Close Wormhole**.
- Kept the media picker hidden until **Select Wormhole** is clicked.
- Added compatibility with both the Dynamic-Wormhole menu button and the original SG1 v4 **Open Wormhole** button.

## 2.0.1 - 2026-09-19

- Added `restore.sh --remove-all` for complete removal of the legacy v1 overlay and v2 integration.
- Reused the smallest available sequence number after a media file is deleted.
- Confirmed WebM upload and automatic conversion to Safari-compatible MP4/H.264.
- Added explicit deletion of numbered Wormhole/Black Hole uploads when complete removal is requested.
- Preserved the default manifest-based restore behavior and all historical releases.

## 2.0.0 - 2026-09-19

- Added the Select Wormhole control to the SG1 v4 debug page.
- Added a shared Wormhole and Black Hole media picker.
- Added GIF, PNG, JPG/JPEG, MP4, and WebM upload support.
- Added automatic sequential naming for both media libraries.
- Added thumbnail preview, selection, protected deletion, and per-file 50–250% scaling.
- Added centered circular cropping for images and video.
- Added automatic video conversion to Safari-compatible MP4/H.264.
- Added exact manifest-based restore for installer-managed files.

## 1.0.0 - 2026-09-17

- Original animated Wormhole and Black Hole GIF overlay.
- Surgical HTML, CSS, and dial-state patching.
