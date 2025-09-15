export interface AnalysisConfig {
  type: 'general' | 'architectural' | 'business';
  files: string[];
  promptId?: string;
  documentId?: string;
  criteria?: string[];
}

export interface Analysis {
  id: string;
  sessionId: string;
  type: 'general' | 'architectural' | 'business';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  files: File[];
  startTime: Date;
  endTime?: Date;
  results: AnalysisResult[];
  error?: string;
}

export interface AnalysisResult {
  id: string;
  analysisId: string;
  criterion: string;
  description: string;
  status: 'pass' | 'fail' | 'warning';
  score: number;
  details: string;
  evidence?: Evidence[];
  fileLocation?: string;
  lineNumber?: number;
  createdAt: Date;
}

export interface Evidence {
  id: string;
  content: string;
  fileName: string;
  startLine: number;
  endLine: number;
  severity: 'low' | 'medium' | 'high';
}

export interface AnalysisSummary {
  totalCriteria: number;
  passed: number;
  failed: number;
  warnings: number;
  overallScore: number;
  breakdown: {
    general: { passed: number; failed: number; warnings: number };
    architectural: { passed: number; failed: number; warnings: number };
    business: { passed: number; failed: number; warnings: number };
  };
}