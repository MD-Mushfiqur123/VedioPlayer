# MediaPlayer (PyQt6)

A modern desktop media player built with PyQt6 featuring a sleek dark UI, rich playback controls, and playlist management. Ideal for local audio/video playback with equalizer presets, bookmarks, and quick playlist tools.

## Features
- Plays common audio/video formats via QtMultimedia
- Playlist manager with add/remove/clear, search filter, save/load, favorites
- Playback controls: play/pause, stop, previous/next, repeat, shuffle, speed control
- Precision tools: A/B loop, frame step, progress scrubbing, time display
- Enhancements: equalizer presets, volume slider, screenshots, bookmarks dropdown
- Subtitle loading and fullscreen toggle

## Requirements
- Python 3.10+ (recommended)
- Dependencies: `PyQt6`, `pyinstaller` (see `requirements.txt`)
- Windows is the primary build target (PyInstaller is configured for a Windows `.exe`).

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app
```bash
python main.py
```

## Build a standalone `.exe`
Uses PyInstaller via `build_exe.py`.
```bash
python build_exe.py
```
The packaged app will appear in `dist/MediaPlayer.exe`.

## Useful shortcuts
- `Ctrl+O`: Open file
- `Ctrl+F`: Open folder
- `Space`: Play/Pause
- `Ctrl+Left / Ctrl+Right`: Previous / Next
- `F`: Fullscreen toggle
- `Alt+F4`: Exit

## Project structure
- `main.py` — Application entry point and UI/logic
- `build_exe.py` — PyInstaller build script for Windows
- `requirements.txt` — Python dependencies
- `QUICKSTART.md` — Additional quick notes (if present)

## Troubleshooting
- Missing codecs: ensure the required media codecs are installed on the system.
- If PyInstaller build fails, update `pip`, `setuptools`, and `pyinstaller`, then retry.


