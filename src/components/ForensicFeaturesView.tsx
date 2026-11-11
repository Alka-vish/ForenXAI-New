import React, { useState } from 'react';
import { Layers, Activity, Cpu, HardDrive, Zap, Eye } from 'lucide-react';

interface ForensicFeaturesViewProps {
  features?: {
    spatial_features?: Record<string, any>;
    noise_analysis?: Record<string, any>;
    frequency_analysis?: Record<string, any>;
    srm_analysis?: Record<string, any>;
    wavelet_analysis?: Record<string, any>;
    compression_analysis?: Record<string, any>;
    recompression_ela_analysis?: Record<string, any>;
    ai_detection?: Record<string, any>;
  };
}

export const ForensicFeaturesView: React.FC<ForensicFeaturesViewProps> = ({
  features,
}) => {
  const [activeTab, setActiveTab] = useState<string>('spatial');

  if (!features) {
    return null;
  }

  const tabs = [
    {
      id: 'spatial',
      label: 'Spatial & Gradients',
      data: features.spatial_features,
      icon: Eye,
    },
    {
      id: 'noise',
      label: 'Noise Residuals',
      data: features.noise_analysis,
      icon: Activity,
    },
    {
      id: 'frequency',
      label: 'Frequency / FFT',
      data: features.frequency_analysis,
      icon: Zap,
    },
    {
      id: 'srm',
      label: 'SRM Filters',
      data: features.srm_analysis,
      icon: Layers,
    },
    {
      id: 'wavelet',
      label: 'DWT Wavelet',
      data: features.wavelet_analysis,
      icon: Layers,
    },
    {
      id: 'compression',
      label: 'Compression / ELA',
      data:
        features.recompression_ela_analysis ||
        features.compression_analysis,
      icon: HardDrive,
    },
    {
      id: 'ai',
      label: 'AI Artifact Detector',
      data: features.ai_detection,
      icon: Cpu,
    },
  ].filter((tab) => tab.data && Object.keys(tab.data).length > 0);

  const currentTabData =
    tabs.find((tab) => tab.id === activeTab)?.data || tabs[0]?.data;

  return (
    <div
      id="forensic-features-card"
      className="mb-6 rounded-xl border border-neutral-800 bg-[#111111] p-5 shadow-lg shadow-black/20"
    >
      <div className="mb-4 flex flex-col justify-between gap-2 border-b border-neutral-800 pb-3 sm:flex-row sm:items-center">
        <div>
          <h2
            id="features-title"
            className="text-base font-semibold text-white"
          >
            Extracted Forensic Features
          </h2>

          <p className="mt-0.5 text-xs text-neutral-500">
            Deterministic spatial, frequency, residual, and compression matrices
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-4 flex flex-wrap gap-1.5 border-b border-neutral-800 pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
                isActive
                  ? 'border-red-600 bg-red-600 text-white shadow-lg shadow-red-950/30'
                  : 'border-neutral-800 bg-[#181818] text-neutral-400 hover:border-red-600/60 hover:bg-red-950/30 hover:text-red-300'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {currentTabData ? (
        <div
          id="feature-data-table"
          className="rounded-lg border border-neutral-800 bg-[#181818] p-3.5 font-mono text-xs"
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(currentTabData).map(([key, value]) => {
              if (
                typeof value === 'object' &&
                value !== null &&
                !Array.isArray(value)
              ) {
                return (
                  <div
                    key={key}
                    className="col-span-full rounded border border-neutral-800 bg-[#111111] p-2.5"
                  >
                    <span className="mb-1 block font-semibold capitalize text-neutral-300">
                      {key.replace(/_/g, ' ')}:
                    </span>

                    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                      {Object.entries(value).map(([subK, subV]) => (
                        <div key={subK} className="text-[11px]">
                          <span className="block truncate text-neutral-500">
                            {subK}:
                          </span>

                          <span className="font-semibold text-red-300">
                            {typeof subV === 'number'
                              ? subV.toFixed(4).replace(/\.?0+$/, '')
                              : String(subV)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              return (
                <div
                  key={key}
                  className="flex flex-col justify-between rounded border border-neutral-800 bg-[#111111] p-2.5 transition-colors hover:border-red-600/50"
                >
                  <span
                    className="truncate text-[11px] text-neutral-500"
                    title={key}
                  >
                    {key.replace(/_/g, ' ')}
                  </span>

                  <span className="mt-1 font-bold text-white">
                    {typeof value === 'number'
                      ? value.toFixed(4).replace(/\.?0+$/, '')
                      : Array.isArray(value)
                      ? `[${value.length} items]`
                      : String(value)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-neutral-800 bg-[#181818] p-4 text-center text-xs text-neutral-500">
          No feature attributes recorded for this module.
        </div>
      )}
    </div>
  );
};