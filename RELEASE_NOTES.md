# Release Notes — CamFilter Recorder

---

## v1.3.0 — May 12, 2026

### New Features

- **Settings dialog** (`Ctrl+,` / File → Settings… / sidebar button)
  Configure video format (AVI or MP4), snapshot image format (PNG, JPG, BMP, or TIFF), and separate output folders for recordings and snapshots — all from a single dark-themed dialog. JPEG quality defaults to 95 % when JPG format is selected.

- **Persistent user preferences**
  All settings survive app restarts via OS-native `QSettings` storage (Windows registry, macOS plist, Linux INI). The new `settings.py` module provides a clean dataclass-based API with `load_settings()` / `save_settings()` helpers.

- **Open Output Folder** (`Ctrl+O` / File → Open Output Folder)
  Opens the currently configured output folder in the system file manager — works on Windows, macOS, and Linux.

- **Linux desktop integration**
  A freedesktop.org `.desktop` file (`packaging/camfilter-recorder.desktop`) is included so the application appears in the system application menu on Linux.

- **MIT License**
  `LICENSE.txt` — full MIT license text added to the repository.

### Improvements

- **Splash screen overhaul**
  The startup splash screen is now drawn programmatically with `QPainter` — a dark-themed 520 × 300 display with gradient background, teal accent glow, version info, author credit, and technology stack line. Shows for 1.8 seconds before the main window appears.

- **Windows builds now use `--onedir` mode**
  PyInstaller packaging switched from `--onefile` to `--onedir`, resulting in faster application startup times. The NSIS installer copies the entire `--onedir` output directory.

- **New developer launcher** (`install_and_run.py`)
  A cross-platform convenience script that automatically creates a virtual environment, installs dependencies, and launches the app — one command from a fresh clone.

- **CI: DEB and macOS build jobs added**
  - Ubuntu/Debian DEB package built via `dpkg-deb` on `ubuntu-22.04`
  - macOS `.app` bundle built via PyInstaller `--onefile --windowed`, then zipped for distribution
  - All three platform artifacts (EXE, RPM, DEB, macOS .zip) are uploaded and attached to GitHub releases

### Documentation

- Added `LICENSE.txt` — MIT License

---

## v1.2.0 — May 12, 2026

### Bug Fixes

- **Sidebar controls are now responsive at any window height**
  All settings controls (Camera, Filter, Resolution, Brightness, Contrast, Output Folder) are placed inside a slim scroll area so they remain accessible when the window is resized to a small height. The Record and Snapshot buttons stay pinned at the bottom and are always visible regardless of window size.

- **Sepia, Vintage, Cartoon, Emboss, Vignette no longer freeze the app on high-res sources**
  Filter processing (brightness, contrast, and the active filter) was running on the UI thread, causing the event loop to block on expensive operations at 1080p. All processing is now done inside the camera background thread, so the UI always stays responsive. Specific optimisations per filter:
  - **Cartoon** — bilateral filter now runs on a half-resolution copy (4–10× faster at 1080p), then upscales back.
  - **Sepia / Vintage** — switched from `float64` to `float32` matrix operations (≈2× faster).
  - **Vignette / Vintage** — the vignette gradient mask is computed once per resolution and cached; subsequent frames reuse the cached mask with no allocation.
  - **Night Vision / High Contrast** — CLAHE objects are created once at module load and reused every frame instead of being rebuilt per frame.
  - **Emboss** — kernel cast to `float32`; result clamped via `cv2.CV_32F` to avoid signed-overflow artefacts.

- **Windows installer now detects an existing installation and offers to upgrade**
  Running a newer installer while the app is already installed now shows a dialog: *"CamFilter Recorder 1.0.0 is already installed. Click OK to remove it and install 1.1.0."* Clicking OK silently uninstalls the old version before the new one is written. Clicking Cancel exits without making changes. The same uninstall-then-reinstall flow works for any future version bump — no manual uninstallation step needed.

---

### New Features

- **Snapshot capture** (`Ctrl+S` / File → Take Snapshot / sidebar button)
  Save the current filtered frame as a full-resolution PNG at any time — while previewing or mid-recording. Files are named automatically with a timestamp and the active filter name (e.g. `snapshot_20260510_143022_Night_Vision.png`) and saved to the configured output folder. A 2.5-second confirmation flash appears below the button after each save.

### Improvements

- **Code architecture refactored to MVC**
  The application has been reorganised from a single 800-line file into focused modules:
  - `controller.py` — all business logic (camera thread, VideoWriter lifecycle, FPS measurement, snapshot saving). Communicates with the UI exclusively through Qt signals.
  - `window.py` — pure UI layer. No file I/O or OpenCV calls.
  - `dialogs.py` — About and Keyboard Shortcuts dialogs.
  - `constants.py` — single source of truth for app name, version, resolutions, codec list, and shortcut table.

- **Pencil Sketch filter is now real-time**
  Replaced the slow built-in `cv2.pencilSketch()` (which caused visible frame drops) with a fast Gaussian divide-blend: `gray / GaussianBlur(gray) × 256`. Renders in under 2 ms per frame.

- **Accurate recording FPS**
  FPS is now measured from a rolling window of the last 60 frame timestamps (`time.monotonic()`) instead of a hardcoded value. This prevents recordings from playing back in slow motion or fast motion when the camera delivers frames at a rate other than 30 FPS. The measured value is clamped between 5 and 60 FPS with a fallback of 25 FPS.

- **Keyboard Shortcuts dialog updated**
  The new `Ctrl+S` snapshot shortcut is listed alongside all existing shortcuts under Help → Keyboard Shortcuts.

### Bug Fixes

- **Windows CI: NSIS installer build no longer fails**
  After `choco install nsis`, `makensis` was not on the PATH in the same PowerShell session, causing the build step to fail with "term not recognized". The install and build steps are now combined in a single run block with an explicit `$env:PATH` update so `makensis` is always found.

- **Fedora RPM: corrected system package name**
  The CI was installing `libXcb` (wrong case, does not exist on Fedora 40) instead of `libxcb`. The spec and workflow now use the correct lowercase package name.

### Documentation

- Added `README.md` covering installation instructions for all four platforms, keyboard shortcuts, build instructions, project structure, and output file naming conventions.

---

## v1.0.0 — May 10, 2026

Initial release.

### Features

- Live webcam preview with 14 real-time filters:
  Normal, Grayscale, Night Vision, Infrared/Thermal, Cartoon, Pencil Sketch, Sepia, Vignette, Negative, Emboss, Blur, Edge Detection, Vintage, Pixelate
- Resolution selection: 240p · 360p · 480p · 720p · 1080p
- Brightness and Contrast sliders applied before filter processing
- Video recording with smart codec fallback (XVID → mp4v → MJPG → X264)
- Recording timer with blinking REC indicator
- Output folder picker with persistent path
- Always on Top and Fullscreen Preview modes
- Dark-themed UI (PyQt6)
- Splash screen on startup
- Menu bar with File, View, and Help menus
- About dialog and Keyboard Shortcuts dialog
- Self-contained installers — no Python required for end users:
  - Windows: NSIS setup installer (Start Menu + Desktop shortcuts, Add/Remove Programs entry)
  - Fedora: RPM package
  - Ubuntu / Debian: DEB package
  - macOS: standalone app bundle
- GitHub Actions CI for all four platform builds triggered on version tags
- `install_and_run.py` dev launcher with automatic virtual environment creation

---

*Author: Lowil Ray Delos Reyes*
