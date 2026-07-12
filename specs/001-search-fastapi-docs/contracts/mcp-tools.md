# Contrato: MCP Tools

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

Três MCP tools, nomes e parâmetros em inglês (ver `research.md` §3).
Formato de schema: JSON Schema, como o MCP Python SDK espera para
`inputSchema`.

## `search_docs`

Cobre User Story 1 (P1) — FR-001, FR-002, FR-005, FR-006, FR-008.

**Input**:
```json
{
  "type": "object",
  "properties": {
    "query": { "type": "string", "minLength": 1, "description": "Search text (topic, keyword, or short phrase)" }
  },
  "required": ["query"]
}
```

**Output** (lista, possivelmente vazia; máx. 10 itens):
```json
[
  {
    "document_id": "08 Background Tasks - BackgroundTasks",
    "title": "Background Tasks - BackgroundTasks",
    "excerpt": "...trecho onde o termo buscado aparece...",
    "score": 0.83
  }
]
```

**Erros**:
- `query` ausente, vazia ou só espaço → erro de validação (não uma lista
  vazia) — FR-006.

## `get_document`

Cobre User Story 2 (P2) — FR-003, FR-007.

**Input**:
```json
{
  "type": "object",
  "properties": {
    "document_id": { "type": "string", "minLength": 1 }
  },
  "required": ["document_id"]
}
```

**Output**:
```json
{
  "document_id": "08 Background Tasks - BackgroundTasks",
  "title": "Background Tasks - BackgroundTasks",
  "content": "...conteúdo markdown completo e sem modificação..."
}
```

**Erros**:
- `document_id` que não existe no corpus → resposta clara de "não
  encontrado" (não uma exceção não tratada) — FR-007.

## `list_documents`

Cobre User Story 3 (P3) — FR-004, FR-010.

**Input**: nenhum parâmetro.

**Output** (todos os documentos do corpus):
```json
[
  { "document_id": "01 FastAPI class", "title": "FastAPI class" },
  { "document_id": "02 Request Parameters", "title": "Request Parameters" }
]
```

## Cenários de contrato (para os testes de `tests/contract/`)

1. `search_docs({"query": "background tasks"})` → resultado inclui
   `document_id` do documento de background tasks entre os 3 primeiros
   (SC-001).
2. `search_docs({"query": "termo-que-nao-existe-em-nenhum-doc"})` → `[]`.
3. `search_docs({"query": ""})` → erro de validação, não `[]`.
4. `get_document({"document_id": <id válido>})` → `content` idêntico ao
   arquivo fonte em `docs/references/` (SC-004).
5. `get_document({"document_id": "nao-existe"})` → resposta "não
   encontrado", sem exceção não tratada (SC-005).
6. `list_documents({})` → tamanho da lista igual à quantidade de arquivos em
   `docs/references/*.md` (SC-003).
