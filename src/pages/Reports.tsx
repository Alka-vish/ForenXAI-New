import React from 'react';
import { Button } from '../components/Button';
import { PageId } from '../components/Navbar';
import { InvestigationRecord } from '../types';
import { FileText, ArrowRight, Scale, CheckCircle, AlertTriangle } from 'lucide-react';

interface ReportsProps {
  onNavigate: (page: PageId) => void;
  activeRecord: InvestigationRecord | null;
}

export const Reports: React.FC<ReportsProps> = ({
  onNavigate,
  activeRecord,
}) => {
  const hasRecord = !!activeRecord && !!activeRecord.response;

  const assessment =
    activeRecord?.response?.debate?.judge_result?.assessment || '';

  const normalizedAssessment = assessment.toLowerCase();

  const isAiGenerated =
    normalizedAssessment.includes('ai') ||
    normalizedAssessment.includes('artificial') ||
    normalizedAssessment.includes('synthetic') ||
    normalizedAssessment.includes('fake');

  const isHuman =
    normalizedAssessment.includes('human') ||
    normalizedAssessment.includes('real');

  const verdict = isAiGenerated && !isHuman
    ? 'AI-GENERATED'
    : 'REAL / HUMAN';

  const verdictIsAI = verdict === 'AI-GENERATED';

  return (
    <main
      id="reports-main"
      className="flex-1 w-full max-w-4xl mx-auto p-4 sm:p-6 flex flex-col space-y-6 bg-[#090909]"
    >
      {/* Header */}
      <div className="bg-white/[0.035] backdrop-blur-xl border border-white/[0.10] rounded-2xl p-5 shadow-xl shadow-black/30">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-red-500/[0.08] border border-red-500/20">
            <Scale className="w-5 h-5 text-red-500" />
          </div>

          <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-red-500">
            Forensic Archive
          </span>
        </div>

        <h1
          id="reports-title"
          className="text-2xl font-bold tracking-tight text-white"
        >
          Forensic Reports
        </h1>

        <p
          id="reports-subtitle"
          className="text-xs text-neutral-400 mt-1"
        >
          Investigation results and forensic reporting summaries
        </p>
      </div>

      {/* Reports Content */}
      <div className="border border-white/[0.10] rounded-2xl p-6 bg-white/[0.025] backdrop-blur-xl shadow-xl shadow-black/30">
        {hasRecord ? (
          <div className="space-y-5">

            {/* Active Report */}
            <div className="rounded-xl border border-white/[0.10] bg-white/[0.025] overflow-hidden">

              {/* Report Header */}
              <div className="p-5 border-b border-white/[0.08]">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2.5 rounded-lg bg-red-500/[0.08] border border-red-500/20 shrink-0">
                      <FileText className="w-6 h-6 text-red-500" />
                    </div>

                    <div className="min-w-0">
                      <h2 className="text-sm font-semibold text-white break-words">
                        {activeRecord.imageName}
                      </h2>

                      <p className="text-xs text-neutral-500 font-mono mt-1 break-all">
                        ID: {activeRecord.id}
                      </p>
                    </div>
                  </div>

                  <Button
                    id="reports-view-active-btn"
                    type="button"
                    variant="primary"
                    size="sm"
                    onClick={() => onNavigate('result')}
                  >
                    View Full Report
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                  </Button>

                </div>
              </div>

              {/* Clear Verdict */}
              <div className="p-5">
                <p className="text-[10px] uppercase tracking-[0.18em] text-neutral-500 font-semibold mb-3">
                  Final Classification
                </p>

                <div
                  className={`flex items-center gap-3 rounded-xl px-4 py-4 border ${
                    verdictIsAI
                      ? 'bg-red-500/[0.06] border-red-500/25'
                      : 'bg-emerald-500/[0.06] border-emerald-500/25'
                  }`}
                >
                  <div
                    className={`p-2 rounded-full ${
                      verdictIsAI
                        ? 'bg-red-500/10'
                        : 'bg-emerald-500/10'
                    }`}
                  >
                    {verdictIsAI ? (
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                    )}
                  </div>

                  <div>
                    <p
                      className={`text-lg font-bold tracking-wide ${
                        verdictIsAI
                          ? 'text-red-500'
                          : 'text-emerald-400'
                      }`}
                    >
                      {verdict}
                    </p>

                    <p className="text-xs text-neutral-400 mt-0.5">
                      Based on the final forensic assessment
                    </p>
                  </div>
                </div>

                {/* Assessment */}
                {assessment && (
                  <div className="mt-4">
                    <p className="text-[10px] uppercase tracking-[0.16em] text-neutral-500 font-semibold mb-2">
                      Assessment
                    </p>

                    <p className="text-sm text-neutral-300 leading-relaxed">
                      {assessment}
                    </p>
                  </div>
                )}
              </div>
            </div>

          </div>
        ) : (
          <div className="text-center py-10">
            <div className="p-3 bg-white/[0.035] border border-white/[0.10] rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-neutral-500">
              <FileText className="w-6 h-6" />
            </div>

            <h2 className="text-base font-semibold text-white mb-1">
              No Generated Reports Available
            </h2>

            <p className="text-xs text-neutral-400 max-w-md mx-auto mb-6 leading-relaxed">
              Forensic reports will appear here once an investigation is completed.
            </p>

            <Button
              id="reports-new-btn"
              type="button"
              variant="primary"
              onClick={() => onNavigate('new-investigation')}
            >
              Start New Investigation
            </Button>
          </div>
        )}
      </div>
    </main>
  );
};