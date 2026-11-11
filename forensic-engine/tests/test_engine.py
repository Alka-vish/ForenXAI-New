import io
import sys
from pathlib import Path

# Add parent directory to sys.path to enable importing forensic engine packages
PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

import numpy as np
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def create_sample_png() -> bytes:
    """Generates a realistic 128x128 PNG image with geometric patterns and gradients."""
    arr = np.zeros((128, 128, 3), dtype=np.uint8)
    for y in range(128):
        for x in range(128):
            arr[y, x] = [x * 2, y * 2, (x + y)]
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 60, 60], fill=(255, 100, 50), outline=(255, 255, 255))
    draw.ellipse([70, 70, 110, 110], fill=(50, 200, 255), outline=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def create_sample_jpeg() -> bytes:
    """Generates a realistic 128x128 JPEG image with standard quantization tables."""
    arr = np.zeros((128, 128, 3), dtype=np.uint8)
    for y in range(128):
        for x in range(128):
            arr[y, x] = [(x * 3) % 256, (y * 3) % 256, ((x + y) * 2) % 256]
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    draw.line([(0, 0), (127, 127)], fill=(255, 255, 0), width=3)
    draw.rectangle([30, 30, 90, 90], fill=(100, 255, 100))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf.getvalue()


def test_health():
    print("=== Testing GET /health ===")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.json()
    assert data.get("status") == "ok"
    print("✓ Health check passed:", data)


def test_png_analysis():
    print("\n=== Testing POST /analyze with PNG ===")
    png_bytes = create_sample_png()
    files = {"image": ("test_image.png", png_bytes, "image/png")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200, f"PNG analysis failed: {res.status_code} - {res.text}"
    data = res.json()

    # Image Information
    info = data["image_information"]
    assert info["width"] == 128 and info["height"] == 128
    assert info["format"] == "PNG"
    print("✓ Image Info:", info)

    # Spatial Features
    spatial = data["spatial_features"]
    assert spatial["status"] == "success"
    assert "brightness" in spatial and "contrast" in spatial and "sharpness_laplacian_var" in spatial
    print("✓ Spatial Features:", spatial)

    # Noise Analysis
    noise = data["noise_analysis"]
    assert noise["status"] == "success"
    assert noise["noise_level"] > 0
    print("✓ Noise Analysis:", noise)

    # Frequency Analysis
    freq = data["frequency_analysis"]
    assert freq["status"] == "success"
    assert freq["total_energy"] > 0
    print("✓ Frequency Analysis:", freq)

    # SRM Analysis
    srm = data["srm_analysis"]
    assert srm["status"] == "success"
    assert srm["filter_count"] == 7
    assert "average_residual_energy" in srm and srm["average_residual_energy"] > 0
    assert "visualization_map" in srm
    print("✓ SRM Analysis:", srm["filter_count"], "filters evaluated. Avg Energy:", srm["average_residual_energy"])

    # Wavelet Analysis
    wavelet = data["wavelet_analysis"]
    assert wavelet["status"] == "success"
    assert wavelet["wavelet_family"] == "Haar (2D DWT Level 1)"
    assert wavelet["ll_energy"] > 0 and wavelet["total_high_frequency_energy"] > 0
    assert "visualization_map" in wavelet
    print("✓ Wavelet Analysis:", wavelet["wavelet_family"], "LL:", wavelet["ll_energy"], "High:", wavelet["total_high_frequency_energy"])

    # Compression Analysis (unavailable for PNG)
    comp = data["compression_analysis"]
    assert comp["status"] == "unavailable"
    assert "unavailable" in comp["message"].lower()
    print("✓ Compression Analysis (PNG):", comp["status"], "-", comp["message"])

    # ELA Analysis
    ela = data["recompression_ela_analysis"]
    assert ela["status"] == "success"
    assert ela["average_difference"] > 0
    assert len(ela["regional_difference_information"]["regions"]) == 9
    assert "visualization_map" in ela
    print("✓ ELA Analysis:", "Avg Diff:", ela["average_difference"], "Regions:", len(ela["regional_difference_information"]["regions"]))

    # AI Detection Analysis
    assert "ai_detection" in data
    ai_det = data["ai_detection"]
    assert ai_det["model_name"] == "umm-maybe/AI-image-detector"
    assert ai_det["model_architecture"] == "Swin Transformer for Image Classification"
    assert ai_det["status"] in ["success", "unavailable"]
    if ai_det["status"] == "success":
        assert ai_det["prediction"] in ["artificial", "human"]
        assert isinstance(ai_det["model_score"], (int, float))
        assert "confidence_scores" in ai_det
        assert "score_interpretation" in ai_det
        assert "limitations" in ai_det
        print(f"✓ AI Detection in /analyze: Prediction = {ai_det['prediction']}, Score = {ai_det['model_score']}")
    else:
        assert ai_det["prediction"] is None
        print(f"✓ AI Detection in /analyze (fallback): {ai_det['message']}")

    # Evidence Ledger Verification
    assert "evidence" in data
    evidence_items = data["evidence"]
    assert isinstance(evidence_items, list)
    assert len(evidence_items) >= 8, f"Expected at least 8 evidence items, got {len(evidence_items)}"
    
    # Check unique IDs
    evidence_ids = [item["evidence_id"] for item in evidence_items]
    assert len(evidence_ids) == len(set(evidence_ids)), "Evidence IDs must be unique"
    for eid in evidence_ids:
        assert eid.startswith("E") and eid[1:].isdigit(), f"Invalid ID format: {eid}"

    # Required evidence schema validation
    required_evidence_fields = [
        "evidence_id",
        "category",
        "title",
        "observation",
        "measurement",
        "source_module",
        "coordinates",
        "strength",
        "alternative_explanations",
        "limitations",
    ]
    for item in evidence_items:
        for field in required_evidence_fields:
            assert field in item, f"Missing '{field}' in evidence item: {item.get('evidence_id')}"
        assert isinstance(item["measurement"], dict)
        assert isinstance(item["alternative_explanations"], list)
        assert len(item["alternative_explanations"]) > 0
        assert isinstance(item["limitations"], list)
        assert len(item["limitations"]) > 0
        assert item["strength"] in ["informational", "low", "medium", "high"]
        # If coordinates are present, verify valid spatial grid position
        if item["coordinates"] is not None:
            assert isinstance(item["coordinates"], dict)
            assert "grid_position" in item["coordinates"]
            gp = item["coordinates"]["grid_position"]
            assert isinstance(gp, list) and len(gp) == 2
            assert 0 <= gp[0] < 3 and 0 <= gp[1] < 3
            print(f"  ✓ Valid coordinates in {item['evidence_id']}: {item['coordinates']}")

    print(f"✓ Evidence Ledger: Successfully verified {len(evidence_items)} structured evidence items with unique IDs")

    # Map Retrieval
    maps = data["analysis_maps"]
    for map_key, map_path in maps.items():
        assert map_path.startswith("/maps/")
        map_res = client.get(map_path)
        assert map_res.status_code == 200, f"Map retrieval failed for {map_path}"
        assert map_res.headers["content-type"] == "image/png"
    print(f"✓ Successfully verified {len(maps)} analysis maps retrieved via GET /maps/...")

    # Verify exact schema ordering
    expected_keys = [
        "image_information",
        "spatial_features",
        "noise_analysis",
        "frequency_analysis",
        "srm_analysis",
        "wavelet_analysis",
        "compression_analysis",
        "recompression_ela_analysis",
        "ai_detection",
        "evidence",
        "analysis_maps",
    ]
    assert list(data.keys()) == expected_keys
    print("✓ Exact response key hierarchy and ordering verified:", list(data.keys()))


def test_jpeg_analysis():
    print("\n=== Testing POST /analyze with JPEG ===")
    jpeg_bytes = create_sample_jpeg()
    files = {"image": ("photo.jpg", jpeg_bytes, "image/jpeg")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200, f"JPEG analysis failed: {res.status_code} - {res.text}"
    data = res.json()

    info = data["image_information"]
    assert info["format"] == "JPEG"
    print("✓ JPEG Image Info:", info)

    comp = data["compression_analysis"]
    assert comp["status"] == "success"
    assert comp["has_quantization_tables"] is True
    assert comp["estimated_quality_factor"] is not None
    print(f"✓ JPEG Compression Analysis: Estimated Quality Factor = {comp['estimated_quality_factor']}")
    print(f"  Quantization Table Steps: Mean = {comp['quantization_info']['mean_luminance_step']}")
    print(f"  Blocking Artifact Factor = {comp['block_level_statistics']['blocking_artifact_factor']}")
    print(f"  Evaluated Blocks = {comp['block_level_statistics']['total_evaluated_blocks']}")

    ela = data["recompression_ela_analysis"]
    assert ela["status"] == "success"
    print(f"✓ ELA on JPEG: Avg Diff = {ela['average_difference']}, Max Diff = {ela['maximum_difference']}")

    # Verify Evidence in JPEG analysis
    assert "evidence" in data
    assert isinstance(data["evidence"], list)
    comp_ev = [e for e in data["evidence"] if e["category"] == "compression_analysis"]
    assert len(comp_ev) == 1
    assert comp_ev[0]["measurement"]["estimated_quality_factor"] is not None
    assert comp_ev[0]["measurement"]["block_level_statistics"]["blocking_artifact_factor"] is not None
    print(f"✓ JPEG Evidence Item: Q={comp_ev[0]['measurement']['estimated_quality_factor']}, BAF={comp_ev[0]['measurement']['block_level_statistics']['blocking_artifact_factor']}")


def test_error_handling():
    print("\n=== Testing Error Handling ===")

    # 1. Unsupported format (PDF)
    res_pdf = client.post(
        "/analyze",
        files={"image": ("document.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    )
    assert res_pdf.status_code == 400
    assert "unsupported format" in res_pdf.json()["detail"].lower()
    print("✓ Unsupported format (.pdf) rejected with 400:", res_pdf.json()["detail"])

    # 2. Corrupted image
    res_corrupt = client.post(
        "/analyze",
        files={"image": ("corrupted.png", b"\x89PNG\r\n\x1a\n\x00\x00corrupted_bytes", "image/png")}
    )
    assert res_corrupt.status_code == 400
    assert "corrupted" in res_corrupt.json()["detail"].lower()
    print("✓ Corrupted image rejected with 400:", res_corrupt.json()["detail"])

    # 3. Empty file
    res_empty = client.post(
        "/analyze",
        files={"image": ("empty.png", b"", "image/png")}
    )
    assert res_empty.status_code == 400
    print("✓ Empty file rejected with 400:", res_empty.json()["detail"])

    # 4. Map not found
    res_404 = client.get("/maps/non_existent_map_12345.png")
    assert res_404.status_code == 404
    print("✓ Non-existent map returned 404:", res_404.json()["detail"])


def test_detect_ai_image():
    print("\n=== Testing POST /detect-ai-image with Real Image ===")
    png_bytes = create_sample_png()
    files = {"image": ("test_art.png", png_bytes, "image/png")}
    res = client.post("/detect-ai-image", files=files)
    assert res.status_code == 200, f"AI detection failed: {res.status_code} - {res.text}"
    data = res.json()

    # Verify image info
    assert "image_information" in data
    assert data["image_information"]["format"] == "PNG"

    # Verify AI detection results
    assert "ai_detection" in data
    detection = data["ai_detection"]
    assert detection["model_name"] == "umm-maybe/AI-image-detector"
    assert detection["status"] in ["success", "unavailable"]

    if detection["status"] == "success":
        assert detection["prediction"] in ["artificial", "human"]
        assert isinstance(detection["model_score"], (int, float))
        assert 0.0 <= detection["model_score"] <= 1.0
        assert "confidence_scores" in detection
        assert "artificial" in detection["confidence_scores"]
        assert "human" in detection["confidence_scores"]
        assert "score_interpretation" in detection
        assert "known_limitations" in detection
        assert "forensic_notice" in detection
        print(f"✓ AI Detector Success: Prediction = {detection['prediction']}, Model Score (artificial) = {detection['model_score']}")
        print(f"  Confidence Scores: {detection['confidence_scores']}")
        print(f"  Forensic Notice: {detection['forensic_notice']}")
    else:
        print(f"✓ AI Detector Graceful Fallback: {detection['message']}")

    # Verify error rejection on corrupt image
    res_corrupt = client.post(
        "/detect-ai-image",
        files={"image": ("corrupted.png", b"\x89PNG\r\n\x1a\n\x00\x00bad", "image/png")}
    )
    assert res_corrupt.status_code == 400
    print("✓ Corrupt image correctly rejected with 400:", res_corrupt.json()["detail"])


def test_ai_detector_unavailable_handling():
    print("\n=== Testing AI Detector Unavailable Handling in POST /analyze ===")
    import services.ai_detector as ai_detector_module

    # Save original getter function
    original_getter = ai_detector_module.get_ai_detector

    try:
        # Simulate an environment where model cannot be loaded (e.g. offline or GPU OOM)
        ai_detector_module.get_ai_detector = lambda: (
            None,
            None,
            "Simulated offline HuggingFace or GPU memory exhaustion error",
        )

        png_bytes = create_sample_png()
        files = {"image": ("test_unavail.png", png_bytes, "image/png")}
        res = client.post("/analyze", files=files)
        assert res.status_code == 200, f"/analyze failed when AI detector is unavailable: {res.status_code}"
        data = res.json()

        # 1. Traditional forensic features MUST still work completely
        assert data["spatial_features"]["status"] == "success"
        assert data["noise_analysis"]["status"] == "success"
        assert data["frequency_analysis"]["status"] == "success"
        assert data["srm_analysis"]["status"] == "success"
        assert data["wavelet_analysis"]["status"] == "success"
        assert data["recompression_ela_analysis"]["status"] == "success"
        assert len(data["analysis_maps"]) > 0
        print("✓ All traditional forensic modules executed successfully despite AI detector being unavailable")

        # 2. AI detection section is included with honest 'unavailable' status
        ai_det = data["ai_detection"]
        assert ai_det["status"] == "unavailable"
        assert "Simulated offline HuggingFace" in ai_det["message"]
        print("✓ AI detection returned honest 'unavailable' status with explanation:", ai_det["message"])

        # 3. No fake prediction or invented score
        assert ai_det["prediction"] is None
        assert ai_det["model_score"] is None
        assert ai_det["confidence_scores"] is None
        print("✓ Verified no fake prediction or fake confidence score was generated")

        # 4. Integrity and schema order preserved
        expected_keys = [
            "image_information",
            "spatial_features",
            "noise_analysis",
            "frequency_analysis",
            "srm_analysis",
            "wavelet_analysis",
            "compression_analysis",
            "recompression_ela_analysis",
            "ai_detection",
            "evidence",
            "analysis_maps",
        ]
        assert list(data.keys()) == expected_keys
        print("✓ Response schema preserved during fallback")

        # 5. Evidence ledger verification under unavailable detector
        assert "evidence" in data
        ai_evs = [e for e in data["evidence"] if e["category"] == "ai_detection"]
        assert len(ai_evs) == 1
        ai_ev = ai_evs[0]
        assert "unavailable" in ai_ev["title"].lower() or "status" in ai_ev["title"].lower()
        assert ai_ev["measurement"]["prediction"] is None
        assert ai_ev["measurement"]["model_score"] is None
        assert ai_ev["measurement"]["confidence_scores"] is None
        assert "Simulated offline HuggingFace" in ai_ev["measurement"]["message"]
        assert ai_ev["strength"] == "informational"
        print("✓ Evidence ledger correctly records unavailable AI detector without fake values")

    finally:
        # Restore original getter function
        ai_detector_module.get_ai_detector = original_getter
        print("✓ Restored AI detector function")


def test_evidence_extraction_service():
    print("\n=== Testing Evidence Extraction Service Unit Logic ===")
    from services.evidence_service import extract_forensic_evidence

    # 1. Test with complete mock data
    mock_spatial = {
        "status": "success",
        "brightness": 128.4,
        "contrast": 34.2,
        "sharpness_laplacian_var": 450.5,
        "edge_density": 0.045,
        "image_entropy": 7.2,
    }
    mock_noise = {
        "status": "success",
        "noise_level": 4.52,
        "residual_energy": 20.4,
        "gaussian_blur": "5x5 kernel (sigma=1.0)",
    }
    mock_freq = {
        "status": "success",
        "fft_dimensions": [256, 256],
        "total_energy": 1.2e8,
        "low_frequency_energy": 1.0e8,
        "mid_frequency_energy": 1.5e7,
        "high_frequency_energy": 5.0e6,
        "low_frequency_ratio": 0.833,
        "mid_frequency_ratio": 0.125,
        "high_frequency_ratio": 0.042,
    }
    mock_srm = {
        "status": "success",
        "filter_count": 7,
        "average_residual_energy": 15.2,
        "max_residual_energy": 38.6,
        "filters": {"1st_order_horizontal": {"mean": 0.0, "residual_energy": 12.1}},
    }
    mock_wavelet = {
        "status": "success",
        "wavelet_family": "Haar (2D DWT Level 1)",
        "subband_dimensions": [128, 128],
        "ll_energy": 16000.0,
        "lh_energy": 45.2,
        "hl_energy": 32.1,
        "hh_energy": 12.4,
        "total_high_frequency_energy": 89.7,
        "energy_ratios": {"high_frequency_ratio": 0.0055},
    }
    mock_compression = {
        "status": "success",
        "format": "JPEG",
        "has_quantization_tables": True,
        "estimated_quality_factor": 85.0,
        "quantization_info": {"mean_luminance_step": 6.2},
        "block_level_statistics": {
            "blocking_artifact_factor": 1.15,
            "mean_boundary_difference": 3.2,
            "mean_internal_difference": 2.78,
            "block_variance_mean": 24.5,
            "block_variance_std": 12.1,
        },
    }
    mock_ela = {
        "status": "success",
        "recompression_quality": 90,
        "average_difference": 2.34,
        "maximum_difference": 18.0,
        "difference_std": 3.12,
        "regional_difference_information": {
            "grid_dimensions": [3, 3],
            "total_regions": 9,
            "regional_variance": 0.45,
            "highest_region_average": 3.8,
            "lowest_region_average": 1.2,
            "regional_contrast_range": 2.6,
            "regions": [
                {
                    "region_id": f"R{r+1}_{c+1}",
                    "grid_position": [r, c],
                    "mean_difference": 1.2 + (r * 0.5) + (c * 0.3),
                    "max_difference": 10.0 + r,
                    "std_difference": 1.5,
                }
                for r in range(3)
                for c in range(3)
            ],
        },
    }
    mock_ai_success = {
        "status": "success",
        "model_name": "umm-maybe/AI-image-detector",
        "model_architecture": "Swin Transformer for Image Classification",
        "prediction": "human",
        "model_score": 0.15,
        "confidence_scores": {"artificial": 0.15, "human": 0.85},
        "score_interpretation": {
            "artificial": "Synthetic indicator",
            "human": "Natural indicator",
        },
    }

    evidence = extract_forensic_evidence(
        spatial_features=mock_spatial,
        noise_analysis=mock_noise,
        frequency_analysis=mock_freq,
        srm_analysis=mock_srm,
        wavelet_analysis=mock_wavelet,
        compression_analysis=mock_compression,
        recompression_ela_analysis=mock_ela,
        ai_detection=mock_ai_success,
        analysis_maps={"edge_map": "/maps/edge.png"},
    )

    # 1. Evidence items generated
    assert len(evidence) >= 8, f"Expected at least 8 evidence items, got {len(evidence)}"

    # 2. Sequential unique IDs
    ids = [e["evidence_id"] for e in evidence]
    assert ids == [f"E{i:03d}" for i in range(1, len(evidence) + 1)]
    assert len(ids) == len(set(ids))

    # 3. All 8 module categories represented
    categories = {e["category"] for e in evidence}
    expected_categories = {
        "spatial_features",
        "noise_analysis",
        "frequency_analysis",
        "srm_analysis",
        "wavelet_analysis",
        "compression_analysis",
        "recompression_ela_analysis",
        "ai_detection",
    }
    assert expected_categories.issubset(categories)

    # 4. Check coordinates validity
    coord_items = [e for e in evidence if e["coordinates"] is not None]
    assert len(coord_items) > 0, "Expected at least one item with valid coordinates (regional ELA)"
    for item in coord_items:
        coords = item["coordinates"]
        assert isinstance(coords, dict)
        assert "grid_position" in coords
        assert "region_id" in coords
        r, c = coords["grid_position"]
        assert 0 <= r < 3 and 0 <= c < 3
        print(f"  ✓ Valid coordinates in {item['evidence_id']}: {coords}")

    # 5. Null coordinates for global measurements
    non_coord_items = [e for e in evidence if e["coordinates"] is None]
    assert len(non_coord_items) > 0

    # 6. Verify alternative explanations and limitations
    for item in evidence:
        assert isinstance(item["alternative_explanations"], list)
        assert len(item["alternative_explanations"]) > 0
        assert isinstance(item["limitations"], list)
        assert len(item["limitations"]) > 0
        assert item["strength"] == "informational"

    # 7. Test AI unavailable fallback in evidence service
    mock_ai_unavail = {
        "status": "unavailable",
        "message": "Model weights not downloaded",
        "model_name": "umm-maybe/AI-image-detector",
        "model_architecture": "Swin Transformer",
        "prediction": None,
        "model_score": None,
        "confidence_scores": None,
    }
    evidence_unavail = extract_forensic_evidence(
        ai_detection=mock_ai_unavail
    )
    assert len(evidence_unavail) == 1
    unavail_item = evidence_unavail[0]
    assert unavail_item["category"] == "ai_detection"
    assert "unavailable" in unavail_item["title"].lower()
    assert unavail_item["measurement"]["prediction"] is None
    assert unavail_item["measurement"]["model_score"] is None
    assert "Model weights not downloaded" in unavail_item["observation"]
    print("✓ Evidence Service Unit Logic: All constraints validated successfully!")


def test_four_agent_debate_workflow():
    print("\n=== Testing LangGraph 4-Agent Forensic Debate Workflow ===")
    from agents.debate_graph import run_forensic_debate
    from services.evidence_service import extract_forensic_evidence

    # Run actual analysis on JPEG to get genuine evidence
    jpeg_bytes = create_sample_jpeg()
    files = {"image": ("test_debate.jpg", jpeg_bytes, "image/jpeg")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    analysis_data = res.json()
    evidence = analysis_data["evidence"]
    assert len(evidence) >= 7

    # Run LangGraph debate
    debate = run_forensic_debate(analysis_data, evidence, image_id="test_debate.jpg")

    # 1. Verification of Debate Completion and Turns
    assert debate["status"] == "completed"
    assert debate["can_proceed"] is True
    assert debate["debate_completed"] is True
    assert debate["completed_iterations"] == 4
    assert debate["total_messages"] == 8

    # 2. Verify Alternating 4-Agent Debate Sequence: P1, D1, P2, D2, P3, D3, P4, D4
    messages = debate["debate_messages"]
    expected_sequence = [
        ("prosecutor", 1),
        ("defence", 1),
        ("prosecutor", 2),
        ("defence", 2),
        ("prosecutor", 3),
        ("defence", 3),
        ("prosecutor", 4),
        ("defence", 4),
    ]
    for idx, (expected_agent, expected_turn) in enumerate(expected_sequence):
        msg = messages[idx]
        assert msg["agent"] == expected_agent, f"Turn {idx}: expected {expected_agent}, got {msg['agent']}"
        assert msg["turn"] == expected_turn, f"Turn {idx}: expected turn {expected_turn}, got {msg['turn']}"
        assert len(msg["argument"]) > 30
        assert isinstance(msg["supporting_evidence_ids"], list)
        assert len(msg["supporting_evidence_ids"]) > 0
        assert isinstance(msg["uncertainties"], list) and len(msg["uncertainties"]) > 0
        assert isinstance(msg["alternative_explanations"], list) and len(msg["alternative_explanations"]) > 0
        print(f"  ✓ Validated Message {idx+1}: {msg['agent'].upper()} Point {msg['turn']} citing {msg['supporting_evidence_ids']}")

    # 3. Verify Expert Agent Report
    expert = debate["expert_report"]
    assert expert is not None
    assert expert["status"] == "verified"
    assert expert["evidence_sufficient"] is True
    assert expert["recommendation"] == "proceed_to_judge"
    assert len(expert["hallucination_flags"]) == 0, f"Unexpected hallucinations: {expert['hallucination_flags']}"
    assert len(expert["verified_claims"]) >= 8
    print("  ✓ Expert Agent Report: Verified with 0 hallucinations. Recommendation:", expert["recommendation"])

    # 4. Verify Judge Agent Assessment
    judge = debate["judge_result"]
    assert judge is not None
    assert judge["status"] == "completed"
    assert judge["assessment"] in ["REAL", "FAKE", "UNCERTAIN"]
    assert len(judge["reasoning"]) > 50
    assert isinstance(judge["supporting_evidence_ids"], list)
    assert isinstance(judge["contradictory_evidence_ids"], list)
    assert len(judge["limitations"]) > 0
    assert len(judge["expert_verification_summary"]) > 0
    print("  ✓ Judge Agent Assessment:", judge["assessment"])
    print("    Judge Reasoning:", judge["reasoning"][:120], "...")


def test_insufficient_evidence_early_stopping():
    print("\n=== Testing Early Stopping on Insufficient Evidence ===")
    from agents.debate_graph import run_forensic_debate

    # Test with empty evidence ledger
    debate = run_forensic_debate({}, [], image_id="empty_image.jpg")
    assert debate["status"] == "insufficient_evidence"
    assert debate["can_proceed"] is False
    assert debate["debate_completed"] is False
    assert debate["message"] == "I cannot proceed with the investigation because the available forensic evidence is insufficient."
    assert debate["completed_iterations"] == 0
    assert debate["expert_report"] is None
    assert debate["judge_result"] is None
    print("  ✓ Empty Evidence Ledger correctly halted with zero agent executions.")

    # Test with only 1 evidence item (below threshold of 3)
    minimal_evidence = [{
        "evidence_id": "E001",
        "category": "noise_analysis",
        "title": "Minimal Noise",
        "observation": "Single measurement",
        "measurement": {"noise_level": 1.2},
        "source_module": "noise_analysis",
        "coordinates": None,
        "alternative_explanations": ["None"],
        "limitations": ["None"],
        "strength": "informational"
    }]
    debate_min = run_forensic_debate({}, minimal_evidence, image_id="minimal_image.jpg")
    assert debate_min["status"] == "insufficient_evidence"
    assert debate_min["can_proceed"] is False
    assert debate_min["debate_completed"] is False
    assert debate_min["expert_report"] is None
    assert debate_min["judge_result"] is None
    print("  ✓ Sub-threshold Evidence Ledger correctly triggered early stopping.")


def test_expert_hallucination_protection():
    print("\n=== Testing Expert Agent Anti-Hallucination Guardrail ===")
    from agents.expert_agent import run_expert_verification
    from agents.state import ForensicDebateState

    valid_evidence = [
        {"evidence_id": "E001", "category": "noise_analysis", "title": "Noise Analysis", "measurement": {}},
        {"evidence_id": "E002", "category": "spatial_features", "title": "Spatial Features", "measurement": {}},
        {"evidence_id": "E003", "category": "frequency_analysis", "title": "Frequency Analysis", "measurement": {}},
    ]

    # Inject a hallucinated evidence ID ("E999") that does not exist in the ledger
    state_with_hallucination: ForensicDebateState = {
        "image_id": "hallucination_test",
        "analysis_result": {},
        "evidence": valid_evidence,
        "prosecutor_turns": [],
        "defence_turns": [],
        "debate_messages": [
            {
                "agent": "prosecutor",
                "turn": 1,
                "argument": "Based on fabricated evidence item E999, the image is fake.",
                "supporting_evidence_ids": ["E999"],
                "uncertainties": [],
                "alternative_explanations": [],
            }
        ],
        "current_iteration": 1,
        "evidence_sufficiency": {"can_proceed": True},
        "stopping_reason": None,
        "expert_report": None,
        "judge_result": None,
        "processing_errors": [],
    }

    report = run_expert_verification(state_with_hallucination)
    assert report["status"] == "verification_failed"
    assert report["evidence_sufficient"] is False
    assert report["recommendation"] == "stop"
    assert len(report["hallucination_flags"]) == 1
    flag = report["hallucination_flags"][0]
    assert flag["evidence_id"] == "E999"
    assert flag["type"] == "fabricated_evidence_id"
    print("  ✓ Expert correctly intercepted fabricated evidence ID 'E999' and issued 'stop' recommendation!")


def test_debate_api_endpoints():
    print("\n=== Testing POST /debate and POST /debate-evidence API Endpoints ===")
    jpeg_bytes = create_sample_jpeg()
    
    # 1. POST /debate with uploaded image
    files = {"image": ("test_api_debate.jpg", jpeg_bytes, "image/jpeg")}
    res = client.post("/debate", files=files)
    assert res.status_code == 200, f"/debate failed: {res.text}"
    data = res.json()
    assert "image_information" in data
    assert "evidence_summary" in data
    assert "debate" in data
    debate = data["debate"]
    assert debate["status"] == "completed"
    assert debate["completed_iterations"] == 4
    assert len(debate["debate_messages"]) == 8
    assert debate["expert_report"]["recommendation"] == "proceed_to_judge"
    assert debate["judge_result"]["assessment"] in ["REAL", "FAKE", "UNCERTAIN"]
    print("  ✓ POST /debate succeeded with full 4-agent LangGraph execution!")

    # 2. POST /debate-evidence with precomputed JSON payload
    analyze_res = client.post("/analyze", files={"image": ("test_precomputed.jpg", jpeg_bytes, "image/jpeg")})
    assert analyze_res.status_code == 200
    analysis_json = analyze_res.json()

    evidence_res = client.post(
        "/debate-evidence",
        json={
            "analysis_result": analysis_json,
            "evidence": analysis_json["evidence"],
            "image_id": "test_precomputed.jpg",
        },
    )
    assert evidence_res.status_code == 200
    ev_data = evidence_res.json()
    assert ev_data["debate"]["status"] == "completed"
    assert len(ev_data["debate"]["debate_messages"]) == 8
    print("  ✓ POST /debate-evidence succeeded with precomputed evidence ledger!")


if __name__ == "__main__":
    test_health()
    test_png_analysis()
    test_jpeg_analysis()
    test_error_handling()
    test_detect_ai_image()
    test_ai_detector_unavailable_handling()
    test_evidence_extraction_service()
    test_four_agent_debate_workflow()
    test_insufficient_evidence_early_stopping()
    test_expert_hallucination_protection()
    test_debate_api_endpoints()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY ON 4-AGENT LANGGRAPH FORENSIC DEBATE SYSTEM!")
