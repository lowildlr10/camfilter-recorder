from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QDialogButtonBox, QGroupBox, QComboBox, QPushButton, QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from constants import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_YEAR, APP_DESC,
    SHORTCUTS, VIDEO_FORMATS, IMAGE_FORMATS,
)
from settings import AppSettings


# ── About ─────────────────────────────────────────────────────────────────────

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(420, 320)
        self.setStyleSheet("background:#1a1a2e; color:#e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)

        logo = QLabel(APP_NAME)
        logo.setFont(QFont("", 20, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color:#00d4aa;")
        layout.addWidget(logo)

        ver = QLabel(f"Version {APP_VERSION}")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color:#888; font-size:12px;")
        layout.addWidget(ver)

        self._sep(layout)

        desc = QLabel(APP_DESC)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc.setStyleSheet("font-size:12px; color:#ccccdd;")
        layout.addWidget(desc)

        self._sep(layout)

        for line in [
            f"Author:   {APP_AUTHOR}",
            "License:  MIT",
            f"Year:     {APP_YEAR}",
            "Stack:    Python · OpenCV · PyQt6",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet("font-size:11px; color:#aaaacc; font-family:monospace;")
            layout.addWidget(lbl)

        layout.addWidget(self._ok_box())

    def _sep(self, layout):
        s = QFrame()
        s.setFrameShape(QFrame.Shape.HLine)
        s.setStyleSheet("color:#2e2e4a;")
        layout.addWidget(s)

    def _ok_box(self):
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        btns.setStyleSheet(
            "QPushButton { background:#252540; border:1px solid #3a3a5c;"
            " border-radius:4px; padding:5px 18px; color:#e0e0e0; }"
            "QPushButton:hover { background:#2e2e55; }"
        )
        return btns


# ── Keyboard Shortcuts ────────────────────────────────────────────────────────

class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(360, 310)
        self.setStyleSheet("background:#1a1a2e; color:#e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title = QLabel("Keyboard Shortcuts")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setStyleSheet("color:#00d4aa;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#2e2e4a;")
        layout.addWidget(sep)

        for key, desc in SHORTCUTS:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setFixedWidth(90)
            k.setStyleSheet(
                "background:#252540; border:1px solid #3a3a5c; border-radius:3px;"
                " padding:2px 6px; font-family:monospace; color:#00d4aa; font-size:11px;"
            )
            d = QLabel(desc)
            d.setStyleSheet("font-size:12px; color:#ccccdd;")
            row.addWidget(k)
            row.addWidget(d)
            layout.addLayout(row)

        layout.addStretch()

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        btns.setStyleSheet(
            "QPushButton { background:#252540; border:1px solid #3a3a5c;"
            " border-radius:4px; padding:5px 18px; color:#e0e0e0; }"
            "QPushButton:hover { background:#2e2e55; }"
        )
        layout.addWidget(btns)


# ── Settings ──────────────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    """
    User-configurable settings:
      Recording — video format (AVI / MP4) and output folder
      Snapshot  — image format (PNG / JPG / BMP / TIFF) and output folder
    """

    _DIALOG_STYLE = """
        QDialog, QWidget  { background:#1a1a2e; color:#e0e0e0; }
        QGroupBox {
            font-weight:bold; color:#00d4aa;
            border:1px solid #2e2e4a; border-radius:6px;
            margin-top:8px; padding-top:6px;
        }
        QGroupBox::title { subcontrol-origin:margin; left:10px; top:2px; }
        QLabel  { color:#ccccdd; font-size:12px; }
        QComboBox {
            background:#252540; border:1px solid #3a3a5c;
            border-radius:4px; padding:4px 8px; color:#e0e0e0; font-size:12px;
        }
        QComboBox::drop-down { border:none; }
        QComboBox QAbstractItemView {
            background:#252540; color:#e0e0e0;
            selection-background-color:#00d4aa; selection-color:#000;
        }
        QPushButton {
            background:#252540; border:1px solid #3a3a5c;
            border-radius:4px; padding:5px 14px; color:#e0e0e0; font-size:12px;
        }
        QPushButton:hover { background:#2e2e55; }
    """

    def __init__(self, current: AppSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedWidth(460)
        self.setStyleSheet(self._DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        # Title
        title = QLabel("⚙  Settings")
        title.setFont(QFont("", 15, QFont.Weight.Bold))
        title.setStyleSheet("color:#00d4aa;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#2e2e4a;")
        layout.addWidget(sep)

        # ── Recording section ─────────────────────────────────────────────────
        rec_group = QGroupBox("Recording")
        rec_layout = QVBoxLayout(rec_group)
        rec_layout.setSpacing(8)
        rec_layout.setContentsMargins(12, 10, 12, 12)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Video Format"))
        self._vid_fmt = QComboBox()
        self._vid_fmt.addItems(list(VIDEO_FORMATS.keys()))
        idx = self._vid_fmt.findText(current.video_format)
        if idx >= 0:
            self._vid_fmt.setCurrentIndex(idx)
        self._vid_fmt.setFixedWidth(100)
        fmt_row.addStretch()
        fmt_row.addWidget(self._vid_fmt)
        rec_layout.addLayout(fmt_row)

        rec_layout.addWidget(self._folder_label("Output Folder"))
        self._vid_dir = self._path_label(current.video_output_dir)
        rec_layout.addWidget(self._vid_dir)
        vid_browse = QPushButton("Browse…")
        vid_browse.clicked.connect(lambda: self._browse(self._vid_dir))
        rec_layout.addWidget(vid_browse)

        layout.addWidget(rec_group)

        # ── Snapshot section ──────────────────────────────────────────────────
        snap_group = QGroupBox("Snapshot")
        snap_layout = QVBoxLayout(snap_group)
        snap_layout.setSpacing(8)
        snap_layout.setContentsMargins(12, 10, 12, 12)

        img_row = QHBoxLayout()
        img_row.addWidget(QLabel("Image Format"))
        self._img_fmt = QComboBox()
        self._img_fmt.addItems(list(IMAGE_FORMATS.keys()))
        idx = self._img_fmt.findText(current.image_format)
        if idx >= 0:
            self._img_fmt.setCurrentIndex(idx)
        self._img_fmt.setFixedWidth(100)
        img_row.addStretch()
        img_row.addWidget(self._img_fmt)
        snap_layout.addLayout(img_row)

        snap_layout.addWidget(self._folder_label("Output Folder"))
        self._img_dir = self._path_label(current.image_output_dir)
        snap_layout.addWidget(self._img_dir)
        img_browse = QPushButton("Browse…")
        img_browse.clicked.connect(lambda: self._browse(self._img_dir))
        snap_layout.addWidget(img_browse)

        layout.addWidget(snap_group)

        # ── Buttons ───────────────────────────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color:#2e2e4a;")
        layout.addWidget(sep2)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet(
            "QPushButton { background:#252540; border:1px solid #3a3a5c;"
            " border-radius:4px; padding:5px 18px; color:#e0e0e0; }"
            "QPushButton:hover { background:#2e2e55; }"
            "QPushButton[text='Save'] { background:#00695c; border-color:#00897b; }"
            "QPushButton[text='Save']:hover { background:#00796b; }"
        )
        layout.addWidget(btns)

        self.adjustSize()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _folder_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#888; font-size:11px; margin-top:4px;")
        return lbl

    def _path_label(self, path: str) -> QLabel:
        lbl = QLabel(path or "(not set)")
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            "background:#0d0d1f; border:1px solid #2e2e4a; border-radius:4px;"
            " padding:4px 8px; color:#aaa; font-size:11px;"
        )
        return lbl

    def _browse(self, label: QLabel):
        current = label.text() if label.text() != "(not set)" else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", current)
        if folder:
            label.setText(folder)

    # ── Result ────────────────────────────────────────────────────────────────

    def get_settings(self, base: AppSettings) -> AppSettings:
        """Return a new AppSettings populated from the dialog's current values."""
        vid_dir = self._vid_dir.text()
        img_dir = self._img_dir.text()
        return AppSettings(
            video_format     = self._vid_fmt.currentText(),
            video_output_dir = vid_dir if vid_dir != "(not set)" else base.video_output_dir,
            image_format     = self._img_fmt.currentText(),
            image_output_dir = img_dir if img_dir != "(not set)" else base.image_output_dir,
        )
