import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from utils.image_utils import MAPS_DIR
from utils.response_utils import build_analysis_response, format_error_section
from services.image_service import (
    validate_and_read_image,
    load_pil_image,
    load_cv_image,
    extract_image_information,
)
from services.spatial_analysis import compute_spatial_features
from services.noise_analysis import compute_noise_analysis
from services.frequency_analysis import compute_frequency_analysis
from services.srm_analysis import compute_srm_residuals
from services.wavelet_analysis import compute_wavelet_decomposition
from services.compression_analysis import compute_jpeg_compression_analysis
from services.ela_analysis import compute_recompression_ela
from services.ai_detector import detect_ai_generated_image
from services.evidence_service import extract_forensic_evidence
from agents.debate_graph import run_forensic_debate

router = APIRouter()


@router.get("/health", summary="Health Check")
def health_check() -> Dict[str, str]:
    """
    Simple health verification endpoint.
    """
    return {"status": "ok"}


@router.get("/maps/{filename}", summary="Retrieve Generated Analysis Map")
def get_analysis_map(filename: str):
    """
    Serve a generated analysis map from temporary storage.
    Includes path traversal protection.
    """
    safe_filename = Path(filename).name
    file_path = MAPS_DIR / safe_filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested analysis map was not found.",
        )

    return FileResponse(file_path, media_type="image/png")


