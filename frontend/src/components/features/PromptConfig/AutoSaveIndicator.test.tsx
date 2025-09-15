import { render, screen } from '@testing-library/react';
import { AutoSaveIndicator } from '../AutoSaveIndicator';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Mock date-fns
jest.mock('date-fns', () => ({
  formatDistanceToNow: jest.fn(),
}));

const mockFormatDistanceToNow = formatDistanceToNow as jest.MockedFunction<typeof formatDistanceToNow>;

describe('AutoSaveIndicator Component', () => {
  beforeEach(() => {
    mockFormatDistanceToNow.mockReturnValue('há 5 minutos');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('shows saving state when isSaving is true', () => {
    render(
      <AutoSaveIndicator
        isSaving={true}
        lastSaved={null}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Salvando...')).toBeInTheDocument();
    expect(screen.getByText('Salvando...')).toHaveClass('warning');
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-spinner');
  });

  it('shows unsaved state when hasUnsavedChanges is true', () => {
    render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={null}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByText('Não salvo')).toBeInTheDocument();
    expect(screen.getByText('Não salvo')).toHaveClass('danger');
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-exclamation-circle');
  });

  it('shows saved state with time when lastSaved is provided', () => {
    const lastSaved = new Date();
    mockFormatDistanceToNow.mockReturnValue('há 2 minutos');

    render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={lastSaved}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Salvo há 2 minutos')).toBeInTheDocument();
    expect(screen.getByText('Salvo há 2 minutos')).toHaveClass('success');
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-check-circle');
    expect(mockFormatDistanceToNow).toHaveBeenCalledWith(lastSaved, {
      addSuffix: true,
      locale: ptBR
    });
  });

  it('shows default saved state when no lastSaved but saved', () => {
    render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={null}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Salvo')).toBeInTheDocument();
    expect(screen.getByText('Salvo')).toHaveClass('success');
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-check-circle');
  });

  it('prioritizes saving state over other states', () => {
    const lastSaved = new Date();
    render(
      <AutoSaveIndicator
        isSaving={true}
        lastSaved={lastSaved}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByText('Salvando...')).toBeInTheDocument();
    expect(screen.getByText('Salvando...')).toHaveClass('warning');
  });

  it('uses correct CSS classes for different states', () => {
    const { rerender } = render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={null}
        hasUnsavedChanges={true}
      />
    );

    let indicator = screen.getByText('Não salvo');
    expect(indicator).toHaveClass('danger');

    rerender(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={new Date()}
        hasUnsavedChanges={false}
      />
    );

    indicator = screen.getByText(/Salvo/);
    expect(indicator).toHaveClass('success');

    rerender(
      <AutoSaveIndicator
        isSaving={true}
        lastSaved={null}
        hasUnsavedChanges={false}
      />
    );

    indicator = screen.getByText('Salvando...');
    expect(indicator).toHaveClass('warning');
  });

  it('uses correct icons for different states', () => {
    const { rerender } = render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={null}
        hasUnsavedChanges={true}
      />
    );

    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-exclamation-circle');

    rerender(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={new Date()}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-check-circle');

    rerender(
      <AutoSaveIndicator
        isSaving={true}
        lastSaved={null}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByRole('img', { hidden: true })).toHaveClass('fa-spinner');
  });

  it('formats time correctly for recent saves', () => {
    const recentTime = new Date(Date.now() - 5 * 60 * 1000); // 5 minutes ago
    mockFormatDistanceToNow.mockReturnValue('há 5 minutos');

    render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={recentTime}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Salvo há 5 minutos')).toBeInTheDocument();
    expect(mockFormatDistanceToNow).toHaveBeenCalledWith(recentTime, {
      addSuffix: true,
      locale: ptBR
    });
  });

  it('formats time correctly for older saves', () => {
    const oldTime = new Date(Date.now() - 2 * 60 * 60 * 1000); // 2 hours ago
    mockFormatDistanceToNow.mockReturnValue('há 2 horas');

    render(
      <AutoSaveIndicator
        isSaving={false}
        lastSaved={oldTime}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Salvo há 2 horas')).toBeInTheDocument();
  });
});