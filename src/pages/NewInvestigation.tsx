import React, { useState } from 'react';
import { ImageUpload, isValidImageFile } from '../components/ImageUpload';
import { Button } from '../components/Button';
import {
  uploadImageAndDebate,
  saveInvestigation,
} from '../services/forensicApi';
import {
  DebateApiResponse,
  InvestigationRecord,
} from '../types';
import {
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Shield,
  Scale,
  Layers,
  ScanSearch,
  ArrowRight,
  Activity,
} from 'lucide-react';

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

function dataURLtoFile(
  dataurl: string,
  filename: string
): File | null {
  try {
    const arr = dataurl.split(',');
    if (arr.length < 2) return null;

    const mimeMatch = arr[0].match(/:(.*?);/);
    const mime = mimeMatch ? mimeMatch[1] : 'image/png';

    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);

    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }

    return new File([u8arr], filename, { type: mime });
  } catch {
    return null;
  }
}

interface NewInvestigationProps {
  selectedImage: string | null;
  imageFile: File | null;
  imageName: string;
  imageSize: number | null;
  onSelectImage: (file: File) => void;
  onRemoveImage: () => void;
  onInvestigationFinished: (record: InvestigationRecord) => void;
}

export const NewInvestigation: React.FC<
  NewInvestigationProps
