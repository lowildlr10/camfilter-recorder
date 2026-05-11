APP_NAME    = "CamFilter Recorder"
APP_VERSION = "1.3.0"
APP_AUTHOR  = "Lowil Ray Delos Reyes"
APP_YEAR    = "2026"
APP_DESC    = (
    "A cross-platform desktop application for recording webcam "
    "or camera input with real-time filters including Night Vision, "
    "Infrared/Thermal, Cartoon, Pencil Sketch, and more.\n\n"
    "Built with Python, OpenCV, and PyQt6."
)

RESOLUTIONS: dict[str, tuple[int, int]] = {
    "1080p (1920x1080)": (1920, 1080),
    "720p  (1280x720)":  (1280, 720),
    "480p  (854x480)":   (854,  480),
    "360p  (640x360)":   (640,  360),
    "240p  (426x240)":   (426,  240),
}

FALLBACK_FPS      = 25.0
FPS_SAMPLE_WINDOW = 60

# ── Video formats ─────────────────────────────────────────────────────────────
# Each entry maps a user-facing name to an ordered list of (fourcc, extension)
# codec candidates.  The first one that opens successfully will be used.
VIDEO_FORMATS: dict[str, list[tuple[str, str]]] = {
    "AVI": [("XVID", ".avi"), ("MJPG", ".avi")],
    "MP4": [("mp4v", ".mp4"), ("avc1", ".mp4"), ("X264", ".mp4")],
}

# ── Image (snapshot) formats ──────────────────────────────────────────────────
# Maps user-facing name to the file extension used by cv2.imwrite().
IMAGE_FORMATS: dict[str, str] = {
    "PNG":  ".png",
    "JPG":  ".jpg",
    "BMP":  ".bmp",
    "TIFF": ".tiff",
}

SHORTCUTS: list[tuple[str, str]] = [
    ("Ctrl+R", "Start / Stop Recording"),
    ("Ctrl+S", "Take Snapshot"),
    ("Ctrl+,", "Open Settings"),
    ("Ctrl+O", "Open Output Folder"),
    ("Ctrl+T", "Toggle Always on Top"),
    ("F11",    "Toggle Fullscreen Preview"),
    ("Ctrl+Q", "Quit"),
]
