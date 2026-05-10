APP_NAME    = "CamFilter Recorder"
APP_VERSION = "1.1.0"
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

CODEC_CANDIDATES: list[tuple[str, str]] = [
    ("XVID", ".avi"),
    ("mp4v", ".mp4"),
    ("MJPG", ".avi"),
    ("X264", ".mp4"),
]

SHORTCUTS: list[tuple[str, str]] = [
    ("Ctrl+R", "Start / Stop Recording"),
    ("Ctrl+S", "Take Snapshot"),
    ("Ctrl+O", "Open Output Folder"),
    ("Ctrl+F", "Change Output Folder"),
    ("Ctrl+T", "Toggle Always on Top"),
    ("F11",    "Toggle Fullscreen Preview"),
    ("Ctrl+Q", "Quit"),
]
