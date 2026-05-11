import time
import pytest

from controller import RecordingController


class TestRecordingController:
    def test_not_recording_by_default(self):
        controller = RecordingController()
        assert controller.is_recording is False

    def test_measured_fps_returns_fallback_when_no_frames(self):
        controller = RecordingController()
        assert controller.measured_fps == 25.0

    def test_measured_fps_with_single_frame(self):
        controller = RecordingController()
        controller.record_frame_time()
        assert controller.measured_fps == 25.0

    def test_measured_fps_with_multiple_frames(self):
        controller = RecordingController()
        for _ in range(10):
            controller.record_frame_time()
            time.sleep(0.01)
        fps = controller.measured_fps
        assert 5.0 <= fps <= 60.0

    def test_measured_fps_clamped_low(self):
        controller = RecordingController()
        now = time.monotonic()
        for i in range(10):
            controller._frame_times.append(now + i * 10.0)
        fps = controller.measured_fps
        assert fps == 5.0

    def test_reset_frame_times_clears_deque(self):
        controller = RecordingController()
        controller.record_frame_time()
        controller.reset_frame_times()
        assert len(controller._frame_times) == 0

    def test_double_stop_recording_is_safe(self):
        controller = RecordingController()
        controller.stop_recording()
        controller.stop_recording()
