#!/usr/bin/env python3
import re

# Test content based on what we see in latest_response.txt
test_content = """## Avaliação Geral
A análise do código-fonte revela problemas arquiteturais significativos que, embora funcionais, comprometem a manutenibilidade, testabilidade e escalabilidade da aplicação. As principais violações estão relacionadas aos princípios SOLID, especialmente a Responsabilidade Única (SRP) e a Inversão de Dependência (DI), e ao forte acoplamento com o framework web subjacente (Express).

O `LaudoController` é um exemplo claro de violação de SRP, acumulando responsabilidades que vão desde a manipulação de arquivos e orquestração de chamadas a APIs externas até o acesso direto a dados e o serviço de arquivos estáticos. Além disso, a aplicação utiliza consistentemente o padrão Service Locator para obter dependências de banco de dados (`getRepository`), em vez de aproveitar o robusto sistema de injeção de dependência do NestJS, o que viola o princípio de Inversão de Dependência.

O acoplamento ao Express é evidente pelo uso do decorador `@Res()` em múltiplos controllers, o que impede o correto funcionamento de interceptors, pipes e outros mecanismos globais do NestJS, tornando o fluxo de requisição/resposta menos previsível e mais difícil de gerenciar.

A correção desses pontos é crucial para alinhar o projeto com as melhores práticas do ecossistema NestJS, resultando em um código mais limpo, desacoplado e fácil de manter.

## Critério 1: Princípios SOLID: Analisar violações do Princípio da Responsabilidade Única (SRP), como controllers com múltiplos endpoints, e do Princípio da Inversão de Dependência (DI), como a instanciação manual de dependências em vez de usar a injeção padrão do NestJS.
**Status:** Não Conforme
**Confiança:** 100.0%

A análise do código revela violações claras e consistentes dos princípios da Responsabilidade Única (SRP) e da Inversão de Dependência (DI).

**1. Violação do Princípio da Responsabilidade Única (SRP):**

O `LaudoController` é o principal infrator deste princípio. Ele acumula um número excessivo de responsabilidades distintas, tornando-o uma classe "faz-tudo" (God Class). Suas responsabilidades incluem:
- **Manipulação de Sistema de Arquivos:** Interage diretamente com o módulo `fs` para criar e remover arquivos temporários (`this.removeFile`, `fs.createWriteStream`).
- **Comunicação com API Externa:** Utiliza `axios` para se comunicar com uma API de IA (`/extract-pdf-data` e `/data-processing`).
- **Acesso e Persistência de Dados:** Acessa diretamente os repositórios do TypeORM usando uma função helper (`getRepository`) para buscar e salvar entidades `LaudoOlivia` e `Usuario`.
- **Lógica de Negócio:** Contém lógica para extração de CPF, validação de dados de entrada e geração de nomes de arquivo.
- **Armazenamento de Objetos (MinIO):** Interage diretamente com o cliente MinIO para salvar e recuperar arquivos.
- **Serviço de Arquivos (File Serving):** Possui um endpoint (`/laudo/:filename`) dedicado a servir arquivos PDF diretamente do MinIO.

**Evidência (SRP) - `sistema_teste/olivia-back/src/gateways/http/controllers/domain/laudo/laudo.controller.ts`:**
```typescript
@Controller('api')
export class LaudoController {
  // Responsabilidade: Manipulação de FS
  private async removeFile(filePath?: string): Promise<void> { /*...*/ }

  @Post('extract-pdf-data')
  async extractPdfData(/*...*/) {
    // ...
    // Responsabilidade: Acesso a Dados
    const userRepo = getRepository<Usuario>(Usuario);
    // ...
    // Responsabilidade: Armazenamento de Objetos
    await minioClient.fPutObject(MINIO_BUCKET, usuarioFileName, laudoFile.path);
    // Responsabilidade: Comunicação com API Externa
    const apiResponse = await axios.post(`${process.env.IA_API_URL}/extract-pdf-data`, formData, { /*...*/ });
    // ...
  }

  @Get('laudo/historico')
  async getHistorico() {
    // Responsabilidade: Acesso a Dados
    const laudoRepo = getRepository<LaudoOlivia>(LaudoOlivia);
    // ...
  }

  @Get('laudo/:filename')
  async getLaudoPdf(@Param('filename') filename: string, @Res() res: Response) {
    // Responsabilidade: Serviço de Arquivos
    const fileStream = await minioClient.getObject(MINIO_BUCKET, sanitizedFilename);
    // ...
  }
}
```

**2. Violação do Princípio da Inversão de Dependência (DI):**

A aplicação utiliza o padrão **Service Locator**, que é um anti-padrão e uma violação direta do DI. Em vez de declarar suas dependências e recebê-las via injeção no construtor, as classes (como o `LaudoController`) buscam ativamente suas dependências usando a função `getRepository()`. Isso acopla fortemente o controller à implementação concreta do provedor de dados, dificulta os testes (exigindo mock da função global `getRepository` em vez de simplesmente prover um repositório falso) e esconde as dependências da classe.

**Evidência (DI) - `sistema_teste/olivia-back/src/infrastructure/databases/typeorm/postgres/database.providers.ts`:**
```typescript
// Helper que implementa o Service Locator
export const getRepository = <T extends { id?: any }>(target: any): RepositoryLike<T> => {
  return (getDataSource() as any).getRepository(target) as RepositoryLike<T>;
};
```

**Evidência (DI) - Uso no `LaudoController`:**
```typescript
// O controller "pede" a dependência em vez de recebê-la
const userRepo = getRepository<Usuario>(Usuario);
const usuario = await userRepo.findOne({ where: { nrCpf: cpf } });

const laudoRepo = getRepository<LaudoOlivia>(LaudoOlivia);
const laudo = await laudoRepo.findOne({ /*...*/ });
```
Outra violação de DI é a importação e uso direto de clientes de serviços externos, como o `minioClient`. A instância do cliente é criada e exportada diretamente, e qualquer classe que precise dela a importa, criando um acoplamento forte.

**Evidência (DI) - `sistema_teste/olivia-back/src/infrastructure/minio/minio.client.ts`:**
```typescript
import { Client } from 'minio';

// Instanciação direta e exportação
const minioClient = new Client({ /*...*/ });

export default minioClient;
```

**Recomendações:**
- **Refatorar para SRP:** Dividir o `LaudoController` em componentes menores e mais focados.
    - Criar um `LaudoService` que encapsule a lógica de negócio principal (orquestração de chamadas à IA, salvamento no banco, etc.).
    - Criar um `StorageService` (ou `MinioService`) para abstrair a interação com o MinIO. Este serviço deve ser injetado no `LaudoService`.
    - O controller deve ser "magro", apenas recebendo a requisição, validando a entrada (usando Pipes do NestJS) e delegando o trabalho para o `LaudoService`.
    - O endpoint de download de arquivos (`/laudo/:filename`) poderia ser movido para um `FileController` dedicado ou permanecer, mas delegando a lógica para o `StorageService`.
- **Adotar Injeção de Dependência:** Abandonar o padrão Service Locator (`getRepository`).
    - Configurar `TypeOrmModule.forFeature([LaudoOlivia, Usuario])` no módulo correspondente (provavelmente `HttpModule` ou um novo `LaudoModule`).
    - Injetar os repositórios diretamente no construtor dos serviços e controllers usando o decorador `@InjectRepository()`.
    - **Exemplo de correção:**
      ```typescript
      // laudo.controller.ts
"""

