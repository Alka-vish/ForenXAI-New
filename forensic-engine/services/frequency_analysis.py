from typing import Tuple, Dict, Any

import cv2
import numpy as np

from utils.image_utils import save_visualization_map


def compute_frequency_analysis(gray: np.ndarray, session_id: str) -> Tuple[Dict[str, Any], str]:
    """
    Computes 2D Fast Fourier Transform (FFT) and radial frequency distribution:
    - Shifted DC component power spectrum
    - Total energy and radial partition energies (Low, Mid, High)
    - Normalized energy ratios
    Generates and saves log-magnitude frequency spectrum map.
    """
    h, w = gray.shape
    fft_transformed = np.fft.fft2(gray.astype(np.float64))
    fft_shifted = np.fft.fftshift(fft_transformed)

    magnitude_spectrum = np.abs(fft_shifted)
    power_spectrum = magnitude_spectrum ** 2
    total_energy = float(np.sum(power_spectrum))

    center_y, center_x = h // 2, w // 2
    y_coords, x_coords = np.ogrid[:h, :w]
    radii = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
    max_radius = np.sqrt(center_x ** 2 + center_y ** 2)

    norm_radii = radii / max_radius if max_radius > 0 else radii

    low_mask = norm_radii <= 0.15
    mid_mask = (norm_radii > 0.15) & (norm_radii <= 0.50)
    high_mask = norm_radii > 0.50

    low_frequency_energy = float(np.sum(power_spectrum[low_mask]))
    mid_frequency_energy = float(np.sum(power_spectrum[mid_mask]))
    high_frequency_energy = float(np.sum(power_spectrum[high_mask]))

    low_frequency_ratio = (
        float(low_frequency_energy / total_energy) if total_energy > 0 else 0.0
    )
    mid_frequency_ratio = (
        float(mid_frequency_energy / total_energy) if total_energy > 0 else 0.0
    )
    high_frequency_ratio = (
        float(high_frequency_energy / total_energy) if total_energy > 0 else 0.0
    )

    # Log magnitude visualization map
    log_magnitude = np.log1p(magnitude_spectrum)
    freq_norm = cv2.normalize(log_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    freq_map_colored = cv2.applyColorMap(freq_norm, cv2.COLORMAP_INFERNO)

    freq_map_filename = f"frequency_map_{session_id}.png"
    freq_map_url = save_visualization_map(freq_map_filename, freq_map_colored)

    result = {
        "status": "success",
        "fft_dimensions": [int(h), int(w)],
        "total_energy": float(f"{total_energy:.6e}"),
        "low_frequency_energy": float(f"{low_frequency_energy:.6e}"),
        "mid_frequency_energy": float(f"{mid_frequency_energy:.6e}"),
        "high_frequency_energy": float(f"{high_frequency_energy:.6e}"),
        "low_frequency_ratio": round(low_frequency_ratio, 6),
        "mid_frequency_ratio": round(mid_frequency_ratio, 6),
        "high_frequency_ratio": round(high_frequency_ratio, 6),
    }

    return result, freq_map_url
