# Quickstart: Searchable FastAPI Reference Docs

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

Guia para validar a feature rodando de ponta a ponta. Detalhes de schema em
`contracts/mcp-tools.md`, de entidades em `data-model.md`.

## Pré-requisitos

- Python 3.12+
- `uv` instalado
- Repositório clonado, com `docs/references/*.md` presente

## Setup

```bash
uv sync
```

## Rodar o servidor MCP (stdio)

```bash
uv run python -m mcp_fastapi
```

## Validar os três fluxos (Acceptance Scenarios da spec)

Usando o inspector do MCP Python SDK (`mcp dev`) ou um cliente MCP
qualquer conectado via stdio ao comando acima:

1. **Busca (User Story 1)**: chame `search_docs` com
   `{"query": "background tasks"}` → espera-se que
   `08 Background Tasks - BackgroundTasks` apareça nos resultados.
2. **Busca sem match**: `search_docs` com
   `{"query": "termo-que-nao-existe-em-nenhum-doc"}` → espera-se `[]`.
3. **Busca inválida**: `search_docs` com `{"query": ""}` → espera-se erro de
   validação.
4. **Obter documento (User Story 2)**: pegue um `document_id` retornado no
   passo 1 e chame `get_document` com ele → espera-se o `content` completo,
   idêntico ao arquivo em `docs/references/`.
5. **Documento inexistente**: `get_document` com
   `{"document_id": "nao-existe"}` → espera-se resposta clara de "não
   encontrado".
6. **Listar (User Story 3)**: chame `list_documents` sem parâmetros →
   espera-se um item por arquivo em `docs/references/*.md`.

## Rodar a suíte automatizada

```bash
uv run pytest
```

Os cenários acima têm equivalentes automatizados em `tests/contract/` e
`tests/unit/` (ver `tasks.md` para o detalhamento por tarefa).