@router.post("/analyze", summary="Perform Forensic Feature & Residual Extraction")
async def analyze_image(image: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Orchestrates deterministic image forensic analyses:
    1. Validation and image loading (Pillow & OpenCV)
    2. Spatial feature extraction (brightness, contrast, sharpness, edge density, entropy)
    3. Noise residual analysis (Gaussian residual, noise level, energy)
    4. Frequency analysis (2D FFT, radial energy distribution)
    5. SRM residual filtering (7 spatial rich model kernels)
    6. Wavelet subband decomposition (Haar 2D DWT)
    7. JPEG compression analysis (quantization tables, BAF, block variance)
    8. Error Level Analysis (in-memory JPEG recompression difference)
    """
    # 1. Validate file presence, extension, and load bytes
    contents, ext = await validate_and_read_image(image)

    # 2. Decode and verify with Pillow
    pil_image, color_mode, img_format, width, height = load_pil_image(contents, ext)

    # 3. Decode with OpenCV for matrix calculations
    cv_img, gray, total_pixels = load_cv_image(contents)

    session_id = uuid.uuid4().hex[:12]
    analysis_maps: Dict[str, str] = {}

    # Metadata
    image_info = extract_image_information(
        filename=image.filename or "unknown",
        width=width,
        height=height,
        color_mode=color_mode,
        img_format=img_format,
        file_size_bytes=len(contents),
    )

    # Spatial features
    try:
        spatial_features, edge_map_url = compute_spatial_features(gray, session_id)
        analysis_maps["edge_map"] = edge_map_url
    except Exception as e:
        spatial_features = format_error_section(str(e))

    # Noise analysis
    try:
        noise_analysis, noise_map_url = compute_noise_analysis(gray, session_id)
        analysis_maps["noise_residual_map"] = noise_map_url
    except Exception as e:
        noise_analysis = format_error_section(str(e))

    # Frequency analysis (2D FFT)
    try:
        frequency_analysis, freq_map_url = compute_frequency_analysis(gray, session_id)
        analysis_maps["frequency_map"] = freq_map_url
    except Exception as e:
        frequency_analysis = format_error_section(str(e))

    # SRM analysis
    try:
        srm_analysis, srm_map_url = compute_srm_residuals(gray, session_id)
        analysis_maps["srm_residual_map"] = srm_map_url
    except Exception as e:
        srm_analysis = format_error_section(str(e))

    # Wavelet analysis (Haar 2D DWT)
    try:
        wavelet_analysis, wavelet_map_url = compute_wavelet_decomposition(gray, session_id)
        analysis_maps["wavelet_map"] = wavelet_map_url
    except Exception as e:
        wavelet_analysis = format_error_section(str(e))

    # JPEG Compression analysis
    try:
        compression_analysis = compute_jpeg_compression_analysis(pil_image, gray, ext)
    except Exception as e:
        compression_analysis = format_error_section(str(e))

    # ELA Recompression analysis
    try:
        recompression_ela_analysis, ela_map_url = compute_recompression_ela(
            pil_image, cv_img, session_id, quality=90
        )
        analysis_maps["ela_recompression_map"] = ela_map_url
    except Exception as e:
        recompression_ela_analysis = format_error_section(str(e))

    # AI-Generated Image Detection (deep learning probabilistic indicator)
    try:
        ai_detection = detect_ai_generated_image(pil_image)
    except Exception as e:
        ai_detection = {
            "status": "unavailable",
            "model_name": "umm-maybe/AI-image-detector",
            "model_architecture": "Swin Transformer for Image Classification",
            "message": f"AI detector execution failure: {str(e)}",
            "prediction": None,
            "model_score": None,
            "confidence_scores": None,
            "score_interpretation": None,
            "limitations": [
                "Trained on early diffusion generators (Midjourney v4, Stable Diffusion 1.x/2.x).",
                "May exhibit concept drift or reduced sensitivity on newer architectures.",
                "Heavy compression, resizing, or visual noise can alter probabilistic outputs.",
            ],
            "forensic_notice": (
                "AI detection model is unavailable. Forensic analysis relies exclusively "
                "on empirical spatial, noise, wavelet, and frequency evidence."
            ),
        }

    # Extract structured, traceable forensic evidence ledger
    evidence = extract_forensic_evidence(
        spatial_features=spatial_features,
        noise_analysis=noise_analysis,
        frequency_analysis=frequency_analysis,
        srm_analysis=srm_analysis,
        wavelet_analysis=wavelet_analysis,
        compression_analysis=compression_analysis,
        recompression_ela_analysis=recompression_ela_analysis,
        ai_detection=ai_detection,
        analysis_maps=analysis_maps,
    )

    # Build and return consolidated response payload
    return build_analysis_response(
        image_info=image_info,
        spatial_features=spatial_features,
        noise_analysis=noise_analysis,
        frequency_analysis=frequency_analysis,
        srm_analysis=srm_analysis,
        wavelet_analysis=wavelet_analysis,
        compression_analysis=compression_analysis,
        recompression_ela_analysis=recompression_ela_analysis,
        ai_detection=ai_detection,
        analysis_maps=analysis_maps,
        evidence=evidence,
    )


@router.post("/detect-ai-image", summary="Detect Synthetic/AI-Generated Image Probability")
async def detect_ai_image(image: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Executes deep learning inference using a pretrained Swin Transformer
    (umm-maybe/AI-image-detector) to evaluate artificial vs. human probabilities.

    Safety & Integrity Constraints:
    - Only provides an empirical probabilistic indicator; does NOT issue a final REAL/FAKE verdict.
    - If the model is unavailable or encounters an error, returns an honest descriptive status
      without crashing the service or producing synthetic confidence figures.
    """
    # 1. Validate file presence, extension, and load bytes
    contents, ext = await validate_and_read_image(image)

    # 2. Decode and verify with Pillow
    pil_image, color_mode, img_format, width, height = load_pil_image(contents, ext)

    # 3. Extract basic image metadata
    image_info = extract_image_information(
        filename=image.filename or "unknown",
        width=width,
        height=height,
        color_mode=color_mode,
        img_format=img_format,
        file_size_bytes=len(contents),
    )

    # 4. Run model inference
    detection_result = detect_ai_generated_image(pil_image)

    return {
        "image_information": image_info,
        "ai_detection": detection_result,
    }


@router.post("/debate", summary="Perform Forensic Analysis and Execute 4-Agent LangGraph Debate")
async def debate_image(image: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Complete end-to-end pipeline:
    1. Runs all deterministic forensic modules + AI detection on the uploaded image.
    2. Extracts structured, traceable forensic evidence ledger (E001, E002, etc.).
    3. Executes the 4-agent LangGraph debate workflow:
       - Prosecutor (4 turns) & Defence (4 turns) alternating on real evidence
       - Intermediate Sufficiency checks
       - Expert Agent verification and anti-hallucination audit
       - Judge Agent final assessment (REAL, FAKE, or UNCERTAIN)
    """
    # 1. Run standard forensic analysis
    analysis_res = await analyze_image(image=image)

    # 2. Extract structured evidence ledger
    evidence = analysis_res.get("evidence", [])
    image_id = analysis_res.get("image_information", {}).get("filename", "unknown")

    # 3. Execute LangGraph 4-agent debate
    debate_result = run_forensic_debate(
        analysis_result=analysis_res,
        evidence=evidence,
        image_id=image_id,
    )

    return {
        "image_information": analysis_res.get("image_information"),
        "features": {
            "spatial_features": analysis_res.get("spatial_features"),
            "noise_analysis": analysis_res.get("noise_analysis"),
            "frequency_analysis": analysis_res.get("frequency_analysis"),
            "srm_analysis": analysis_res.get("srm_analysis"),
            "wavelet_analysis": analysis_res.get("wavelet_analysis"),
            "compression_analysis": analysis_res.get("compression_analysis"),
            "recompression_ela_analysis": analysis_res.get("recompression_ela_analysis"),
            "ai_detection": analysis_res.get("ai_detection"),
        },
        "evidence": evidence,
        "evidence_summary": {
            "total_evidence_items": len(evidence),
            "evidence_categories": list(set(e.get("category", "") for e in evidence)),
        },
        "debate": debate_result,
        "analysis": analysis_res,
    }


@router.post("/debate-evidence", summary="Execute 4-Agent LangGraph Debate on Extracted Evidence")
async def debate_extracted_evidence(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the 4-agent LangGraph forensic debate workflow directly from
    an existing analysis result and evidence ledger payload.
    """
    analysis_result = payload.get("analysis_result", {})
    evidence = payload.get("evidence", [])
    image_id = payload.get("image_id") or analysis_result.get("image_information", {}).get("filename", "unknown")

    if not evidence and "evidence" in analysis_result:
        evidence = analysis_result["evidence"]

    debate_result = run_forensic_debate(
        analysis_result=analysis_result,
        evidence=evidence,
        image_id=image_id,
    )

    return {"debate": debate_result}
