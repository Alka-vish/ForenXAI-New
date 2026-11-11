import React from 'react';
import { Button } from '../components/Button';
import { PageId } from '../components/Navbar';
import {
  ShieldCheck,
  ScanSearch,
  FolderOpen,
  History,
  CheckCircle2,
  ArrowRight,
  Activity,
  ImageIcon,
  Zap,
} from 'lucide-react';

interface DashboardProps {
  onNavigate: (page: PageId) => void;
  hasActiveImage: boolean;
  imageName?: string;
}

export const Dashboard: React.FC<DashboardProps> = ({
  onNavigate,
  hasActiveImage,
  imageName,
}) => {
  return (
    <main
      id="dashboard-main"
      className="relative min-h-[calc(100vh-4rem)] w-full overflow-hidden bg-[#050609] px-4 py-8 text-white sm:px-6 lg:px-8"
    >
      {/* Background Effects */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 top-20 h-96 w-96 rounded-full bg-red-600/10 blur-[130px]" />
        <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-red-900/10 blur-[120px]" />

        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              'linear-gradient(#ef4444 1px, transparent 1px), linear-gradient(90deg, #ef4444 1px, transparent 1px)',
            backgroundSize: '45px 45px',
          }}
        />
      </div>

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-8">

        {/* Header */}
        <section className="relative">
          <div className="mb-4 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.25em] text-red-400">
            <Activity className="h-4 w-4" />
            System Overview
          </div>

          <h1
            id="dashboard-title"
            className="text-4xl font-black tracking-tight text-white sm:text-5xl"
          >
            Forensic{' '}
            <span className="text-red-500">Intelligence</span>
          </h1>

          <p
            id="dashboard-subtitle"
            className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-400 sm:text-base"
          >
            Investigate image authenticity using AI detection and
            forensic signal analysis.
          </p>

          <div className="mt-5 h-px w-32 bg-gradient-to-r from-red-500 to-transparent" />
        </section>

        {/* Main Action Cards */}
        <section className="grid grid-cols-1 gap-5 md:grid-cols-2">

          {/* New Investigation */}
          <div
            id="quick-launch-card"
            className="group relative overflow-hidden rounded-2xl border border-red-500/20 bg-gradient-to-br from-red-950/30 via-[#101116] to-[#090a0f] p-6 shadow-[0_0_35px_rgba(239,68,68,0.04)] transition-all duration-300 hover:border-red-500/60 hover:shadow-[0_0_35px_rgba(239,68,68,0.14)]"
          >
            <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-red-600/10 blur-3xl transition group-hover:bg-red-600/20" />

            <div className="relative flex h-full flex-col justify-between">
              <div>
                <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl border border-red-500/40 bg-red-500/10 shadow-[0_0_20px_rgba(239,68,68,0.12)]">
                  <ScanSearch className="h-7 w-7 text-red-400" />
                </div>

                <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-red-400">
                  Analysis Module
                </p>

                <h2 className="text-2xl font-black text-white">
                  New Investigation
                </h2>

                <p className="mt-3 max-w-sm text-sm leading-relaxed text-slate-400">
                  Upload an image and analyze its visual features,
                  AI-generated probability, and forensic indicators.
                </p>
              </div>

              <div className="mt-8">
                <Button
                  id="dashboard-start-btn"
                  type="button"
                  variant="primary"
                  onClick={() => onNavigate('new-investigation')}
                >
                  Start Investigation
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Current Session */}
          <div
            id="status-card"
            className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-[#151923] via-[#0e1017] to-[#090a0f] p-6 transition-all duration-300 hover:border-slate-500/50"
          >
            <div className="absolute -right-20 -top-20 h-56 w-56 rounded-full bg-blue-500/5 blur-3xl" />

            <div className="relative flex h-full flex-col justify-between">
              <div>
                <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl border border-white/15 bg-white/[0.06]">
                  <FolderOpen className="h-7 w-7 text-slate-300" />
                </div>

                <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                  Investigation Session
                </p>

                <h2 className="text-2xl font-black text-white">
                  Current Session
                </h2>

                <div className="mt-4 flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.03] p-3">
                  <span
                    className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                      hasActiveImage
                        ? 'bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.8)]'
                        : 'bg-slate-500'
                    }`}
                  />

                  <p className="text-sm leading-relaxed text-slate-400">
                    {hasActiveImage
                      ? `Active target: ${imageName || 'Image ready'}`
                      : 'No active image loaded in this session.'}
                  </p>
                </div>
              </div>

              <div className="relative mt-8 flex flex-wrap gap-3">
                <Button
                  id="dashboard-workspace-btn"
                  type="button"
                  variant="outline"
                  onClick={() => onNavigate('workspace')}
                >
                  <FolderOpen className="mr-2 h-4 w-4" />
                  Workspace
                </Button>

                <Button
                  id="dashboard-history-btn"
                  type="button"
                  variant="secondary"
                  onClick={() => onNavigate('history')}
                >
                  <History className="mr-2 h-4 w-4" />
                  History
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* System Status */}
        <section
          id="system-overview"
          className="relative overflow-hidden rounded-2xl border border-red-500/20 bg-gradient-to-br from-[#11131b] to-[#090a0f] p-6 shadow-[0_0_35px_rgba(239,68,68,0.04)]"
        >
          <div className="mb-6 flex items-center justify-between border-b border-white/10 pb-5">
            <div>
              <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.2em] text-red-400">
                Infrastructure
              </p>

              <h2 className="text-sm font-black uppercase tracking-[0.15em] text-slate-200">
                System Status
              </h2>
            </div>

            <span className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-bold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
              Operational
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

            {/* Status */}
            <div className="group rounded-xl border border-emerald-400/20 bg-gradient-to-br from-emerald-400/[0.08] to-transparent p-5 transition hover:border-emerald-400/50">
              <div className="mb-4 flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-xs font-semibold">System Status</span>
              </div>

              <p className="text-lg font-black text-white">
                Operational
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Core services are available
              </p>
            </div>

            {/* Formats */}
            <div className="group rounded-xl border border-blue-400/20 bg-gradient-to-br from-blue-400/[0.08] to-transparent p-5 transition hover:border-blue-400/50">
              <div className="mb-4 flex items-center gap-2 text-blue-400">
                <ImageIcon className="h-5 w-5" />
                <span className="text-xs font-semibold">Supported Formats</span>
              </div>

              <p className="text-lg font-black text-white">
                JPG · PNG · WEBP
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Supported image input formats
              </p>
            </div>

            {/* Pipeline */}
            <div className="group rounded-xl border border-purple-400/20 bg-gradient-to-br from-purple-400/[0.08] to-transparent p-5 transition hover:border-purple-400/50">
              <div className="mb-4 flex items-center gap-2 text-purple-400">
                <Zap className="h-5 w-5" />
                <span className="text-xs font-semibold">Pipeline</span>
              </div>

              <p className="text-lg font-black text-white">
                Forensic Analyzer
              </p>

              <p className="mt-2 text-xs text-slate-500">
                AI and signal processing modules
              </p>
            </div>
          </div>
        </section>

        {/* Disclaimer */}
        <div className="flex items-start gap-3 rounded-xl border border-red-500/15 bg-red-500/[0.04] p-4">
          <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />

          <p className="text-xs leading-relaxed text-slate-400">
            ForenXAI provides AI-assisted analysis. Results represent
            probability-based indicators and should not be treated as
            conclusive proof.
          </p>
        </div>

      </div>
    </main>
  );
};