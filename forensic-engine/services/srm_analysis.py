from typing import Tuple, Dict, Any, List, Optional

import cv2
import numpy as np

from utils.image_utils import save_visualization_map


def compute_srm_residuals(gray: np.ndarray, session_id: str) -> Tuple[Dict[str, Any], str]:
    """
    Applies standard Spatial Rich Model (SRM) linear high-pass filter kernels:
    - 1st order horizontal difference
    - 1st order vertical difference
    - 2nd order horizontal difference
    - 2nd order vertical difference
    - 3x3 Laplacian high-pass
    - 3x3 Ker-Böhme (KB) square kernel
    - 3x3 Edge detector kernel
    Calculates deterministic residual energies and statistics.
    Generates and saves the SRM residual visualization map.
    """
    img_float = gray.astype(np.float64)

    srm_kernels = {
        "1st_order_horizontal": np.array([
            [0, 0, 0],
            [-1, 1, 0],
            [0, 0, 0]
        ], dtype=np.float64),
        "1st_order_vertical": np.array([
            [0, -1, 0],
            [0, 1, 0],
            [0, 0, 0]
        ], dtype=np.float64),
        "2nd_order_horizontal": np.array([
            [0, 0, 0],
            [-1, 2, -1],
            [0, 0, 0]
        ], dtype=np.float64),
        "2nd_order_vertical": np.array([
            [0, -1, 0],
            [0, 2, 0],
            [0, -1, 0]
        ], dtype=np.float64),
        "laplacian_3x3": np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ], dtype=np.float64),
        "square_3x3_kb": np.array([
            [-1, 2, -1],
            [2, -4, 2],
            [-1, 2, -1]
        ], dtype=np.float64),
        "edge_3x3": np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ], dtype=np.float64),
    }

    filters_results: Dict[str, Any] = {}
    energies: List[float] = []
    kb_residual_abs: Optional[np.ndarray] = None

    for name, kernel in srm_kernels.items():
        res = cv2.filter2D(img_float, -1, kernel, borderType=cv2.BORDER_REFLECT)
        mean_val = float(np.mean(res))
        std_val = float(np.std(res))
        var_val = float(np.var(res))
        energy_val = float(np.mean(res ** 2))
        min_val = float(np.min(res))
        max_val = float(np.max(res))

        energies.append(energy_val)

        filters_results[name] = {
            "kernel_shape": list(kernel.shape),
            "mean": round(mean_val, 4),
            "std_dev": round(std_val, 4),
            "variance": round(var_val, 4),
            "residual_energy": round(energy_val, 4),
            "min_residual": round(min_val, 4),
            "max_residual": round(max_val, 4),
        }

        if name == "square_3x3_kb":
            kb_residual_abs = np.abs(res)

    if kb_residual_abs is None:
        kb_residual_abs = np.abs(res)

    norm_res = cv2.normalize(kb_residual_abs, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    srm_colored = cv2.applyColorMap(norm_res, cv2.COLORMAP_TWILIGHT)

    srm_filename = f"srm_residual_{session_id}.png"
    srm_map_url = save_visualization_map(srm_filename, srm_colored)

    result = {
        "status": "success",
        "filter_count": len(srm_kernels),
        "filters": filters_results,
        "average_residual_energy": round(float(np.mean(energies)), 4),
        "max_residual_energy": round(float(np.max(energies)), 4),
        "visualization_map": srm_map_url,
    }

    return result, srm_map_url