print("Testing regex pattern...")

# Original regex from llm_service.py
criteria_pattern = r'##\s*Crit[ée]rio\s*(?:(\d+(?:\.\d+)*)\s*[:]\s*)?(?:[:]\s*)?(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*(?:(?:\d+)\s*[:]?\s*)?(?:[:]\s*)?|\n##\s*(?:Resultado|Recomendações)\s*(?:Geral|)|#FIM#|$)'

print(f"Pattern: {criteria_pattern}")
print(f"Looking for criteria in content of length: {len(test_content)}")

matches = re.findall(criteria_pattern, test_content, re.DOTALL)
print(f"Matches found: {len(matches)}")
for i, match in enumerate(matches):
    print(f"Match {i+1}: {match}")

# Try simpler pattern
simple_pattern = r'##\s*Crit[ée]rio\s*(\d+)\s*[:]\s*(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*\d+|\n##\s*(?:Resultado|Recomendações)|#FIM#|$)'
print(f"\nTrying simpler pattern: {simple_pattern}")
simple_matches = re.findall(simple_pattern, test_content, re.DOTALL)
print(f"Simple pattern matches: {len(simple_matches)}")
for i, match in enumerate(simple_matches):
    print(f"Simple match {i+1}: {match}")

# Even simpler pattern
very_simple_pattern = r'##\s*Crit[ée]rio\s*(\d+)\s*[:]\s*(.+?)(?=\n##|$)'
print(f"\nTrying very simple pattern: {very_simple_pattern}")
very_simple_matches = re.findall(very_simple_pattern, test_content, re.DOTALL)
print(f"Very simple pattern matches: {len(very_simple_matches)}")
for i, match in enumerate(very_simple_matches):
    print(f"Very simple match {i+1}: {match}")