import os
from pathlib import Path
import cv2
import numpy as np

# Base directory for storing temporary analysis visualization maps
BASE_DIR = Path(__file__).resolve().parent.parent
MAPS_DIR = BASE_DIR / "temp_maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions for analysis
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Standard Independent JPEG Group (IJG) 50% Luminance Quantization Table
STD_IJG_LUM_Q50 = np.array([
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99
], dtype=np.float64)


def save_visualization_map(filename: str, img_matrix: np.ndarray) -> str:
    """
    Saves a generated visualization map to the temporary maps directory
    and returns its relative serving URL.
    """
    dest_path = MAPS_DIR / filename
    cv2.imwrite(str(dest_path), img_matrix)
    return f"/maps/{filename}"
