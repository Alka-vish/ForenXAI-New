/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Navbar, PageId } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NewInvestigation } from './pages/NewInvestigation';
import { Workspace } from './pages/Workspace';
import { History } from './pages/History';
import { Reports } from './pages/Reports';
import { Result } from './pages/Result';
import { InvestigationRecord } from './types';
import { getStoredInvestigations } from './services/forensicApi';

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('new-investigation');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageName, setImageName] = useState<string>('');
  const [imageSize, setImageSize] = useState<number | null>(null);
  const [activeRecord, setActiveRecord] = useState<InvestigationRecord | null>(null);

  // Load latest recorded investigation on initial startup for Workspace/Reports/Result views
  useEffect(() => {
    const existing = getStoredInvestigations();
    if (existing && existing.length > 0) {
      setActiveRecord(existing[0]);
    }
  }, []);

  const handleSelectImage = (file: File) => {
    setImageFile(file);
    setImageName(file.name);
    setImageSize(file.size);

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      setSelectedImage(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImageFile(null);
    setImageName('');
    setImageSize(null);
  };

  const handleInvestigationFinished = (record: InvestigationRecord) => {
    setActiveRecord(record);
    setSelectedImage(record.imagePreview || selectedImage);
    setImageName(record.imageName);
    setImageSize(record.imageSize);
    // Explicit user requirement: Navigate to Workspace page on completion
    setCurrentPage('workspace');
  };

  const handleSelectRecord = (record: InvestigationRecord, targetPage: PageId) => {
    setActiveRecord(record);
    if (record.imagePreview) {
      setSelectedImage(record.imagePreview);
    }
    setImageName(record.imageName);
    setImageSize(record.imageSize);
    setCurrentPage(targetPage);
  };

  const handleNewInvestigation = () => {
    handleRemoveImage();
    setCurrentPage('new-investigation');
  };

  const handleOpenWorkspace = () => {
    setCurrentPage('workspace');
  };

  const handleNavigate = (page: PageId) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-neutral-50/50 text-neutral-900 flex flex-col font-sans">
      <Navbar currentPage={currentPage} onNavigate={handleNavigate} />

      <div className="flex-1 flex flex-col">
        {currentPage === 'dashboard' && (
          <Dashboard
            onNavigate={handleNavigate}
            hasActiveImage={!!selectedImage || !!activeRecord}
            imageName={imageName}
          />
        )}

        {currentPage === 'new-investigation' && (
          <NewInvestigation
            selectedImage={selectedImage}
            imageFile={imageFile}
            imageName={imageName}
            imageSize={imageSize}
            onSelectImage={handleSelectImage}
            onRemoveImage={handleRemoveImage}
            onInvestigationFinished={handleInvestigationFinished}
          />
        )}

        {currentPage === 'workspace' && (
          <Workspace
            onNavigate={handleNavigate}
            activeRecord={activeRecord}
            selectedImage={selectedImage}
            imageName={imageName}
            imageSize={imageSize}
          />
        )}

        {currentPage === 'history' && (
          <History
            onNavigate={handleNavigate}
            onSelectRecord={handleSelectRecord}
          />
        )}

        {currentPage === 'reports' && (
          <Reports
            onNavigate={handleNavigate}
            activeRecord={activeRecord}
          />
        )}

        {currentPage === 'result' && (
          <Result
            activeRecord={activeRecord}
            onNewInvestigation={handleNewInvestigation}
            onOpenWorkspace={handleOpenWorkspace}
          />
        )}
      </div>
    </div>
  );
}
