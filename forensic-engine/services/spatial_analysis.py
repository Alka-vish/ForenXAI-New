from typing import Tuple, Dict, Any

import cv2
import numpy as np

from utils.image_utils import save_visualization_map


def compute_spatial_features(gray: np.ndarray, session_id: str) -> Tuple[Dict[str, Any], str]:
    """
    Computes deterministic spatial features:
    - Brightness (mean pixel luminance)
    - Contrast (standard deviation of pixel intensities)
    - Sharpness (variance of the Laplacian operator)
    - Edge density (ratio of Canny edge pixels)
    - Image entropy (Shannon entropy of 8-bit histogram)
    Generates and saves Canny edge visualization map.
    """
    total_pixels = int(gray.size)

    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness_laplacian_var = float(laplacian.var())

    canny_edges = cv2.Canny(gray, threshold1=100, threshold2=200)
    edge_pixel_count = int(np.count_nonzero(canny_edges))
    edge_density = float(edge_pixel_count / total_pixels) if total_pixels > 0 else 0.0

    hist, _ = np.histogram(gray, bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    image_entropy = float(-np.sum(hist * np.log2(hist))) if len(hist) > 0 else 0.0

    edge_map_filename = f"edge_map_{session_id}.png"
    edge_map_url = save_visualization_map(edge_map_filename, canny_edges)

    result = {
        "status": "success",
        "brightness": round(brightness, 4),
        "contrast": round(contrast, 4),
        "sharpness_laplacian_var": round(sharpness_laplacian_var, 4),
        "edge_density": round(edge_density, 6),
        "image_entropy": round(image_entropy, 4),
    }

    return result, edge_map_url
