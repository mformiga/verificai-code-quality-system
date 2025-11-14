import { useState, useCallback } from 'react';
import { UploadedFile, ValidationResult } from '../types/fileUpload';
import { fileUploadService } from '../services/fileUploadService';

export const useFileUpload = () => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadedFile[]>([]);
  const [completedFiles, setCompletedFiles] = useState<UploadedFile[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    processFiles(files);
  }, []);

  const handleFileSelect = useCallback((files: FileList) => {
    processFiles(files);
  }, []);

  const processFiles = useCallback(async (files: FileList) => {
    try {
      // Simple file processing - just take the files directly
      const fileArray = Array.from(files);

      if (fileArray.length === 0) {
        setErrors(prev => [...prev, 'No files selected']);
        return;
      }

      // Create UploadedFile objects
      const newUploadingFiles = fileArray.map(file => ({
        id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        path: file.name,
        size: file.size,
        type: file.type,
        uploadDate: new Date(),
        status: 'uploading' as const,
        progress: 0
      }));

      setUploadingFiles(prev => [...prev, ...newUploadingFiles]);

      // Simulate upload process
      for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        const uploadingFile = newUploadingFiles[i];

        try {
          // Simulate upload progress
          for (let progress = 0; progress <= 100; progress += 10) {
            setUploadingFiles(prev =>
              prev.map(f =>
                f.id === uploadingFile.id
                  ? { ...f, progress, status: 'uploading' as const }
                  : f
              )
            );
            await new Promise(resolve => setTimeout(resolve, 50));
          }

          // Move from uploading to completed
          const completedFile = {
            ...uploadingFile,
            status: 'completed' as const,
            progress: 100
          };

          setUploadingFiles(prev => prev.filter(f => f.id !== uploadingFile.id));
          setCompletedFiles(prev => [...prev, completedFile]);

        } catch (error) {
          setUploadingFiles(prev =>
            prev.map(f =>
              f.id === uploadingFile.id
                ? {
                    ...f,
                    status: 'error' as const,
                    error: error instanceof Error ? error.message : 'Upload failed'
                  }
                : f
            )
          );
          setErrors(prev => [...prev, `${file.name}: ${error instanceof Error ? error.message : 'Upload failed'}`]);
        }
      }
    } catch (error) {
      setErrors(prev => [...prev, `Processing error: ${error instanceof Error ? error.message : 'Unknown error'}`]);
    }
  }, []);

  const removeFile = useCallback((fileId: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== fileId));
    setCompletedFiles(prev => prev.filter(f => f.id !== fileId));
    setErrors(prev => prev.filter(e => !e.includes(fileId)));
  }, []);

  const retryUpload = useCallback((fileId: string) => {
    const failedFile = uploadingFiles.find(f => f.id === fileId && f.status === 'error');
    if (failedFile) {
      // Remove from errors
      setErrors(prev => prev.filter(e => !e.includes(failedFile.name)));

      // Reset status
      setUploadingFiles(prev =>
        prev.map(f =>
          f.id === fileId
            ? { ...f, status: 'uploading' as const, progress: 0, error: undefined }
            : f
        )
      );
    }
  }, [uploadingFiles]);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const clearAll = useCallback(() => {
    setUploadingFiles([]);
    setCompletedFiles([]);
    setErrors([]);
  }, []);

  const getAllFiles = useCallback(() => {
    return [...uploadingFiles, ...completedFiles];
  }, [uploadingFiles, completedFiles]);

  const getStats = useCallback(() => {
    const totalFiles = getAllFiles().length;
    const completedCount = completedFiles.length;
    const uploadingCount = uploadingFiles.length;
    const errorCount = uploadingFiles.filter(f => f.status === 'error').length;
    const totalSize = getAllFiles().reduce((sum, file) => sum + file.size, 0);

    return {
      totalFiles,
      completedCount,
      uploadingCount,
      errorCount,
      totalSize,
      successRate: totalFiles > 0 ? Math.round((completedCount / totalFiles) * 100) : 0
    };
  }, [getAllFiles, completedFiles, uploadingFiles]);

  return {
    isDragActive,
    uploadingFiles,
    completedFiles,
    errors,
    handleDrag,
    handleDrop,
    handleFileSelect,
    removeFile,
    retryUpload,
    clearErrors,
    clearAll,
    getAllFiles,
    getStats
  };
};