> = ({
  selectedImage,
  imageFile,
  imageName,
  imageSize,
  onSelectImage,
  onRemoveImage,
  onInvestigationFinished,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStepText, setCurrentStepText] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [validationWarning, setValidationWarning] = useState<string | null>(null);

  const handleCustomSelectImage = (file: File) => {
    setErrorMessage(null);
    setValidationWarning(null);

    if (!isValidImageFile(file)) {
      setValidationWarning(
        'Unsupported format. Please upload JPG, JPEG, PNG, or WEBP images.'
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setValidationWarning(
        `File size exceeds 10MB limit (${(
          file.size /
          (1024 * 1024)
        ).toFixed(1)}MB).`
      );
      return;
    }

    onSelectImage(file);
  };

  const handleStartInvestigation = async () => {
    if (!selectedImage) {
      setValidationWarning(
        'Please select an image to begin the investigation.'
      );
      return;
    }

    setErrorMessage(null);
    setValidationWarning(null);
    setIsProcessing(true);

    setCurrentStepText('Uploading image to forensic engine...');

    let stepTimer1: ReturnType<typeof setTimeout> | undefined;
    let stepTimer2: ReturnType<typeof setTimeout> | undefined;
    let stepTimer3: ReturnType<typeof setTimeout> | undefined;

    try {
      let fileToSend: File | null = imageFile;

      if (
        !fileToSend &&
        selectedImage.startsWith('data:')
      ) {
        fileToSend = dataURLtoFile(
          selectedImage,
          imageName || 'investigation_target.png'
        );
      }

      if (!fileToSend) {
        setIsProcessing(false);
        setValidationWarning(
          'Please select or upload a valid image file.'
        );
        return;
      }

      if (fileToSend.size > MAX_FILE_SIZE_BYTES) {
        throw new Error(
          `Image size (${(
            fileToSend.size /
            (1024 * 1024)
          ).toFixed(1)}MB) exceeds the 10MB limit.`
        );
      }

      stepTimer1 = setTimeout(() => {
        setCurrentStepText(
          'Extracting visual and forensic features...'
        );
      }, 1500);

      stepTimer2 = setTimeout(() => {
        setCurrentStepText(
          'Analyzing image authenticity indicators...'
        );
      }, 3500);

      stepTimer3 = setTimeout(() => {
        setCurrentStepText(
          'Running the four-agent verification pipeline...'
        );
      }, 6000);

      const debateResponse: DebateApiResponse =
        await uploadImageAndDebate(fileToSend);

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      setCurrentStepText(
        'Analysis completed. Preparing your report...'
      );

      const uniqueId = `inv_${Date.now().toString(36)}_${Math.random()
        .toString(36)
        .substring(2, 7)}`;

      const timestamp = new Date().toISOString();

      const record: InvestigationRecord = {
        id: uniqueId,
        timestamp,
        imageName: fileToSend.name,
        imageSize: fileToSend.size,
        imagePreview: selectedImage,
        response: debateResponse,
      };

      saveInvestigation(record);

      setTimeout(() => {
        setIsProcessing(false);
        onInvestigationFinished(record);
      }, 600);
    } catch (err: any) {
      if (stepTimer1) clearTimeout(stepTimer1);
      if (stepTimer2) clearTimeout(stepTimer2);
      if (stepTimer3) clearTimeout(stepTimer3);

      setIsProcessing(false);

      setErrorMessage(
        err?.message ||
          'An unexpected error occurred while communicating with the forensic engine.'
      );
    }
  };

  return (
    <main
      id="new-investigation-main"
      className="relative min-h-[calc(100vh-4rem)] w-full overflow-hidden bg-[#050609] px-4 py-8 text-white sm:px-6 lg:px-8"
    >
      {/* Background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 top-20 h-96 w-96 rounded-full bg-red-600/10 blur-[130px]" />
        <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-red-900/10 blur-[120px]" />

        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(#ef4444 1px, transparent 1px), linear-gradient(90deg, #ef4444 1px, transparent 1px)',
            backgroundSize: '45px 45px',
          }}
        />
      </div>

      <div className="relative mx-auto flex w-full max-w-3xl flex-col gap-6">

        {/* Header */}
        <section className="text-center">
          <div className="mb-4 flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-[0.25em] text-red-400">
            <Activity className="h-4 w-4" />
            Analysis Module
          </div>

          <h1
            id="page-title"
            className="text-3xl font-black tracking-tight text-white sm:text-4xl"
          >
            New <span className="text-red-500">Investigation</span>
          </h1>

          <p
            id="page-subtitle"
            className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-slate-400"
          >
            Upload an image to analyze its authenticity using
            AI detection and forensic signal processing.
          </p>

          <div className="mx-auto mt-5 h-px w-28 bg-gradient-to-r from-transparent via-red-500 to-transparent" />
        </section>

        {/* Validation Warning */}
        {validationWarning && (
          <div
            id="validation-warning"
            className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs text-amber-200"
          >
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
            <span>{validationWarning}</span>
          </div>
        )}

        {/* API Error */}
        {errorMessage && (
          <div
            id="api-error-alert"
            className="flex flex-col gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-200"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />

              <div>
                <span className="block font-bold text-red-300">
                  Investigation Error
                </span>

                <p className="mt-1 leading-relaxed">
                  {errorMessage}
                </p>
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                id="retry-investigation-btn"
                type="button"
                variant="outline"
                size="sm"
                onClick={handleStartInvestigation}
              >
                Retry Investigation
              </Button>
            </div>
          </div>
        )}

        {/* Main Content */}
        {isProcessing ? (
          <section
            id="processing-container"
            className="relative overflow-hidden rounded-2xl border border-red-500/25 bg-gradient-to-br from-red-950/20 via-[#101116] to-[#090a0f] p-6 shadow-[0_0_40px_rgba(239,68,68,0.06)] sm:p-8"
          >
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-red-600/10 blur-3xl" />

            <div className="relative flex flex-col items-center text-center">
              <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-red-500/40 bg-red-500/10 shadow-[0_0_25px_rgba(239,68,68,0.15)]">
                <Loader2 className="h-8 w-8 animate-spin text-red-400" />
              </div>

              <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-red-400">
                Processing Target
              </p>

              <h2
                id="processing-status-title"
                className="text-xl font-black text-white"
              >
                Investigation in Progress
              </h2>

              <p
                id="processing-step-desc"
                className="mt-3 max-w-md text-sm leading-relaxed text-slate-400"
              >
                {currentStepText}
              </p>

              {/* Pipeline */}
              <div className="mt-8 grid w-full max-w-md grid-cols-2 gap-3">
                {[
                  {
                    label: 'Feature Extraction',
                    icon: ScanSearch,
                    color: 'text-red-400',
                  },
                  {
                    label: 'Evidence Synthesis',
                    icon: Layers,
                    color: 'text-blue-400',
                  },
                  {
                    label: 'Expert Verification',
                    icon: Shield,
                    color: 'text-emerald-400',
                  },
                  {
                    label: 'Judge Assessment',
                    icon: Scale,
                    color: 'text-purple-400',
                  },
                ].map((step) => {
                  const Icon = step.icon;

                  return (
                    <div
                      key={step.label}
                      className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] p-3 text-left"
                    >
                      <Icon className={`h-4 w-4 shrink-0 ${step.color}`} />

                      <span className="text-[11px] font-semibold text-slate-300">
                        {step.label}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="mt-8 flex items-center gap-2 text-[11px] text-slate-500">
                <Loader2 className="h-3 w-3 animate-spin" />
                Please keep this window open
              </div>
            </div>
          </section>
        ) : (
          <>
            {/* Upload Card */}
            <section className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#14161e] to-[#090a0f] p-5 shadow-[0_0_35px_rgba(239,68,68,0.04)] sm:p-6">
              <div className="mb-5 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-red-500/30 bg-red-500/10">
                  <ScanSearch className="h-5 w-5 text-red-400" />
                </div>

                <div>
                  <h2 className="text-base font-bold text-white">
                    Upload Target Image
                  </h2>

                  <p className="mt-0.5 text-xs text-slate-500">
                    JPG, PNG, JPEG, or WEBP · Maximum 10MB
                  </p>
                </div>
              </div>

              <ImageUpload
                selectedImage={selectedImage}
                imageName={imageName}
                imageSize={imageSize}
                onSelectImage={handleCustomSelectImage}
                onRemoveImage={onRemoveImage}
              />
            </section>

            {/* Action */}
            <section className="flex flex-col items-center gap-3">
              <Button
                id="start-investigation-btn"
                type="button"
                variant="primary"
                size="lg"
                fullWidth
                disabled={!selectedImage || isProcessing}
                onClick={handleStartInvestigation}
              >
                <ScanSearch className="mr-2 h-5 w-5" />
                Start Investigation
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>

              <div className="flex items-center gap-2 text-center text-[11px] text-slate-500">
                <Shield className="h-3.5 w-3.5 text-red-400" />
                AI-assisted forensic analysis
              </div>
            </section>

            {/* Information */}
            <div className="flex items-start gap-3 rounded-xl border border-red-500/15 bg-red-500/[0.04] p-4">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />

              <p className="text-xs leading-relaxed text-slate-400">
                Your image is analyzed using multiple visual and
                statistical indicators. Results represent probabilities,
                not conclusive proof of authenticity.
              </p>
            </div>
          </>
        )}
      </div>
    </main>
  );
};