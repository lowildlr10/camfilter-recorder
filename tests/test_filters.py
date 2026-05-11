import numpy as np
import pytest

from filters import apply_filter, FILTER_NAMES


class TestFilters:
    def _assert_valid_output(self, frame: np.ndarray, out: np.ndarray):
        """Check that the filter output is a valid BGR image."""
        assert isinstance(out, np.ndarray), "output must be a numpy array"
        assert out.ndim == 3, "output must be 3-dimensional (H, W, C)"
        assert out.shape[2] == 3, "output must have 3 channels (BGR)"
        assert out.shape[:2] == frame.shape[:2], "output must match input resolution"
        assert out.dtype == np.uint8, "output must be uint8"

    @pytest.mark.parametrize("name", FILTER_NAMES)
    def test_all_filters_produce_valid_output(self, test_frame, name):
        """Every filter in FILTER_NAMES must return a valid BGR image."""
        out = apply_filter(test_frame, name)
        self._assert_valid_output(test_frame, out)

    @pytest.mark.parametrize("name", FILTER_NAMES)
    def test_all_filters_handle_small_frame(self, blank_frame, name):
        """Every filter must handle the smallest frame without crashing."""
        out = apply_filter(blank_frame, name)
        self._assert_valid_output(blank_frame, out)

    @pytest.mark.parametrize("name", FILTER_NAMES)
    def test_filter_is_deterministic(self, test_frame, name):
        """Running the same filter twice on the same input should match."""
        if name in ("Night Vision",):
            pytest.skip("Night Vision adds random noise — skip determinism check")
        out1 = apply_filter(test_frame, name)
        out2 = apply_filter(test_frame, name)
        assert np.array_equal(out1, out2)

    def test_unknown_filter_falls_back_to_normal(self, test_frame):
        """An unrecognized filter name should return the frame unchanged."""
        out = apply_filter(test_frame, "NonExistentFilter")
        assert np.array_equal(out, test_frame)

    def test_normal_returns_frame_unchanged(self, test_frame):
        """The Normal filter is the identity function."""
        out = apply_filter(test_frame, "Normal")
        assert np.array_equal(out, test_frame)

    @pytest.mark.parametrize(
        ("name", "expected_change"),
        [
            ("Grayscale", True),
            ("Sepia", True),
            ("Negative", True),
            ("Edge Detection", True),
            ("Pencil Sketch", True),
            ("High Contrast", True),
        ],
    )
    def test_filter_visibly_changes_frame(self, test_frame, name, expected_change):
        """A frame of random noise should be visibly altered by non-trivial filters."""
        out = apply_filter(test_frame, name)
        diff = np.abs(out.astype(np.int16) - test_frame.astype(np.int16)).mean()
        if expected_change:
            assert diff > 1.0, f"{name} should change the image (mean diff={diff:.2f})"
        else:
            assert diff < 1.0
