import sys
import os
import time
import cv2
import numpy as np
from collections import deque
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QStatusBar,
    QGroupBox, QSlider, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont

from filters import apply_filter, FILTER_NAMES

RESOLUTIONS = {
    "1080p (1920x1080)": (1920, 1080),
    "720p  (1280x720)":  (1280, 720),
    "480p  (854x480)":   (854,  480),
    "360p  (640x360)":   (640,  360),
    "240p  (426x240)":   (426,  240),
}

FALLBACK_FPS = 25.0
FPS_SAMPLE_WINDOW = 60   # number of recent frames used to compute real FPS

CODEC_CANDIDATES = [
    ("XVID", ".avi"),
    ("mp4v", ".mp4"),
    ("MJPG", ".avi"),
    ("X264", ".mp4"),
]


def _try_open_writer(filepath_no_ext: str, w: int, h: int, fps: float):
    """Try codec candidates in order and return (writer, actual_path) or (None, None)."""
    for fourcc_str, ext in CODEC_CANDIDATES:
        path = filepath_no_ext + ext
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
        if writer.isOpened():
            return writer, path
        writer.release()
    return None, None


class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self._running = False
        self.cap = None

    def run(self):
        self._running = True
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        while self._running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame)
        self.cap.release()

    def stop(self):
        self._running = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamFilter Recorder")
        self.setMinimumSize(980, 720)

        self.camera_thread: CameraThread | None = None
        self.video_writer: cv2.VideoWriter | None = None
        self.is_recording = False
        self.current_frame: np.ndarray | None = None
        self._last_saved_path: str = ""
        self._rec_elapsed_secs: int = 0
        # rolling window of frame-arrival timestamps for live FPS measurement
        self._frame_times: deque[float] = deque(maxlen=FPS_SAMPLE_WINDOW)

        self.output_path = self._default_output_dir()

        self._build_ui()
        self._apply_dark_theme()
        self._start_camera()

    def _default_output_dir(self) -> str:
        candidates = [
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/Movies"),
            os.path.expanduser("~"),
        ]
        for path in candidates:
            try:
                os.makedirs(path, exist_ok=True)
                test = os.path.join(path, ".write_test")
                with open(test, "w") as f:
                    f.write("")
                os.remove(test)
                return path
            except OSError:
                continue
        return os.path.expanduser("~")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.preview_label = QLabel("Starting camera…")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.preview_label.setStyleSheet(
            "background:#111; border-radius:8px; color:#666; font-size:14px;"
        )
        root.addWidget(self.preview_label, stretch=1)

        sidebar = QVBoxLayout()
        sidebar.setSpacing(14)
        root.addLayout(sidebar)

        title = QLabel("CamFilter\nRecorder")
        title.setFont(QFont("", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#00d4aa; margin-bottom:4px;")
        sidebar.addWidget(title)

        camera_group = QGroupBox("Camera")
        cg_layout = QVBoxLayout(camera_group)
        self.camera_combo = QComboBox()
        self._populate_cameras()
        self.camera_combo.currentIndexChanged.connect(self._change_camera)
        cg_layout.addWidget(self.camera_combo)
        sidebar.addWidget(camera_group)

        filter_group = QGroupBox("Filter")
        fg_layout = QVBoxLayout(filter_group)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(FILTER_NAMES)
        fg_layout.addWidget(self.filter_combo)
        sidebar.addWidget(filter_group)

        res_group = QGroupBox("Resolution")
        rg_layout = QVBoxLayout(res_group)
        self.res_combo = QComboBox()
        self.res_combo.addItems(list(RESOLUTIONS.keys()))
        rg_layout.addWidget(self.res_combo)
        sidebar.addWidget(res_group)

        bright_group = QGroupBox("Brightness")
        bg_layout = QVBoxLayout(bright_group)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-80, 80)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickInterval(20)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        bg_layout.addWidget(self.brightness_slider)
        sidebar.addWidget(bright_group)

        contrast_group = QGroupBox("Contrast")
        ctg_layout = QVBoxLayout(contrast_group)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(10, 250)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickInterval(40)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        ctg_layout.addWidget(self.contrast_slider)
        sidebar.addWidget(contrast_group)

        out_group = QGroupBox("Output folder")
        og_layout = QVBoxLayout(out_group)
        self.out_label = QLabel(self.output_path)
        self.out_label.setWordWrap(True)
        self.out_label.setStyleSheet("font-size:11px; color:#aaa;")
        og_layout.addWidget(self.out_label)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_output)
        og_layout.addWidget(browse_btn)
        sidebar.addWidget(out_group)

        sidebar.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#333;")
        sidebar.addWidget(line)

        self.record_btn = QPushButton("⏺  Start Recording")
        self.record_btn.setFixedHeight(48)
        self.record_btn.setFont(QFont("", 13, QFont.Weight.Bold))
        self.record_btn.setStyleSheet(
            "QPushButton { background:#e53935; border-radius:8px; color:white; }"
            "QPushButton:hover { background:#ef5350; }"
            "QPushButton:pressed { background:#c62828; }"
        )
        self.record_btn.clicked.connect(self._toggle_recording)
        sidebar.addWidget(self.record_btn)

        self.rec_indicator = QLabel("")
        self.rec_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rec_indicator.setStyleSheet("color:#e53935; font-size:13px; font-weight:bold; letter-spacing:1px;")
        sidebar.addWidget(self.rec_indicator)

        self.rec_timer_label = QLabel("")
        self.rec_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rec_timer_label.setFont(QFont("Courier", 22, QFont.Weight.Bold))
        self.rec_timer_label.setStyleSheet("color:#00d4aa; letter-spacing:2px;")
        sidebar.addWidget(self.rec_timer_label)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.blink_timer = QTimer()
        self.blink_timer.setInterval(600)
        self.blink_timer.timeout.connect(self._blink_rec)
        self._blink_state = False

        self.clock_timer = QTimer()
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self._tick_clock)

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#1a1a2e; color:#e0e0e0; }
            QGroupBox {
                font-weight:bold; color:#00d4aa;
                border:1px solid #2e2e4a; border-radius:6px;
                margin-top:6px; padding-top:4px;
            }
            QGroupBox::title { subcontrol-origin:margin; left:8px; top:2px; }
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

    def _populate_cameras(self):
        self.camera_combo.clear()
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_combo.addItem(f"Camera {i}", i)
                cap.release()
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("No camera found", 0)

    def _start_camera(self, index: int = 0):
        if self.camera_thread:
            self.camera_thread.stop()
        self.camera_thread = CameraThread(index)
        self.camera_thread.frame_ready.connect(self._on_frame)
        self.camera_thread.start()
        self.status_bar.showMessage(f"Camera {index} started")

    def _change_camera(self, _):
        if self.is_recording:
            return
        idx = self.camera_combo.currentData()
        if idx is not None:
            self._start_camera(idx)

    @property
    def _measured_fps(self) -> float:
        """Return actual camera FPS from recent frame timestamps, or FALLBACK_FPS."""
        if len(self._frame_times) < 2:
            return FALLBACK_FPS
        elapsed = self._frame_times[-1] - self._frame_times[0]
        if elapsed <= 0:
            return FALLBACK_FPS
        fps = (len(self._frame_times) - 1) / elapsed
        return max(5.0, min(60.0, fps))

    def _on_frame(self, frame: np.ndarray):
        self._frame_times.append(time.monotonic())
        self.current_frame = frame.copy()

        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)

        filter_name = self.filter_combo.currentText()
        filtered = apply_filter(frame, filter_name)

        if self.is_recording and self.video_writer and self.video_writer.isOpened():
            res_key = self.res_combo.currentText()
            w, h = RESOLUTIONS[res_key]
            out_frame = cv2.resize(filtered, (w, h))
            self.video_writer.write(out_frame)

        self._show_frame(filtered)

    def _show_frame(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _toggle_recording(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        res_key = self.res_combo.currentText()
        w, h = RESOLUTIONS[res_key]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_tag = self.filter_combo.currentText().replace(" ", "_").replace("/", "-")
        base_name = f"recording_{timestamp}_{filter_tag}_{res_key[:5].strip()}"
        filepath_no_ext = os.path.join(self.output_path, base_name)

        actual_fps = round(self._measured_fps, 2)
        writer, actual_path = _try_open_writer(filepath_no_ext, w, h, actual_fps)

        if writer is None:
            QMessageBox.critical(
                self,
                "Recording Error",
                "Could not open any video codec on this system.\n\n"
                "Try installing opencv-python and ffmpeg:\n"
                "  Fedora: sudo dnf install ffmpeg opencv\n"
                "  Ubuntu: sudo apt install ffmpeg python3-opencv",
            )
            return

        self.video_writer = writer
        self._last_saved_path = actual_path
        self._last_write_time = 0.0
        self._rec_elapsed_secs = 0
        self.is_recording = True

        self.record_btn.setText("⏹  Stop Recording")
        self.record_btn.setStyleSheet(
            "QPushButton { background:#37474f; border-radius:8px; color:white; }"
            "QPushButton:hover { background:#455a64; }"
        )
        self.filter_combo.setEnabled(False)
        self.res_combo.setEnabled(False)
        self.camera_combo.setEnabled(False)
        self.blink_timer.start()
        self.clock_timer.start()
        self.rec_timer_label.setText("00:00:00")
        self.status_bar.showMessage(f"Recording at {actual_fps} FPS → {actual_path}")

    def _stop_recording(self):
        self.is_recording = False
        saved_path = self._last_saved_path

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.record_btn.setText("⏺  Start Recording")
        self.record_btn.setStyleSheet(
            "QPushButton { background:#e53935; border-radius:8px; color:white; }"
            "QPushButton:hover { background:#ef5350; }"
            "QPushButton:pressed { background:#c62828; }"
        )
        self.filter_combo.setEnabled(True)
        self.res_combo.setEnabled(True)
        self.camera_combo.setEnabled(True)
        self.blink_timer.stop()
        self.clock_timer.stop()
        self.rec_indicator.setText("")
        self.rec_timer_label.setText("")

        if saved_path and os.path.isfile(saved_path):
            size_mb = os.path.getsize(saved_path) / (1024 * 1024)
            self.status_bar.showMessage(
                f"Saved: {saved_path}  ({size_mb:.1f} MB)"
            )
            QMessageBox.information(
                self,
                "Recording Saved",
                f"File saved successfully:\n{saved_path}\n\nSize: {size_mb:.1f} MB",
            )
        else:
            self.status_bar.showMessage("Warning: recording file not found after save.")
            QMessageBox.warning(
                self,
                "Recording Warning",
                f"Recording stopped but file was not found at:\n{saved_path}\n\n"
                "The file may have failed to write. Check folder permissions.",
            )

    def _blink_rec(self):
        self._blink_state = not self._blink_state
        self.rec_indicator.setText("● REC" if self._blink_state else "")

    def _tick_clock(self):
        self._rec_elapsed_secs += 1
        h = self._rec_elapsed_secs // 3600
        m = (self._rec_elapsed_secs % 3600) // 60
        s = self._rec_elapsed_secs % 60
        self.rec_timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_path)
        if folder:
            self.output_path = folder
            self.out_label.setText(folder)

    def closeEvent(self, event):
        if self.is_recording:
            self._stop_recording()
        if self.camera_thread:
            self.camera_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CamFilter Recorder")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
