import React from 'react';

const BusinessAnalysisPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Análise de Conformidade Negocial</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-600">
          Esta tela permite analisar a conformidade do código com as regras de negócio.
        </p>
      </div>
    </div>
  );
};

export default BusinessAnalysisPage;