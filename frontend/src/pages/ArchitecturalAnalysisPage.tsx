import React from 'react';

const ArchitecturalAnalysisPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Análise de Conformidade Arquitetural</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-600">
          Esta tela permite analisar a conformidade do código com a arquitetura definida.
        </p>
      </div>
    </div>
  );
};

export default ArchitecturalAnalysisPage;