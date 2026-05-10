"""
controller.py — Business logic layer (no UI code).

Responsibilities:
  - CameraThread   : reads raw frames from OpenCV in a background thread.
  - RecordingController : manages VideoWriter lifecycle, FPS measurement,
                          snapshot saving, and recording state.  Communicates
                          with the UI exclusively through Qt signals.
"""

import os
import time
import cv2
import numpy as np
from collections import deque
from datetime import datetime

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from constants import (
    RESOLUTIONS, FALLBACK_FPS, FPS_SAMPLE_WINDOW, CODEC_CANDIDATES,
)


# ── Camera thread ─────────────────────────────────────────────────────────────

class CameraThread(QThread):
    """Reads frames from a camera device and emits them via a Qt signal."""

    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._running = False

    def run(self):
        self._running = True
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        while self._running:
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()


# ── Recording controller ──────────────────────────────────────────────────────

class RecordingController(QObject):
    """
    Manages the full recording lifecycle.

    Signals emitted (observed by the UI):
      recording_started(path, fps)  — recording opened successfully
      recording_stopped(path)       — recording finalized; path is the saved file
      recording_error(message)      — codec/IO failure
      snapshot_saved(path)          — snapshot PNG written
      snapshot_error(message)       — snapshot write failure
    """

    recording_started = pyqtSignal(str, float)
    recording_stopped = pyqtSignal(str)
    recording_error   = pyqtSignal(str)
    snapshot_saved    = pyqtSignal(str)
    snapshot_error    = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._writer: cv2.VideoWriter | None = None
        self._saved_path: str = ""
        self.is_recording: bool = False
        self._frame_times: deque[float] = deque(maxlen=FPS_SAMPLE_WINDOW)

    # ── FPS measurement ───────────────────────────────────────────────────────

    def record_frame_time(self):
        """Call once per incoming camera frame to track the real FPS."""
        self._frame_times.append(time.monotonic())

    def reset_frame_times(self):
        self._frame_times.clear()

    @property
    def measured_fps(self) -> float:
        if len(self._frame_times) < 2:
            return FALLBACK_FPS
        elapsed = self._frame_times[-1] - self._frame_times[0]
        if elapsed <= 0:
            return FALLBACK_FPS
        return max(5.0, min(60.0, (len(self._frame_times) - 1) / elapsed))

    # ── Recording ─────────────────────────────────────────────────────────────

    def start_recording(self, output_dir: str, resolution_key: str, filter_tag: str):
        """
        Open a VideoWriter using the best available codec and emit
        ``recording_started`` or ``recording_error``.
        """
        w, h = RESOLUTIONS[resolution_key]
        fps = round(self.measured_fps, 2)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_tag = filter_tag.replace(" ", "_").replace("/", "-")
        res_tag = resolution_key[:5].strip()
        base = os.path.join(output_dir, f"recording_{timestamp}_{safe_tag}_{res_tag}")

        writer, path = self._open_writer(base, w, h, fps)
        if writer is None:
            self.recording_error.emit(
                "Could not open any video codec on this system.\n\n"
                "Try installing ffmpeg:\n"
                "  Fedora: sudo dnf install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg"
            )
            return

        self._writer = writer
        self._saved_path = path
        self.is_recording = True
        self.recording_started.emit(path, fps)

    def write_frame(self, frame: np.ndarray, resolution_key: str):
        """Write a single filtered frame to the open VideoWriter."""
        if not self.is_recording or self._writer is None:
            return
        if not self._writer.isOpened():
            return
        w, h = RESOLUTIONS[resolution_key]
        self._writer.write(cv2.resize(frame, (w, h)))

    def stop_recording(self):
        """Finalize and close the VideoWriter, then emit ``recording_stopped``."""
        self.is_recording = False
        if self._writer:
            self._writer.release()
            self._writer = None
        self.recording_stopped.emit(self._saved_path)

    # ── Snapshot ──────────────────────────────────────────────────────────────

    def take_snapshot(self, frame: np.ndarray, output_dir: str, filter_name: str):
        """Save the current filtered frame as a PNG and emit the result signal."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:21]
        safe_tag = filter_name.replace(" ", "_").replace("/", "-")
        filename = f"snapshot_{timestamp}_{safe_tag}.png"
        filepath = os.path.join(output_dir, filename)
        try:
            cv2.imwrite(filepath, frame)
            self.snapshot_saved.emit(filepath)
        except Exception as exc:
            self.snapshot_error.emit(str(exc))

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _open_writer(
        base_path: str, w: int, h: int, fps: float
    ) -> tuple[cv2.VideoWriter | None, str]:
        for fourcc_str, ext in CODEC_CANDIDATES:
            path = base_path + ext
            fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
            writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
            if writer.isOpened():
                return writer, path
            writer.release()
        return None, ""
