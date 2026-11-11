import React from 'react';
import { DebateMessage } from '../types';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  CornerDownRight,
} from 'lucide-react';

interface DebateTimelineViewProps {
  messages: DebateMessage[];
  onSelectEvidenceId?: (id: string) => void;
  selectedEvidenceId?: string | null;
}

export const DebateTimelineView: React.FC<DebateTimelineViewProps> = ({
  messages,
  onSelectEvidenceId,
  selectedEvidenceId,
}) => {
  if (!messages || messages.length === 0) {
    return (
      <div
        id="debate-timeline-empty"
        className="p-6 bg-[#111111] border border-neutral-800 rounded-xl text-center"
      >
        <p className="text-sm text-neutral-500">
          No debate messages recorded in this investigation.
        </p>
      </div>
    );
  }

  return (
    <div
      id="debate-timeline-container"
      className="bg-[#111111] border border-neutral-800 rounded-xl p-5 shadow-lg shadow-black/10"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5 pb-3 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <h2
              id="debate-timeline-heading"
              className="text-base font-semibold text-white"
            >
              Prosecutor & Defence Debate
            </h2>

            <span
              id="turn-count-badge"
              className="px-2 py-0.5 rounded-full text-xs font-mono font-medium bg-[#242424] text-neutral-300"
            >
              {messages.length} messages (4 turns)
            </span>
          </div>

          <p className="text-xs text-neutral-500 mt-0.5">
            Evidence-based adversarial analysis
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {messages.map((msg, idx) => {
          const isProsecutor = msg.agent === 'prosecutor';
          const agentTitle = isProsecutor ? 'Prosecutor' : 'Defence';
          const turnLabel = `${agentTitle} ${msg.turn}`;

          return (
            <div
              key={`${msg.agent}-${msg.turn}-${idx}`}
              id={`debate-message-${idx + 1}`}
              className={`rounded-xl border p-4 transition-all ${
                isProsecutor
                  ? 'border-red-900/70 bg-red-950/20'
                  : 'border-blue-900/70 bg-blue-950/20'
              }`}
            >
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-2 border-b border-neutral-800">
                <div className="flex items-center gap-2">
                  <span
                    id={`agent-icon-${idx + 1}`}
                    className={`p-1 rounded-md ${
                      isProsecutor
                        ? 'bg-red-900/40 text-red-400'
                        : 'bg-blue-900/40 text-blue-400'
                    }`}
                  >
                    {isProsecutor ? (
                      <ShieldAlert className="w-4 h-4" />
                    ) : (
                      <ShieldCheck className="w-4 h-4" />
                    )}
                  </span>

                  <span
                    id={`turn-label-${idx + 1}`}
                    className={`text-xs font-bold uppercase tracking-wider ${
                      isProsecutor ? 'text-red-400' : 'text-blue-400'
                    }`}
                  >
                    {turnLabel}
                  </span>

                  <span className="text-[11px] text-neutral-500 font-mono">
                    Sequence #{idx + 1}
                  </span>
                </div>

                {/* Evidence IDs Cited */}
                <div className="flex items-center flex-wrap gap-1.5">
                  <span className="text-[11px] text-neutral-500 font-medium">
                    Evidence:
                  </span>

                  {msg.supporting_evidence_ids &&
                  msg.supporting_evidence_ids.length > 0 ? (
                    msg.supporting_evidence_ids.map((id) => {
                      const isSelected = selectedEvidenceId === id;

                      return (
                        <button
                          key={id}
                          id={`msg-${idx + 1}-evidence-${id}`}
                          type="button"
                          onClick={() =>
                            onSelectEvidenceId && onSelectEvidenceId(id)
                          }
                          className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold transition-colors ${
                            isSelected
                              ? 'bg-red-600 text-white ring-2 ring-red-400/50'
                              : 'bg-[#242424] border border-neutral-700 text-neutral-300 hover:border-red-500 hover:text-red-300'
                          }`}
                        >
                          {id}
                        </button>
                      );
                    })
                  ) : (
                    <span className="text-[11px] text-neutral-500 italic">
                      None
                    </span>
                  )}
                </div>
              </div>

              {/* Argument Text */}
              <div className="text-xs sm:text-sm text-neutral-300 leading-relaxed space-y-2">
                <p
                  id={`argument-text-${idx + 1}`}
                  className="whitespace-pre-line"
                >
                  {msg.argument}
                </p>
              </div>

              {/* Uncertainties & Alternative Explanations */}
              {((msg.uncertainties && msg.uncertainties.length > 0) ||
                (msg.alternative_explanations &&
                  msg.alternative_explanations.length > 0)) && (
                <div className="mt-3 pt-2.5 border-t border-neutral-800 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {msg.uncertainties &&
                    msg.uncertainties.length > 0 && (
                      <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
                        <span className="font-semibold text-neutral-300 block mb-1 flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                          Technical Uncertainties:
                        </span>

                        <ul className="list-disc list-inside space-y-0.5 text-neutral-400">
                          {msg.uncertainties.map((u, i) => (
                            <li key={i} className="leading-snug">
                              {typeof u === 'string'
                                ? u
                                : JSON.stringify(u)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {msg.alternative_explanations &&
                    msg.alternative_explanations.length > 0 && (
                      <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
                        <span className="font-semibold text-neutral-300 block mb-1 flex items-center gap-1">
                          <CornerDownRight className="w-3.5 h-3.5 text-blue-400" />
                          Alternative Explanations:
                        </span>

                        <ul className="list-disc list-inside space-y-0.5 text-neutral-400">
                          {msg.alternative_explanations.map((a, i) => (
                            <li key={i} className="leading-snug">
                              {typeof a === 'string'
                                ? a
                                : JSON.stringify(a)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};