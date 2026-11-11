from typing import Tuple, Dict, Any

import cv2
import numpy as np

from utils.image_utils import save_visualization_map


def compute_wavelet_decomposition(gray: np.ndarray, session_id: str) -> Tuple[Dict[str, Any], str]:
    """
    Performs 2D Haar discrete wavelet decomposition:
    Decomposes the image into LL (Approximation), LH (Horizontal High),
    HL (Vertical High), and HH (Diagonal High) frequency subbands.
    Calculates subband energies and generates a 2x2 collage visualization.
    """
    h, w = gray.shape
    h_even = h if h % 2 == 0 else h - 1
    w_even = w if w % 2 == 0 else w - 1

    img_even = gray[:h_even, :w_even].astype(np.float64)

    # 1. Row decomposition (Low & High)
    L_row = (img_even[:, 0::2] + img_even[:, 1::2]) / np.sqrt(2.0)
    H_row = (img_even[:, 0::2] - img_even[:, 1::2]) / np.sqrt(2.0)

    # 2. Column decomposition on row outputs
    LL = (L_row[0::2, :] + L_row[1::2, :]) / np.sqrt(2.0)  # Approximation
    LH = (L_row[0::2, :] - L_row[1::2, :]) / np.sqrt(2.0)  # Horizontal details
    HL = (H_row[0::2, :] + H_row[1::2, :]) / np.sqrt(2.0)  # Vertical details
    HH = (H_row[0::2, :] - H_row[1::2, :]) / np.sqrt(2.0)  # Diagonal details

    ll_energy = float(np.mean(LL ** 2))
    lh_energy = float(np.mean(LH ** 2))
    hl_energy = float(np.mean(HL ** 2))
    hh_energy = float(np.mean(HH ** 2))

    total_high_energy = float(lh_energy + hl_energy + hh_energy)
    total_energy = float(ll_energy + total_high_energy)

    ll_ratio = float(ll_energy / total_energy) if total_energy > 0 else 0.0
    lh_ratio = float(lh_energy / total_energy) if total_energy > 0 else 0.0
    hl_ratio = float(hl_energy / total_energy) if total_energy > 0 else 0.0
    hh_ratio = float(hh_energy / total_energy) if total_energy > 0 else 0.0
    high_freq_ratio = float(total_high_energy / total_energy) if total_energy > 0 else 0.0

    # 2x2 Collage visualization [LL, HL; LH, HH]
    ll_vis = cv2.normalize(LL, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    hl_vis = cv2.normalize(np.abs(HL), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    lh_vis = cv2.normalize(np.abs(LH), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    hh_vis = cv2.normalize(np.abs(HH), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    top_row = np.hstack([ll_vis, hl_vis])
    bottom_row = np.hstack([lh_vis, hh_vis])
    wavelet_collage = np.vstack([top_row, bottom_row])

    # Crosshair quadrant divider
    mid_y, mid_x = top_row.shape[0], ll_vis.shape[1]
    wavelet_collage[mid_y - 1 : mid_y + 1, :] = 255
    wavelet_collage[:, mid_x - 1 : mid_x + 1] = 255

    wavelet_colored = cv2.applyColorMap(wavelet_collage, cv2.COLORMAP_VIRIDIS)
    wavelet_filename = f"wavelet_decomposition_{session_id}.png"
    wavelet_map_url = save_visualization_map(wavelet_filename, wavelet_colored)

    result = {
        "status": "success",
        "wavelet_family": "Haar (2D DWT Level 1)",
        "subband_dimensions": [int(LL.shape[0]), int(LL.shape[1])],
        "ll_energy": round(ll_energy, 4),
        "lh_energy": round(lh_energy, 4),
        "hl_energy": round(hl_energy, 4),
        "hh_energy": round(hh_energy, 4),
        "total_high_frequency_energy": round(total_high_energy, 4),
        "energy_ratios": {
            "ll_ratio": round(ll_ratio, 6),
            "lh_ratio": round(lh_ratio, 6),
            "hl_ratio": round(hl_ratio, 6),
            "hh_ratio": round(hh_ratio, 6),
            "high_frequency_ratio": round(high_freq_ratio, 6),
        },
        "visualization_map": wavelet_map_url,
    }

    return result, wavelet_map_url
