# Pesquisa: Searchable FastAPI Reference Docs

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

## 1. SDK do servidor MCP

**Decisão**: usar o **MCP Python SDK** oficial (`mcp`) para implementar o
servidor e expor as três capacidades (buscar, obter documento, listar) como
MCP tools, com transporte **stdio** para v1.

**Motivo**: é a implementação de referência do protocolo, evita reimplementar
serialização JSON-RPC/schemas à mão (Princípio II — priorizar primitivos
existentes antes de código novo). stdio é o transporte padrão para servidores
MCP rodados localmente por um cliente/agente e cobre o caso de uso descrito
na spec sem exigir infraestrutura HTTP.

**Alternativas consideradas**:
- Implementar o protocolo MCP manualmente sobre stdio — rejeitado: reinventa
  o que o SDK oficial já resolve (viola YAGNI/Princípio II).
- Expor via FastAPI + transporte HTTP/SSE — a constituição permite (`FastAPI
  MAY ser usado`), mas não há requisito na spec que exija rede/HTTP para v1;
  fica como extensão futura se um cliente remoto precisar.

## 2. Estratégia de busca

**Decisão**: busca por palavra-chave/full-text usando **apenas a standard
library** — tokenização simples (`re`), pontuação por frequência de termo no
título (peso maior) e no corpo (peso menor), sem dependência externa de
busca (ex.: whoosh, rapidfuzz, elasticsearch).

**Motivo**: o corpus tem ~39 documentos (dezenas de KB), pequeno o bastante
para varrer em memória a cada consulta dentro da meta de <1s (SC-002). Isso
já foi documentado como suposição na spec (`Assumptions`). Uma dependência de
busca dedicada seria complexidade sem necessidade correspondente de produto
— Princípio II (YAGNI) e a régua do projeto (stdlib antes de dependência
nova).

**Alternativas consideradas**:
- `rapidfuzz`/`whoosh`: melhor ranking e fuzzy matching, mas dependência
  extra para um ganho não comprovadamente necessário nesta escala. Fica como
  upgrade se a precisão da busca stdlib se mostrar insuficiente em uso real.
- Busca semântica/embeddings: rejeitada na própria spec (`Assumptions`) —
  fora de escopo para v1.

## 3. Nomenclatura das MCP tools

**Decisão**: nomes de tool/parâmetro em **inglês** (`search_docs`,
`get_document`, `list_documents`), descrições (`description` exibida ao
agente) também em inglês por serem sobre a documentação oficial do FastAPI
(em inglês); prosa de design/specs/comentários do projeto continua em pt-BR.

**Motivo**: Princípio V da constituição trata identificadores técnicos de
protocolo/framework como "termos técnicos padrão de mercado" — seguem a
convenção usual (inglês), assim como nomes de tools MCP em geral no
ecossistema. O que é pt-BR é o vocabulário de domínio do *projeto*
(specs, comentários, comunicação), não a superfície de protocolo consumida
por qualquer cliente MCP.

**Alternativas consideradas**: nomes de tool em pt-BR (`buscar_documentos`)
— rejeitado por destoar da convenção do ecossistema MCP e por não ser
"vocabulário de negócio" no sentido do Princípio V.

## 4. Carregamento do corpus

**Decisão**: carregar todos os arquivos de `docs/references/*.md` em memória na
inicialização do servidor (uma lista de documentos com id estável, título e
conteúdo); sem cache em disco, sem banco de dados.

**Motivo**: consistente com a suposição documentada na spec (recarregar
requer reiniciar o servidor) e com a constituição (sem persistência). Mantém
a implementação em uma única responsabilidade simples.

**Alternativas consideradas**: watch de sistema de arquivos para hot-reload
— rejeitado por não haver requisito funcional para isso (FR/SC da spec não
exigem atualização sem restart).

## 5. Identificador estável de documento

**Decisão**: o identificador é o **nome do arquivo sem extensão** dentro de
`docs/references/` (ex.: `08 Background Tasks - BackgroundTasks`), usado tanto no
resultado de busca/listagem quanto como parâmetro de `get_document`.

**Motivo**: já é único por construção (checado na carga do corpus) e legível
— cobre FR-002/FR-003/FR-004 sem precisar inventar um esquema de IDs
paralelo.

**Alternativas consideradas**: hash de conteúdo ou índice numérico
sequencial — rejeitados por serem menos legíveis para depuração sem
benefício adicional.

## Status

Todas as incógnitas do Technical Context foram resolvidas. Nenhum
`NEEDS CLARIFICATION` remanescente.
