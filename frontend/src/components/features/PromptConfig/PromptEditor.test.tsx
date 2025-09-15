import { render, screen, fireEvent } from '@testing-library/react';
import { PromptEditor } from '../PromptEditor';

describe('PromptEditor Component', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('renders editor with initial content', () => {
    render(
      <PromptEditor
        value="# Test Prompt\n\nThis is a test prompt content."
        onChange={mockOnChange}
        language="markdown"
        placeholder="Enter your prompt here..."
      />
    );

    const textarea = screen.getByDisplayValue('# Test Prompt\n\nThis is a test prompt content.');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('placeholder', 'Enter your prompt here...');
  });

  it('calls onChange when content changes', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'New content' } });

    expect(mockOnChange).toHaveBeenCalledWith('New content');
  });

  it('displays formatting toolbar buttons', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    expect(screen.getByTitle('Negrito')).toBeInTheDocument();
    expect(screen.getByTitle('Itálico')).toBeInTheDocument();
    expect(screen.getByTitle('Código')).toBeInTheDocument();
    expect(screen.getByTitle('Título 2')).toBeInTheDocument();
    expect(screen.getByTitle('Título 3')).toBeInTheDocument();
    expect(screen.getByTitle('Lista')).toBeInTheDocument();
    expect(screen.getByTitle('Link')).toBeInTheDocument();
    expect(screen.getByTitle('Bloco de código')).toBeInTheDocument();
  });

  it('formats text when bold button is clicked', () => {
    render(
      <PromptEditor
        value="selected text"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');
    const boldButton = screen.getByTitle('Negrito');

    // Simulate text selection
    textarea.setSelectionRange(0, 13);
    fireEvent.click(boldButton);

    expect(mockOnChange).toHaveBeenCalledWith('**selected text**');
  });

  it('formats text when italic button is clicked', () => {
    render(
      <PromptEditor
        value="selected text"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');
    const italicButton = screen.getByTitle('Itálico');

    textarea.setSelectionRange(0, 13);
    fireEvent.click(italicButton);

    expect(mockOnChange).toHaveBeenCalledWith('*selected text*');
  });

  it('inserts H2 heading when H2 button is clicked', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const h2Button = screen.getByText('H2');
    fireEvent.click(h2Button);

    expect(mockOnChange).toHaveBeenCalledWith('## ');
  });

  it('inserts list item when list button is clicked', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const listButton = screen.getByTitle('Lista');
    fireEvent.click(listButton);

    expect(mockOnChange).toHaveBeenCalledWith('- ');
  });

  it('disables buttons when disabled prop is true', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
        disabled={true}
      />
    );

    const boldButton = screen.getByTitle('Negrito');
    expect(boldButton).toBeDisabled();
  });

  it('shows character and word count in footer', () => {
    render(
      <PromptEditor
        value="Hello world test"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    expect(screen.getByText('17 caracteres')).toBeInTheDocument();
    expect(screen.getByText('3 palavras')).toBeInTheDocument();
  });

  it('shows markdown hint for markdown language', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    expect(screen.getByText(/Dica: Ctrl\+B para negrito/)).toBeInTheDocument();
  });

  it('does not show markdown hint for non-markdown language', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="plaintext"
      />
    );

    expect(screen.queryByText(/Dica: Ctrl\+B para negrito/)).not.toBeInTheDocument();
  });

  it('handles keyboard shortcuts', () => {
    render(
      <PromptEditor
        value="selected text"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');

    // Simulate Ctrl+B for bold
    textarea.setSelectionRange(0, 13);
    fireEvent.keyDown(textarea, {
      key: 'b',
      ctrlKey: true,
      bubbles: true,
      cancelable: true
    });

    expect(mockOnChange).toHaveBeenCalledWith('**selected text**');
  });

  it('handles Tab key insertion', () => {
    render(
      <PromptEditor
        value=""
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');

    fireEvent.keyDown(textarea, {
      key: 'Tab',
      bubbles: true,
      cancelable: true
    });

    expect(mockOnChange).toHaveBeenCalledWith('  ');
  });

  it('auto-resizes textarea based on content', () => {
    const { rerender } = render(
      <PromptEditor
        value="Short content"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    const textarea = screen.getByRole('textbox');
    const initialHeight = textarea.style.height;

    rerender(
      <PromptEditor
        value="Long content\nwith\nmultiple\nlines\n\nto test auto-resize functionality"
        onChange={mockOnChange}
        language="markdown"
      />
    );

    // Height should have changed (auto-resize)
    expect(textarea.style.height).not.toBe(initialHeight);
  });
});