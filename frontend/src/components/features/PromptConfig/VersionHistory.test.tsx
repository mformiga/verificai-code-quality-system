import { render, screen, fireEvent } from '@testing-library/react';
import { VersionHistory } from '../VersionHistory';
import { PromptVersion } from '@/types/prompt';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn(),
}));

const mockFormat = format as jest.MockedFunction<typeof format>;

describe('VersionHistory Component', () => {
  const mockOnRestore = jest.fn();
  const testDate = new Date('2023-12-01T10:30:00');

  const mockVersions: PromptVersion[] = [
    {
      version: 1,
      content: 'Initial version content',
      createdAt: testDate,
      author: 'John Doe',
      changeDescription: 'Initial setup',
    },
    {
      version: 2,
      content: 'Updated version content',
      createdAt: new Date('2023-12-02T14:45:00'),
      author: 'Jane Smith',
      changeDescription: 'Added new criteria',
    },
    {
      version: 3,
      content: 'Latest version content',
      createdAt: new Date('2023-12-03T09:15:00'),
      author: 'Bob Johnson',
      changeDescription: 'Final updates',
    },
  ];

  beforeEach(() => {
    mockOnRestore.mockClear();
    mockFormat.mockReturnValue('01/12/2023 10:30');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders version history component', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    expect(screen.getByText('Histórico de Versões')).toBeInTheDocument();
  });

  it('displays all versions sorted by version number (descending)', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    expect(screen.getByText('v3')).toBeInTheDocument();
    expect(screen.getByText('v2')).toBeInTheDocument();
    expect(screen.getByText('v1')).toBeInTheDocument();

    // Versions should be in descending order
    const versionElements = screen.getAllByText(/v\d/);
    expect(versionElements[0]).toHaveTextContent('v3');
    expect(versionElements[1]).toHaveTextContent('v2');
    expect(versionElements[2]).toHaveTextContent('v1');
  });

  it('shows current version indicator', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={2}
      />
    );

    const currentVersionTag = screen.getByText('Atual');
    expect(currentVersionTag).toBeInTheDocument();
    expect(currentVersionTag).toHaveClass('success');

    // Should be next to v2
    const version2Element = screen.getByText('v2');
    expect(currentVersionTag.closest('.version-item')).toContainElement(version2Element);
  });

  it('shows version dates formatted correctly', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    expect(screen.getByText('01/12/2023 10:30')).toBeInTheDocument();
    expect(mockFormat).toHaveBeenCalledWith(
      testDate,
      'dd/MM/yyyy HH:mm',
      { locale: ptBR }
    );
  });

  it('shows version authors', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    expect(screen.getByText('por John Doe')).toBeInTheDocument();
    expect(screen.getByText('por Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('por Bob Johnson')).toBeInTheDocument();
  });

  it('shows change descriptions when available', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    expect(screen.getByText('Initial setup')).toBeInTheDocument();
    expect(screen.getByText('Added new criteria')).toBeInTheDocument();
    expect(screen.getByText('Final updates')).toBeInTheDocument();
  });

  it('does not show restore button for current version', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    // Should have restore buttons for v1 and v2, but not for v3
    const restoreButtons = screen.getAllByText('Restaurar esta versão');
    expect(restoreButtons).toHaveLength(2);

    // Check that v3 doesn't have a restore button
    const v3Item = screen.getByText('v3').closest('.version-item');
    expect(v3Item).not.toContainElement(screen.queryByText('Restaurar esta versão'));
  });

  it('shows restore buttons for non-current versions', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={2}
      />
    );

    // Should have restore buttons for v1 and v3
    const restoreButtons = screen.getAllByText('Restaurar esta versão');
    expect(restoreButtons).toHaveLength(2);
  });

  it('calls onRestore when restore button is clicked', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    const restoreButtons = screen.getAllByText('Restaurar esta versão');

    // Click restore button for v1
    fireEvent.click(restoreButtons[0]);

    expect(mockOnRestore).toHaveBeenCalledWith(1);
  });

  it('handles empty versions array', () => {
    render(
      <VersionHistory
        versions={[]}
        onRestore={mockOnRestore}
        currentVersion={1}
      />
    );

    expect(screen.getByText('Histórico de Versões')).toBeInTheDocument();
    expect(screen.queryByText(/v\d/)).not.toBeInTheDocument();
  });

  it('handles single version', () => {
    const singleVersion: PromptVersion[] = [
      {
        version: 1,
        content: 'Only version',
        createdAt: testDate,
        author: 'Single Author',
      },
    ];

    render(
      <VersionHistory
        versions={singleVersion}
        onRestore={mockOnRestore}
        currentVersion={1}
      />
    );

    expect(screen.getByText('v1')).toBeInTheDocument();
    expect(screen.getByText('Atual')).toBeInTheDocument();
    expect(screen.queryByText('Restaurar esta versão')).not.toBeInTheDocument();
  });

  it('handles versions without change descriptions', () => {
    const versionsWithoutDescription: PromptVersion[] = [
      {
        version: 1,
        content: 'Version without description',
        createdAt: testDate,
        author: 'Author',
      },
      {
        version: 2,
        content: 'Another version',
        createdAt: new Date('2023-12-02T14:45:00'),
        author: 'Another Author',
        changeDescription: 'Has description',
      },
    ];

    render(
      <VersionHistory
        versions={versionsWithoutDescription}
        onRestore={mockOnRestore}
        currentVersion={2}
      />
    );

    // v1 should not have a description
    const v1Item = screen.getByText('v1').closest('.version-item');
    expect(v1Item).not.toContainElement(screen.queryByText('Initial setup'));

    // v2 should have description
    expect(screen.getByText('Has description')).toBeInTheDocument();
  });

  it('applies correct CSS classes to version items', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={2}
      />
    );

    const currentVersionItem = screen.getByText('v2').closest('.version-item');
    const otherVersionItem = screen.getByText('v1').closest('.version-item');

    expect(currentVersionItem).toHaveClass('current');
    expect(otherVersionItem).not.toHaveClass('current');
  });

  it('shows correct number of version items', () => {
    render(
      <VersionHistory
        versions={mockVersions}
        onRestore={mockOnRestore}
        currentVersion={3}
      />
    );

    const versionItems = screen.getAllByTestId(/version-item/);
    // Using getAllByText as fallback since data-testid might not be set
    const versionNumbers = screen.getAllByText(/v\d/);
    expect(versionNumbers).toHaveLength(3);
  });
});