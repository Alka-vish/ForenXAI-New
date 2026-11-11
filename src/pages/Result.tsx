import React, { useState } from 'react';
import { Button } from '../components/Button';
import { InvestigationRecord } from '../types';

import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Download,
  FileText,
  Info,
  ShieldCheck,
  Sparkles,
  Copy,
} from 'lucide-react';

interface ResultProps {
  activeRecord: InvestigationRecord | null;
  onNewInvestigation: () => void;
  onOpenWorkspace: () => void;
}

export const Result: React.FC<ResultProps> = ({
  activeRecord,
  onNewInvestigation,
  onOpenWorkspace,
}) => {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [copiedNotification, setCopiedNotification] = useState(false);

  if (!activeRecord || !activeRecord.response) {
    return (
      <main className="min-h-screen flex-1 bg-[#050505] text-white flex items-center justify-center p-6">
        <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/[0.035] p-8 text-center shadow-2xl backdrop-blur-xl">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-red-500/20 bg-red-500/10 text-red-400">
            <FileText className="h-7 w-7" />
          </div>

          <h1 className="mb-2 text-xl font-bold">
            No Investigation Result
          </h1>

          <p className="mb-6 text-sm leading-relaxed text-neutral-400">
            Start a new investigation or select a previous investigation
            from your history.
          </p>

          <Button type="button" variant="primary" onClick={onNewInvestigation}>
            Start New Investigation
          </Button>
        </div>
      </main>
    );
  }

  const {
    response,
    timestamp,
    id: recordId,
    imageName,
  } = activeRecord;

  const {
    image_information,
    evidence = [],
    debate,
  } = response;

  const judgeResult = debate?.judge_result as any;
  const expertReport = debate?.expert_report as any;

  /* =========================================================
     AI SCORE
     ========================================================= */

  const aiEvidence = evidence.find(
    (item: any) => item.category === 'ai_detection'
  ) as any;

  const measurement = aiEvidence?.measurement || {};

  const rawAiScore =
    judgeResult?.ai_likelihood ??
    measurement?.artificial_probability ??
    measurement?.model_score ??
    null;

  let aiLikelihood: number | null = null;

  if (rawAiScore !== null && rawAiScore !== undefined) {
    const numericScore = Number(rawAiScore);

    if (!Number.isNaN(numericScore)) {
      /*
       * Supports both:
       * 0.294  -> 29.4%
       * 29.4   -> 29.4%
       */
      aiLikelihood =
        numericScore <= 1
          ? Math.round(numericScore * 10000) / 100
          : Math.round(numericScore * 100) / 100;

      // Keep score inside valid percentage range
      aiLikelihood = Math.min(100, Math.max(0, aiLikelihood));
    }
  }

  const humanLikelihood =
    aiLikelihood !== null
      ? Math.round((100 - aiLikelihood) * 100) / 100
      : null;

  /* =========================================================
     FINAL CLASSIFICATION
     
     IMPORTANT:
     The percentage is the source of truth.
     Judge classification is NOT used here because it can
     conflict with the numerical AI score.
     ========================================================= */

  const isAiGenerated =
    aiLikelihood !== null && aiLikelihood >= 50;

  const isHumanGenerated =
    aiLikelihood !== null && aiLikelihood < 50;

  const classification =
    aiLikelihood === null
      ? 'RESULT UNAVAILABLE'
      : isAiGenerated
        ? 'AI-GENERATED'
        : 'REAL / HUMAN-GENERATED';

  const displayedLikelihood =
    aiLikelihood === null
      ? null
      : isAiGenerated
        ? aiLikelihood
        : humanLikelihood;

  const likelihoodLabel =
    aiLikelihood === null
      ? 'Likelihood'
      : isAiGenerated
        ? 'AI LIKELIHOOD'
        : 'HUMAN LIKELIHOOD';

  /* =========================================================
     RESULT THEME
     ========================================================= */

  const resultTheme = isAiGenerated
    ? {
        accent: 'text-red-500',
        border: 'border-red-500/30',
        background: 'bg-red-500/[0.06]',
        badge: 'bg-red-500/10 text-red-400 border-red-500/25',
        bar: 'bg-red-500',
        icon: AlertCircle,
      }
    : {
        accent: 'text-emerald-400',
        border: 'border-emerald-500/30',
        background: 'bg-emerald-500/[0.06]',
        badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
        bar: 'bg-emerald-500',
        icon: CheckCircle2,
      };

  const ResultIcon = resultTheme.icon;

  /* =========================================================
     IMAGE CHARACTERISTICS
     ========================================================= */

  const imageCharacteristics = [
    {
      title: 'AI visual patterns',
      value:
        aiLikelihood === null
          ? 'Unavailable'
          : aiLikelihood >= 60
            ? 'Elevated'
            : aiLikelihood >= 40
              ? 'Moderate'
              : 'Low',
      description:
        'Visual patterns evaluated by the AI image detection model.',
    },
    {
      title: 'Noise characteristics',
      value: 'Analyzed',
      description:
        'Pixel-level noise characteristics were examined for inconsistencies.',
    },
    {
      title: 'Frequency structure',
      value: 'Analyzed',
      description:
        'Frequency and wavelet patterns were examined for image artifacts.',
    },
    {
      title: 'Compression indicators',
      value: 'Analyzed',
      description:
        'JPEG compression and recompression indicators were examined.',
    },
  ];

  /* =========================================================
     CONCISE ASSESSMENT
     ========================================================= */

  const getConciseAssessment = () => {
    let reasoning = String(
      judgeResult?.reasoning ||
        'The investigation was completed, but a detailed assessment was not available.'
    )
      .replace(/\s+/g, ' ')
      .trim();

    /*
     * Remove contradictory classification language from the
     * judge reasoning when possible.
     */
    if (isHumanGenerated) {
      reasoning = reasoning
        .replace(/possibly ai/gi, 'AI indicators')
        .replace(/likely ai/gi, 'AI indicators')
        .replace(/ai-generated/gi, 'AI indicators');
    }

    const sentence = reasoning.split(/(?<=[.!?])\s+/)[0];

    if (sentence.length <= 280) {
      return sentence;
    }

    return `${sentence.slice(0, 277).trim()}...`;
  };

  const conciseAssessment = getConciseAssessment();

  /* =========================================================
     EXPORT
     ========================================================= */

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(activeRecord, null, 2);

    const blob = new Blob([jsonStr], {
      type: 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');

    anchor.href = url;
    anchor.download = `forenxai_report_${recordId}.json`;

    document.body.appendChild(anchor);
    anchor.click();

    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  };

  /* =========================================================
     COPY SUMMARY
     ========================================================= */

  const handleCopySummary = async () => {
    const summaryText = `ForenXAI Investigation Summary

Image: ${imageName}
Record ID: ${recordId}

Final Classification: ${classification}

AI Likelihood: ${
      aiLikelihood !== null ? `${aiLikelihood}%` : 'Unavailable'
    }

Human Likelihood: ${
      humanLikelihood !== null ? `${humanLikelihood}%` : 'Unavailable'
    }

Primary Likelihood: ${
      displayedLikelihood !== null ? `${displayedLikelihood}%` : 'Unavailable'
    }

Image Dimensions: ${image_information.width} x ${
      image_information.height
    } px

Format: ${image_information.format}

Evidence Items: ${evidence.length}

Expert Status: ${expertReport?.status || 'Unavailable'}

Assessment: ${conciseAssessment}

Note: This is an AI-assisted forensic assessment and not conclusive proof.`;

    try {
      await navigator.clipboard.writeText(summaryText);

      setCopiedNotification(true);

      setTimeout(() => {
        setCopiedNotification(false);
      }, 2500);
    } catch (error) {
      console.error('Unable to copy summary:', error);
    }
  };

  return (
    <main
      id="result-main"
      className="min-h-screen flex-1 bg-[#050505] px-4 py-6 text-white sm:px-6 lg:px-10"
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">

        {/* =====================================================
            HEADER
            ===================================================== */}

        <header className="flex flex-col justify-between gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-center">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-red-400">
              <ShieldCheck className="h-4 w-4" />
              ForenXAI
            </div>

            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Investigation Result
            </h1>

            <p className="mt-1 text-xs text-neutral-500">
              {imageName} · {new Date(timestamp).toLocaleString()}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onOpenWorkspace}
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              Workspace
            </Button>

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleExportJson}
            >
              <Download className="mr-1 h-4 w-4" />
              Export
            </Button>

            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={onNewInvestigation}
            >
              New Investigation
            </Button>
          </div>
        </header>

        {/* =====================================================
            COPY NOTIFICATION
            ===================================================== */}

        {copiedNotification && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-center text-sm text-emerald-300">
            Investigation summary copied.
          </div>
        )}

        {/* =====================================================
            MAIN RESULT
            ===================================================== */}

        <section
          id="result-primary-card"
          className={`overflow-hidden rounded-2xl border ${resultTheme.border} bg-white/[0.035] shadow-2xl backdrop-blur-xl`}
        >
          <div className="grid grid-cols-1 lg:grid-cols-[0.9fr_1.1fr]">

            {/* IMAGE */}
            <div className="flex min-h-[300px] items-center justify-center border-b border-white/10 bg-black/20 p-5 sm:p-8 lg:border-b-0 lg:border-r">
              {activeRecord.imagePreview ? (
                <img
                  id="result-image-preview"
                  src={activeRecord.imagePreview}
                  alt="Investigated image"
                  className="max-h-[390px] w-full rounded-xl border border-white/10 object-contain shadow-xl"
                />
              ) : (
                <div className="flex h-64 items-center justify-center text-sm text-neutral-500">
                  Image preview unavailable
                </div>
              )}
            </div>

            {/* RESULT INFORMATION */}
            <div className="flex flex-col justify-center p-6 sm:p-10">

              {/* Classification label */}
              <div className="mb-5 flex items-center justify-between gap-4">
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-neutral-500">
                  Final Classification
                </span>

                <div
                  className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${resultTheme.badge}`}
                >
                  {isAiGenerated ? 'AI DETECTED' : 'HUMAN SIGNAL'}
                </div>
              </div>

              {/* CLEAR VERDICT */}
              <div className="flex items-center gap-3">
                <ResultIcon
                  className={`h-8 w-8 shrink-0 ${resultTheme.accent}`}
                />

                <h2
                  className={`text-3xl font-black tracking-tight sm:text-4xl ${resultTheme.accent}`}
                >
                  {classification}
                </h2>
              </div>

              {/* PRIMARY PERCENTAGE */}
              <div className="mt-6">
                <span className="block text-[10px] font-semibold uppercase tracking-[0.2em] text-neutral-500">
                  {likelihoodLabel}
                </span>

                <span
                  className={`mt-1 block text-7xl font-black tracking-tighter sm:text-8xl ${resultTheme.accent}`}
                >
                  {displayedLikelihood !== null
                    ? `${displayedLikelihood}%`
                    : '—'}
                </span>
              </div>

              {/* EXPLICIT SECONDARY SCORE */}
              <div className="mt-5 grid grid-cols-2 gap-3">

                <div className="rounded-xl border border-red-500/20 bg-red-500/[0.04] p-3">
                  <span className="block text-[10px] uppercase tracking-wider text-neutral-500">
                    AI likelihood
                  </span>

                  <span className="mt-1 block text-lg font-bold text-red-400">
                    {aiLikelihood !== null
                      ? `${aiLikelihood}%`
                      : '—'}
                  </span>
                </div>

                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/[0.04] p-3">
                  <span className="block text-[10px] uppercase tracking-wider text-neutral-500">
                    Human likelihood
                  </span>

                  <span className="mt-1 block text-lg font-bold text-emerald-400">
                    {humanLikelihood !== null
                      ? `${humanLikelihood}%`
                      : '—'}
                  </span>
                </div>

              </div>

              {/* SCORE BAR */}
              <div className="mt-6">
                <div className="flex h-3 w-full overflow-hidden rounded-full bg-white/10">

                  <div
                    className="bg-red-500 transition-all duration-700"
                    style={{
                      width: `${aiLikelihood ?? 0}%`,
                    }}
                  />

                  <div
                    className="bg-emerald-500 transition-all duration-700"
                    style={{
                      width: `${humanLikelihood ?? 0}%`,
                    }}
                  />

                </div>

                <div className="mt-2 flex justify-between text-[11px]">
                  <span className="text-red-400">
                    AI {aiLikelihood !== null ? `${aiLikelihood}%` : '—'}
                  </span>

                  <span className="text-emerald-400">
                    Human{' '}
                    {humanLikelihood !== null
                      ? `${humanLikelihood}%`
                      : '—'}
                  </span>
                </div>
              </div>

              {/* SIMPLE INTERPRETATION */}
              <p className="mt-6 text-sm leading-relaxed text-neutral-400">
                {aiLikelihood === null
                  ? 'A reliable classification could not be calculated from the available model results.'
                  : isAiGenerated
                    ? 'The forensic analysis shows a higher AI-generation likelihood than human likelihood.'
                    : 'The forensic analysis shows a higher human likelihood than AI-generation likelihood.'}
              </p>

              {/* DISCLAIMER */}
              <div className="mt-6 flex items-start gap-2 rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs leading-relaxed text-neutral-500">
                <Info className="mt-0.5 h-4 w-4 shrink-0 text-neutral-400" />

                <span>
                  These percentages are estimated model scores and should not
                  be treated as conclusive forensic proof.
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* =====================================================
            IMAGE OVERVIEW
            ===================================================== */}

        <section className="rounded-2xl border border-white/10 bg-white/[0.035] p-5 shadow-xl backdrop-blur-xl sm:p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-red-400">
                Image Overview
              </p>

              <h2 className="mt-1 text-lg font-bold">
                Examined Image
              </h2>
            </div>

            <Sparkles className="h-5 w-5 text-neutral-600" />
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              ['Filename', imageName],
              [
                'Dimensions',
                `${image_information.width} × ${image_information.height}`,
              ],
              ['Format', image_information.format],
              ['Evidence', `${evidence.length} indicators`],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-3"
              >
                <span className="block text-[11px] text-neutral-500">
                  {label}
                </span>

                <span className="mt-1 block truncate text-sm font-medium uppercase text-white">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* =====================================================
            IMAGE CHARACTERISTICS
            ===================================================== */}

        <section className="rounded-2xl border border-white/10 bg-white/[0.035] p-5 shadow-xl backdrop-blur-xl sm:p-6">
          <div className="mb-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-red-400">
              Analysis Summary
            </p>

            <h2 className="mt-1 text-lg font-bold">
              Image Characteristics
            </h2>

            <p className="mt-1 text-sm text-neutral-500">
              Simplified findings from the forensic pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {imageCharacteristics.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-medium text-neutral-300">
                    {feature.title}
                  </h3>

                  <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-neutral-300">
                    {feature.value}
                  </span>
                </div>

                <p className="mt-2 text-xs leading-relaxed text-neutral-500">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* =====================================================
            FINAL ASSESSMENT
            ===================================================== */}

        <section
          className={`rounded-2xl border ${resultTheme.border} ${resultTheme.background} p-5 shadow-xl backdrop-blur-xl sm:p-6`}
        >
          <div className="flex items-start gap-3">
            <ResultIcon
              className={`mt-0.5 h-6 w-6 shrink-0 ${resultTheme.accent}`}
            />

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-lg font-bold text-white">
                  Final Assessment
                </h2>

                <span
                  className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase ${resultTheme.badge}`}
                >
                  {classification}
                </span>
              </div>

              <p className="mt-3 text-sm leading-relaxed text-neutral-300">
                {conciseAssessment}
              </p>

              <p className="mt-3 text-[11px] text-neutral-500">
                Detailed forensic evidence and agent analysis are available
                under Technical Investigation.
              </p>
            </div>
          </div>
        </section>

        {/* =====================================================
            TECHNICAL DETAILS
            ===================================================== */}

        <section className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] shadow-xl backdrop-blur-xl">
          <button
            type="button"
            onClick={() =>
              setShowTechnicalDetails(!showTechnicalDetails)
            }
            className="flex w-full items-center justify-between px-5 py-4 text-left transition hover:bg-white/[0.04] sm:px-6"
          >
            <div>
              <p className="text-sm font-semibold text-white">
                Technical Investigation
              </p>

              <p className="mt-1 text-xs text-neutral-500">
                Evidence, agent verification, and detailed measurements
              </p>
            </div>

            {showTechnicalDetails ? (
              <ChevronUp className="h-5 w-5 text-neutral-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-neutral-400" />
            )}
          </button>

          {showTechnicalDetails && (
            <div className="border-t border-white/10 p-5 sm:p-6">

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">

                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <span className="block text-xs text-neutral-500">
                    Evidence Items
                  </span>

                  <span className="mt-1 block text-xl font-bold text-white">
                    {evidence.length}
                  </span>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <span className="block text-xs text-neutral-500">
                    Debate Messages
                  </span>

                  <span className="mt-1 block text-xl font-bold text-white">
                    {debate?.debate_messages?.length || 0}
                  </span>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <span className="block text-xs text-neutral-500">
                    Expert Status
                  </span>

                  <span className="mt-1 block text-sm font-bold capitalize text-white">
                    {expertReport?.status || 'Unavailable'}
                  </span>
                </div>

              </div>

              {/* Evidence */}
              <div className="mt-5">
                <h3 className="mb-3 text-sm font-semibold text-white">
                  Evidence References
                </h3>

                <div className="space-y-2">
                  {evidence.map((item: any) => (
                    <div
                      key={item.evidence_id}
                      className="rounded-xl border border-white/10 bg-white/[0.02] p-3"
                    >
                      <div className="flex items-start gap-3">
                        <span className="font-mono text-xs font-bold text-red-400">
                          {item.evidence_id}
                        </span>

                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-neutral-200">
                            {item.title}
                          </p>

                          <p className="mt-1 text-xs leading-relaxed text-neutral-500">
                            {item.observation}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* =====================================================
            ACTIONS
            ===================================================== */}

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          <button
            type="button"
            onClick={handleCopySummary}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-xs font-semibold text-neutral-400 transition hover:border-red-500/30 hover:text-white"
          >
            <Copy className="h-4 w-4" />
            Copy Summary
          </button>

          <button
            type="button"
            onClick={onNewInvestigation}
            className="rounded-xl bg-red-600 px-5 py-3 text-xs font-bold uppercase tracking-wider text-white transition hover:bg-red-500"
          >
            Start New Investigation
          </button>
        </div>

        {/* =====================================================
            DISCLAIMER
            ===================================================== */}

        <footer className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.02] p-4 text-xs leading-relaxed text-neutral-500">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />

          <p>
            ForenXAI provides an AI-assisted forensic assessment. Results are
            probabilistic and should not be treated as definitive proof of
            image authenticity or manipulation.
          </p>
        </footer>

      </div>
    </main>
  );
};