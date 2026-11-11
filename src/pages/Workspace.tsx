import React, { useState } from 'react';
import { PageId } from '../components/Navbar';
import { Button } from '../components/Button';
import { InvestigationRecord } from '../types';
import { InvestigationStages } from '../components/InvestigationStages';
import { EvidenceLedgerView } from '../components/EvidenceLedgerView';
import { DebateTimelineView } from '../components/DebateTimelineView';
import { ExpertVerificationView } from '../components/ExpertVerificationView';
import { JudgeVerdictView } from '../components/JudgeVerdictView';
import { ForensicFeaturesView } from '../components/ForensicFeaturesView';
import {
  FileText,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Layers,
  ArrowRight,
} from 'lucide-react';

interface WorkspaceProps {
  onNavigate: (page: PageId) => void;
  activeRecord: InvestigationRecord | null;
  selectedImage: string | null;
  imageName: string;
  imageSize: number | null;
}

export const Workspace: React.FC<WorkspaceProps> = ({
  onNavigate,
  activeRecord,
  selectedImage,
  imageName,
  imageSize,
}) => {
  const [highlightedEvidenceId, setHighlightedEvidenceId] = useState<string | null>(null);

  if (!activeRecord || !activeRecord.response) {
    return (
      <main
        id="workspace-empty-main"
        className="flex-1 w-full max-w-4xl mx-auto p-6 flex flex-col justify-center items-center text-center bg-[#090909]"
      >
        <div className="w-full max-w-md border border-neutral-800 rounded-xl p-8 bg-[#111111] shadow-lg shadow-black/20">
          <div className="p-3 bg-red-950/30 border border-red-900/40 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-red-500">
            <Layers className="w-6 h-6" />
          </div>

          <h1
            id="workspace-no-active-title"
            className="text-xl font-bold tracking-tight text-white mb-2"
          >
            No Active Investigation Loaded
          </h1>

          <p className="text-xs text-neutral-400 mb-6 leading-relaxed">
            Upload an image in New Investigation to run the multi-module forensic
            analysis and witness the 4-agent LangGraph adversarial debate in real time.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              id="workspace-start-new-btn"
              type="button"
              variant="primary"
              onClick={() => onNavigate('new-investigation')}
            >
              Start New Investigation
            </Button>

            <Button
              id="workspace-view-history-btn"
              type="button"
              variant="outline"
              onClick={() => onNavigate('history')}
            >
              View History
            </Button>
          </div>
        </div>
      </main>
    );
  }

  const { response, timestamp, id: recordId } = activeRecord;
  const { image_information, features, evidence, debate } = response;

  const isStoppedEarly =
    !debate.can_proceed ||
    debate.status === 'insufficient_evidence' ||
    !!debate.stopping_reason;

  const stoppingReason = debate.stopping_reason || debate.message;

  // Determine active stage number (1-7)
  let currentStage = 7;

  if (isStoppedEarly) {
    currentStage = 3;
  } else if (!debate.judge_result) {
    currentStage = debate.expert_report ? 5 : 4;
  }

  const handleSelectEvidence = (id: string) => {
    setHighlightedEvidenceId(id);

    const element = document.getElementById(`evidence-card-${id}`);

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  };

  const imageDisplayUrl = activeRecord.imagePreview || selectedImage;

  return (
    <main
      id="workspace-main"
      className="flex-1 w-full max-w-5xl mx-auto p-4 sm:p-6 flex flex-col space-y-6 bg-[#090909]"
    >
      {/* Top Header & Investigation Control */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#111111] border border-neutral-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <div className="flex items-center gap-4 min-w-0">
          {imageDisplayUrl && (
            <img
              id="workspace-target-thumb"
              src={imageDisplayUrl}
              alt="Investigation target thumbnail"
              className="w-14 h-14 rounded-lg object-cover border border-neutral-700 shrink-0"
            />
          )}

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1
                id="workspace-title"
                className="text-lg font-bold tracking-tight text-white"
              >
                Forensic Investigation Workspace
              </h1>

              <span
                id="record-id-badge"
                className="text-[11px] font-mono text-neutral-400 bg-[#181818] border border-neutral-800 px-2 py-0.5 rounded"
              >
                {recordId}
              </span>
            </div>

            <p className="text-xs text-neutral-400 mt-0.5">
              Target:{' '}
              <span className="font-semibold text-neutral-200">
                {activeRecord.imageName}
              </span>{' '}
              | Recorded:{' '}
              {new Date(timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end md:self-auto">
          <Button
            id="workspace-view-result-btn"
            type="button"
            variant="outline"
            size="sm"
            onClick={() => onNavigate('result')}
          >
            <FileText className="w-4 h-4 mr-1.5" />
            View Forensic Report
          </Button>

          <Button
            id="workspace-new-investigation-btn"
            type="button"
            variant="primary"
            size="sm"
            onClick={() => onNavigate('new-investigation')}
          >
            New Investigation
          </Button>
        </div>
      </div>

      {/* Stage 1-7 Pipeline Indicator */}
      <InvestigationStages
        currentStage={currentStage}
        isStoppedEarly={isStoppedEarly}
        stoppingReason={stoppingReason}
      />

      {/* Stage 1: Image Information */}
      <div
        id="image-information-card"
        className="bg-[#111111] border border-neutral-800 rounded-xl p-5 shadow-lg shadow-black/20"
      >
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-neutral-800">
          <h2
            id="image-info-heading"
            className="text-sm font-semibold text-white"
          >
            Stage 1: Image Metadata & Integrity
          </h2>

          <span className="text-[11px] font-mono text-neutral-500">
            {image_information?.filename}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
          <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
            <span className="text-neutral-500 block">Resolution</span>
            <span className="font-bold text-white font-mono">
              {image_information?.width} × {image_information?.height} px
            </span>
          </div>

          <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
            <span className="text-neutral-500 block">Format</span>
            <span className="font-bold text-white uppercase">
              {image_information?.format || 'UNKNOWN'}
            </span>
          </div>

          <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
            <span className="text-neutral-500 block">Color Mode</span>
            <span className="font-bold text-white">
              {image_information?.color_mode || 'RGB'}
            </span>
          </div>

          <div className="bg-[#181818] p-2.5 rounded border border-neutral-800">
            <span className="text-neutral-500 block">File Size</span>
            <span className="font-bold text-white font-mono">
              {image_information?.file_size_bytes
                ? (image_information.file_size_bytes / 1024).toFixed(1) + ' KB'
                : 'N/A'}
            </span>
          </div>

          <div className="bg-[#181818] p-2.5 rounded border border-neutral-800 col-span-2 sm:col-span-1">
            <span className="text-neutral-500 block">Pipeline Status</span>
            <span className="font-bold text-emerald-400 capitalize">
              {debate.status.replace(/_/g, ' ')}
            </span>
          </div>
        </div>
      </div>

      {/* Stage 2: Extracted Forensic Features */}
      {features && <ForensicFeaturesView features={features} />}

      {/* Stage 3: Evidence Ledger & Sufficiency Check */}
      <div className="space-y-4">
        {/* Sufficiency Status Banner */}
        <div
          id="evidence-sufficiency-card"
          className={`p-4 rounded-xl border flex items-start gap-3 ${
            debate.can_proceed
              ? 'bg-emerald-950/20 border-emerald-900/50 text-emerald-200'
              : 'bg-amber-950/20 border-amber-900/50 text-amber-200'
          }`}
        >
          {debate.can_proceed ? (
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}

          <div className="text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold uppercase tracking-wider text-[11px]">
                Stage 3 Evidence Gate:
              </span>

              <span
                id="evidence-sufficiency-status"
                className={`px-2 py-0.5 rounded font-semibold text-[10px] uppercase ${
                  debate.can_proceed
                    ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-900/50'
                    : 'bg-amber-950/60 text-amber-300 border border-amber-900/50'
                }`}
              >
                {debate.can_proceed
                  ? 'Sufficient Evidence'
                  : 'Insufficient Evidence'}
              </span>
            </div>

            <p
              id="evidence-sufficiency-message"
              className="mt-1 leading-relaxed text-neutral-300"
            >
              {debate.message ||
                (debate.can_proceed
                  ? `Evidence sufficiency verified with ${evidence.length} empirical measurements across ${
                      response.evidence_summary?.evidence_categories?.length || 0
                    } categories.`
                  : stoppingReason)}
            </p>
          </div>
        </div>

        {/* Evidence Ledger */}
        <EvidenceLedgerView
          evidence={evidence}
          highlightId={highlightedEvidenceId}
          onSelectEvidence={setHighlightedEvidenceId}
        />
      </div>

      {/* Early Stopping UI or Stage 4 Debate */}
      {isStoppedEarly ? (
        <div
          id="early-stopping-notice-container"
          className="p-6 rounded-xl border border-amber-900/50 bg-amber-950/20 text-center"
        >
          <div className="p-3 bg-amber-950/40 border border-amber-900/50 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-amber-400">
            <AlertTriangle className="w-6 h-6" />
          </div>

          <h3
            id="early-stopping-heading"
            className="text-base font-bold text-amber-300 mb-1"
          >
            Adversarial Debate Halted Early
          </h3>

          <p
            id="early-stopping-explanation"
            className="text-xs text-amber-200/80 max-w-xl mx-auto mb-4 leading-relaxed"
          >
            {stoppingReason ||
              'The forensic evidence ledger did not contain sufficient verified empirical measurements to conduct a fair adversarial debate.'}
          </p>

          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#181818] border border-amber-900/50 text-xs font-medium text-neutral-300 mb-4">
            <span>Debate turns executed:</span>
            <span className="font-bold text-white font-mono">0 turns</span>
          </div>

          <p className="text-[11px] text-amber-300/70 max-w-md mx-auto">
            Per system safeguards, Expert verification and Judicial assessment
            were safely bypassed because the evidentiary threshold was not met.
            No speculative verdict was created.
          </p>
        </div>
      ) : (
        <>
          {/* Stage 4: Prosecutor and Defence Adversarial Debate */}
          <div id="debate-section" className="space-y-4">
            <DebateTimelineView
              messages={debate.debate_messages}
              onSelectEvidenceId={handleSelectEvidence}
              selectedEvidenceId={highlightedEvidenceId}
            />
          </div>

          {/* Stage 5: Expert Verification */}
          {debate.expert_report && (
            <div id="expert-section" className="space-y-4">
              <ExpertVerificationView
                expertReport={debate.expert_report}
                onSelectEvidenceId={handleSelectEvidence}
              />
            </div>
          )}

          {/* Stage 6 & 7: Judge Assessment */}
          {debate.expert_report?.recommendation === 'proceed_to_judge' &&
          debate.judge_result ? (
            <div id="judge-section" className="space-y-4">
              <JudgeVerdictView
                judgeResult={debate.judge_result}
                onSelectEvidenceId={handleSelectEvidence}
              />
            </div>
          ) : (
            debate.expert_report &&
            debate.expert_report.recommendation !== 'proceed_to_judge' && (
              <div
                id="judge-blocked-notice"
                className="p-4 rounded-xl border border-red-900/60 bg-red-950/20 text-xs text-red-200 flex items-start gap-2.5"
              >
                <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />

                <div>
                  <span className="font-semibold block text-red-400">
                    Judicial Assessment Blocked by Expert Agent:
                  </span>

                  <p className="mt-0.5 leading-relaxed text-neutral-300">
                    The Expert Agent recommended stopping adjudication due to
                    evidentiary discrepancies or unverified claims. No judicial
                    verdict was rendered.
                  </p>
                </div>
              </div>
            )
          )}
        </>
      )}

      {/* Bottom Navigation Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-neutral-800">
        <Button
          id="bottom-new-btn"
          type="button"
          variant="outline"
          onClick={() => onNavigate('new-investigation')}
        >
          Start New Investigation
        </Button>

        <Button 
          id="bottom-report-btn"
          type="button"
          variant="primary"
          onClick={() => onNavigate('result')}
        >
          View Comprehensive Report
          <ArrowRight className="w-4 h-4 ml-1.5" />
        </Button>
      </div>
    </main> 
  );
};