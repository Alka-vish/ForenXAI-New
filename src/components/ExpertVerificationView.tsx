import React from 'react';
import { ExpertReport, ContradictionItem } from '../types';
import {
  ShieldCheck,
  CheckCircle2,
  AlertOctagon,
  FileCheck,
  HelpCircle,
  Scale,
  AlertTriangle,
} from 'lucide-react';

interface ExpertVerificationViewProps {
  expertReport: ExpertReport | null;
  onSelectEvidenceId?: (id: string) => void;
}

export const ExpertVerificationView: React.FC<
  ExpertVerificationViewProps
> = ({ expertReport, onSelectEvidenceId }) => {
  if (!expertReport) {
    return null;
  }

  const isVerified = expertReport.status === 'verified';
  const canProceed = expertReport.recommendation === 'proceed_to_judge';
  const hasHallucinations =
    expertReport.hallucination_flags &&
    expertReport.hallucination_flags.length > 0;

  return (
    <div
      id="expert-verification-card"
      className="bg-[#111111] border border-neutral-800 rounded-xl p-5 shadow-lg shadow-black/10"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />

            <h2
              id="expert-verification-heading"
              className="text-base font-semibold text-white"
            >
              Expert Agent Verification Report
            </h2>
          </div>

          <p className="text-xs text-neutral-500 mt-0.5">
            Audit of debate claims and evidence consistency
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span
            id="expert-status-badge"
            className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
              isVerified
                ? 'bg-emerald-950/50 text-emerald-300 border border-emerald-800'
                : 'bg-amber-950/50 text-amber-300 border border-amber-800'
            }`}
          >
            {expertReport.status.replace(/_/g, ' ')}
          </span>

          <span
            id="expert-recommendation-badge"
            className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
              canProceed
                ? 'bg-blue-950/50 text-blue-300 border border-blue-800'
                : 'bg-red-950/50 text-red-300 border border-red-800'
            }`}
          >
            {canProceed ? 'Proceed to Judge' : 'Stop Investigation'}
          </span>
        </div>
      </div>

      {/* Grid Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4 text-xs">
        <div className="bg-[#181818] p-3 rounded-lg border border-neutral-800">
          <span className="text-neutral-500 block mb-1">
            Evidence Sufficiency
          </span>

          <span
            className={`font-semibold ${
              expertReport.evidence_sufficient
                ? 'text-emerald-400'
                : 'text-amber-400'
            }`}
          >
            {expertReport.evidence_sufficient
              ? 'Sufficient for Adjudication'
              : 'Insufficient'}
          </span>
        </div>

        <div className="bg-[#181818] p-3 rounded-lg border border-neutral-800">
          <span className="text-neutral-500 block mb-1">
            Evidence Citations Audited
          </span>

          <span className="font-semibold font-mono text-neutral-200">
            {expertReport.checked_evidence_ids
              ? expertReport.checked_evidence_ids.length
              : 0}{' '}
            items checked
          </span>
        </div>

        <div className="bg-[#181818] p-3 rounded-lg border border-neutral-800">
          <span className="text-neutral-500 block mb-1">
            Hallucination / Fabrication Flags
          </span>

          <span
            className={`font-semibold ${
              hasHallucinations ? 'text-red-400' : 'text-emerald-400'
            }`}
          >
            {hasHallucinations
              ? `${expertReport.hallucination_flags.length} Flagged`
              : '0 Flags'}
          </span>
        </div>
      </div>

      {/* Explanation */}
      {expertReport.explanation && (
        <div
          id="expert-explanation-box"
          className="mb-4 p-3 rounded-lg bg-[#181818] border border-neutral-800 text-xs text-neutral-400 leading-relaxed"
        >
          <span className="font-semibold text-neutral-200 block mb-1 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Verification Assessment:
          </span>

          {expertReport.explanation}
        </div>
      )}

      {/* Evidence IDs Checked */}
      {expertReport.checked_evidence_ids &&
        expertReport.checked_evidence_ids.length > 0 && (
          <div className="mb-4">
            <span className="text-xs font-semibold text-neutral-300 block mb-1.5 flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5 text-red-400" />
              Evidence IDs Verified:
            </span>

            <div className="flex flex-wrap gap-1.5">
              {expertReport.checked_evidence_ids.map((id) => (
                <button
                  key={id}
                  type="button"
                  id={`expert-checked-evidence-${id}`}
                  onClick={() =>
                    onSelectEvidenceId && onSelectEvidenceId(id)
                  }
                  className="px-2 py-0.5 rounded bg-[#242424] hover:bg-red-950/40 border border-neutral-700 hover:border-red-500 font-mono text-xs text-neutral-300 hover:text-red-300 transition-colors cursor-pointer"
                >
                  {id}
                </button>
              ))}
            </div>
          </div>
        )}

      {/* Hallucinations */}
      {hasHallucinations && (
        <div
          id="hallucination-alert-box"
          className="mb-4 p-3 rounded-lg bg-red-950/30 border border-red-800 text-xs text-red-300"
        >
          <div className="font-semibold flex items-center gap-1.5 mb-1 text-red-400">
            <AlertOctagon className="w-4 h-4" />
            Hallucination Intercept Triggered:
          </div>

          <ul className="list-disc list-inside space-y-1 text-red-300 pl-1">
            {expertReport.hallucination_flags.map((flag, idx) => (
              <li key={idx}>
                Turn {flag.turn} ({flag.agent}): {flag.details} (Evidence ID:{' '}
                {flag.evidence_id})
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Contradictions */}
      {expertReport.contradictions &&
        expertReport.contradictions.length > 0 && (
          <div id="expert-contradictions-section" className="mb-4">
            <div className="text-xs font-semibold text-amber-300 mb-2 flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-amber-400" />

              <span>
                Evaluated Contradictions (
                {expertReport.contradictions.length}):
              </span>
            </div>

            <div className="space-y-2.5">
              {expertReport.contradictions.map((c, idx) => {
                if (typeof c === 'string') {
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-amber-950/30 border border-amber-800 text-xs text-amber-300"
                    >
                      {c}
                    </div>
                  );
                }

                const item = c as ContradictionItem;

                return (
                  <div
                    key={idx}
                    id={`expert-contradiction-item-${idx}`}
                    className="p-3 rounded-lg bg-[#181818] border border-amber-900/70 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2 border-b border-neutral-800 pb-1.5">
                      <span className="font-semibold text-amber-300 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block" />

                        {item.point || `Discrepancy Point #${idx + 1}`}
                      </span>

                      {item.status && (
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono font-medium tracking-wide bg-amber-950/50 text-amber-300 border border-amber-800">
                          {item.status.replace(/_/g, ' ')}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11.5px]">
                      {item.prosecutor_claim && (
                        <div className="p-2 rounded bg-red-950/30 border border-red-900/60">
                          <span className="font-semibold text-red-300 block mb-0.5">
                            Prosecution Argument:
                          </span>

                          <p className="text-red-400 leading-relaxed">
                            {item.prosecutor_claim}
                          </p>
                        </div>
                      )}

                      {item.defence_claim && (
                        <div className="p-2 rounded bg-blue-950/30 border border-blue-900/60">
                          <span className="font-semibold text-blue-300 block mb-0.5">
                            Defence Counter-Argument:
                          </span>

                          <p className="text-blue-400 leading-relaxed">
                            {item.defence_claim}
                          </p>
                        </div>
                      )}
                    </div>

                    {item.expert_resolution && (
                      <div className="p-2 rounded bg-emerald-950/30 border border-emerald-800 text-emerald-300">
                        <span className="font-semibold text-emerald-400 block mb-0.5">
                          Expert Resolution:
                        </span>

                        <p className="leading-relaxed">
                          {item.expert_resolution}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

      {/* Reliability Concerns */}
      {expertReport.reliability_concerns &&
        expertReport.reliability_concerns.length > 0 && (
          <div className="mb-3 p-3 rounded-lg bg-[#181818] border border-neutral-800 text-xs text-neutral-400">
            <div className="font-semibold mb-1 text-neutral-300 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              Reliability Concerns:
            </div>

            <ul className="list-disc list-inside space-y-1 text-neutral-400 pl-1">
              {expertReport.reliability_concerns.map((rc, idx) => (
                <li key={idx}>
                  {typeof rc === 'string' ? rc : JSON.stringify(rc)}
                </li>
              ))}
            </ul>
          </div>
        )}

      {/* Missing Information */}
      {expertReport.missing_information &&
        expertReport.missing_information.length > 0 && (
          <div className="mb-3 p-3 rounded-lg bg-[#181818] border border-neutral-800 text-xs text-neutral-400">
            <div className="font-semibold mb-1 text-neutral-300 flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5 text-neutral-500" />
              Missing Information:
            </div>

            <ul className="list-disc list-inside space-y-1 text-neutral-400 pl-1">
              {expertReport.missing_information.map((m, idx) => (
                <li key={idx}>
                  {typeof m === 'string' ? m : JSON.stringify(m)}
                </li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );
};