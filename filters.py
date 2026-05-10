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
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    noise = np.random.randint(0, 15, enhanced.shape, dtype=np.uint8)
    enhanced = cv2.add(enhanced, noise)
    green = np.zeros_like(frame)
    green[:, :, 1] = enhanced
    return green


def _infrared(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    thermal = cv2.applyColorMap(inverted, cv2.COLORMAP_INFERNO)
    return thermal


def _deep_blue_thermal(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return thermal


def _grayscale(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _sepia(frame: np.ndarray) -> np.ndarray:
    kernel = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189],
    ])
    sepia = cv2.transform(frame.astype(np.float64), kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)


def _vintage(frame: np.ndarray) -> np.ndarray:
    sepia = _sepia(frame)
    h, w = sepia.shape[:2]
    X = np.linspace(-1, 1, w)
    Y = np.linspace(-1, 1, h)
    Xg, Yg = np.meshgrid(X, Y)
    vignette = np.clip(1 - (Xg**2 + Yg**2) * 0.55, 0, 1)
    vignette = (vignette * 255).astype(np.uint8)
    vignette_3 = cv2.merge([vignette, vignette, vignette])
    return cv2.multiply(sepia, vignette_3, scale=1 / 255.0).astype(np.uint8)


def _edge_detection(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def _cartoon(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9
    )
    color = cv2.bilateralFilter(frame, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


def _emboss(frame: np.ndarray) -> np.ndarray:
    kernel = np.array([
        [-2, -1,  0],
        [-1,  1,  1],
        [ 0,  1,  2],
    ])
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    embossed = cv2.filter2D(gray, -1, kernel) + 128
    return cv2.cvtColor(embossed.astype(np.uint8), cv2.COLOR_GRAY2BGR)


def _pencil_sketch(frame: np.ndarray) -> np.ndarray:
    gray, _ = cv2.pencilSketch(frame, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _negative(frame: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(frame)


def _high_contrast(frame: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _vignette(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    X = np.linspace(-1, 1, w)
    Y = np.linspace(-1, 1, h)
    Xg, Yg = np.meshgrid(X, Y)
    mask = np.clip(1 - (Xg**2 + Yg**2) * 0.6, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    mask_3 = cv2.merge([mask, mask, mask])
    return cv2.multiply(frame, mask_3, scale=1 / 255.0).astype(np.uint8)
