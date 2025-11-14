import { BusinessAnalysisResult, DocumentInfo } from '@/stores/businessAnalysisStore';

/**
 * Utility class for generating and downloading analysis reports
 */
export class ReportGenerator {
  /**
   * Generate a comprehensive markdown report from business analysis results
   */
  static generateMarkdownReport(
    analysisResult: BusinessAnalysisResult,
    documents: DocumentInfo[]
  ): string {
    const reportDate = new Date().toLocaleString('pt-BR');
    const overallScore = Math.round(analysisResult.alignmentScore * 100);

    let markdown = `# Relatório de Análise de Negócio\n\n`;
    markdown += `**Gerado em:** ${reportDate}\n`;
    markdown += `**Score de Alinhamento Geral:** ${overallScore}%\n\n`;

    // Executive Summary
    markdown += `## 📊 Resumo Executivo\n\n`;
    markdown += `${analysisResult.overallAssessment}\n\n`;
    markdown += `### Métricas Principais\n\n`;
    markdown += `- **Documentos Analisados:** ${documents.length}\n`;
    markdown += `- **Score de Alinhamento:** ${overallScore}%\n`;
    markdown += `- **Gaps Identificados:** ${analysisResult.gaps.length}\n`;
    markdown += `- **Recomendações:** ${analysisResult.recommendations.length}\n`;
    markdown += `- **Tempo de Processamento:** ${(analysisResult.processingTime / 1000).toFixed(1)}s\n`;
    markdown += `- **Tokens Utilizados:** ${analysisResult.tokenUsage.total.toLocaleString('pt-BR')}\n\n`;

    // Document Analysis
    if (documents.length > 0) {
      markdown += `## 📋 Análise por Documento\n\n`;

      documents.forEach((doc, index) => {
        markdown += `### ${index + 1}. ${doc.name}\n\n`;
        markdown += `- **Tipo:** ${this.getDocumentTypeLabel(doc.type)}\n`;
        markdown += `- **ID:** ${doc.id}\n`;
        markdown += `- **Data de Upload:** ${doc.uploadDate.toLocaleString('pt-BR')}\n`;

        if (doc.metadata?.fileSize) {
          const sizeKB = Math.round(doc.metadata.fileSize / 1024);
          markdown += `- **Tamanho:** ${sizeKB} KB\n`;
        }

        markdown += `\n#### Conteúdo do Documento\n\n`;
        markdown += `\`\`\`\n${doc.content.substring(0, 500)}${doc.content.length > 500 ? '...' : ''}\n\`\`\`\n\n`;
      });
    }

    // Semantic Results
    if (analysisResult.semanticResults && analysisResult.semanticResults.length > 0) {
      markdown += `## 🧠 Resultados da Análise Semântica\n\n`;

      analysisResult.semanticResults.forEach((result: any, index: number) => {
        markdown += `### Requisito ${index + 1}\n\n`;
        markdown += `**Descrição:** ${result.requirement || result.description || 'N/A'}\n\n`;

        if (result.codeAlignment) {
          markdown += `**Alinhamento com Código:** ${this.getAlignmentLabel(result.codeAlignment)}\n\n`;
        }

        if (result.confidence) {
          const confidence = Math.round(result.confidence * 100);
          markdown += `**Nível de Confiança:** ${confidence}%\n\n`;
        }

        if (result.businessImpact) {
          markdown += `**Impacto de Negócio:** ${this.getBusinessImpactLabel(result.businessImpact)}\n\n`;
        }

        if (result.evidence && result.evidence.length > 0) {
          markdown += `#### Evidências Encontradas\n\n`;
          result.evidence.forEach((evidence: any, i: number) => {
            markdown += `${i + 1}. **Arquivo:** \`${evidence.filePath || evidence.file}\`\n`;
            if (evidence.lineNumbers) {
              markdown += `   - **Linhas:** ${evidence.lineNumbers[0]}-${evidence.lineNumbers[1]}\n`;
            }
            if (evidence.language) {
              markdown += `   - **Linguagem:** ${evidence.language}\n`;
            }
            if (evidence.code) {
              markdown += `   - **Código:** \`${evidence.code.substring(0, 100)}${evidence.code.length > 100 ? '...' : ''}\`\n`;
            }
            markdown += `\n`;
          });
        }

        if (result.relatedRequirements && result.relatedRequirements.length > 0) {
          markdown += `#### Requisitos Relacionados\n\n`;
          result.relatedRequirements.forEach((req: string, i: number) => {
            markdown += `${i + 1}. ${req}\n`;
          });
          markdown += `\n`;
        }

        markdown += `---\n\n`;
      });
    }

    // Gaps Analysis
    if (analysisResult.gaps && analysisResult.gaps.length > 0) {
      markdown += `## ⚠️ Gaps Identificados\n\n`;

      analysisResult.gaps.forEach((gap: any, index: number) => {
        const severity = this.getSeverityIcon(gap.severity || gap.businessImpact);
        markdown += `### ${index + 1}. ${severity} ${gap.description}\n\n`;

        if (gap.affectedRequirements && gap.affectedRequirements.length > 0) {
          markdown += `**Requisitos Afetados:**\n`;
          gap.affectedRequirements.forEach((req: string) => {
            markdown += `- ${req}\n`;
          });
          markdown += `\n`;
        }

        if (gap.suggestedActions && gap.suggestedActions.length > 0) {
          markdown += `**Ações Sugeridas:**\n`;
          gap.suggestedActions.forEach((action: string) => {
            markdown += `- ${action}\n`;
          });
          markdown += `\n`;
        }

        markdown += `**Severidade:** ${this.getSeverityLabel(gap.severity || gap.businessImpact)}\n\n`;
      });
    }

    // Recommendations
    if (analysisResult.recommendations && analysisResult.recommendations.length > 0) {
      markdown += `## 💡 Recomendações\n\n`;

      analysisResult.recommendations.forEach((rec: string, index: number) => {
        markdown += `${index + 1}. ${rec}\n`;
      });
      markdown += `\n`;
    }

    // Token Usage Analysis
    markdown += `## 📈 Análise de Utilização\n\n`;
    markdown += `### Consumo de Tokens\n\n`;
    markdown += `- **Tokens de Prompt:** ${analysisResult.tokenUsage.prompt.toLocaleString('pt-BR')}\n`;
    markdown += `- **Tokens de Resposta:** ${analysisResult.tokenUsage.completion.toLocaleString('pt-BR')}\n`;
    markdown += `- **Total de Tokens:** ${analysisResult.tokenUsage.total.toLocaleString('pt-BR')}\n\n`;

    // Calculate estimated cost (rough estimate)
    const estimatedCost = (analysisResult.tokenUsage.total / 1000) * 0.002; // ~$0.002 per 1K tokens
    markdown += `### Custo Estimado\n\n`;
    markdown += `- **Custo Estimado:** $${estimatedCost.toFixed(4)} USD\n\n`;

    // Performance Metrics
    markdown += `### Métricas de Performance\n\n`;
    markdown += `- **Tempo de Processamento:** ${(analysisResult.processingTime / 1000).toFixed(2)} segundos\n`;
    markdown += `- **Throughput:** ${(analysisResult.tokenUsage.total / (analysisResult.processingTime / 1000)).toFixed(0)} tokens/segundo\n\n`;

    // Footer
    markdown += `---\n\n`;
    markdown += `## 📝 Notas\n\n`;
    markdown += `- Este relatório foi gerado automaticamente pelo sistema VerificAI\n`;
    markdown += `- A análise foi realizada usando técnicas de processamento de linguagem natural\n`;
    markdown += `- Para questões ou esclarecimentos, entre em contato com a equipe de QA\n\n`;

    markdown += `### Metodologia\n\n`;
    markdown += `1. **Extração de Requisitos:** Processamento dos documentos de negócio para identificar requisitos\n`;
    markdown += `2. **Análise Semântica:** Comparação entre requisitos e implementação do código\n`;
    markdown += `3. **Mapeamento de Alinhamento:** Avaliação do grau de conformidade\n`;
    markdown += `4. **Identificação de Gaps:** Detecção de discrepâncias e oportunidades\n`;
    markdown += `5. **Geração de Recomendações:** Sugestões baseadas nas análises realizadas\n\n`;

    return markdown;
  }

