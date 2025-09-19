import React, { useState } from 'react';
import FolderSelector from '@/components/features/CodeUpload/FolderSelector';
import PathList from '@/components/features/CodeUpload/PathList';
import toast from 'react-hot-toast';

const CodeUploadPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleFolderSelect = (paths: any[]) => {
    toast.success(`${paths.length} caminho(s) extraído(s) com sucesso!`);
  };

  const handleFolderError = (error: string) => {
    toast.error(`Erro: ${error}`);
  };

  const handleSelectionComplete = () => {
    // Force refresh the path list when folder selection is complete
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="code-upload-page">
      {/* File Paths List */}
      <div className="path-list-section">
        <PathList
          key={refreshKey}
          autoRefresh={true}
          onFolderSelect={handleFolderSelect}
          onError={handleFolderError}
          onSelectionComplete={handleSelectionComplete}
        />
      </div>
    </div>
  );
};

export default CodeUploadPage;