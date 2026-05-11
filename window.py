"""
window.py — Presentation layer (UI only).

The sidebar exposes only the live-session controls (Camera, Filter,
Resolution, Brightness, Contrast) and action buttons (Record, Snapshot).
All file/format preferences live in SettingsDialog.
"""

import sys
import os
import cv2
import numpy as np

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QStatusBar,
    QGroupBox, QSlider, QFrame, QSizePolicy, QMessageBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont, QAction

from constants import APP_NAME, APP_VERSION, APP_AUTHOR, RESOLUTIONS
from filters import FILTER_NAMES
from controller import CameraThread, RecordingController
from dialogs import AboutDialog, ShortcutsDialog, SettingsDialog
from settings import AppSettings, load_settings, save_settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(980, 600)

        self._camera_thread: CameraThread | None = None
        self._last_filtered: np.ndarray | None = None

        # Load persisted settings; fill empty dirs with the OS default
        self._settings = load_settings()
        default_dir = self._default_output_dir()
        if not self._settings.video_output_dir:
            self._settings.video_output_dir = default_dir
        if not self._settings.image_output_dir:
            self._settings.image_output_dir = default_dir

        self._controller = RecordingController(self)
        self._connect_controller_signals()

        self._build_menu()
        self._build_ui()
        self._apply_dark_theme()
        self._start_camera()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _default_output_dir(self) -> str:
        for candidate in [
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/Movies"),
            os.path.expanduser("~"),
        ]:
            try:
                os.makedirs(candidate, exist_ok=True)
                test = os.path.join(candidate, ".write_test")
                open(test, "w").close()
                os.remove(test)
                return candidate
            except OSError:
                continue
        return os.path.expanduser("~")

    # ── Controller signals ────────────────────────────────────────────────────

    def _connect_controller_signals(self):
        c = self._controller
        c.recording_started.connect(self._on_recording_started)
        c.recording_stopped.connect(self._on_recording_stopped)
        c.recording_error.connect(self._on_recording_error)
        c.snapshot_saved.connect(self._on_snapshot_saved)
        c.snapshot_error.connect(self._on_snapshot_error)

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("&File")
        self._add_action(file_menu, "&Open Output Folder", "Ctrl+O", self._open_output_folder)
        file_menu.addSeparator()
        self._add_action(file_menu, "&Start / Stop Recording", "Ctrl+R", self._toggle_recording)
        self._add_action(file_menu, "&Take Snapshot",          "Ctrl+S", self._take_snapshot)
        file_menu.addSeparator()
        self._add_action(file_menu, "S&ettings…", "Ctrl+,", self._open_settings)
        file_menu.addSeparator()
        self._add_action(file_menu, "&Quit", "Ctrl+Q", self.close)

        view_menu = mb.addMenu("&View")
        self._act_on_top = QAction("Always on &Top", self, checkable=True)
        self._act_on_top.setShortcut("Ctrl+T")
        self._act_on_top.toggled.connect(self._toggle_on_top)
        view_menu.addAction(self._act_on_top)
        view_menu.addSeparator()
        self._add_action(view_menu, "&Fullscreen Preview", "F11", self._toggle_fullscreen)

        help_menu = mb.addMenu("&Help")
        self._add_action(help_menu, "&Keyboard Shortcuts", "", self._show_shortcuts)
        help_menu.addSeparator()
        self._add_action(help_menu, f"&About {APP_NAME}", "", self._show_about)

    def _add_action(self, menu, label: str, shortcut: str, slot):
        act = QAction(label, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(slot)
        menu.addAction(act)
        return act

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ── Preview ───────────────────────────────────────────────────────────
        self._preview = QLabel("Starting camera…")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._preview.setStyleSheet(
            "background:#111; border-radius:8px; color:#666; font-size:14px;"
        )
        root.addWidget(self._preview, stretch=1)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = QVBoxLayout()
        sidebar.setSpacing(8)
        sidebar.setContentsMargins(0, 0, 0, 0)
        root.addLayout(sidebar)

        # Title (always visible)
        self._add_title(sidebar)

        # Scrollable live-session controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        controls = QWidget()
        ctrl_layout = QVBoxLayout(controls)
        ctrl_layout.setSpacing(10)
        ctrl_layout.setContentsMargins(0, 0, 4, 0)

        self._cam_combo    = self._add_combo_group(ctrl_layout, "Camera", [])
        self._filter_combo = self._add_combo_group(ctrl_layout, "Filter", FILTER_NAMES)
        self._res_combo    = self._add_combo_group(ctrl_layout, "Resolution", list(RESOLUTIONS.keys()))
        self._brightness   = self._add_slider(ctrl_layout, "Brightness", -80, 80, 0)
        self._contrast     = self._add_slider(ctrl_layout, "Contrast",   10, 250, 100)
        ctrl_layout.addStretch()

        scroll.setWidget(controls)
        sidebar.addWidget(scroll, stretch=1)

        # Settings button (below scroll, above separator)
        settings_btn = QPushButton("⚙  Settings")
        settings_btn.setFixedHeight(30)
        settings_btn.setStyleSheet(self._STYLE_SETTINGS)
        settings_btn.clicked.connect(self._open_settings)
        sidebar.addWidget(settings_btn)

        sidebar.addWidget(self._make_separator())

        # Record button
        self._record_btn = self._make_record_button()
        sidebar.addWidget(self._record_btn)

        # Snapshot button
        self._snap_btn = self._make_snapshot_button()
        sidebar.addWidget(self._snap_btn)

        self._snap_flash = QLabel("")
        self._snap_flash.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._snap_flash.setStyleSheet("color:#1976d2; font-size:11px;")
        sidebar.addWidget(self._snap_flash)

        self._rec_indicator = QLabel("")
        self._rec_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rec_indicator.setStyleSheet(
            "color:#e53935; font-size:13px; font-weight:bold; letter-spacing:1px;"
        )
        sidebar.addWidget(self._rec_indicator)

        self._timer_label = QLabel("")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer_label.setFont(QFont("Courier", 22, QFont.Weight.Bold))
        self._timer_label.setStyleSheet("color:#00d4aa; letter-spacing:2px;")
        sidebar.addWidget(self._timer_label)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

        # Timers
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(600)
        self._blink_timer.timeout.connect(self._blink_rec)
        self._blink_state = False

        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._elapsed_secs = 0

        self._snap_clear_timer = QTimer(self)
        self._snap_clear_timer.setSingleShot(True)
        self._snap_clear_timer.setInterval(2500)
        self._snap_clear_timer.timeout.connect(lambda: self._snap_flash.setText(""))

        # Wire controls
        self._populate_cameras()
        self._cam_combo.currentIndexChanged.connect(self._on_camera_changed)
        self._filter_combo.currentTextChanged.connect(self._sync_filter)
        self._brightness.valueChanged.connect(self._sync_brightness)
        self._contrast.valueChanged.connect(self._sync_contrast)

    # ── Widget factories ──────────────────────────────────────────────────────

    def _add_title(self, layout: QVBoxLayout):
        title = QLabel(APP_NAME)
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#00d4aa; margin-bottom:2px;")
        layout.addWidget(title)
        sub = QLabel(f"v{APP_VERSION}  •  {APP_AUTHOR}")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#555577; font-size:10px;")
        layout.addWidget(sub)

    def _add_combo_group(self, layout: QVBoxLayout, label: str, items: list) -> QComboBox:
        group = QGroupBox(label)
        g = QVBoxLayout(group)
        g.setContentsMargins(6, 4, 6, 6)
        combo = QComboBox()
        if items:
            combo.addItems(items)
        g.addWidget(combo)
        layout.addWidget(group)
        return combo

    def _add_slider(
        self, layout: QVBoxLayout, label: str,
        minimum: int, maximum: int, default: int,
    ) -> QSlider:
        group = QGroupBox(label)
        g = QVBoxLayout(group)
        g.setContentsMargins(6, 4, 6, 6)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(default)
        slider.setTickInterval((maximum - minimum) // 5)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        g.addWidget(slider)
        layout.addWidget(group)
        return slider

    def _make_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#333;")
        return line

    def _make_record_button(self) -> QPushButton:
        btn = QPushButton("⏺  Start Recording")
        btn.setFixedHeight(48)
        btn.setFont(QFont("", 13, QFont.Weight.Bold))
        btn.setStyleSheet(self._STYLE_RECORD_IDLE)
        btn.clicked.connect(self._toggle_recording)
        return btn

    def _make_snapshot_button(self) -> QPushButton:
        btn = QPushButton("📷  Take Snapshot")
        btn.setFixedHeight(36)
        btn.setFont(QFont("", 11))
        btn.setStyleSheet(self._STYLE_SNAPSHOT)
        btn.clicked.connect(self._take_snapshot)
        return btn

    _STYLE_RECORD_IDLE = (
        "QPushButton { background:#e53935; border-radius:8px; color:white; }"
        "QPushButton:hover { background:#ef5350; }"
        "QPushButton:pressed { background:#c62828; }"
    )
    _STYLE_RECORD_ACTIVE = (
        "QPushButton { background:#37474f; border-radius:8px; color:white; }"
        "QPushButton:hover { background:#455a64; }"
    )
    _STYLE_SNAPSHOT = (
        "QPushButton { background:#1565c0; border-radius:6px; color:white; }"
        "QPushButton:hover { background:#1976d2; }"
        "QPushButton:pressed { background:#0d47a1; }"
        "QPushButton:disabled { background:#252540; color:#555; }"
    )
    _STYLE_SETTINGS = (
        "QPushButton { background:#252540; border:1px solid #3a3a5c;"
        " border-radius:5px; color:#aaa; font-size:11px; }"
        "QPushButton:hover { background:#2e2e55; color:#e0e0e0; }"
        "QPushButton:pressed { background:#1a1a3a; }"
    )

    # ── Dark theme ────────────────────────────────────────────────────────────

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#1a1a2e; color:#e0e0e0; }
            QMenuBar { background:#141428; color:#e0e0e0; padding:2px; }
            QMenuBar::item:selected { background:#252540; border-radius:4px; }
            QMenu { background:#1e1e36; color:#e0e0e0; border:1px solid #3a3a5c; }
            QMenu::item:selected { background:#00d4aa; color:#000; }
            QMenu::separator { height:1px; background:#3a3a5c; margin:4px 8px; }
            QGroupBox {
                font-weight:bold; color:#00d4aa;
                border:1px solid #2e2e4a; border-radius:6px;
                margin-top:6px; padding-top:4px;
            }
            QGroupBox::title { subcontrol-origin:margin; left:8px; top:2px; }
            QScrollArea { background:transparent; border:none; }
            QScrollBar:vertical {
                background:#141428; width:6px; border-radius:3px;
            }
            QScrollBar::handle:vertical {
                background:#3a3a5c; border-radius:3px; min-height:20px;
            }
            QScrollBar::handle:vertical:hover { background:#00d4aa; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
            QComboBox {
                background:#252540; border:1px solid #3a3a5c;
                border-radius:4px; padding:4px 8px; color:#e0e0e0;
            }
            QComboBox::drop-down { border:none; }
            QComboBox QAbstractItemView {
                background:#252540; color:#e0e0e0;
                selection-background-color:#00d4aa; selection-color:#000;
            }
            QPushButton {
                background:#252540; border:1px solid #3a3a5c;
                border-radius:4px; padding:6px 10px; color:#e0e0e0;
            }
            QPushButton:hover { background:#2e2e55; }
            QSlider::groove:horizontal { height:4px; background:#3a3a5c; border-radius:2px; }
            QSlider::handle:horizontal {
                background:#00d4aa; width:14px; height:14px;
                margin:-5px 0; border-radius:7px;
            }
            QSlider::sub-page:horizontal { background:#00d4aa; border-radius:2px; }
            QStatusBar { color:#888; font-size:11px; }
            QMessageBox { background:#1a1a2e; color:#e0e0e0; }
        """)

    # ── Camera ────────────────────────────────────────────────────────────────

    def _populate_cameras(self):
        self._cam_combo.clear()
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self._cam_combo.addItem(f"Camera {i}", i)
                cap.release()
        if self._cam_combo.count() == 0:
            self._cam_combo.addItem("No camera found", 0)

    def _start_camera(self, index: int = 0):
        if self._camera_thread:
            self._camera_thread.stop()
        self._controller.reset_frame_times()

        self._camera_thread = CameraThread(index, self)
        self._camera_thread.filter_name = self._filter_combo.currentText()
        self._camera_thread.brightness  = self._brightness.value()
        self._camera_thread.contrast    = self._contrast.value() / 100.0

        self._camera_thread.frame_ready.connect(self._on_frame)
        self._camera_thread.start()
        self._status.showMessage(f"Camera {index} started")

    def _on_camera_changed(self):
        if self._controller.is_recording:
            return
        idx = self._cam_combo.currentData()
        if idx is not None:
            self._start_camera(idx)

    # ── Sync UI → camera thread ───────────────────────────────────────────────

    def _sync_filter(self, name: str):
        if self._camera_thread:
            self._camera_thread.filter_name = name

    def _sync_brightness(self, value: int):
        if self._camera_thread:
            self._camera_thread.brightness = value

    def _sync_contrast(self, value: int):
        if self._camera_thread:
            self._camera_thread.contrast = value / 100.0

    # ── Frame processing ──────────────────────────────────────────────────────

    def _on_frame(self, filtered: np.ndarray):
        self._controller.record_frame_time()
        self._last_filtered = filtered

        if self._controller.is_recording:
            self._controller.write_frame(filtered, self._res_combo.currentText())

        self._render_frame(filtered)

    def _render_frame(self, frame: np.ndarray):
        rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self._preview.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self._preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    # ── Recording ─────────────────────────────────────────────────────────────

    def _toggle_recording(self):
        if self._controller.is_recording:
            self._controller.stop_recording()
        else:
            self._controller.start_recording(
                output_dir=self._settings.video_output_dir,
                resolution_key=self._res_combo.currentText(),
                filter_tag=self._filter_combo.currentText(),
                video_format=self._settings.video_format,
            )

    def _on_recording_started(self, path: str, fps: float):
        self._elapsed_secs = 0
        self._record_btn.setText("⏹  Stop Recording")
        self._record_btn.setStyleSheet(self._STYLE_RECORD_ACTIVE)
        self._filter_combo.setEnabled(False)
        self._res_combo.setEnabled(False)
        self._cam_combo.setEnabled(False)
        self._blink_timer.start()
        self._clock_timer.start()
        self._timer_label.setText("00:00:00")
        fmt = self._settings.video_format
        self._status.showMessage(f"Recording {fmt} at {fps} FPS → {path}")

    def _on_recording_stopped(self, path: str):
        self._record_btn.setText("⏺  Start Recording")
        self._record_btn.setStyleSheet(self._STYLE_RECORD_IDLE)
        self._filter_combo.setEnabled(True)
        self._res_combo.setEnabled(True)
        self._cam_combo.setEnabled(True)
        self._blink_timer.stop()
        self._clock_timer.stop()
        self._rec_indicator.setText("")
        self._timer_label.setText("")

        if path and os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self._status.showMessage(f"Saved: {path}  ({size_mb:.1f} MB)")
            QMessageBox.information(
                self, "Recording Saved",
                f"File saved:\n{path}\n\nSize: {size_mb:.1f} MB",
            )
        else:
            QMessageBox.warning(
                self, "Recording Warning",
                f"File not found at:\n{path}\n\nCheck folder permissions.",
            )

    def _on_recording_error(self, message: str):
        QMessageBox.critical(self, "Recording Error", message)

    # ── Snapshot ──────────────────────────────────────────────────────────────

    def _take_snapshot(self):
        if self._last_filtered is None:
            self._status.showMessage("No frame available yet.")
            return
        self._controller.take_snapshot(
            frame=self._last_filtered,
            output_dir=self._settings.image_output_dir,
            filter_name=self._filter_combo.currentText(),
            image_format=self._settings.image_format,
        )

    def _on_snapshot_saved(self, path: str):
        filename = os.path.basename(path)
        fmt = self._settings.image_format
        self._snap_flash.setText(f"Saved {fmt}: {filename}")
        self._status.showMessage(f"Snapshot → {path}")
        self._snap_clear_timer.start()

    def _on_snapshot_error(self, message: str):
        QMessageBox.warning(self, "Snapshot Error", f"Could not save snapshot:\n{message}")

    # ── Settings dialog ───────────────────────────────────────────────────────

    def _open_settings(self):
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec():
            self._settings = dlg.get_settings(self._settings)
            save_settings(self._settings)
            self._status.showMessage(
                f"Settings saved — Video: {self._settings.video_format}  "
                f"Image: {self._settings.image_format}"
            )

    # ── Timer callbacks ───────────────────────────────────────────────────────

    def _blink_rec(self):
        self._blink_state = not self._blink_state
        self._rec_indicator.setText("● REC" if self._blink_state else "")

    def _tick_clock(self):
        self._elapsed_secs += 1
        h = self._elapsed_secs // 3600
        m = (self._elapsed_secs % 3600) // 60
        s = self._elapsed_secs % 60
        self._timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    # ── Menu handlers ─────────────────────────────────────────────────────────

    def _open_output_folder(self):
        path = self._settings.video_output_dir
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def _toggle_on_top(self, checked: bool):
        flags = self.windowFlags()
        flag  = Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags | flag if checked else flags & ~flag)
        self.show()

    def _toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def _show_shortcuts(self):
        ShortcutsDialog(self).exec()

    def _show_about(self):
        AboutDialog(self).exec()

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._controller.is_recording:
            self._controller.stop_recording()
        if self._camera_thread:
            self._camera_thread.stop()
        event.accept()