  /**
   * Download the markdown report as a file
   */
  static downloadMarkdownReport(
    analysisResult: BusinessAnalysisResult,
    documents: DocumentInfo[],
    filename?: string
  ): void {
    const markdown = this.generateMarkdownReport(analysisResult, documents);
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });

    const defaultFilename = `relatorio-analise-negocio-${new Date().toISOString().split('T')[0]}.md`;
    const finalFilename = filename || defaultFilename;

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = finalFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Download analysis as JSON
   */
  static downloadJSONReport(
    analysisResult: BusinessAnalysisResult,
    documents: DocumentInfo[],
    filename?: string
  ): void {
    const report = {
      metadata: {
        generatedAt: new Date().toISOString(),
        reportType: 'business-analysis',
        version: '1.0.0'
      },
      analysis: analysisResult,
      documents: documents,
      summary: {
        overallAlignmentScore: Math.round(analysisResult.alignmentScore * 100),
        documentsAnalyzed: documents.length,
        gapsIdentified: analysisResult.gaps.length,
        recommendationsCount: analysisResult.recommendations.length,
        processingTimeSeconds: analysisResult.processingTime / 1000,
        tokenUsage: analysisResult.tokenUsage
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });

    const defaultFilename = `analise-negocio-${new Date().toISOString().split('T')[0]}.json`;
    const finalFilename = filename || defaultFilename;

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = finalFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // Helper methods
  private static getDocumentTypeLabel(type: string): string {
    switch (type) {
      case 'user-story': return 'User Story';
      case 'epic': return 'Épico';
      case 'business-rule': return 'Regra de Negócio';
      case 'requirement': return 'Requisito';
      default: return type;
    }
  }

  private static getAlignmentLabel(alignment: string): string {
    switch (alignment?.toLowerCase()) {
      case 'aligned': return 'Alinhado';
      case 'partially_aligned': return 'Parcialmente Alinhado';
      case 'not_aligned': return 'Não Alinhado';
      case 'conform': return 'Conforme';
      case 'partially_conform': return 'Parcialmente Conforme';
      case 'non_conform': return 'Não Conforme';
      default: return alignment || 'Não avaliado';
    }
  }

  private static getBusinessImpactLabel(impact: string): string {
    switch (impact?.toLowerCase()) {
      case 'high': return 'Alto Impacto';
      case 'medium': return 'Médio Impacto';
      case 'low': return 'Baixo Impacto';
      default: return impact || 'Não avaliado';
    }
  }

  private static getSeverityIcon(severity: string): string {
    switch (severity?.toLowerCase()) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  }

  private static getSeverityLabel(severity: string): string {
    switch (severity?.toLowerCase()) {
      case 'high': return 'Alto';
      case 'medium': return 'Médio';
      case 'low': return 'Baixo';
      default: return severity || 'Não avaliado';
    }
  }
}

export default ReportGenerator;