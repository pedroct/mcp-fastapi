# Contrato: MCP Tools

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

Três MCP tools, nomes e parâmetros em português brasileiro (ver
`research.md` §3). Formato de schema: JSON Schema, como o MCP Python SDK
espera para `inputSchema`.

## `buscar_documentos`

Cobre User Story 1 (P1) — FR-001, FR-002, FR-005, FR-006, FR-008.

**Input**:
```json
{
  "type": "object",
  "properties": {
    "consulta": { "type": "string", "minLength": 1, "description": "Texto de busca (tópico, palavra-chave ou frase curta)" }
  },
  "required": ["consulta"]
}
```

**Output** (lista, possivelmente vazia; máx. 10 itens):
```json
[
  {
    "id_documento": "08 Background Tasks - BackgroundTasks",
    "titulo": "Background Tasks - BackgroundTasks",
    "trecho": "...trecho onde o termo buscado aparece...",
    "pontuacao": 0.83
  }
]
```

**Erros**:
- `consulta` ausente, vazia ou só espaço → erro de validação (não uma lista
  vazia) — FR-006.

## `obter_documento`

Cobre User Story 2 (P2) — FR-003, FR-007.

**Input**:
```json
{
  "type": "object",
  "properties": {
    "id_documento": { "type": "string", "minLength": 1 }
  },
  "required": ["id_documento"]
}
```

**Output** (encontrado):
```json
{
  "encontrado": true,
  "id_documento": "08 Background Tasks - BackgroundTasks",
  "titulo": "Background Tasks - BackgroundTasks",
  "conteudo": "...conteúdo markdown completo e sem modificação...",
  "mensagem": null
}
```

**Output** (não encontrado — FR-007; `titulo`/`conteudo` ficam `null`, não
omitidos, para manter um shape único no schema):
```json
{
  "encontrado": false,
  "id_documento": "nao-existe",
  "titulo": null,
  "conteudo": null,
  "mensagem": "documento 'nao-existe' não encontrado"
}
```

**Erros**:
- `id_documento` ausente, vazio ou só espaço → erro de validação (não a
  resposta de "não encontrado" acima) — mesma regra de `consulta` em
  `buscar_documentos` (FR-006 aplicada por simetria).
- `id_documento` que não existe no corpus → resposta "não encontrado" acima
  (não uma exceção não tratada) — FR-007.

## `listar_documentos`

Cobre User Story 3 (P3) — FR-004, FR-010.

**Input**: nenhum parâmetro.

**Output** (todos os documentos do corpus):
```json
[
  { "id_documento": "01 FastAPI class", "titulo": "FastAPI class" },
  { "id_documento": "02 Request Parameters", "titulo": "Request Parameters" }
]
```

## Cenários de contrato (para os testes de `tests/contract/`)

1. Para cada um dos termos `"background tasks"`, `"websockets"` e
   `"middleware"` (os 3 exemplos citados na spec — US1 e SC-001):
   `buscar_documentos({"consulta": <termo>})` → resultado inclui o
   `id_documento` do documento correspondente entre os 3 primeiros (SC-001
   exige ≥90% de acerto; testar os 3 exemplos nomeados na spec é a
   verificação mínima, não uma amostra estatística completa).
2. `buscar_documentos({"consulta": "termo-que-nao-existe-em-nenhuma-referencia"})` →
   `[]`.
3. `buscar_documentos({"consulta": ""})` → erro de validação, não `[]`.
4. `obter_documento({"id_documento": <id válido>})` → `conteudo` idêntico ao
   arquivo fonte em `docs/references/` (SC-004).
5. `obter_documento({"id_documento": "nao-existe"})` → resposta "não
   encontrado", sem exceção não tratada (SC-005).
6. `listar_documentos({})` → tamanho da lista igual à quantidade de arquivos
   em `docs/references/*.md` (SC-003).
7. `obter_documento({"id_documento": ""})` → erro de validação, não a
   resposta de "não encontrado" (FR-006 por simetria com `consulta`).
