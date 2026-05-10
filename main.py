"""
main.py — Application entry point.

Responsibilities:
  - Create the QApplication instance.
  - Display the splash screen while the main window initialises.
  - Hand off to MainWindow and start the event loop.
"""

import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QPainter, QPixmap, QColor, QFont,
    QLinearGradient, QRadialGradient, QPen,
)

from constants import APP_NAME, APP_VERSION, APP_AUTHOR
from window import MainWindow


def _build_splash(w: int = 520, h: int = 300) -> QPixmap:
    pix = QPixmap(w, h)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    grad = QLinearGradient(0, 0, 0, h)
    grad.setColorAt(0.0, QColor("#1a1a2e"))
    grad.setColorAt(1.0, QColor("#0f0f1a"))
    p.fillRect(0, 0, w, h, grad)

    glow = QRadialGradient(w / 2, h / 2, h * 0.6)
    glow.setColorAt(0.0, QColor(0, 212, 170, 30))
    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.fillRect(0, 0, w, h, glow)

    p.setPen(QPen(QColor("#00d4aa"), 1.5))
    p.drawRect(1, 1, w - 2, h - 2)

    p.setPen(QColor("#00d4aa"))
    p.setFont(QFont("", 36, QFont.Weight.Bold))
    p.drawText(0, 40, w, 60, Qt.AlignmentFlag.AlignCenter, "CamFilter")

    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("", 22))
    p.drawText(0, 95, w, 40, Qt.AlignmentFlag.AlignCenter, "Recorder")

    p.setPen(QColor("#555577"))
    p.drawLine(w // 2 - 80, 148, w // 2 + 80, 148)

    p.setPen(QColor("#aaaacc"))
    p.setFont(QFont("", 11))
    p.drawText(0, 158, w, 28, Qt.AlignmentFlag.AlignCenter, f"Version {APP_VERSION}")
    p.drawText(0, 182, w, 28, Qt.AlignmentFlag.AlignCenter, f"by {APP_AUTHOR}")

    p.setPen(QColor("#444466"))
    p.setFont(QFont("", 9))
    p.drawText(0, 240, w, 24, Qt.AlignmentFlag.AlignCenter,
               "Powered by Python  •  OpenCV  •  PyQt6")

    p.setPen(QColor("#00d4aa"))
    p.setFont(QFont("", 10))
    p.drawText(0, 268, w, 24, Qt.AlignmentFlag.AlignCenter, "Starting, please wait…")

    p.end()
    return pix


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_AUTHOR)

    splash = QSplashScreen(_build_splash(), Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    win = MainWindow()
    QTimer.singleShot(1800, lambda: (splash.finish(win), win.show()))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
