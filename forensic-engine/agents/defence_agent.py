from typing import Dict, Any, List
from agents.state import ForensicDebateState, DebateMessage
from agents.prosecutor_agent import find_evidence_by_category, find_evidence_by_categories


def run_defence_turn(state: ForensicDebateState, turn: int) -> DebateMessage:
    """
    Executes a single turn for the Defence Agent.
    Directly addresses the preceding Prosecutor argument, provides benign alternative
    explanations, and references actual evidence from the structured ledger.
    Never fabricates measurements or evidence IDs.
    """
    evidence = state.get("evidence", [])
    debate_messages = state.get("debate_messages", [])

    # Find the corresponding Prosecutor message for this turn
    prosecutor_msg = next((m for m in reversed(debate_messages) if m["agent"] == "prosecutor" and m["turn"] == turn), None)

    if turn == 1:
        # Turn 1: Response to Prosecutor on Spatial & Noise
        target_items = find_evidence_by_categories(evidence, ["spatial_features", "noise_analysis"])
        supporting_ids = [e["evidence_id"] for e in target_items]

        noise_item = next((e for e in target_items if e["category"] == "noise_analysis"), None)
        spatial_item = next((e for e in target_items if e["category"] == "spatial_features"), None)

        nl_val = noise_item.get("measurement", {}).get("noise_level", "recorded") if noise_item else "recorded"
        ent_val = spatial_item.get("measurement", {}).get("image_entropy", "recorded") if spatial_item else "recorded"

        argument = (
            f"DEFENCE POINT 1 (Rebuttal on Spatial & Sensor Noise): "
            f"The Prosecutor cites evidence items {', '.join(supporting_ids)} to suggest potential synthetic smoothing. "
            f"However, the observed noise level of {nl_val} and entropy of {ent_val} bits are completely consistent with "
            f"authentic physical capture under standard camera shooting conditions. Modern digital cameras employ sophisticated "
            f"in-camera ISP (Image Signal Processor) bilateral filtering and low-ISO sensor optimization to minimize thermal grain. "
            f"The absence of aggressive noise does not indicate AI generation; rather, it reflects clean optical sensor acquisition "
            f"and standard post-processing."
        )

        uncertainties = [
            "Noise metrics cannot differentiate in-camera hardware noise reduction from software denoising algorithms.",
            "Optical lens quality and aperture directly influence measured sharpness and edge density.",
        ]
        alternative_explanations = [
            "Low sensor noise is standard in well-lit daylight photography and studio portraits.",
            "Luminance smoothness is a direct consequence of low ISO sensitivity (e.g. ISO 100/200).",
        ]

    elif turn == 2:
        # Turn 2: Response to Prosecutor on Spectral & Wavelet Decay
        target_items = find_evidence_by_categories(evidence, ["frequency_analysis", "wavelet_analysis"])
        supporting_ids = [e["evidence_id"] for e in target_items]

        freq_item = next((e for e in target_items if e["category"] == "frequency_analysis"), None)
        wav_item = next((e for e in target_items if e["category"] == "wavelet_analysis"), None)

        lfr_val = freq_item.get("measurement", {}).get("low_frequency_ratio", "recorded") if freq_item else "recorded"
        ll_val = wav_item.get("measurement", {}).get("energy_ratios", {}).get("ll_ratio", "recorded") if wav_item else "recorded"

        argument = (
            f"DEFENCE POINT 2 (Rebuttal on Spectral & Wavelet Falloff): "
            f"Addressing the Prosecutor's point on evidence items {', '.join(supporting_ids)}, the low-frequency dominance "
            f"(Fourier low-frequency ratio {lfr_val}, Wavelet approximation LL ratio {ll_val}) is the textbook signature of "
            f"natural photographic scenes under Fourier power-law decay (1/f^alpha). Natural photographs possess continuous surfaces, "
            f"sky gradients, and soft lighting that naturally concentrate energy in low spectral frequencies. Furthermore, any standard "
            f"image resizing or lossy compression pipeline aggressively discards high-frequency coefficients without requiring any AI synthesis."
        )

        uncertainties = [
            "Power-law spectral decay is universal across natural imagery and cannot definitively establish or refute synthetic origin.",
            "Fourier transform averages radial frequencies across the entire frame, concealing localized spectral variations.",
        ]
        alternative_explanations = [
            "Atmospheric haze, soft depth-of-field, and motion blur naturally depress high-frequency spectral ratios.",
            "Web distribution formats routinely compress and resample high-frequency detail.",
        ]

    elif turn == 3:
        # Turn 3: Response to Prosecutor on SRM & Error Level Analysis
        target_items = find_evidence_by_categories(
            evidence, ["srm_analysis", "recompression_ela_analysis", "compression_analysis"]
        )
        supporting_ids = [e["evidence_id"] for e in target_items]

        ela_item = next((e for e in target_items if e["category"] == "recompression_ela_analysis" and e["coordinates"] is None), None)
        ela_diff = ela_item.get("measurement", {}).get("average_difference", "recorded") if ela_item else "recorded"

        argument = (
            f"DEFENCE POINT 3 (Rebuttal on SRM Residuals & ELA Variance): "
            f"The Prosecutor argues that localized ELA differences across evidence items {', '.join(supporting_ids)} indicate "
            f"potential splicing or manipulation. We strongly challenge this inference. Error Level Analysis recompression difference "
            f"(global average {ela_diff}) is fundamentally governed by local image contrast and texture complexity. Under standard JPEG DCT "
            f"quantization, high-contrast edges and saturated chromatic boundaries inherently yield higher recompression error than smooth surfaces. "
            f"Regional variance in ELA reflects scene content heterogeneity (e.g. subject in foreground vs. uniform backdrop), not illicit tampering."
        )

        uncertainties = [
            "ELA recompression is highly sensitive to the chosen recompression quality parameter (Q=90) relative to the source quality.",
            "Color space conversion between RGB and YCbCr generates baseline recompression error across all authentic images.",
        ]
        alternative_explanations = [
            "Heterogeneous ELA error maps naturally occur across untouched photographs featuring both detailed subjects and plain backgrounds.",
            "Camera hardware quantization matrices vary widely across manufacturer firmware.",
        ]

    else:
        # Turn 4: Response to Prosecutor on AI Detection & Conclusion
        target_items = find_evidence_by_category(evidence, "ai_detection")
        supporting_ids = [e["evidence_id"] for e in target_items]

        ai_item = target_items[0] if target_items else None
        pred = ai_item.get("measurement", {}).get("prediction") if ai_item else None
        score = ai_item.get("measurement", {}).get("model_score") if ai_item else None

        if pred is not None:
            ai_context = (
                f"The AI classifier in evidence item {ai_item['evidence_id']} returned prediction '{pred}' with score {score}. "
                f"As documented in the official model limitations, this Swin Transformer was trained on early diffusion generators "
                f"and is well-known to produce probabilistic fluctuations when presented with non-standard artistic styles, high compression, "
                f"or rescaled web media."
            )
        else:
            ai_context = (
                f"The AI detector is offline/unavailable in evidence item {ai_item['evidence_id'] if ai_item else 'N/A'}, "
                f"meaning no automated deep learning classification can be relied upon."
            )

        argument = (
            f"DEFENCE POINT 4 (Final Synthesis on Limitations & Authenticity): "
            f"{ai_context} Crucially, across all 4 turns of examination, the empirical forensic record fails to establish any "
            f"definitive signature of forgery: noise residuals remain plausible, spectral decay aligns with natural photographic laws, "
            f"and recompression differences match expected scene geometry. In the absence of conclusive physical tampering artifacts, "
            f"the hypothesis of authenticity remains robust, and a finding of manipulation is scientifically unsupported."
        )

        uncertainties = [
            "Probabilistic classifiers produce statistical associations, not forensic certainty.",
            "No single automated forensic test provides definitive determination in isolation.",
        ]
        alternative_explanations = [
            "Authentic photographs subjected to social media recompression or editorial color correction frequently exhibit minor statistical anomalies.",
            "A probabilistic AI indicator must not override consistent physical sensor and compression evidence.",
        ]

    return {
        "agent": "defence",
        "turn": turn,
        "argument": argument,
        "supporting_evidence_ids": supporting_ids,
        "uncertainties": uncertainties,
        "alternative_explanations": alternative_explanations,
    }
