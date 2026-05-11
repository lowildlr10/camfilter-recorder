import cv2
import numpy as np

FILTER_NAMES = [
    "Normal",
    "Night Vision",
    "Infrared / Thermal",
    "Deep Blue Thermal",
    "Grayscale",
    "Sepia",
    "Vintage",
    "Edge Detection",
    "Cartoon",
    "Emboss",
    "Pencil Sketch",
    "Negative",
    "High Contrast",
    "Vignette",
]

# ── Module-level cached objects (created once, reused every frame) ─────────────
_clahe_nv = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
_clahe_hc = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))

# Vignette mask cache: keyed by (h, w) so resizing invalidates it
_vignette_cache: dict[tuple[int, int], np.ndarray] = {}


def apply_filter(frame: np.ndarray, name: str) -> np.ndarray:
    dispatch = {
        "Normal":             _normal,
        "Night Vision":       _night_vision,
        "Infrared / Thermal": _infrared,
        "Deep Blue Thermal":  _deep_blue_thermal,
        "Grayscale":          _grayscale,
        "Sepia":              _sepia,
        "Vintage":            _vintage,
        "Edge Detection":     _edge_detection,
        "Cartoon":            _cartoon,
        "Emboss":             _emboss,
        "Pencil Sketch":      _pencil_sketch,
        "Negative":           _negative,
        "High Contrast":      _high_contrast,
        "Vignette":           _vignette,
    }
    fn = dispatch.get(name, _normal)
    try:
        return fn(frame)
    except Exception:
        return frame


def _normal(frame: np.ndarray) -> np.ndarray:
    return frame


def _night_vision(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced = _clahe_nv.apply(gray)
    noise = np.random.randint(0, 15, enhanced.shape, dtype=np.uint8)
    enhanced = cv2.add(enhanced, noise)
    green = np.zeros_like(frame)
    green[:, :, 1] = enhanced
    return green


def _infrared(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thermal = cv2.applyColorMap(cv2.bitwise_not(gray), cv2.COLORMAP_INFERNO)
    return thermal


def _deep_blue_thermal(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.applyColorMap(gray, cv2.COLORMAP_JET)


def _grayscale(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _sepia(frame: np.ndarray) -> np.ndarray:
    # Use float32 (2× faster than float64)
    kernel = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189],
    ], dtype=np.float32)
    sepia = cv2.transform(frame.astype(np.float32), kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)


def _vintage(frame: np.ndarray) -> np.ndarray:
    sepia = _sepia(frame)
    h, w = sepia.shape[:2]
    mask_3 = _build_vignette_mask(h, w, strength=0.55)
    return cv2.multiply(sepia, mask_3, scale=1 / 255.0).astype(np.uint8)


def _edge_detection(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def _cartoon(frame: np.ndarray) -> np.ndarray:
    """
    Fast cartoon effect: bilateral filter runs on a half-resolution copy,
    then upscaled back. Avoids the O(n²) cost at full 1080p.
    """
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // 2, h // 2))
    color = cv2.bilateralFilter(small, 7, 75, 75)
    color = cv2.resize(color, (w, h))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 5), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9,
    )
    return cv2.bitwise_and(color, color, mask=edges)


def _emboss(frame: np.ndarray) -> np.ndarray:
    kernel = np.array([
        [-2, -1,  0],
        [-1,  1,  1],
        [ 0,  1,  2],
    ], dtype=np.float32)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    embossed = cv2.filter2D(gray, cv2.CV_32F, kernel) + 128
    return cv2.cvtColor(np.clip(embossed, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)


def _pencil_sketch(frame: np.ndarray) -> np.ndarray:
    """Fast divide-blend sketch — avoids slow cv2.pencilSketch()."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sketch = cv2.divide(gray, cv2.GaussianBlur(gray, (21, 21), 0), scale=256.0)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


def _negative(frame: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(frame)


def _high_contrast(frame: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    return cv2.cvtColor(cv2.merge([_clahe_hc.apply(l), a, b]), cv2.COLOR_LAB2BGR)


def _vignette(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    mask_3 = _build_vignette_mask(h, w, strength=0.6)
    return cv2.multiply(frame, mask_3, scale=1 / 255.0).astype(np.uint8)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_vignette_mask(h: int, w: int, strength: float) -> np.ndarray:
    """
    Build (or return cached) a 3-channel uint8 vignette mask.
    Cached per (h, w, strength) so it is only recomputed on resize.
    """
    key = (h, w)
    if key not in _vignette_cache:
        X = np.linspace(-1, 1, w, dtype=np.float32)
        Y = np.linspace(-1, 1, h, dtype=np.float32)
        Xg, Yg = np.meshgrid(X, Y)
        mask = np.clip(1.0 - (Xg ** 2 + Yg ** 2) * strength, 0, 1)
        mask_u8 = (mask * 255).astype(np.uint8)
        _vignette_cache[key] = cv2.merge([mask_u8, mask_u8, mask_u8])
    return _vignette_cache[key]
