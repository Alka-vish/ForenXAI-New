from typing import Tuple, Dict, Any

import cv2
import numpy as np

from utils.image_utils import save_visualization_map


def compute_noise_analysis(gray: np.ndarray, session_id: str) -> Tuple[Dict[str, Any], str]:
    """
    Computes spatial high-pass noise residual using Gaussian smoothing:
    - Gaussian blur (5x5, sigma=1.0)
    - Residual: Image - GaussianBlur
    - Noise level: Standard deviation of residual
    - Residual energy: Mean squared energy of residual
    Generates and saves colored noise residual visualization map.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), sigmaX=1.0)
    residual = gray.astype(np.float64) - blurred.astype(np.float64)

    noise_level = float(np.std(residual))
    residual_energy = float(np.mean(residual ** 2))

    # Normalized residual map (amplified absolute residual)
    abs_residual = np.abs(residual)
    noise_norm = cv2.normalize(abs_residual, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    noise_map_colored = cv2.applyColorMap(noise_norm, cv2.COLORMAP_VIRIDIS)

    noise_map_filename = f"noise_residual_{session_id}.png"
    noise_map_url = save_visualization_map(noise_map_filename, noise_map_colored)

    result = {
        "status": "success",
        "gaussian_blur": "5x5 kernel (sigma=1.0)",
        "high_pass_noise_residual": "Image - GaussianBlur",
        "noise_level": round(noise_level, 4),
        "residual_energy": round(residual_energy, 4),
    }

    return result, noise_map_url
