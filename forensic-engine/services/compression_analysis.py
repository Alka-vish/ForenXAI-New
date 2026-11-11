from typing import Dict, Any, List, Optional

import numpy as np
from PIL import Image

from utils.image_utils import STD_IJG_LUM_Q50


def compute_jpeg_compression_analysis(
    pil_image: Image.Image, gray: np.ndarray, ext: str
) -> Dict[str, Any]:
    """
    Inspects JPEG compression information:
    - Verifies format
    - Extracts luminance/chrominance quantization tables if present
    - Inverts IJG quantization scale to estimate JPEG quality factor
    - Measures 8x8 DCT grid boundary discontinuities (Blocking Artifact Factor)
    - Computes 8x8 block-level variance uniformity
    If image is non-JPEG or lacks JPEG quantization tables, returns unavailable status.
    """
    is_jpeg = (pil_image.format == "JPEG") or (ext in {".jpg", ".jpeg"})

    if not is_jpeg:
        return {
            "status": "unavailable",
            "message": "JPEG compression analysis unavailable for non-JPEG format.",
        }

    # Inspect Pillow quantization tables
    quant_tables = getattr(pil_image, "quantization", None)
    if not quant_tables or not isinstance(quant_tables, dict) or len(quant_tables) == 0:
        return {
            "status": "unavailable",
            "message": "JPEG quantization tables unavailable or stripped from image metadata.",
        }

    # 1. Quantization Table Analysis
    lum_table_raw = quant_tables.get(0)
    chrom_table_raw = quant_tables.get(1)

    lum_table: Optional[List[int]] = None
    estimated_quality: Optional[float] = None
    mean_lum_step: Optional[float] = None

    if lum_table_raw and len(lum_table_raw) >= 64:
        lum_table = [int(v) for v in lum_table_raw[:64]]
        lum_arr = np.array(lum_table, dtype=np.float64)
        mean_lum_step = float(np.mean(lum_arr))

        # Estimate IJG quality factor by inverting scaling factor relative to Q50
        scale_factors = (lum_arr * 100.0) / STD_IJG_LUM_Q50
        median_scale = float(np.median(scale_factors))
        if median_scale <= 100.0:
            quality = (200.0 - median_scale) / 2.0
        else:
            quality = 5000.0 / median_scale
        estimated_quality = round(float(np.clip(quality, 1.0, 100.0)), 2)

    chrom_table: Optional[List[int]] = None
    if chrom_table_raw and len(chrom_table_raw) >= 64:
        chrom_table = [int(v) for v in chrom_table_raw[:64]]

    # 2. Block-level 8x8 DCT grid boundary statistics
    h, w = gray.shape
    h_blocks = h // 8
    w_blocks = w // 8

    if h_blocks < 2 or w_blocks < 2:
        return {
            "status": "partial",
            "message": "Image dimensions too small to evaluate 8x8 block grid statistics.",
            "estimated_quality_factor": estimated_quality,
            "quantization_tables_present": True,
            "luminance_quantization_table": lum_table,
        }

    gray_sub = gray[: h_blocks * 8, : w_blocks * 8].astype(np.float64)

    # Horizontal boundary difference: between 8k-1 and 8k vs internal 8k+3 and 8k+4
    b_h_diffs = []
    i_h_diffs = []
    for k in range(1, h_blocks):
        border = np.abs(gray_sub[8 * k, :] - gray_sub[8 * k - 1, :])
        internal = np.abs(gray_sub[8 * k - 4, :] - gray_sub[8 * k - 5, :])
        b_h_diffs.append(np.mean(border))
        i_h_diffs.append(np.mean(internal))

    # Vertical boundary difference: between 8m-1 and 8m vs internal 8m+3 and 8m+4
    b_v_diffs = []
    i_v_diffs = []
    for m in range(1, w_blocks):
        border = np.abs(gray_sub[:, 8 * m] - gray_sub[:, 8 * m - 1])
        internal = np.abs(gray_sub[:, 8 * m - 4] - gray_sub[:, 8 * m - 5])
        b_v_diffs.append(np.mean(border))
        i_v_diffs.append(np.mean(internal))

    mean_b_diff = (float(np.mean(b_h_diffs)) + float(np.mean(b_v_diffs))) / 2.0
    mean_i_diff = (float(np.mean(i_h_diffs)) + float(np.mean(i_v_diffs))) / 2.0

    blocking_artifact_factor = (
        float(mean_b_diff / (mean_i_diff + 1e-6)) if mean_i_diff >= 0 else 1.0
    )

    # 3. Compression Consistency: Variance across 8x8 blocks
    block_variances: List[float] = []
    for r in range(h_blocks):
        for c in range(w_blocks):
            block = gray_sub[r * 8 : (r + 1) * 8, c * 8 : (c + 1) * 8]
            block_variances.append(float(np.var(block)))

    block_var_mean = float(np.mean(block_variances))
    block_var_std = float(np.std(block_variances))

    return {
        "status": "success",
        "format": "JPEG",
        "has_quantization_tables": True,
        "estimated_quality_factor": estimated_quality,
        "quantization_info": {
            "luminance_table_size": len(lum_table) if lum_table else 0,
            "mean_luminance_step": round(mean_lum_step, 4) if mean_lum_step else None,
            "chrominance_table_size": len(chrom_table) if chrom_table else 0,
            "luminance_table": lum_table,
        },
        "block_level_statistics": {
            "grid_size": [8, 8],
            "total_evaluated_blocks": h_blocks * w_blocks,
            "mean_boundary_difference": round(mean_b_diff, 4),
            "mean_internal_difference": round(mean_i_diff, 4),
            "blocking_artifact_factor": round(blocking_artifact_factor, 4),
            "block_variance_mean": round(block_var_mean, 4),
            "block_variance_std": round(block_var_std, 4),
        },
    }
