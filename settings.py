"""
settings.py — App settings model and QSettings persistence.

AppSettings is the single source of truth for user-configurable preferences.
Call load_settings() on startup and save_settings() when the user clicks Save
in SettingsDialog.  Values are persisted across launches via QSettings (stored
in the OS-native location: registry on Windows, plist on macOS, INI on Linux).
"""

from __future__ import annotations
from dataclasses import dataclass
from PyQt6.QtCore import QSettings
from constants import APP_NAME, APP_AUTHOR

_ORG = APP_AUTHOR
_APP = APP_NAME


@dataclass
class AppSettings:
    video_format:     str = "AVI"
    video_output_dir: str = ""    # empty → window fills in the default dir
    image_format:     str = "PNG"
    image_output_dir: str = ""    # empty → window fills in the default dir


def load_settings() -> AppSettings:
    """Load settings from persistent storage, returning defaults for missing keys."""
    qs = QSettings(_ORG, _APP)
    return AppSettings(
        video_format     = str(qs.value("recording/video_format",     "AVI")),
        video_output_dir = str(qs.value("recording/video_output_dir", "")),
        image_format     = str(qs.value("snapshot/image_format",      "PNG")),
        image_output_dir = str(qs.value("snapshot/image_output_dir",  "")),
    )


def save_settings(s: AppSettings) -> None:
    """Persist settings to the OS-native storage."""
    qs = QSettings(_ORG, _APP)
    qs.setValue("recording/video_format",     s.video_format)
    qs.setValue("recording/video_output_dir", s.video_output_dir)
    qs.setValue("snapshot/image_format",      s.image_format)
    qs.setValue("snapshot/image_output_dir",  s.image_output_dir)
