import pytest

import settings as settings_module
from settings import AppSettings, load_settings, save_settings


@pytest.fixture(autouse=True)
def _unique_qsettings_org(monkeypatch, request):
    org = f"camfilter_test_{request.node.name}"
    monkeypatch.setattr(settings_module, "_ORG", org)


class TestAppSettings:
    def test_default_values(self):
        s = AppSettings()
        assert s.video_format == "AVI"
        assert s.video_output_dir == ""
        assert s.image_format == "PNG"
        assert s.image_output_dir == ""

    def test_custom_values(self):
        s = AppSettings(
            video_format="MP4",
            video_output_dir="/tmp/videos",
            image_format="JPG",
            image_output_dir="/tmp/snapshots",
        )
        assert s.video_format == "MP4"
        assert s.video_output_dir == "/tmp/videos"
        assert s.image_format == "JPG"
        assert s.image_output_dir == "/tmp/snapshots"

    def test_save_and_load_round_trip(self):
        save_settings(AppSettings(
            video_format="MP4",
            video_output_dir="/tmp/videos",
            image_format="JPG",
            image_output_dir="/tmp/snapshots",
        ))
        loaded = load_settings()
        assert loaded.video_format == "MP4"
        assert loaded.video_output_dir == "/tmp/videos"
        assert loaded.image_format == "JPG"
        assert loaded.image_output_dir == "/tmp/snapshots"

    def test_load_returns_defaults_when_no_settings_saved(self):
        loaded = load_settings()
        assert loaded.video_format == "AVI"
        assert loaded.video_output_dir == ""
        assert loaded.image_format == "PNG"
        assert loaded.image_output_dir == ""

    def test_save_and_load_with_empty_dirs(self):
        original = AppSettings(video_format="AVI", image_format="PNG")
        save_settings(original)
        loaded = load_settings()
        assert loaded.video_format == "AVI"
        assert loaded.image_format == "PNG"
