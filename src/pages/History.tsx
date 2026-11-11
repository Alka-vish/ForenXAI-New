import React, { useState, useEffect } from 'react';
import { Button } from '../components/Button';
import { PageId } from '../components/Navbar';
import { InvestigationRecord } from '../types';
import {
  getStoredInvestigations,
  deleteInvestigation,
  clearAllInvestigations,
} from '../services/forensicApi';
import {
  History as HistoryIcon,
  Trash2,
  FileText,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Info,
} from 'lucide-react';

interface HistoryProps {
  onNavigate: (page: PageId) => void;
  onSelectRecord: (
    record: InvestigationRecord,
    targetPage: PageId
  ) => void;
}

export const History: React.FC<HistoryProps> = ({
  onNavigate,
  onSelectRecord,
}) => {
  const [records, setRecords] = useState<InvestigationRecord[]>([]);

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = () => {
    const list = getStoredInvestigations();
    setRecords(list);
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteInvestigation(id);
    loadRecords();
  };

  const handleClearAll = () => {
    if (
      window.confirm(
        'Are you sure you want to clear all locally stored investigations?'
      )
    ) {
      clearAllInvestigations();
      loadRecords();
    }
  };

  return (
    <main
      id="history-main"
      className="mx-auto flex w-full max-w-4xl flex-1 flex-col space-y-6 p-4 sm:p-6"
    >
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-neutral-800 bg-[#111111] p-5 shadow-xl shadow-black/20 sm:flex-row sm:items-center">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <HistoryIcon className="h-5 w-5 text-red-400" />

            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-red-400">
              Case Archive
            </span>
          </div>

          <h1
            id="history-title"
            className="text-2xl font-bold tracking-tight text-white"
          >
            Investigation History
          </h1>

          <p
            id="history-subtitle"
            className="mt-1 text-xs text-neutral-500"
          >
            Local archive of previous image forensic examinations and verdicts
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {records.length > 0 && (
            <Button
              id="clear-all-history-btn"
              type="button"
              variant="outline"
              size="sm"
              onClick={handleClearAll}
              className="border-red-800/60 text-red-400 hover:border-red-500 hover:bg-red-950/30"
            >
              <Trash2 className="mr-1.5 h-4 w-4" />
              Clear History
            </Button>
          )}

          <Button
            id="history-new-investigation-btn"
            type="button"
            variant="primary"
            size="sm"
            onClick={() => onNavigate('new-investigation')}
          >
            New Investigation
          </Button>
        </div>
      </div>

      {/* Storage Disclaimer Banner */}
      <div
        id="history-disclaimer"
        className="flex items-start gap-2.5 rounded-xl border border-neutral-800 bg-[#181818] p-3.5 text-xs text-neutral-400"
      >
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />

        <div>
          <span className="font-semibold text-neutral-200">
            Local Browser Storage:
          </span>{' '}
          Data is stored locally in your browser and is not permanently stored
          on a central server.
        </div>
      </div>

      {/* Records List or Empty State */}
      {records.length > 0 ? (
        <div id="history-records-list" className="space-y-3">
          {records.map((rec) => {
            const judgeRes = rec.response?.debate?.judge_result;
            const expertRep = rec.response?.debate?.expert_report;

            const isPermitted =
              expertRep?.recommendation === 'proceed_to_judge' &&
              !!judgeRes;

            const isStopped =
              !rec.response?.debate?.can_proceed ||
              !!rec.response?.debate?.stopping_reason ||
              !isPermitted;

            const assessment =
              isPermitted && judgeRes ? judgeRes.assessment : null;

            let badgeClass =
              'border-amber-800/60 bg-amber-950/30 text-amber-300';
            let StatusIcon = AlertCircle;

            if (isStopped) {
              badgeClass =
                'border-neutral-700 bg-neutral-800/70 text-neutral-400';
              StatusIcon = AlertCircle;
            } else if (assessment === 'REAL') {
              badgeClass =
                'border-emerald-800/60 bg-emerald-950/30 text-emerald-300';
              StatusIcon = CheckCircle2;
            } else if (assessment === 'FAKE') {
              badgeClass =
                'border-red-800/60 bg-red-950/30 text-red-300';
              StatusIcon = XCircle;
            }

            return (
              <div
                key={rec.id}
                id={`history-item-${rec.id}`}
                className="flex flex-col justify-between gap-4 rounded-xl border border-neutral-800 bg-[#111111] p-4 shadow-lg shadow-black/10 transition-all duration-200 hover:border-red-600/50 sm:flex-row sm:items-center"
              >
                <div className="flex min-w-0 items-center gap-3.5">
                  {rec.imagePreview ? (
                    <img
                      src={rec.imagePreview}
                      alt={rec.imageName}
                      className="h-14 w-14 shrink-0 rounded-xl border border-neutral-800 object-cover"
                    />
                  ) : (
                    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-neutral-800 bg-[#181818] text-neutral-600">
                      <FileText className="h-6 w-6" />
                    </div>
                  )}

                  <div className="min-w-0">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <h2 className="max-w-full truncate text-sm font-semibold text-white">
                        {rec.imageName}
                      </h2>

                      <span
                        className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${badgeClass}`}
                      >
                        <StatusIcon className="h-3 w-3" />
                        {isStopped ? 'HALTED' : assessment}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[10px] text-neutral-500 sm:text-xs">
                      <span>
                        {new Date(rec.timestamp).toLocaleString()}
                      </span>

                      <span className="text-neutral-700">•</span>

                      <span>ID: {rec.id}</span>

                      <span className="text-neutral-700">•</span>

                      <span>
                        {rec.response?.evidence?.length || 0} evidence
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-2 self-end sm:self-auto">
                  <Button
                    id={`open-workspace-${rec.id}`}
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => onSelectRecord(rec, 'workspace')}
                  >
                    Workspace
                  </Button>

                  <Button
                    id={`view-report-${rec.id}`}
                    type="button"
                    variant="primary"
                    size="sm"
                    onClick={() => onSelectRecord(rec, 'result')}
                  >
                    Report
                  </Button>

                  <button
                    id={`delete-record-${rec.id}`}
                    type="button"
                    title="Delete record"
                    aria-label={`Delete record ${rec.id}`}
                    onClick={(e) => handleDelete(rec.id, e)}
                    className="rounded-lg border border-neutral-800 p-2 text-neutral-500 transition-colors hover:border-red-700/60 hover:bg-red-950/30 hover:text-red-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div
          id="history-empty-card"
          className="rounded-2xl border border-neutral-800 bg-[#111111] p-10 text-center shadow-xl shadow-black/20"
        >
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-red-600/30 bg-red-950/30 text-red-400">
            <HistoryIcon className="h-7 w-7" />
          </div>

          <h2
            id="history-empty-title"
            className="mb-1 text-base font-semibold text-white"
          >
            No Previous Investigations Found
          </h2>

          <p className="mx-auto mb-5 max-w-sm text-xs leading-relaxed text-neutral-500">
            Completed investigations and forensic debates are archived in your
            local browser for future review.
          </p>

          <Button
            id="history-start-first-btn"
            type="button"
            variant="primary"
            onClick={() => onNavigate('new-investigation')}
          >
            Start First Investigation
          </Button>
        </div>
      )}
    </main>
  );
};