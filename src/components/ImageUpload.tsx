import React, { useRef, useState } from 'react';
import { Image as ImageIcon, UploadCloud, X, FileImage } from 'lucide-react';
import { Button } from './Button';

export const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
export const ACCEPTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k, 2));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function isValidImageFile(file: File): boolean {
  if (ACCEPTED_TYPES.includes(file.type)) return true;

  const lowerName = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
}

interface ImageUploadProps {
  selectedImage: string | null;
  imageName: string;
  imageSize: number | null;
  onSelectImage: (file: File) => void;
  onRemoveImage: () => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  selectedImage,
  imageName,
  imageSize,
  onSelectImage,
  onRemoveImage,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = (file?: File) => {
    if (!file) return;

    if (isValidImageFile(file)) {
      setError(null);
      onSelectImage(file);
    } else {
      setError('Invalid file type. Please upload JPG, PNG, or WEBP.');
    }
  };

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    processFile(e.target.files?.[0]);

    // Allow selecting the same file again
    e.target.value = '';
  };

  const handleChooseImage = () => {
    fileInputRef.current?.click();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    processFile(e.dataTransfer.files?.[0]);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  return (
    <div
      id="upload-section"
      className={`mb-6 w-full rounded-2xl border bg-[#111111] p-5 shadow-xl shadow-black/20 transition-all duration-300 sm:p-6 ${
        isDragging
          ? 'border-red-500 bg-red-950/20 shadow-red-950/20'
          : 'border-neutral-800 hover:border-red-600/50'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-red-600/30 bg-red-950/40">
          <ImageIcon className="h-5 w-5 text-red-400" />
        </div>

        <div>
          <p
            id="upload-instruction"
            className="text-sm font-semibold text-white"
          >
            Upload an image for analysis
          </p>

          <p
            id="supported-formats"
            className="mt-0.5 text-xs text-neutral-500"
          >
            JPG, JPEG, PNG, or WEBP
          </p>
        </div>
      </div>

      <input
        id="image-file-input"
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFileChange}
      />

      {!selectedImage ? (
        <div
          className={`group flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed px-5 py-8 text-center transition-all duration-300 ${
            isDragging
              ? 'border-red-500 bg-red-950/30'
              : 'border-neutral-700 bg-[#181818] hover:border-red-500/70 hover:bg-red-950/10'
          }`}
        >
          <div
            className={`mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border transition-all duration-300 ${
              isDragging
                ? 'border-red-500 bg-red-600/20'
                : 'border-neutral-700 bg-[#111111] group-hover:border-red-500/60 group-hover:bg-red-950/30'
            }`}
          >
            <UploadCloud
              className={`h-7 w-7 transition-colors ${
                isDragging
                  ? 'text-red-400'
                  : 'text-neutral-500 group-hover:text-red-400'
              }`}
            />
          </div>

          <h3 className="text-sm font-medium text-neutral-200">
            {isDragging ? 'Drop your image here' : 'Drag and drop your image'}
          </h3>

          <p className="mt-1 text-xs text-neutral-500">
            or choose a file from your device
          </p>

          <Button
            id="choose-image-btn"
            type="button"
            variant="outline"
            onClick={handleChooseImage}
            className="mt-5"
          >
            <UploadCloud className="mr-2 h-4 w-4" />
            Choose Image
          </Button>

          <div className="mt-5 flex items-center gap-2 text-[10px] uppercase tracking-wider text-neutral-600">
            <span className="h-1 w-1 rounded-full bg-red-500" />
            Secure local upload
            <span className="h-1 w-1 rounded-full bg-red-500" />
            Image forensic analysis
          </div>
        </div>
      ) : (
        <div
          id="image-preview-container"
          className="rounded-xl border border-neutral-800 bg-[#181818] p-4"
        >
          <div className="relative flex min-h-52 items-center justify-center overflow-hidden rounded-xl border border-neutral-800 bg-[#090909] p-3">
            <img
              id="selected-image-preview"
              src={selectedImage}
              alt="Selected preview"
              className="max-h-72 max-w-full rounded-lg object-contain"
            />

            <div className="absolute right-3 top-3 rounded-lg border border-red-600/30 bg-black/70 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-red-300 backdrop-blur-sm">
              Preview
            </div>
          </div>

          <div
            id="image-metadata"
            className="mt-4 flex items-center gap-3"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-neutral-700 bg-[#111111]">
              <FileImage className="h-5 w-5 text-red-400" />
            </div>

            <div className="min-w-0 flex-1">
              <span
                id="selected-image-name"
                title={imageName}
                className="block truncate text-sm font-medium text-white"
              >
                {imageName}
              </span>

              {imageSize !== null && (
                <span
                  id="selected-image-size"
                  className="mt-0.5 block text-xs text-neutral-500"
                >
                  {formatFileSize(imageSize)}
                </span>
              )}
            </div>

            <button
              type="button"
              onClick={onRemoveImage}
              aria-label="Remove selected image"
              className="rounded-lg border border-neutral-700 p-2 text-neutral-500 transition-colors hover:border-red-600/60 hover:bg-red-950/30 hover:text-red-400"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-4 flex flex-col gap-2 sm:flex-row">
            <Button
              id="change-image-btn"
              type="button"
              variant="outline"
              size="sm"
              onClick={handleChooseImage}
              className="flex-1"
            >
              <UploadCloud className="mr-2 h-4 w-4" />
              Change Image
            </Button>

            <Button
              id="remove-image-btn"
              type="button"
              variant="secondary"
              size="sm"
              onClick={onRemoveImage}
              className="flex-1"
            >
              <X className="mr-2 h-4 w-4" />
              Remove Image
            </Button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-2 text-xs text-red-300">
          {error}
        </div>
      )}
    </div>
  );
};