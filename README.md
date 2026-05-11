# CamFilter Recorder

**Version 1.3.0** — Cross-platform webcam recorder with real-time filters.

Record your camera with 14 live filters — Night Vision, Infrared/Thermal, Cartoon, Pencil Sketch, Sepia, and more — at resolutions from 240p up to 1080p. Save snapshots at any time. Ships as a self-contained installer on Windows, Fedora, and Ubuntu/Debian, and as a bundle on macOS. No Python installation required for end users.

---

## Features

- **14 real-time filters** — Normal, Grayscale, Night Vision, Infrared/Thermal, Cartoon, Pencil Sketch, Sepia, Vignette, Negative, Emboss, Blur, Edge Detection, Vintage, Pixelate
- **Resolution control** — 240p · 360p · 480p · 720p · 1080p
- **Brightness & Contrast sliders** applied before the filter
- **Snapshot** — save any frame as PNG, JPG, BMP, or TIFF with filter name and timestamp baked into the filename (`Ctrl+S`)
- **Video recording** with accurate FPS measurement and smart codec fallback
- **Recording timer** with blinking REC indicator
- **Always on Top** and **Fullscreen Preview** modes
- **Settings dialog** — configure video format (AVI / MP4), image format, and separate output folders for recordings and snapshots
- **Persistent preferences** — all settings survive app restarts
- **Dark theme** UI built with PyQt6

---

## Installation

> End users do **not** need Python or any other dependency. Everything is bundled.

### Windows

1. Download `CamFilterRecorder-Setup.exe` from the [Releases](../../releases) page.
2. Run the installer — it installs to `Program Files`, creates a Start Menu group and a Desktop shortcut.
3. Launch **CamFilter Recorder** from the Start Menu or Desktop.

To uninstall: **Control Panel → Programs → CamFilter Recorder → Uninstall**, or use the shortcut in the Start Menu group.

### Fedora / RHEL

```bash
sudo dnf install CamFilterRecorder-1.3.0-1.fc40.x86_64.rpm
# Launch from your application menu or:
CamFilterRecorder
```

### Ubuntu / Debian

```bash
sudo dpkg -i camfilter-recorder_1.3.0_amd64.deb
# Launch from your application menu or:
CamFilterRecorder
```

### macOS

1. Download `CamFilterRecorder-macos.zip` from the [Releases](../../releases) page.
2. Unzip and move `CamFilterRecorder` to your Applications folder.
3. Double-click to launch. If macOS blocks it, right-click → Open to bypass Gatekeeper.

---

## Running from Source

Requires **Python 3.10+**.

```bash
git clone https://github.com/your-username/camfilter-recorder.git
cd camfilter-recorder/camera-recorder-app
python install_and_run.py
```

`install_and_run.py` automatically creates a virtual environment, installs all dependencies, and launches the app. You only need to run it once for setup; subsequent runs reuse the existing environment.

Manual setup:

```bash
pip install -r requirements.txt
python main.py
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+R` | Start / Stop Recording |
| `Ctrl+S` | Take Snapshot |
| `Ctrl+,` | Open Settings |
| `Ctrl+O` | Open Output Folder |
| `Ctrl+T` | Toggle Always on Top |
| `F11` | Toggle Fullscreen Preview |
| `Ctrl+Q` | Quit |

All shortcuts are also listed in **Help → Keyboard Shortcuts**.

---

## Building from Source

### Windows (NSIS installer)

```bat
cd camera-recorder-app
build_windows.bat
cd packaging
makensis installer.nsi
```

Output: `packaging/CamFilterRecorder-Setup.exe`

### Fedora (RPM)

```bash
cd camera-recorder-app
./build_linux.sh
rpmdev-setuptree
cp dist/CamFilterRecorder ~/rpmbuild/BUILD/
cp packaging/CamFilterRecorder.spec ~/rpmbuild/SPECS/
rpmbuild -bb ~/rpmbuild/SPECS/CamFilterRecorder.spec
```

### Ubuntu / Debian (DEB)

```bash
cd camera-recorder-app
./build_linux.sh
mkdir -p deb-pkg/usr/local/bin deb-pkg/usr/share/applications
cp dist/CamFilterRecorder deb-pkg/usr/local/bin/
cp packaging/camfilter-recorder.desktop deb-pkg/usr/share/applications/
cp -r packaging/deb/DEBIAN deb-pkg/DEBIAN
dpkg-deb --build deb-pkg dist/camfilter-recorder_1.3.0_amd64.deb
```

### macOS

```bash
cd camera-recorder-app
./build_macos.sh
```

Output: `dist/CamFilterRecorder` (or `dist/CamFilterRecorder.app`)

### CI (GitHub Actions)

Push a tag starting with `v` (e.g. `v1.3.0`) to trigger all four platform builds automatically. Installers are attached to the GitHub Release.

```bash
git tag v1.3.0
git push origin v1.3.0
```

---

## Project Structure

```
camera-recorder-app/
├── main.py              # Entry point — splash screen + QApplication startup
├── window.py            # MainWindow — all UI, no business logic (MVC View)
├── controller.py        # CameraThread + RecordingController (MVC Controller)
├── dialogs.py           # AboutDialog, ShortcutsDialog, SettingsDialog
├── settings.py          # AppSettings dataclass + QSettings persistence
├── constants.py         # App-wide constants (name, version, resolutions, shortcuts)
├── filters.py           # 14 filter implementations (Strategy pattern)
├── install_and_run.py   # Cross-platform dev launcher with auto-venv
├── requirements.txt     # Python dependencies
├── build_windows.bat    # Local Windows build script
├── build_linux.sh       # Local Linux build script (auto-detects distro)
├── build_macos.sh       # Local macOS build script
├── LICENSE.txt          # MIT License
├── packaging/
│   ├── installer.nsi              # NSIS Windows installer
│   ├── CamFilterRecorder.spec     # Fedora RPM spec
│   ├── camfilter-recorder.desktop # Linux desktop entry
│   └── deb/DEBIAN/control         # Ubuntu/Debian DEB control
└── .github/
    └── workflows/
        └── build.yml              # CI: builds all four platform packages
```

---

## Output Files

By default recordings and snapshots are saved to your **Videos** folder (or **Movies** on macOS, or home directory as fallback). You can configure separate output folders for each in **File → Settings** or via the **Settings** button.

- **Recordings**: `recording_YYYYMMDD_HHMMSS_FilterName_720p.avi` (or `.mp4`)
- **Snapshots**: `snapshot_YYYYMMDD_HHMMSS_FilterName.png`

---

## Requirements (source / development)

| Package | Version |
|---|---|
| Python | 3.10+ |
| PyQt6 | latest |
| opencv-python | latest |
| numpy | latest |

---

## License

MIT License — see [LICENSE.txt](LICENSE.txt) for details.

**Author:** Lowil Ray Delos Reyes
