from typing import Dict, Any, List
from agents.state import ForensicDebateState, DebateMessage


def find_evidence_by_category(evidence: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """Helper to locate all evidence items matching a category."""
    return [e for e in evidence if e.get("category") == category]


def find_evidence_by_categories(evidence: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
    """Helper to locate all evidence items matching any of the specified categories."""
    return [e for e in evidence if e.get("category") in categories]


def run_prosecutor_turn(state: ForensicDebateState, turn: int) -> DebateMessage:
    """
    Executes a single turn for the Prosecutor Agent.
    Strictly derives all observations from existing evidence in the ledger.
    Never fabricates measurements or evidence IDs.
    """
    evidence = state.get("evidence", [])
    debate_messages = state.get("debate_messages", [])

    if turn == 1:
        # Turn 1: Spatial & Noise Residual Analysis
        target_items = find_evidence_by_categories(evidence, ["spatial_features", "noise_analysis"])
        supporting_ids = [e["evidence_id"] for e in target_items]
        
        noise_item = next((e for e in target_items if e["category"] == "noise_analysis"), None)
        spatial_item = next((e for e in target_items if e["category"] == "spatial_features"), None)
        
        obs_lines = []
        if noise_item:
            m = noise_item.get("measurement", {})
            nl = m.get("noise_level", "N/A")
            re = m.get("residual_energy", "N/A")
            obs_lines.append(
                f"Under evidence item {noise_item['evidence_id']} (Noise Analysis), "
                f"the spatial high-pass noise residual exhibits a noise level standard deviation of {nl} "
                f"and mean squared residual energy of {re}."
            )
        if spatial_item:
            m = spatial_item.get("measurement", {})
            sh = m.get("sharpness_laplacian_var", "N/A")
            ent = m.get("image_entropy", "N/A")
            ed = m.get("edge_density", "N/A")
            obs_lines.append(
                f"Under evidence item {spatial_item['evidence_id']} (Spatial Features), "
                f"Laplacian sharpness variance is measured at {sh} with edge density {ed} "
                f"and Shannon entropy {ent} bits."
            )

        argument = (
            "PROSECUTOR POINT 1 (Spatial & Noise Evaluation): "
            + " ".join(obs_lines)
            + " From a forensic perspective, generative diffusion models and composite manipulations "
            "frequently exhibit non-uniform noise distribution or residual smoothing inconsistencies across textures. "
            "While natural camera sensors produce continuous physical shot noise (PRNU), synthetic rendering pipelines "
            "often present unnatural decoupling between high-contrast structural edges and smooth interior regions."
        )

        uncertainties = [
            "Global noise estimation does not segment sensor-specific PRNU fingerprint patterns.",
            "Post-capture compression, denoising, or photographic ISO scaling can alter noise standard deviations.",
        ]
        alternative_explanations = [
            "Low sensor noise may reflect low ISO photographic conditions, studio lighting, or camera hardware noise reduction.",
            "High edge density can be introduced by physical scene complexity or optical lens characteristics.",
        ]

    elif turn == 2:
        # Turn 2: Frequency & Wavelet Decomposition
        target_items = find_evidence_by_categories(evidence, ["frequency_analysis", "wavelet_analysis"])
        supporting_ids = [e["evidence_id"] for e in target_items]

        freq_item = next((e for e in target_items if e["category"] == "frequency_analysis"), None)
        wav_item = next((e for e in target_items if e["category"] == "wavelet_analysis"), None)

        # Reference previous Defence point if available
        last_defence_msg = next((m for m in reversed(debate_messages) if m["agent"] == "defence"), None)
        ref_rebuttal = ""
        if last_defence_msg:
            ref_rebuttal = (
                f"In response to the Defence's initial argument regarding environmental noise explanations, "
                f"we must look beyond spatial domain variance to multi-scale spectral decay. "
            )

        obs_lines = []
        if freq_item:
            m = freq_item.get("measurement", {})
            hfr = m.get("high_frequency_ratio", "N/A")
            lfr = m.get("low_frequency_ratio", "N/A")
            obs_lines.append(
                f"Under evidence item {freq_item['evidence_id']} (2D Fourier Analysis), "
                f"the radial spectral energy breakdown demonstrates low-frequency dominance of {lfr} "
                f"compared to high-frequency ratio {hfr}."
            )
        if wav_item:
            m = wav_item.get("measurement", {})
            er = m.get("energy_ratios", {})
            ll_r = er.get("ll_ratio", "N/A")
            hf_r = er.get("high_frequency_ratio", "N/A")
            obs_lines.append(
                f"Under evidence item {wav_item['evidence_id']} (Haar Wavelet Decomposition), "
                f"Level-1 approximation (LL) subband carries ratio {ll_r} of energy against high-frequency detail ratio {hf_r}."
            )

        argument = (
            "PROSECUTOR POINT 2 (Spectral & Wavelet Decomposition): "
            + ref_rebuttal
            + " ".join(obs_lines)
            + " Fourier and Wavelet transformations highlight whether high-frequency spatial frequencies decay naturally. "
            "AI generation architectures relying on transposed convolutions or latent upsampling often induce distinct "
            "spectral drop-offs or subtle grid periodicities, departing from typical photographic power-law decay."
        )

        uncertainties = [
            "Radial Fourier partitioning averages spectral rings globally without spatial coordinates of spectral anomalies.",
            "Wavelet subband ratios are sensitive to scene composition and natural atmospheric haze.",
        ]
        alternative_explanations = [
            "Shallow depth of field or smooth subjects (sky, uniform surfaces) naturally suppress high-frequency Fourier energy.",
            "Lossy recompression (JPEG/WebP) deliberately truncates high-frequency DCT and wavelet detail.",
        ]

    elif turn == 3:
        # Turn 3: SRM Residuals, Compression & Error Level Analysis
        target_items = find_evidence_by_categories(
            evidence, ["srm_analysis", "recompression_ela_analysis", "compression_analysis"]
        )
        supporting_ids = [e["evidence_id"] for e in target_items]

        srm_item = next((e for e in target_items if e["category"] == "srm_analysis"), None)
        ela_global = next((e for e in target_items if e["category"] == "recompression_ela_analysis" and e["coordinates"] is None), None)
        ela_regional = next((e for e in target_items if e["category"] == "recompression_ela_analysis" and e["coordinates"] is not None), None)
        comp_item = next((e for e in target_items if e["category"] == "compression_analysis"), None)

        obs_lines = []
        if srm_item:
            m = srm_item.get("measurement", {})
            avg_res = m.get("average_residual_energy", "N/A")
            max_res = m.get("max_residual_energy", "N/A")
            obs_lines.append(
                f"Evidence item {srm_item['evidence_id']} (SRM Analysis) reports an average residual energy of {avg_res} "
                f"and maximum filter energy of {max_res} across 7 high-pass linear kernels."
            )
        if ela_global:
            m = ela_global.get("measurement", {})
            avg_d = m.get("average_difference", "N/A")
            max_d = m.get("maximum_difference", "N/A")
            obs_lines.append(
                f"Evidence item {ela_global['evidence_id']} (ELA Recompression) shows an average pixel difference of {avg_d} "
                f"with maximum recompression disparity {max_d} at quality factor 90."
            )
        if ela_regional:
            m = ela_regional.get("measurement", {})
            reg_id = m.get("region_id", "N/A")
            reg_m = m.get("mean_difference", "N/A")
            obs_lines.append(
                f"Regional evidence item {ela_regional['evidence_id']} identifies localized discrepancy in {reg_id} "
                f"with regional mean difference {reg_m}."
            )
        if comp_item:
            m = comp_item.get("measurement", {})
            if m.get("status") == "success":
                qf = m.get("estimated_quality_factor", "N/A")
                baf = m.get("block_level_statistics", {}).get("blocking_artifact_factor", "N/A")
                obs_lines.append(
                    f"Evidence item {comp_item['evidence_id']} (Compression Analysis) verifies JPEG compression with "
                    f"estimated quality factor {qf} and blocking artifact factor {baf}."
                )
            else:
                obs_lines.append(
                    f"Evidence item {comp_item['evidence_id']} notes JPEG compression tables are unavailable ({m.get('message', 'non-JPEG format')})."
                )

        argument = (
            "PROSECUTOR POINT 3 (SRM Filter Bank & Error Level Analysis): "
            + " ".join(obs_lines)
            + " High-order SRM filter residuals and ELA error differentials evaluate whether compression and spatial correlation "
            "are uniform. Spliced objects, localized inpainting, or synthetic insertions frequently manifest localized error "
            "gradients or residual attenuation inconsistent with native single-capture camera hardware."
        )

        uncertainties = [
            "ELA error levels correlate strongly with contrast, color saturation, and edge density, not solely forgery.",
            "SRM linear filters highlight pixel dependencies but require comprehensive feature ensembles for definitive classification.",
        ]
        alternative_explanations = [
            "Local texture variance (e.g. sharp subject against blurred backdrop) inherently produces uneven regional ELA difference.",
            "Uniform recompression error is expected across authentic untampered photos as well as uniformly generated AI images.",
        ]

    else:
        # Turn 4: AI Detector Indicator & Cumulative Weight
        target_items = find_evidence_by_category(evidence, "ai_detection")
        supporting_ids = [e["evidence_id"] for e in target_items]

        ai_item = target_items[0] if target_items else None
        obs_lines = []
        if ai_item:
            m = ai_item.get("measurement", {})
            pred = m.get("prediction")
            score = m.get("model_score")
            conf = m.get("confidence_scores")
            if pred is not None:
                obs_lines.append(
                    f"Under evidence item {ai_item['evidence_id']} (AI Detection), the Swin Transformer classifier "
                    f"reports prediction '{pred}' with model score {score} and confidence distribution {conf}."
                )
            else:
                obs_lines.append(
                    f"Under evidence item {ai_item['evidence_id']} (AI Detection), the deep learning detector is unavailable "
                    f"({m.get('message', 'offline/unloaded')}); hence no probabilistic AI score can be leveraged."
                )

        argument = (
            "PROSECUTOR POINT 4 (AI Classifier Indicator & Synthesis): "
            + " ".join(obs_lines)
            + " Synthesizing this with our preceding empirical findings across spatial noise, spectral decay, and residual metrics, "
            "the forensic record highlights measurable points of analytical interest. We emphasize, however, that deep learning "
            "classifiers serve as statistical indicators rather than mathematical proofs, and must be weighed strictly alongside "
            "underlying physical sensor signatures."
        )

        uncertainties = [
            "Pretrained vision transformers may experience concept drift when encountering emerging diffusion architectures.",
            "Heavy social media compression or resizing can degrade AI classifier accuracy.",
        ]
        alternative_explanations = [
            "Unusual artistic framing, digital grading, or CGI rendering can trigger elevated synthetic probability scores on authentic imagery.",
            "A low synthetic score does not definitively prove absence of localized image tampering.",
        ]

    return {
        "agent": "prosecutor",
        "turn": turn,
        "argument": argument,
        "supporting_evidence_ids": supporting_ids,
        "uncertainties": uncertainties,
        "alternative_explanations": alternative_explanations,
    }
