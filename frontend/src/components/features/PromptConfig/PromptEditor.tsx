import React, { useRef, useEffect, useState } from 'react';
import { PromptEditorProps } from '@/types/prompt';
import './PromptEditor.css';

export const PromptEditor: React.FC<PromptEditorProps> = ({
  value,
  onChange,
  language = 'markdown',
  placeholder,
  disabled = false,
}) => {
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);

  const insertText = (text: string) => {
    if (!editorRef.current) return;

    const textarea = editorRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const newText = text.replace('${selection}', selectedText);

    const newValue = value.substring(0, start) + newText + value.substring(end);
    onChange(newValue);

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start, start + newText.length);
    }, 0);
  };

  const formatSelection = (before: string, after: string = before) => {
    if (!editorRef.current) return;

    const textarea = editorRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);

    if (selectedText) {
      const newText = before + selectedText + after;
      const newValue = value.substring(0, start) + newText + value.substring(end);
      onChange(newValue);

      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start, start + newText.length);
      }, 0);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (disabled) return;

    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'b':
          e.preventDefault();
          formatSelection('**', '**');
          break;
        case 'i':
          e.preventDefault();
          formatSelection('*', '*');
          break;
        case 'k':
          e.preventDefault();
          formatSelection('[', ']()');
          break;
        case 'e':
          e.preventDefault();
          formatSelection('`', '`');
          break;
      }
    }

    if (e.key === 'Tab') {
      e.preventDefault();
      insertText('  ');
    }
  };

  const handleSelectionChange = () => {
    if (editorRef.current) {
      setSelectionStart(editorRef.current.selectionStart);
      setSelectionEnd(editorRef.current.selectionEnd);
    }
  };

  const getWordCount = () => {
    return value.trim() ? value.trim().split(/\s+/).length : 0;
  };

  const getCharCount = () => {
    return value.length;
  };

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.style.height = 'auto';
      editorRef.current.style.height = `${editorRef.current.scrollHeight}px`;
    }
  }, [value]);

  return (
    <div className="br-textarea-wrapper">
      <div className="editor-toolbar br-button-group">
        <div className="br-button-group">
          <button
            type="button"
            onClick={() => formatSelection('**', '**')}
            title="Negrito"
            disabled={disabled}
            className="br-button small"
            aria-label="Negrito"
          >
            <span className="fas fa-bold"></span>
          </button>
          <button
            type="button"
            onClick={() => formatSelection('*', '*')}
            title="Itálico"
            disabled={disabled}
            className="br-button small"
            aria-label="Itálico"
          >
            <span className="fas fa-italic"></span>
          </button>
          <button
            type="button"
            onClick={() => formatSelection('`', '`')}
            title="Código"
            disabled={disabled}
            className="br-button small"
            aria-label="Código"
          >
            <span className="fas fa-code"></span>
          </button>
        </div>

        <div className="br-button-group">
          <button
            type="button"
            onClick={() => formatSelection('## ')}
            title="Título 2"
            disabled={disabled}
            className="br-button small"
            aria-label="Título 2"
          >
            H2
          </button>
          <button
            type="button"
            onClick={() => formatSelection('### ')}
            title="Título 3"
            disabled={disabled}
            className="br-button small"
            aria-label="Título 3"
          >
            H3
          </button>
          <button
            type="button"
            onClick={() => formatSelection('- ')}
            title="Lista"
            disabled={disabled}
            className="br-button small"
            aria-label="Lista"
          >
            <span className="fas fa-list-ul"></span>
          </button>
        </div>

        <div className="br-button-group">
          <button
            type="button"
            onClick={() => formatSelection('[', ']()')}
            title="Link"
            disabled={disabled}
            className="br-button small"
            aria-label="Link"
          >
            <span className="fas fa-link"></span>
          </button>
          <button
            type="button"
            onClick={() => formatSelection('```\n', '\n```')}
            title="Bloco de código"
            disabled={disabled}
            className="br-button small"
            aria-label="Bloco de código"
          >
            <span className="fas fa-code"></span>
          </button>
        </div>
      </div>

      <textarea
        ref={editorRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onSelect={handleSelectionChange}
        onKeyUp={handleSelectionChange}
        onMouseUp={handleSelectionChange}
        placeholder={placeholder}
        disabled={disabled}
        className="br-textarea"
        rows={15}
        style={{
          resize: 'vertical',
          minHeight: '400px',
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          fontSize: '14px',
          lineHeight: '1.5',
        }}
      />

      <div className="editor-footer">
        <div className="editor-stats text-small text-muted">
          <span className="me-3">
            <i className="fas fa-font me-1"></i>
            {getCharCount()} caracteres
          </span>
          <span>
            <i className="fas fa-align-left me-1"></i>
            {getWordCount()} palavras
          </span>
        </div>

        {language === 'markdown' && (
          <div className="markdown-hint text-small text-muted">
            <i className="fas fa-keyboard me-1"></i>
            Dica: Ctrl+B para negrito, Ctrl+I para itálico, Ctrl+E para código
          </div>
        )}
      </div>
    </div>
  );
};