from typing import Dict, Any, List, Optional

def format_error_section(message: str) -> Dict[str, Any]:
    """
    Standard error structure for an individual forensic analysis section.
    """
    return {
        "status": "error",
        "message": message,
    }

def build_analysis_response(
    image_info: Dict[str, Any],
    spatial_features: Dict[str, Any],
    noise_analysis: Dict[str, Any],
    frequency_analysis: Dict[str, Any],
    srm_analysis: Dict[str, Any],
    wavelet_analysis: Dict[str, Any],
    compression_analysis: Dict[str, Any],
    recompression_ela_analysis: Dict[str, Any],
    ai_detection: Dict[str, Any],
    analysis_maps: Dict[str, str],
    evidence: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Assembles the standard forensic analysis JSON payload, strictly preserving
    the schema and naming conventions.
    """
    return {
        "image_information": image_info,
        "spatial_features": spatial_features,
        "noise_analysis": noise_analysis,
        "frequency_analysis": frequency_analysis,
        "srm_analysis": srm_analysis,
        "wavelet_analysis": wavelet_analysis,
        "compression_analysis": compression_analysis,
        "recompression_ela_analysis": recompression_ela_analysis,
        "ai_detection": ai_detection,
        "evidence": evidence if evidence is not None else [],
        "analysis_maps": analysis_maps,
    }
