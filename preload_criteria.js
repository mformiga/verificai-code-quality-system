// Script to preload correct criteria into localStorage
localStorage.setItem("criteria-storage", JSON.stringify([
  {"id": "criteria_64", "text": "Violação de Camadas: Identificar se a lógica de negócio está incorretamente localizada em camadas de interface (como controladores de API), em vez de residir em camadas de serviço ou domínio dedicadas.", "active": true, "order": 6},
  {"id": "criteria_66", "text": "Princípios SOLID: Analisar violações do Princípio da Responsabilidade Única (SRP), como controllers com múltiplos endpoints, e do Princípio da Inversão de Dependência (DI), como a instanciação manual de dependências em vez de usar a injeção padrão do NestJS.", "active": true, "order": 7},
  {"id": "criteria_67", "text": "Acoplamento a Frameworks: Detectar o uso de funcionalidades que acoplam o código a implementações específicas do framework (ex: uso de @Res() do Express no NestJS), o que dificulta a manutenção e a aplicação de interceptors e pipes globais.", "active": true, "order": 8},
]));

console.log("✅ Criteria preloaded successfully!");
console.log("Current criteria in localStorage:", JSON.parse(localStorage.getItem("criteria-storage") || "[]"));