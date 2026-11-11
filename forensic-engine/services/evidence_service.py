
"""
ForenXAI Evidence Extraction Service

Transforms empirical calculations from all forensic modules and AI detection
into a structured, transparent, and traceable evidence ledger.

Principles:
- Strict empirical grounding: Uses only calculated values from the analysis response.
- No arbitrary verdicts: Never labels an image as REAL, FAKE, HUMAN, or AI-GENERATED.
- No synthetic numbers: If a detector/tool is unavailable, states it honestly.
- Confounding awareness: Supplies plausible alternative explanations.
- Documented limitations: Explains forensic boundaries and constraints.
"""

from typing import Dict, Any, List, Optional


def extract_forensic_evidence(
    analysis_data: Optional[Dict[str, Any]] = None,
    *,
    spatial_features: Optional[Dict[str, Any]] = None,
    noise_analysis: Optional[Dict[str, Any]] = None,
    frequency_analysis: Optional[Dict[str, Any]] = None,
    srm_analysis: Optional[Dict[str, Any]] = None,
    wavelet_analysis: Optional[Dict[str, Any]] = None,
    compression_analysis: Optional[Dict[str, Any]] = None,
    recompression_ela_analysis: Optional[Dict[str, Any]] = None,
    ai_detection: Optional[Dict[str, Any]] = None,
    analysis_maps: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Constructs an ordered list of structured forensic evidence items.

    Accepts either a consolidated analysis_data dictionary or individual
    analysis section keyword arguments.
    """

    # Unpack consolidated analysis data when provided.
    if analysis_data is not None:
        spatial_features = spatial_features or analysis_data.get("spatial_features")
        noise_analysis = noise_analysis or analysis_data.get("noise_analysis")
        frequency_analysis = frequency_analysis or analysis_data.get("frequency_analysis")
        srm_analysis = srm_analysis or analysis_data.get("srm_analysis")
        wavelet_analysis = wavelet_analysis or analysis_data.get("wavelet_analysis")
        compression_analysis = compression_analysis or analysis_data.get("compression_analysis")
        recompression_ela_analysis = (
            recompression_ela_analysis
            or analysis_data.get("recompression_ela_analysis")
        )
        ai_detection = ai_detection or analysis_data.get("ai_detection")
        analysis_maps = analysis_maps or analysis_data.get("analysis_maps", {})

    analysis_maps = analysis_maps or {}
    evidence_list: List[Dict[str, Any]] = []
    counter = 1

    def next_id() -> str:
        nonlocal counter
        evidence_id = f"E{counter:03d}"
        counter += 1
        return evidence_id

    # -------------------------------------------------------------------------
    # 1. Spatial Features Evidence
    # -------------------------------------------------------------------------
    if spatial_features and spatial_features.get("status") == "success":
        brightness = spatial_features.get("brightness")
        contrast = spatial_features.get("contrast")
        sharpness = spatial_features.get("sharpness_laplacian_var")
        edge_density = spatial_features.get("edge_density")
        entropy = spatial_features.get("image_entropy")

        observation = (
            f"Measured luminance average of {brightness}, standard deviation "
            f"contrast of {contrast}, Laplacian sharpness variance of {sharpness}, "
            f"Canny edge density of {edge_density}, and Shannon entropy of "
            f"{entropy} bits."
        )

        measurement = {
            "brightness": brightness,
            "contrast": contrast,
            "sharpness_laplacian_var": sharpness,
            "edge_density": edge_density,
            "image_entropy": entropy,
        }

        if "edge_map" in analysis_maps:
            measurement["edge_map"] = analysis_maps["edge_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "spatial_features",
            "title": "Spatial Intensity, Contrast, and Edge Metrics",
            "observation": observation,
            "measurement": measurement,
            "source_module": "spatial_features",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "Elevated sharpness and edge density can result from optical focus, "
                "lens characteristics, natural texture complexity, or sharpening.",
                "Low entropy and contrast can occur in scenes with flat lighting, "
                "minimal texture, or solid backgrounds.",
            ],
            "limitations": [
                "Global spatial statistics characterize scene composition and "
                "optical conditions rather than authenticating image origin.",
                "These statistics do not independently localize copy-move or "
                "inpainting manipulations.",
            ],
        })

    # -------------------------------------------------------------------------
    # 2. Noise Residual Analysis Evidence
    # -------------------------------------------------------------------------
    if noise_analysis and noise_analysis.get("status") == "success":
        noise_level = noise_analysis.get("noise_level")
        residual_energy = noise_analysis.get("residual_energy")
        blur_kernel = noise_analysis.get(
            "gaussian_blur", "5x5 kernel (sigma=1.0)"
        )

        observation = (
            f"Spatial noise residual extracted via Gaussian smoothing "
            f"({blur_kernel}) exhibits a noise standard deviation of "
            f"{noise_level} and mean squared residual energy of {residual_energy}."
        )

        measurement = {
            "noise_level": noise_level,
            "residual_energy": residual_energy,
            "gaussian_blur": blur_kernel,
        }

        if "noise_map" in analysis_maps:
            measurement["noise_map"] = analysis_maps["noise_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "noise_analysis",
            "title": "High-Pass Spatial Noise Residual",
            "observation": observation,
            "measurement": measurement,
            "source_module": "noise_analysis",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "Noise variations are influenced by camera ISO, sensor noise, "
                "compression smoothing, and artificial grain overlays.",
                "Denoising algorithms and synthetic-image smoothing can reduce "
                "high-pass residual energy.",
            ],
            "limitations": [
                "Gaussian-blur residual is an approximate noise estimate and "
                "does not model camera-specific PRNU sensor patterns.",
                "Fine image textures can affect the estimated noise residual.",
            ],
        })

    # -------------------------------------------------------------------------
    # 3. Frequency Analysis Evidence (2D FFT)
    # -------------------------------------------------------------------------
    if frequency_analysis and frequency_analysis.get("status") == "success":
        low_ratio = frequency_analysis.get("low_frequency_ratio", 0.0)
        mid_ratio = frequency_analysis.get("mid_frequency_ratio", 0.0)
        high_ratio = frequency_analysis.get("high_frequency_ratio", 0.0)
        total_energy = frequency_analysis.get("total_energy")

        observation = (
            "2D Fourier transform power spectrum shows radial energy distribution: "
            f"{low_ratio * 100:.2f}% low-frequency energy, "
            f"{mid_ratio * 100:.2f}% mid-frequency energy, and "
            f"{high_ratio * 100:.2f}% high-frequency energy. "
            f"Total spectral energy: {total_energy}."
        )

        measurement = {
            "fft_dimensions": frequency_analysis.get("fft_dimensions"),
            "total_energy": total_energy,
            "low_frequency_energy": frequency_analysis.get("low_frequency_energy"),
            "mid_frequency_energy": frequency_analysis.get("mid_frequency_energy"),
            "high_frequency_energy": frequency_analysis.get("high_frequency_energy"),
            "low_frequency_ratio": low_ratio,
            "mid_frequency_ratio": mid_ratio,
            "high_frequency_ratio": high_ratio,
        }

        if "frequency_map" in analysis_maps:
            measurement["frequency_map"] = analysis_maps["frequency_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "frequency_analysis",
            "title": "2D Fourier Transform Radial Energy Distribution",
            "observation": observation,
            "measurement": measurement,
            "source_module": "frequency_analysis",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "High-frequency energy can arise from sharp edges, repetitive "
                "textures, or detailed subject matter.",
                "Low-frequency dominance can occur in smooth backgrounds, "
                "shallow depth-of-field photographs, or atmospheric haze.",
                "Lossy compression can discard high-frequency coefficients.",
            ],
            "limitations": [
                "Radial frequency partitioning characterizes global energy "
                "distribution but does not localize spectral anomalies.",
                "Spectral profiles depend on compression, optics, and image content.",
            ],
        })

    # -------------------------------------------------------------------------
    # 4. SRM Residual Analysis Evidence
    # -------------------------------------------------------------------------
    if srm_analysis and srm_analysis.get("status") == "success":
        filter_count = srm_analysis.get("filter_count", 0)
        average_energy = srm_analysis.get("average_residual_energy")
        maximum_energy = srm_analysis.get("max_residual_energy")

        observation = (
            f"Application of {filter_count} Spatial Rich Model (SRM) high-pass "
            f"filters yielded average residual energy of {average_energy} and "
            f"maximum residual energy of {maximum_energy}."
        )

        measurement = {
            "filter_count": filter_count,
            "average_residual_energy": average_energy,
            "max_residual_energy": maximum_energy,
            "filters": srm_analysis.get("filters"),
        }

        if "srm_map" in analysis_maps:
            measurement["srm_map"] = analysis_maps["srm_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "srm_analysis",
            "title": "Spatial Rich Model (SRM) High-Pass Residual Energies",
            "observation": observation,
            "measurement": measurement,
            "source_module": "srm_analysis",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "High residual energy can correspond to authentic fine textures "
                "such as foliage, hair, or fabric.",
                "Reduced residual energy can result from smoothing, downsampling, "
                "or synthetic-image generation.",
            ],
            "limitations": [
                "SRM residuals reveal high-pass pixel-correlation characteristics "
                "but do not independently identify a specific manipulation.",
                "Image boundaries can introduce minor residual variations.",
            ],
        })

    # -------------------------------------------------------------------------
    # 5. Wavelet Analysis Evidence (Haar 2D DWT)
    # -------------------------------------------------------------------------
    if wavelet_analysis and wavelet_analysis.get("status") == "success":
        ll_energy = wavelet_analysis.get("ll_energy")
        lh_energy = wavelet_analysis.get("lh_energy")
        hl_energy = wavelet_analysis.get("hl_energy")
        hh_energy = wavelet_analysis.get("hh_energy")

        energy_ratios = wavelet_analysis.get("energy_ratios", {})
        if not isinstance(energy_ratios, dict):
            energy_ratios = {}

        high_frequency_ratio = energy_ratios.get("high_frequency_ratio")

        observation = (
            f"Level-1 Haar 2D discrete wavelet decomposition produced LL energy "
            f"{ll_energy}, LH energy {lh_energy}, HL energy {hl_energy}, "
            f"and HH energy {hh_energy}; high-frequency energy ratio: "
            f"{high_frequency_ratio}."
        )

        measurement = {
            "wavelet_family": wavelet_analysis.get("wavelet_family"),
            "subband_dimensions": wavelet_analysis.get("subband_dimensions"),
            "ll_energy": ll_energy,
            "lh_energy": lh_energy,
            "hl_energy": hl_energy,
            "hh_energy": hh_energy,
            "total_high_frequency_energy": wavelet_analysis.get(
                "total_high_frequency_energy"
            ),
            "energy_ratios": energy_ratios,
        }

        if "wavelet_map" in analysis_maps:
            measurement["wavelet_map"] = analysis_maps["wavelet_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "wavelet_analysis",
            "title": "Haar Discrete Wavelet Transform (2D DWT) Subband Decomposition",
            "observation": observation,
            "measurement": measurement,
            "source_module": "wavelet_analysis",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "Differences between directional subbands can reflect scene "
                "orientations such as horizons, buildings, or pillars.",
                "Downsampling and interpolation can attenuate high-frequency "
                "wavelet coefficients.",
            ],
            "limitations": [
                "Level-1 Haar decomposition is a single-scale analysis.",
                "Subband ratios vary with subject matter, lighting, and image processing.",
            ],
        })

    # -------------------------------------------------------------------------
    # 6. JPEG Compression Analysis Evidence
    # -------------------------------------------------------------------------
    if compression_analysis:
        compression_status = compression_analysis.get("status")

        if compression_status == "success":
            quality_factor = compression_analysis.get("estimated_quality_factor")
            block_stats = compression_analysis.get("block_level_statistics", {})

            if not isinstance(block_stats, dict):
                block_stats = {}

            blocking_factor = block_stats.get("blocking_artifact_factor")
            boundary_difference = block_stats.get("mean_boundary_difference")
            internal_difference = block_stats.get("mean_internal_difference")
            variance_mean = block_stats.get("block_variance_mean")
            variance_std = block_stats.get("block_variance_std")

            observation = (
                f"JPEG analysis estimated quality factor {quality_factor}. "
                f"8x8 DCT grid analysis yielded Blocking Artifact Factor "
                f"{blocking_factor}, boundary difference {boundary_difference}, "
                f"internal difference {internal_difference}, block variance "
                f"mean {variance_mean}, and standard deviation {variance_std}."
            )

            evidence_list.append({
                "evidence_id": next_id(),
                "category": "compression_analysis",
                "title": "JPEG Quantization and 8x8 DCT Grid Boundary Consistency",
                "observation": observation,
                "measurement": {
                    "format": compression_analysis.get("format"),
                    "has_quantization_tables": compression_analysis.get(
                        "has_quantization_tables"
                    ),
                    "estimated_quality_factor": quality_factor,
                    "quantization_info": compression_analysis.get(
                        "quantization_info"
                    ),
                    "block_level_statistics": block_stats,
                },
                "source_module": "compression_analysis",
                "coordinates": None,
                "strength": "informational",
                "alternative_explanations": [
                    "Blocking artifacts naturally increase with lower-quality "
                    "JPEG encoding and do not independently indicate tampering.",
                    "Block variance can differ between smooth and textured regions.",
                ],
                "limitations": [
                    "Cropping or resizing can shift DCT boundaries and mask "
                    "standard blocking artifacts.",
                    "Re-encoding and social-media processing can alter quantization tables.",
                ],
            })

        elif compression_status in ("unavailable", "partial"):
            message = compression_analysis.get(
                "message",
                "JPEG compression analysis is unavailable for this image format or metadata.",
            )

            evidence_list.append({
                "evidence_id": next_id(),
                "category": "compression_analysis",
                "title": "JPEG Compression Analysis Status",
                "observation": message,
                "measurement": {
                    "status": compression_status,
                    "message": message,
                    "estimated_quality_factor": compression_analysis.get(
                        "estimated_quality_factor"
                    ),
                },
                "source_module": "compression_analysis",
                "coordinates": None,
                "strength": "informational",
                "alternative_explanations": [
                    "The image may be non-JPEG, or JPEG quantization metadata "
                    "may have been stripped during export.",
                ],
                "limitations": [
                    "DCT grid and quantization-table analysis requires applicable "
                    "JPEG compression information.",
                ],
            })

    # -------------------------------------------------------------------------
    # 7. Error Level Analysis (ELA) Recompression Evidence
    # -------------------------------------------------------------------------
    if (
        recompression_ela_analysis
        and recompression_ela_analysis.get("status") == "success"
    ):
        average_difference = recompression_ela_analysis.get("average_difference")
        maximum_difference = recompression_ela_analysis.get("maximum_difference")
        difference_std = recompression_ela_analysis.get("difference_std")
        recompression_quality = recompression_ela_analysis.get(
            "recompression_quality", 90
        )

        regional_info = recompression_ela_analysis.get(
            "regional_difference_information", {}
        )

        if not isinstance(regional_info, dict):
            regional_info = {}

        observation = (
            f"In-memory JPEG recompression at quality {recompression_quality} "
            f"produced global average pixel difference {average_difference}, "
            f"maximum difference {maximum_difference}, and difference "
            f"standard deviation {difference_std}."
        )

        global_measurement = {
            "recompression_quality": recompression_quality,
            "average_difference": average_difference,
            "maximum_difference": maximum_difference,
            "difference_std": difference_std,
            "regional_variance": regional_info.get("regional_variance"),
            "highest_region_average": regional_info.get("highest_region_average"),
            "lowest_region_average": regional_info.get("lowest_region_average"),
            "regional_contrast_range": regional_info.get("regional_contrast_range"),
        }

        if "ela_recompression_map" in analysis_maps:
            global_measurement["ela_map"] = analysis_maps["ela_recompression_map"]

        evidence_list.append({
            "evidence_id": next_id(),
            "category": "recompression_ela_analysis",
            "title": "Error Level Analysis (ELA) Global Recompression Error",
            "observation": observation,
            "measurement": global_measurement,
            "source_module": "recompression_ela_analysis",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "High-contrast edges, fine textures, and saturated colors can "
                "produce higher recompression error.",
                "Uniform recompression errors can occur in untouched photographs "
                "and generated images alike.",
            ],
            "limitations": [
                "ELA sensitivity depends on the relationship between original "
                "compression quality and recompression quality.",
                "Color-space conversion and chroma subsampling can introduce "
                "baseline recompression differences.",
            ],
        })

        # Regional discrepancy evidence, when available.
        regions = regional_info.get("regions", [])

        if isinstance(regions, list) and regions:
            valid_regions = [
                region for region in regions
                if isinstance(region, dict)
            ]

            if valid_regions:
                highest_region = max(
                    valid_regions,
                    key=lambda region: region.get("mean_difference") or 0.0,
                )

                region_id = highest_region.get("region_id", "Unknown")
                region_mean = highest_region.get("mean_difference", 0.0)
                region_max = highest_region.get("max_difference", 0.0)
                grid_position = highest_region.get("grid_position", [0, 0])
                contrast_range = regional_info.get("regional_contrast_range", 0.0)

                regional_observation = (
                    f"Spatial 3x3 grid analysis identified peak recompression "
                    f"difference in region {region_id} (grid {grid_position}), "
                    f"with mean difference {region_mean} and maximum difference "
                    f"{region_max}. Regional low: "
                    f"{regional_info.get('lowest_region_average')}; contrast "
                    f"range: {contrast_range}."
                )

                evidence_list.append({
                    "evidence_id": next_id(),
                    "category": "recompression_ela_analysis",
                    "title": f"Regional ELA Discrepancy (Grid Region {region_id})",
                    "observation": regional_observation,
                    "measurement": {
                        "region_id": region_id,
                        "grid_position": grid_position,
                        "mean_difference": region_mean,
                        "max_difference": region_max,
                        "std_difference": highest_region.get("std_difference"),
                        "regional_contrast_range": contrast_range,
                        "regional_variance": regional_info.get("regional_variance"),
                    },
                    "source_module": "recompression_ela_analysis",
                    "coordinates": {
                        "grid_position": grid_position,
                        "region_id": region_id,
                    },
                    "strength": "informational",
                    "alternative_explanations": [
                        "Regional difference variations can reflect scene-content "
                        "heterogeneity, such as textured subjects and plain backgrounds.",
                        "Localized error differences do not by themselves establish "
                        "digital splicing or localized editing.",
                    ],
                    "limitations": [
                        "A 3x3 grid provides coarse spatial localization and does "
                        "not segment semantic object boundaries.",
                    ],
                })

    # -------------------------------------------------------------------------
    # 8. Pretrained Swin AI-Generated Image Detection Evidence
    # -------------------------------------------------------------------------
    if ai_detection:
        ai_status = ai_detection.get("status")
        model_name = ai_detection.get(
            "model_name", "umm-maybe/AI-image-detector"
        )
        model_architecture = ai_detection.get(
            "model_architecture",
            "Swin Transformer for Image Classification",
        )

        if ai_status == "success":
            prediction = ai_detection.get("prediction")
            model_score = ai_detection.get("model_score")
            confidence_scores = ai_detection.get("confidence_scores", {})

            if not isinstance(confidence_scores, dict):
                confidence_scores = {}

            artificial_confidence = confidence_scores.get("artificial")
            human_confidence = confidence_scores.get("human")

            observation = (
                f"Swin Transformer model '{model_name}' evaluated image visual "
                f"features and returned prediction '{prediction}', with artificial "
                f"confidence {artificial_confidence}, human confidence "
                f"{human_confidence}, and reported model score {model_score}."
            )

            evidence_list.append({
                "evidence_id": next_id(),
                "category": "ai_detection",
                "title": "Pretrained Swin Transformer AI-Generation Indicator",
                "observation": observation,
                "measurement": {
                    "model_name": model_name,
                    "model_architecture": model_architecture,
                    "prediction": prediction,
                    "model_score": model_score,
                    "confidence_scores": confidence_scores,
                    "score_interpretation": ai_detection.get(
                        "score_interpretation"
                    ),
                },
                "source_module": "ai_detection",
                "coordinates": None,
                "strength": "informational",
                "alternative_explanations": [
                    "Visual styles, heavy compression, or post-processing can "
                    "affect model outputs.",
                    "Generators not represented in the training data may produce "
                    "different detection performance.",
                ],
                "limitations": ai_detection.get("limitations", [
                    "The model's performance depends on its training data.",
                    "This is a probabilistic indicator, not a definitive verdict.",
                    "Compression, resizing, and image noise may affect the output.",
                ]),
            })

        elif ai_status in ("unavailable", "error"):
            error_message = ai_detection.get(
                "message", "AI image detector model is currently unavailable."
            )

            evidence_list.append({
                "evidence_id": next_id(),
                "category": "ai_detection",
                "title": "Pretrained AI Detection Model Status",
                "observation": (
                    f"AI detector '{model_name}' is unavailable: {error_message}. "
                    "No probabilistic prediction was generated by this detector."
                ),
                "measurement": {
                    "status": ai_status,
                    "model_name": model_name,
                    "model_architecture": model_architecture,
                    "message": error_message,
                    "prediction": None,
                    "model_score": None,
                    "confidence_scores": None,
                },
                "source_module": "ai_detection",
                "coordinates": None,
                "strength": "informational",
                "alternative_explanations": [
                    "The model may be offline, dependencies may be unavailable, "
                    "or computational resources may be constrained."
                ],
                "limitations": [
                    "This detector did not produce a prediction. Other available "
                    "forensic measurements must not be represented as its output."
                ],
            })

    # -------------------------------------------------------------------------
    # 9. Local CNN Model Evidence
    # -------------------------------------------------------------------------
    # Expected schema:
    # ai_detection["local_model_scores"] = {
    #     "genimage_ai_probability": <actual probability or score>,
    #     "casia_tamper_probability": <actual probability or score>,
    # }
    #
    # These entries record existing outputs; they do not perform inference.
    local_model_scores = {}

    if isinstance(ai_detection, dict):
        local_model_scores = ai_detection.get("local_model_scores", {}) or {}

    if not isinstance(local_model_scores, dict):
        local_model_scores = {}

    # TinyGenImage CNN: AI-generation indicator.
    genimage_probability = local_model_scores.get("genimage_ai_probability")

    if genimage_probability is not None:
        evidence_list.append({
            "evidence_id": next_id(),
            "category": "ai_detection",
            "title": "Local TinyGenImage CNN AI-Generation Indicator",
            "observation": (
                "The local TinyGenImage CNN returned a reported AI-generation "
                f"score of {genimage_probability}. This is a model output, "
                "not a definitive determination of image origin."
            ),
            "measurement": {
                "model_name": "forensic_cnn_tinygenimage_best.pth",
                "model_architecture": "ForensicCNN",
                "ai_generation_probability": genimage_probability,
                "score_interpretation": (
                    "Interpret as an AI-generation probability only after verifying "
                    "the positive-class mapping and probability calibration."
                ),
            },
            "source_module": "ai_detection",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "Unseen image generators, compression, resizing, post-processing, "
                "and differences from the training data may affect the output."
            ],
            "limitations": [
                "The output does not conclusively prove AI generation.",
                "The model's class mapping must be verified before interpreting "
                "the score as an AI-generation probability.",
                "A sigmoid output is not necessarily a calibrated confidence score.",
            ],
        })

    # CASIA CNN: tampering indicator, kept separate from AI generation.
    casia_probability = local_model_scores.get("casia_tamper_probability")

    if casia_probability is not None:
        evidence_list.append({
            "evidence_id": next_id(),
            "category": "tampering_detection",
            "title": "Local CASIA CNN Tampering Indicator",
            "observation": (
                "The local CASIA CNN returned a reported tampering score of "
                f"{casia_probability}. This concerns the model's tampering task "
                "and is not an AI-generation probability."
            ),
            "measurement": {
                "model_name": "forensic_cnn_casia_tamper_best.pth",
                "model_architecture": "ForensicCNN",
                "tampering_probability": casia_probability,
                "score_interpretation": (
                    "Interpret as a tampering probability only after verifying "
                    "the positive-class mapping and probability calibration."
                ),
            },
            "source_module": "ai_detection",
            "coordinates": None,
            "strength": "informational",
            "alternative_explanations": [
                "Benign editing, compression, resizing, image content, or "
                "differences from the training dataset may affect the output."
            ],
            "limitations": [
                "A high score does not independently prove image manipulation.",
                "The score must not be treated as an AI-generation probability.",
                "The model's positive-class mapping must be verified.",
                "A sigmoid output is not necessarily a calibrated probability.",
            ],
        })

    return evidence_list
