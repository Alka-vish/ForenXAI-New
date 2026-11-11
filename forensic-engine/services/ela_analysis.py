import io
from typing import Tuple, Dict, Any, List

import cv2
import numpy as np
from PIL import Image

from utils.image_utils import save_visualization_map


def compute_recompression_ela(
    pil_image: Image.Image, cv_img: np.ndarray, session_id: str, quality: int = 90
) -> Tuple[Dict[str, Any], str]:
    """
    Performs deterministic Error Level Analysis (ELA) via in-memory recompression:
    1. Recompresses the original image to JPEG at the specified quality factor (default 90).
    2. Decodes the recompressed image into identical pixel space.
    3. Calculates absolute pixel differences across channels and luminance.
    4. Evaluates global and regional difference distributions (3x3 grid).
    5. Saves enhanced difference visualization map.
    """
    # Ensure RGB color representation for consistent recompression comparison
    rgb_orig = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_rgb = Image.fromarray(rgb_orig)

    # In-memory JPEG recompression
    buffer = io.BytesIO()
    pil_rgb.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    recompressed_pil = Image.open(buffer)
    rgb_recomp = np.array(recompressed_pil)

    # Calculate absolute difference across all channels
    abs_diff = np.abs(rgb_orig.astype(np.float64) - rgb_recomp.astype(np.float64))
    diff_lum = np.mean(abs_diff, axis=2)

    avg_diff = float(np.mean(diff_lum))
    max_diff = float(np.max(diff_lum))
    std_diff = float(np.std(diff_lum))

    # Regional difference analysis (3x3 grid)
    h, w = diff_lum.shape
    row_step = h // 3
    col_step = w // 3

    regions: List[Dict[str, Any]] = []
    region_means: List[float] = []

    for r in range(3):
        r_start = r * row_step
        r_end = (r + 1) * row_step if r < 2 else h
        for c in range(3):
            c_start = c * col_step
            c_end = (c + 1) * col_step if c < 2 else w

            patch = diff_lum[r_start:r_end, c_start:c_end]
            patch_mean = float(np.mean(patch)) if patch.size > 0 else 0.0
            patch_max = float(np.max(patch)) if patch.size > 0 else 0.0
            patch_std = float(np.std(patch)) if patch.size > 0 else 0.0

            region_means.append(patch_mean)
            regions.append({
                "region_id": f"R{r+1}_{c+1}",
                "grid_position": [r, c],
                "mean_difference": round(patch_mean, 4),
                "max_difference": round(patch_max, 4),
                "std_difference": round(patch_std, 4),
            })

    regional_variance = float(np.var(region_means)) if len(region_means) > 0 else 0.0
    highest_reg = float(np.max(region_means)) if len(region_means) > 0 else 0.0
    lowest_reg = float(np.min(region_means)) if len(region_means) > 0 else 0.0

    # Scaled ELA visualization map (amplified difference for visibility)
    scaled_diff = np.clip(diff_lum * 15.0, 0, 255).astype(np.uint8)
    ela_colored = cv2.applyColorMap(scaled_diff, cv2.COLORMAP_MAGMA)

    ela_filename = f"ela_recompression_{session_id}.png"
    ela_map_url = save_visualization_map(ela_filename, ela_colored)

    result = {
        "status": "success",
        "recompression_quality": quality,
        "average_difference": round(avg_diff, 4),
        "maximum_difference": round(max_diff, 4),
        "difference_std": round(std_diff, 4),
        "regional_difference_information": {
            "grid_dimensions": [3, 3],
            "total_regions": len(regions),
            "regional_variance": round(regional_variance, 4),
            "highest_region_average": round(highest_reg, 4),
            "lowest_region_average": round(lowest_reg, 4),
            "regional_contrast_range": round(highest_reg - lowest_reg, 4),
            "regions": regions,
        },
        "visualization_map": ela_map_url,
    }

    return result, ela_map_url
