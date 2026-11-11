import React, { useState } from 'react';
import { ForensicEvidenceItem } from '../types';
import {
  ChevronDown,
  ChevronUp,
  MapPin,
  Tag,
  Info,
  AlertCircle,
} from 'lucide-react';

interface EvidenceLedgerViewProps {
  evidence: ForensicEvidenceItem[];
  highlightId?: string | null;
  onSelectEvidence?: (id: string) => void;
}

export const EvidenceLedgerView: React.FC<EvidenceLedgerViewProps> = ({
  evidence,
  highlightId,
  onSelectEvidence,
}) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);

      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }

      return next;
    });
  };

  const expandAll = () => {
    setExpandedIds(new Set(evidence.map((e) => e.evidence_id)));
  };

  const collapseAll = () => {
    setExpandedIds(new Set());
  };

  if (!evidence || evidence.length === 0) {
    return (
      <div
        id="evidence-ledger-empty"
        className="p-6 bg-[#111111] border border-neutral-800 rounded-xl text-center"
      >
        <p className="text-sm text-neutral-500">
          No forensic evidence items recorded in ledger.
        </p>
      </div>
    );
  }

  return (
    <div
      id="evidence-ledger-container"
      className="bg-[#111111] border border-neutral-800 rounded-xl p-5 shadow-lg shadow-black/10"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <h2
              id="evidence-ledger-heading"
              className="text-base font-semibold text-white"
            >
              Forensic Evidence Ledger
            </h2>

            <span
              id="evidence-count-badge"
              className="px-2 py-0.5 rounded-full text-xs font-mono font-medium bg-[#242424] text-neutral-300"
            >
              {evidence.length} items
            </span>
          </div>

          <p className="text-xs text-neutral-500 mt-0.5">
            Numerical measurements extracted from image data
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            id="expand-all-evidence-btn"
            type="button"
            onClick={expandAll}
            className="text-xs text-neutral-400 hover:text-red-400 font-medium px-2 py-1 rounded hover:bg-red-950/30 transition-colors"
          >
            Expand All
          </button>

          <span className="text-neutral-700">|</span>

          <button
            id="collapse-all-evidence-btn"
            type="button"
            onClick={collapseAll}
            className="text-xs text-neutral-400 hover:text-red-400 font-medium px-2 py-1 rounded hover:bg-red-950/30 transition-colors"
          >
            Collapse All
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {evidence.map((item) => {
          const isExpanded = expandedIds.has(item.evidence_id);
          const isHighlighted = highlightId === item.evidence_id;

          return (
            <div
              key={item.evidence_id}
              id={`evidence-card-${item.evidence_id}`}
              className={`rounded-lg border transition-all ${
                isHighlighted
                  ? 'border-red-500 bg-red-950/20 ring-2 ring-red-500/20'
                  : 'border-neutral-800 bg-[#181818] hover:border-neutral-700'
              }`}
            >
              <div
                className="p-3.5 cursor-pointer flex items-start justify-between gap-3"
                onClick={() => {
                  toggleExpand(item.evidence_id);

                  if (onSelectEvidence) {
                    onSelectEvidence(item.evidence_id);
                  }
                }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center flex-wrap gap-2 mb-1">
                    <span
                      id={`badge-${item.evidence_id}`}
                      className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-red-600 text-white tracking-wide"
                    >
                      {item.evidence_id}
                    </span>

                    <span className="text-xs font-medium text-neutral-300 bg-[#242424] px-2 py-0.5 rounded capitalize">
                      {item.category.replace(/_/g, ' ')}
                    </span>

                    {item.coordinates ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-mono font-medium text-amber-300 bg-amber-950/40 px-2 py-0.5 rounded">
                        <MapPin className="w-3 h-3" />
                        Region {item.coordinates.region_id} [
                        {item.coordinates.grid_position.join(',')}]
                      </span>
                    ) : (
                      <span className="text-[11px] text-neutral-500">
                        Global metric
                      </span>
                    )}
                  </div>

                  <h3 className="text-sm font-semibold text-white mb-1">
                    {item.title}
                  </h3>

                  <p className="text-xs text-neutral-400 leading-relaxed">
                    {item.observation}
                  </p>
                </div>

                <button
                  type="button"
                  aria-label={isExpanded ? 'Collapse' : 'Expand'}
                  className="p-1 rounded text-neutral-500 hover:text-red-400 hover:bg-red-950/30 shrink-0"
                >
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              </div>

              {isExpanded && (
                <div className="px-3.5 pb-3.5 pt-1 border-t border-neutral-800 text-xs space-y-3 bg-[#111111] rounded-b-lg">
                  {/* Measurements */}
                  {item.measurement &&
                    Object.keys(item.measurement).length > 0 && (
                      <div>
                        <span className="font-semibold text-neutral-300 block mb-1.5 flex items-center gap-1">
                          <Tag className="w-3.5 h-3.5 text-red-400" />
                          Empirical Measurements:
                        </span>

                        <div className="bg-[#181818] p-2.5 rounded border border-neutral-800 font-mono text-[11px] text-neutral-300 overflow-x-auto">
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                            {Object.entries(item.measurement).map(
                              ([key, val]) => (
                                <div
                                  key={key}
                                  className="flex justify-between py-0.5 border-b border-neutral-800 last:border-0"
                                >
                                  <span className="text-neutral-500">
                                    {key}:
                                  </span>

                                  <span className="font-semibold text-neutral-200 ml-2">
                                    {typeof val === 'number'
                                      ? val
                                          .toFixed(4)
                                          .replace(/\.?0+$/, '')
                                      : String(val)}
                                  </span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                  {/* Alternative Explanations */}
                  {item.alternative_explanations &&
                    item.alternative_explanations.length > 0 && (
                      <div>
                        <span className="font-semibold text-neutral-300 block mb-1 flex items-center gap-1">
                          <Info className="w-3.5 h-3.5 text-blue-400" />
                          Alternative Explanations:
                        </span>

                        <ul className="list-disc list-inside space-y-0.5 text-neutral-400 pl-1">
                          {item.alternative_explanations.map(
                            (alt, idx) => (
                              <li key={idx} className="leading-snug">
                                {alt}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                  {/* Limitations */}
                  {item.limitations && item.limitations.length > 0 && (
                    <div>
                      <span className="font-semibold text-neutral-300 block mb-1 flex items-center gap-1">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        Scope & Limitations:
                      </span>

                      <ul className="list-disc list-inside space-y-0.5 text-neutral-400 pl-1">
                        {item.limitations.map((lim, idx) => (
                          <li key={idx} className="leading-snug">
                            {lim}
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