import { render, screen, fireEvent } from '@testing-library/react';
import { PromptToolbar } from '../PromptToolbar';

describe('PromptToolbar Component', () => {
  const mockOnSave = jest.fn();
  const mockOnDiscard = jest.fn();
  const mockOnRestoreDefaults = jest.fn();

  beforeEach(() => {
    mockOnSave.mockClear();
    mockOnDiscard.mockClear();
    mockOnRestoreDefaults.mockClear();
  });

  it('renders all action buttons', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByText('Salvar Alterações')).toBeInTheDocument();
    expect(screen.getByText('Descartar')).toBeInTheDocument();
    expect(screen.getByText('Restaurar Padrões')).toBeInTheDocument();
  });

  it('calls onSave when save button is clicked', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalled();
  });

  it('calls onDiscard when discard button is clicked', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const discardButton = screen.getByText('Descartar');
    fireEvent.click(discardButton);

    expect(mockOnDiscard).toHaveBeenCalled();
  });

  it('calls onRestoreDefaults when restore button is clicked', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const restoreButton = screen.getByText('Restaurar Padrões');
    fireEvent.click(restoreButton);

    expect(mockOnRestoreDefaults).toHaveBeenCalled();
  });

  it('disables save button when no unsaved changes', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    expect(saveButton).toBeDisabled();
  });

  it('disables discard button when no unsaved changes', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const discardButton = screen.getByText('Descartar');
    expect(discardButton).toBeDisabled();
  });

  it('disables all buttons when saving', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={true}
        hasUnsavedChanges={true}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    const discardButton = screen.getByText('Descartar');
    const restoreButton = screen.getByText('Restaurar Padrões');

    expect(saveButton).toBeDisabled();
    expect(discardButton).toBeDisabled();
    expect(restoreButton).toBeDisabled();
  });

  it('disables all buttons when disabled prop is true', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
        disabled={true}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    const discardButton = screen.getByText('Descartar');
    const restoreButton = screen.getByText('Restaurar Padrões');

    expect(saveButton).toBeDisabled();
    expect(discardButton).toBeDisabled();
    expect(restoreButton).toBeDisabled();
  });

  it('shows saving state on save button when isSaving is true', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={true}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByText('Salvando...')).toBeInTheDocument();
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-spinner');
  });

  it('shows normal save state when not saving', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByText('Salvar Alterações')).toBeInTheDocument();
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-save');
  });

  it('enables save button when there are unsaved changes and not saving', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    expect(saveButton).not.toBeDisabled();
  });

  it('enables discard button when there are unsaved changes and not saving', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const discardButton = screen.getByText('Descartar');
    expect(discardButton).not.toBeDisabled();
  });

  it('always enables restore button when not saving or disabled', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const restoreButton = screen.getByText('Restaurar Padrões');
    expect(restoreButton).not.toBeDisabled();
  });

  it('has correct button classes for primary button', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const saveButton = screen.getByText('Salvar Alterações');
    expect(saveButton).toHaveClass('primary');
  });

  it('has correct button classes for secondary button', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const discardButton = screen.getByText('Descartar');
    expect(discardButton).toHaveClass('secondary');
  });

  it('does not have specific class for restore button', () => {
    render(
      <PromptToolbar
        onSave={mockOnSave}
        onDiscard={mockOnDiscard}
        onRestoreDefaults={mockOnRestoreDefaults}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    const restoreButton = screen.getByText('Restaurar Padrões');
    expect(restoreButton).toHaveClass('br-button');
    expect(restoreButton).not.toHaveClass('primary');
    expect(restoreButton).not.toHaveClass('secondary');
  });
});