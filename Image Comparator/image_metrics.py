from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def calculate_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate PSNR between two images."""
    return float(cv2.PSNR(img1, img2))


def calculate_sharpness(image: np.ndarray) -> float:
    """Estimate image sharpness using variance of Laplacian."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())  # type-safe for static analysis


def estimate_noise(image: np.ndarray) -> float:
    """Estimate image noise as variance of high-frequency components."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    diff = np.asarray(gray - blurred, dtype=np.float64)
    return float(np.var(diff))  # type-safe


def calculate_metrics(img1_path: Path | str, img2_path: Path | str) -> dict:
    """Compute PSNR, sharpness, noise, and SSIM metrics between two images."""
    img1_path = Path(img1_path)
    img2_path = Path(img2_path)

    if not img1_path.is_file() or not img2_path.is_file():
        raise FileNotFoundError(f"One or both image paths are invalid: {img1_path}, {img2_path}")

    img1 = cv2.imread(str(img1_path))
    img2 = cv2.imread(str(img2_path))

    if img1 is None or img2 is None:
        raise ValueError(f"Failed to read one or both images: {img1_path}, {img2_path}")

    # Keep native copies for sharpness/noise
    img1_native = img1.copy()
    img2_native = img2.copy()

    # Resize to match dimensions for PSNR + SSIM
    target_h = min(img1.shape[0], img2.shape[0])
    target_w = min(img1.shape[1], img2.shape[1])

    if (img1.shape[0] != target_h) or (img1.shape[1] != target_w):
        img1 = cv2.resize(img1, (target_w, target_h))
    if (img2.shape[0] != target_h) or (img2.shape[1] != target_w):
        img2 = cv2.resize(img2, (target_w, target_h))

    # Metrics
    psnr_1 = calculate_psnr(img1, img2)
    psnr_2 = calculate_psnr(img2, img1)

    sharp_1 = calculate_sharpness(img1_native)
    sharp_2 = calculate_sharpness(img2_native)

    noise_1 = estimate_noise(img1_native)
    noise_2 = estimate_noise(img2_native)

    ssim_value: float = ssim(
        cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY),
        full=False  # ensure float return
    )

    return {
        "psnr1": round(psnr_1, 2),
        "sharpness1": round(sharp_1, 2),
        "noise1": round(noise_1, 2),
        "ssim": round(ssim_value, 4),
        "psnr2": round(psnr_2, 2),
        "sharpness2": round(sharp_2, 2),
        "noise2": round(noise_2, 2),
    }
