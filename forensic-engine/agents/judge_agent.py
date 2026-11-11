
from typing import List
from agents.state import ForensicDebateState, JudgeResult


def classify_ai_probability(
    ai_score: float | None,
) -> dict:
    """
    Converts the artificial score into AI/Human likelihood
    percentages and classification bands.

    Scores are model estimates, not calibrated probabilities.
    """

    if ai_score is None:
        return {
            "ai_likelihood": None,
            "human_likelihood": None,
            "classification": "Unavailable",
            "confidence": "Unknown",
            "interpretation": "AI detection score was unavailable.",
        }

    ai_percentage = round(ai_score * 100, 2)
    human_percentage = round((1 - ai_score) * 100, 2)

    if ai_score >= 0.80:
        classification = "Likely AI"
        confidence = "Medium"
    elif ai_score >= 0.50:
        classification = "AI Detected"
        confidence = "Low"
    elif ai_score >= 0.40:
        classification = "Uncertain"
        confidence = "Low"
    elif ai_score >= 0.20:
        classification = "Possibly Human"
        confidence = "Low"
    else:
        classification = "Likely Human"
        confidence = "Low"

    return {
        "ai_likelihood": ai_percentage,
        "human_likelihood": human_percentage,
        "classification": classification,
        "confidence": confidence,
        "interpretation": (
            "Estimated model score only. This is not a calibrated "
            "statistical probability or conclusive forensic proof."
        ),
    }


