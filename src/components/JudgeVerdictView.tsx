import React from 'react';
import { JudgeResult } from '../types';
import {
  Scale,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from 'lucide-react';

interface JudgeVerdictViewProps {
  judgeResult: JudgeResult | null;
  onSelectEvidenceId?: (id: string) => void;
}

export const JudgeVerdictView: React.FC<JudgeVerdictViewProps> = ({
  judgeResult,
  onSelectEvidenceId,
}) => {
  if (!judgeResult) {
    return null;
  }

  const assessment = judgeResult.assessment;

  let verdictColor =
    'border-neutral-700 bg-[#181818] text-neutral-200';
  let badgeColor =
    'border-neutral-700 bg-[#242424] text-neutral-300';
  let Icon = AlertCircle;

  if (assessment === 'REAL') {
    verdictColor =
      'border-emerald-800/60 bg-emerald-950/25 text-emerald-100';
    badgeColor =
      'border-emerald-700/60 bg-emerald-600 text-white';
    Icon = CheckCircle2;
  } else if (assessment === 'FAKE') {
    verdictColor =
      'border-red-800/60 bg-red-950/25 text-red-100';
    badgeColor =
      'border-red-700/60 bg-red-600 text-white';
    Icon = XCircle;
  } else if (assessment === 'UNCERTAIN') {
    verdictColor =
      'border-amber-800/60 bg-amber-950/25 text-amber-100';
    badgeColor =
      'border-amber-700/60 bg-amber-600 text-white';
    Icon = AlertCircle;
  }

  return (
    <div
      id="judge-verdict-card"
      className="rounded-2xl border border-neutral-800 bg-[#111111] p-5 shadow-xl shadow-black/20"
    >
      {/* Header */}
      <div className="mb-5 flex flex-col justify-between gap-3 border-b border-neutral-800 pb-4 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-red-600/30 bg-red-950/40">
            <Scale className="h-5 w-5 text-red-400" />
          </div>

          <div>
            <h2
              id="judge-verdict-heading"
              className="text-base font-semibold text-white"
            >
              Judge Agent Final Assessment
            </h2>

            <p className="mt-0.5 text-xs text-neutral-500">
              Assessment based on verified evidence and adversarial debate
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-neutral-500">
            Assessment:
          </span>

          <span
            id="judge-verdict-badge"
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold tracking-wider ${badgeColor}`}
          >
            <Icon className="h-3.5 w-3.5" />
            {assessment}
          </span>
        </div>
      </div>

      {/* Primary Verdict Banner */}
      <div
        id="verdict-banner-container"
        className={`mb-5 rounded-xl border p-4 ${verdictColor}`}
      >
        <div className="flex items-start gap-3">
          <div className="shrink-0 rounded-xl border border-white/10 bg-black/20 p-2.5">
            <Icon className="h-6 w-6" />
          </div>

          <div className="min-w-0">
            <span className="block text-[10px] font-bold uppercase tracking-[0.18em] opacity-70">
              Verified Adjudication
            </span>

            <h3
              id="verdict-title"
              className="mt-1 text-lg font-bold tracking-tight"
            >
              Verdict: {assessment}
            </h3>

            <p
              id="verdict-expert-summary"
              className="mt-1 text-xs leading-relaxed opacity-90"
            >
              {judgeResult.expert_verification_summary}
            </p>
          </div>
        </div>
      </div>

      {/* Verified Judicial Reasoning */}
      <div className="mb-5">
        <h4 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
          Verified Reasoning
        </h4>

        <div className="rounded-xl border border-neutral-800 bg-[#181818] p-3.5 text-xs leading-relaxed text-neutral-300 sm:text-sm">
          <p id="judge-reasoning-text" className="whitespace-pre-line">
            {judgeResult.reasoning}
          </p>
        </div>
      </div>

      {/* Evidence References */}
      <div className="mb-5 grid grid-cols-1 gap-4 text-xs md:grid-cols-2">
        {/* Supporting Evidence */}
        <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/20 p-3.5">
          <span className="mb-2 block font-semibold text-emerald-300">
            Supporting Evidence IDs
          </span>

          {judgeResult.supporting_evidence_ids &&
          judgeResult.supporting_evidence_ids.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {judgeResult.supporting_evidence_ids.map((id) => (
                <button
                  key={id}
                  type="button"
                  id={`judge-supporting-ev-${id}`}
                  onClick={() =>
                    onSelectEvidenceId && onSelectEvidenceId(id)
                  }
                  className="rounded border border-emerald-700/60 bg-emerald-950/40 px-2 py-0.5 font-mono text-xs font-semibold text-emerald-300 transition-colors hover:border-emerald-400 hover:bg-emerald-900/50"
                >
                  {id}
                </button>
              ))}
            </div>
          ) : (
            <span className="italic text-neutral-500">
              No specific supporting evidence IDs recorded.
            </span>
          )}
        </div>

        {/* Contradictory Evidence */}
        <div className="rounded-xl border border-amber-800/50 bg-amber-950/20 p-3.5">
          <span className="mb-2 block font-semibold text-amber-300">
            Contradictory / Counter-Evidence IDs
          </span>

          {judgeResult.contradictory_evidence_ids &&
          judgeResult.contradictory_evidence_ids.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {judgeResult.contradictory_evidence_ids.map((id) => (
                <button
                  key={id}
                  type="button"
                  id={`judge-contradictory-ev-${id}`}
                  onClick={() =>
                    onSelectEvidenceId && onSelectEvidenceId(id)
                  }
                  className="rounded border border-amber-700/60 bg-amber-950/40 px-2 py-0.5 font-mono text-xs font-semibold text-amber-300 transition-colors hover:border-amber-400 hover:bg-amber-900/50"
                >
                  {id}
                </button>
              ))}
            </div>
          ) : (
            <span className="italic text-neutral-500">
              No contradictory evidence recorded.
            </span>
          )}
        </div>
      </div>

      {/* Limitations and Disclaimer */}
      {judgeResult.limitations &&
        judgeResult.limitations.length > 0 && (
          <div className="rounded-xl border border-neutral-800 bg-[#181818] p-3 text-xs text-neutral-400">
            <span className="mb-2 block font-semibold text-neutral-200">
              Judicial Limitations & Legal Boundary
            </span>

            <ul className="list-inside list-disc space-y-1 pl-1">
              {judgeResult.limitations.map((lim, idx) => (
                <li key={idx} className="leading-snug">
                  {typeof lim === 'string'
                    ? lim
                    : JSON.stringify(lim)}
                </li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );
};