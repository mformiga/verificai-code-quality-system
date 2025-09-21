// Exemplo de código para análise
import React from 'react';

const ExampleComponent = () => {
  const [count, setCount] = React.useState(0);

  // Função com responsabilidade múltipla (violação SRP)
  const handleComplexOperation = async () => {
    // Lógica de negócio misturada com UI
    const response = await fetch('/api/data');
    const data = await response.json();

    // Validação de negócio
    if (data.valid) {
      // Atualização de UI
      setCount(data.value);

      // Logging (deveria estar em serviço separado)
      console.log('Data updated:', data);

      // Notificação (deveria usar serviço de notificação)
      alert('Data updated successfully!');
    }
  };

  // Acoplamento direto a framework (uso de React hooks em camada de negócio)
  const businessLogic = () => {
    if (count > 10) {
      // Lógica de negócio dependendo do estado do React
      return 'High count';
    }
    return 'Low count';
  };

  return (
    <div>
      <h1>Example Component</h1>
      <p>Count: {count}</p>
      <button onClick={handleComplexOperation}>
        Complex Operation
      </button>
      <p>Status: {businessLogic()}</p>
    </div>
  );
};

export default ExampleComponent;