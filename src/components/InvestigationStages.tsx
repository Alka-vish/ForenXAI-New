import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Scale,
  ShieldCheck,
  Layers,
  MessageSquare,
} from 'lucide-react';

export interface StageInfo {
  id: number;
  label: string;
  status: 'completed' | 'active' | 'pending' | 'halted';
  description?: string;
}

interface InvestigationStagesProps {
  currentStage: number;
  isStoppedEarly?: boolean;
  stoppingReason?: string | null;
}

export const InvestigationStages: React.FC<InvestigationStagesProps> = ({
  currentStage,
  isStoppedEarly = false,
  stoppingReason,
}) => {
  const stages: {
    id: number;
    name: string;
    icon: React.ComponentType<{ className?: string }>;
  }[] = [
    { id: 1, name: 'Image Uploaded', icon: FileCheck },
    { id: 2, name: 'Feature Extraction', icon: Layers },
    { id: 3, name: 'Evidence Synthesis', icon: FileCheck },
    { id: 4, name: 'Prosecutor & Defence Debate', icon: MessageSquare },
    { id: 5, name: 'Expert Verification', icon: ShieldCheck },
    { id: 6, name: 'Judge Assessment', icon: Scale },
    { id: 7, name: 'Final Result', icon: CheckCircle2 },
  ];

  return (
    <div
      id="investigation-stages-card"
      className="mb-6 w-full rounded-2xl border border-neutral-800 bg-[#111111] p-5 shadow-xl shadow-black/20"
    >
      <div className="mb-4 flex flex-col justify-between gap-3 border-b border-neutral-800 pb-4 sm:flex-row sm:items-center">
        <div>
          <h2
            id="pipeline-stages-title"
            className="text-sm font-semibold text-white"
          >
            Forensic Investigation Pipeline
          </h2>

          <p className="mt-1 text-xs text-neutral-500">
            Sequential 7-stage verification workflow with deterministic gatekeeping
          </p>
        </div>

        {isStoppedEarly && (
          <span
            id="stages-stopped-badge"
            className="inline-flex w-fit items-center gap-1.5 rounded-full border border-amber-700/50 bg-amber-950/40 px-2.5 py-1 text-xs font-medium text-amber-300"
          >
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
            Halted at Evidence Gate
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-7">
        {stages.map((stage) => {
          const Icon = stage.icon;

          let stageStatus:
            | 'completed'
            | 'active'
            | 'halted'
            | 'pending' = 'pending';

          if (isStoppedEarly) {
            if (stage.id <= 3) {
              stageStatus = 'completed';
            } else if (stage.id === 4) {
              stageStatus = 'halted';
            }
          } else if (stage.id <= currentStage) {
            stageStatus = 'completed';
          }

          let containerClass =
            'border-neutral-800 bg-[#181818] text-neutral-400';
          let iconColor = 'text-neutral-600';
          let badgeText = 'Pending';
          let badgeClass =
            'border-neutral-700 bg-[#111111] text-neutral-500';

          if (stageStatus === 'completed') {
            containerClass =
              'border-emerald-800/60 bg-emerald-950/20 text-emerald-100';
            iconColor = 'text-emerald-400';
            badgeText = 'Complete';
            badgeClass =
              'border-emerald-800/60 bg-emerald-950/50 text-emerald-300';
          } else if (stageStatus === 'halted') {
            containerClass =
              'border-amber-700/60 bg-amber-950/20 text-amber-100';
            iconColor = 'text-amber-400';
            badgeText = 'Halted';
            badgeClass =
              'border-amber-800/60 bg-amber-950/50 text-amber-300';
          }

          return (
            <div
              key={stage.id}
              id={`stage-indicator-${stage.id}`}
              className={`group flex min-h-[112px] flex-col rounded-xl border p-3 text-left transition-all duration-200 hover:border-red-600/50 ${containerClass}`}
            >
              <div className="mb-3 flex items-center justify-between gap-1">
                <span className="font-mono text-[11px] font-medium text-neutral-600">
                  0{stage.id}
                </span>

                <span
                  className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${badgeClass}`}
                >
                  {badgeText}
                </span>
              </div>

              <div className="mt-auto flex items-start gap-2">
                <Icon
                  className={`mt-0.5 h-4 w-4 shrink-0 ${iconColor}`}
                />

                <span className="line-clamp-3 text-xs font-semibold leading-tight">
                  {stage.name}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {isStoppedEarly && stoppingReason && (
        <div
          id="early-stop-banner"
          className="mt-4 flex items-start gap-2 rounded-xl border border-amber-800/60 bg-amber-950/25 p-3 text-xs text-amber-200"
        >
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />

          <div>
            <span className="font-semibold text-amber-300">
              Pipeline Execution Halted:
            </span>{' '}
            {stoppingReason}

            <div className="mt-1 text-amber-400/80">
              Subsequent downstream phases were prevented from executing.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};