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

  const handleClearAll = async () => {
    try {
      const { getAuthHeaders } = await import('@/utils/auth');
      const authHeaders = getAuthHeaders();

      const response = await fetch('/api/v1/file-paths/', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify([]) // Send empty array directly to delete all
      });

      if (response.ok) {
        toast.success('Todos os caminhos foram limpos!');
        setRefreshKey(prev => prev + 1); // Force refresh
      } else {
        const errorText = await response.text();
        console.error('Erro ao limpar caminhos:', errorText);
        toast.error('Erro ao limpar caminhos');
      }
    } catch (error) {
      console.error('Erro ao limpar caminhos:', error);
      toast.error('Erro ao limpar caminhos');
    }
  };

  return (
    <div className="code-upload-page">
      {/* File Paths List */}
      <div className="path-list-section">
        <PathList
          key={refreshKey}
          autoRefresh={true}
          onClearAll={handleClearAll}
          onRefresh={() => setRefreshKey(prev => prev + 1)}
          onFolderSelect={handleFolderSelect}
          onError={handleFolderError}
          onSelectionComplete={handleSelectionComplete}
        />
      </div>
    </div>
  );
};

export default CodeUploadPage;