def run_judge_assessment(
    state: ForensicDebateState,
) -> JudgeResult:
    """
    Generates the Judge assessment from verified Expert evidence.

    Decision rule:
      AI score >= 0.50 -> FAKE (AI-generated classification)
      AI score < 0.50  -> REAL (human-origin signal)
      Missing/invalid score -> UNCERTAIN
    """

    evidence = state.get("evidence", [])
    expert_report = state.get("expert_report", {})

    # 1. Validate Expert Agent prerequisite
    if (
        not expert_report
        or expert_report.get("status") != "verified"
        or expert_report.get("recommendation") != "proceed_to_judge"
    ):
        return {
            "status": "blocked",
            "assessment": "UNCERTAIN",
            "reasoning": (
                "Judge execution is blocked because Expert verification "
                "was incomplete, failed, or issued a stop recommendation."
            ),
            "supporting_evidence_ids": [],
            "contradictory_evidence_ids": [],
            "limitations": [
                "Expert verification prerequisite was not satisfied."
            ],
            "expert_verification_summary": expert_report.get(
                "explanation",
                "No verified Expert report is available.",
            ),
        }

    # 2. Prepare evidence collections
    supporting_evidence_ids: List[str] = []
    contradictory_evidence_ids: List[str] = []
    contextual_evidence_ids: List[str] = []

    ai_item = next(
        (
            item for item in evidence
            if item.get("category") == "ai_detection"
        ),
        None,
    )

    ela_items = [
        item for item in evidence
        if item.get("category") == "recompression_ela_analysis"
    ]

    for item in evidence:
        if item.get("category") in {
            "compression_analysis",
            "noise_analysis",
            "frequency_analysis",
        }:
            evidence_id = item.get("evidence_id")
            if evidence_id:
                contextual_evidence_ids.append(evidence_id)

    # 3. Extract and validate AI score
    ai_artificial_score = None

    if ai_item:
        measurement = ai_item.get("measurement") or {}

        print("\n========== AI DETECTION DATA ==========")
        print("AI Item:", ai_item)
        print("Measurement:", measurement)

        raw_score = measurement.get("artificial_probability")
        if raw_score is None:
            raw_score = measurement.get("model_score")

        if raw_score is not None:
            try:
                ai_artificial_score = float(raw_score)

                # Accept either 0-1 scores or percentage values.
                if 1 < ai_artificial_score <= 100:
                    ai_artificial_score /= 100

                if not 0 <= ai_artificial_score <= 1:
                    ai_artificial_score = None

            except (TypeError, ValueError):
                ai_artificial_score = None

        print("Validated AI score:", ai_artificial_score)
        print("=======================================\n")

        # Record AI evidence supporting the AI-generated verdict.
        if ai_artificial_score is not None and ai_artificial_score >= 0.50:
            evidence_id = ai_item.get("evidence_id")
            if evidence_id:
                supporting_evidence_ids.append(evidence_id)

    # 4. Evaluate ELA findings
    for item in ela_items:
        measurement = item.get("measurement") or {}
        contrast_range = measurement.get("regional_contrast_range", 0)

        try:
            contrast_range = float(contrast_range or 0)
        except (TypeError, ValueError):
            contrast_range = 0

        if contrast_range > 1.5:
            evidence_id = item.get("evidence_id")
            if evidence_id:
                supporting_evidence_ids.append(evidence_id)

    # 5. Deduplicate evidence IDs
    supporting_evidence_ids = sorted(set(supporting_evidence_ids))
    contradictory_evidence_ids = sorted(set(contradictory_evidence_ids))
    contextual_evidence_ids = sorted(set(contextual_evidence_ids))

    # 6. Calculate likelihoods and classification
    classification_result = classify_ai_probability(ai_artificial_score)

    ai_likelihood = classification_result["ai_likelihood"]
    human_likelihood = classification_result["human_likelihood"]
    classification = classification_result["classification"]
    confidence = classification_result["confidence"]

    # 7. Determine Judge assessment using the 50% threshold
    if ai_artificial_score is None:
        assessment = "UNCERTAIN"
        reasoning = (
            "The AI detector did not provide a valid artificial score. "
            "A classification cannot be established."
        )

    elif ai_artificial_score >= 0.50:
        assessment = "FAKE"
        reasoning = (
            f"The combined AI detector score is "
            f"{ai_artificial_score * 100:.2f}%. "
            "Because the score is at least 50%, the image is classified "
            "as AI-generated under the configured decision rule. "
            "This is a model-based classification, not conclusive proof."
        )

    else:
        assessment = "REAL"
        reasoning = (
            f"The combined AI detector score is "
            f"{ai_artificial_score * 100:.2f}%. "
            "Because the score is below 50%, the image is classified "
            "as showing a human-origin signal under the configured "
            "decision rule. This does not prove authenticity."
        )

    # 8. Add contextual evidence explanation
    if contextual_evidence_ids:
        reasoning += (
            " Compression, noise, and frequency findings were treated "
            "as contextual indicators rather than direct proof."
        )

    if len(supporting_evidence_ids) > 1:
        reasoning += (
            " Additional forensic indicators were also recorded "
            "for consideration."
        )

    # 9. Limitations
    limitations = [
        (
            "The AI score is an estimated model output, not a calibrated "
            "statistical probability."
        ),
        (
            "The 50% threshold is an operational decision rule and "
            "should be validated against representative datasets."
        ),
        (
            "An AI-generated classification does not by itself prove "
            "fraud, malicious manipulation, or deceptive intent."
        ),
        (
            "A score below 50% does not prove that an image is authentic "
            "or human-created."
        ),
        (
            "Lossy recompression, resizing, and social media processing "
            "can obscure image artifacts."
        ),
        (
            "Model performance may vary across faces, artwork, documents, "
            "food, and other image categories."
        ),
        (
            "ELA, compression, noise, and frequency findings are "
            "contextual indicators and are not independently conclusive."
        ),
    ]

    # 10. Expert summary
    expert_summary = expert_report.get(
        "explanation",
        "Expert Agent verified the available evidence citations.",
    )

    # 11. Debug output
    print("\n========== JUDGE DEBUG ==========")
    print("AI score:", ai_artificial_score)
    print("AI likelihood:", ai_likelihood)
    print("Human likelihood:", human_likelihood)
    print("Classification:", classification)
    print("Assessment:", assessment)
    print("Supporting evidence:", supporting_evidence_ids)
    print("=================================\n")

    # 12. Return Judge Result
    return {
        "status": "completed",
        "assessment": assessment,
        "ai_likelihood": ai_likelihood,
        "human_likelihood": human_likelihood,
        "classification": classification,
        "confidence": confidence,
        "ai_classification": classification_result,
        "reasoning": reasoning,
        "supporting_evidence_ids": supporting_evidence_ids,
        "contradictory_evidence_ids": contradictory_evidence_ids,
        "contextual_evidence_ids": contextual_evidence_ids,
        "limitations": limitations,
        "expert_verification_summary": expert_summary,
    }
