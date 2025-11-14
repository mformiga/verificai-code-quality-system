import React, { useState } from 'react';
import { Eye, Edit, Copy, Download, FileText, Maximize2, Minimize2 } from 'lucide-react';
import DOMPurify from 'dompurify';

interface MarkdownViewerProps {
  content: string;
  title?: string;
  showActions?: boolean;
  onEdit?: (content: string) => void;
  onDownload?: (content: string) => void;
  className?: string;
}

const MarkdownViewer: React.FC<MarkdownViewerProps> = ({
  content,
  title = 'Conteúdo Markdown',
  showActions = true,
  onEdit,
  onDownload,
  className = ''
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Simple markdown parser (basic implementation)
  const parseMarkdown = (markdown: string): string => {
    if (!markdown) return '';

    let html = markdown;

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mb-2">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mb-3 mt-4">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mb-4 mt-6">$1</h1>');

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>');

    // Italic
    html = html.replace(/\*(.+?)\*/g, '<em class="italic">$1</em>');

    // Lists
    html = html.replace(/^\* (.+)/gim, '<li class="ml-4">$1</li>');
    html = html.replace(/(<li.*<\/li>)/s, '<ul class="list-disc ml-6 mb-3">$1</ul>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p class="mb-3">');
    html = `<p class="mb-3">${html}</p>`;

    // Code blocks
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-4"><code class="text-sm font-mono">${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">$1</code>');

    // Clean up
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[1-6])/g, '$1');
    html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<pre)/g, '$1');
    html = html.replace(/(<\/pre>)<\/p>/g, '$1');

    return html;
  };

  const handleCopy = async () => {
    const textToCopy = isEditing ? editedContent : content;
    try {
      await navigator.clipboard.writeText(textToCopy);
      alert('Conteúdo copiado para a área de transferência!');
    } catch (err) {
      console.error('Erro ao copiar:', err);
      alert('Erro ao copiar conteúdo');
    }
  };

  const handleEdit = () => {
    setEditedContent(content);
    setIsEditing(true);
    setHasChanges(false);
  };

  const handleSave = () => {
    if (onEdit && hasChanges) {
      onEdit(editedContent);
    }
    setIsEditing(false);
    setHasChanges(false);
  };

  const handleCancel = () => {
    if (hasChanges) {
      const confirmCancel = confirm('Você tem alterações não salvas. Deseja cancelar?');
      if (!confirmCancel) return;
    }
    setEditedContent(content);
    setIsEditing(false);
    setHasChanges(false);
  };

  const handleChange = (value: string) => {
    setEditedContent(value);
    setHasChanges(value !== content);
  };

  const handleDownload = () => {
    if (onDownload) {
      const textToDownload = isEditing ? editedContent : content;
      onDownload(textToDownload);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const currentContent = isEditing ? editedContent : content;
  const wordCount = currentContent.split(/\s+/).filter(word => word.length > 0).length;
  const charCount = currentContent.length;
  const lineCount = currentContent.split('\n').length;

  const containerClasses = `
    ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}
    ${className}
    transition-all duration-200
  `;

  if (!content && !isEditing) {
    return (
      <div className={`text-center py-8 ${containerClasses}`}>
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">Nenhum conteúdo markdown disponível</p>
      </div>
    );
  }

  return (
    <div className={containerClasses}>
      <div className={`${isFullscreen ? 'h-full flex flex-col' : ''}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <h3 className="font-semibold">{title}</h3>
            {isEditing && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                Modo de Edição
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {showActions && !isEditing && (
              <>
                <button
                  onClick={handleCopy}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Copiar conteúdo"
                >
                  <Copy className="w-4 h-4" />
                </button>
                {onEdit && (
                  <button
                    onClick={handleEdit}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Editar conteúdo"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                )}
                {onDownload && (
                  <button
                    onClick={handleDownload}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Baixar como Markdown"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={toggleFullscreen}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title={isFullscreen ? 'Sair da tela cheia' : 'Tela cheia'}
                >
                  {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                </button>
              </>
            )}

            {isEditing && (
              <>
                <button
                  onClick={handleSave}
                  disabled={!hasChanges}
                  className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Salvar
                </button>
                <button
                  onClick={handleCancel}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
              </>
            )}
          </div>
        </div>

        {/* Content */}
        <div className={`${isFullscreen ? 'flex-1 overflow-auto' : ''}`}>
          {isEditing ? (
            <div className="space-y-4">
              {/* Edit Mode Info */}
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Modo de edição:</strong> Use sintaxe Markdown para formatar o conteúdo.
                </p>
              </div>

              {/* Textarea */}
              <div className="relative">
                <textarea
                  value={editedContent}
                  onChange={(e) => handleChange(e.target.value)}
                  className="w-full h-96 p-4 font-mono text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Digite seu conteúdo em Markdown aqui..."
                />

                {/* Character counter */}
                <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white px-2 py-1 rounded">
                  {charCount} chars • {wordCount} words • {lineCount} lines
                </div>
              </div>

              {/* Markdown Preview */}
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-3 py-2 border-b">
                  <span className="text-sm font-medium">Visualização</span>
                </div>
                <div
                  className="p-4 prose prose-sm max-w-none"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(parseMarkdown(editedContent)) }}
                />
              </div>
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              {/* View Mode */}
              <div
                className={`${isFullscreen ? 'h-full overflow-auto' : 'max-h-96 overflow-auto'} prose prose-sm max-w-none p-4`}
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(parseMarkdown(currentContent)) }}
              />

              {/* Content Info */}
              <div className="bg-gray-50 px-3 py-2 border-t text-xs text-gray-500">
                {charCount} caracteres • {wordCount} palavras
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarkdownViewer;