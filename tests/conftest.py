import numpy as np
import pytest

from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def test_frame() -> np.ndarray:
    """Return a small BGR test image (100x100, random noise)."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def blank_frame() -> np.ndarray:
    """Return a solid grey BGR image (50x50)."""
    return np.full((50, 50, 3), 128, dtype=np.uint8)
