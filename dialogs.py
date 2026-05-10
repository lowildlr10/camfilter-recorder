from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDialogButtonBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from constants import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_YEAR, APP_DESC, SHORTCUTS,
)


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

        self._separator(layout)

        desc = QLabel(APP_DESC)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc.setStyleSheet("font-size:12px; color:#ccccdd;")
        layout.addWidget(desc)

        self._separator(layout)

        for line in [
            f"Author:   {APP_AUTHOR}",
            "License:  MIT",
            f"Year:     {APP_YEAR}",
            "Stack:    Python · OpenCV · PyQt6",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet(
                "font-size:11px; color:#aaaacc; font-family: monospace;"
            )
            layout.addWidget(lbl)

        layout.addWidget(self._ok_buttons())

    def _separator(self, layout: QVBoxLayout):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#2e2e4a;")
        layout.addWidget(sep)

    def _ok_buttons(self) -> QDialogButtonBox:
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        btns.setStyleSheet(
            "QPushButton { background:#252540; border:1px solid #3a3a5c;"
            " border-radius:4px; padding:5px 18px; color:#e0e0e0; }"
            "QPushButton:hover { background:#2e2e55; }"
        )
        return btns


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(360, 280)
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
