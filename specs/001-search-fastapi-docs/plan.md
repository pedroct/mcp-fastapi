# Implementation Plan: Searchable FastAPI Reference Docs

**Branch**: `001-search-fastapi-docs` | **Date**: 2026-07-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-search-fastapi-docs/spec.md`

**Note**: repositório Git ainda não foi inicializado neste projeto; a
branch acima é o identificador da feature, a ser criada quando o `git init`
ocorrer.

## Summary

Expor os documentos de `docs/references/` (guias oficiais do FastAPI) como três
MCP tools — busca por palavra-chave, obtenção do conteúdo completo de um
documento e listagem de todos os documentos — para que agentes de IA possam
consultar orientação sobre FastAPI ancorada em fonte real, em vez de
depender só de conhecimento pré-treinado. Abordagem: servidor MCP em Python
(SDK oficial), corpus carregado em memória, busca por palavra-chave com
apenas a standard library (sem banco de dados, sem dependência de busca
externa) — ver `research.md`.

## Technical Context

**Language/Version**: Python 3.12+ (Constituição v1.1.0)

**Primary Dependencies**: MCP Python SDK (`mcp`) para o protocolo/servidor;
fora isso, apenas standard library (`re`, `pathlib`) — sem lib de busca
externa (ver `research.md` §2)

**Storage**: N/A — arquivos markdown somente-leitura em `docs/references/`,
carregados em memória na inicialização (sem banco de dados, ver
`research.md` §4)

**Testing**: pytest

**Target Platform**: processo local falado via transporte MCP stdio
(Linux/macOS/Windows) — sem servidor HTTP em v1

**Project Type**: pacote Python único (servidor MCP) — sem frontend

**Performance Goals**: busca/obtenção/listagem respondem em <1s (SC-002)

**Constraints**: corpus somente-leitura (~39 documentos, dezenas de KB);
sem autenticação (conteúdo é documentação pública do FastAPI, ver
`spec.md` Assumptions)

**Scale/Scope**: 39 documentos de referência hoje; corpus deve seguir na
casa das dezenas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Avaliação |
|---|---|
| I. Test-First (TDD) | PASS — `tasks.md` vai sequenciar testes de contrato/unitários antes da implementação de cada tool |
| II. Tipagem Estrita & Simplicidade (YAGNI) | PASS — busca em stdlib (sem dependência nova), sem banco, sem abstração especulativa; `mypy --strict` cobre o pacote inteiro |
| III. Fidelidade de Contrato MCP/API | PASS — schemas em `contracts/mcp-tools.md` derivam só de `docs/references/`; nenhuma tool alega capacidade não amparada pela fonte |
| IV. Mudanças Versionadas e Revisáveis | PASS — feature inicial (0.x), sem contrato prévio a quebrar; versionamento fica a cargo do python-semantic-release via Conventional Commits |
| V. Idioma — Domínio em pt-BR | PASS — este plano e os demais artefatos de design estão em pt-BR; nomes de tool/parâmetro seguem inglês por serem superfície de protocolo (ver `research.md` §3) |

Nenhuma violação — **Complexity Tracking** não se aplica.

## Project Structure

### Documentation (this feature)

```text
specs/001-search-fastapi-docs/
├── plan.md              # este arquivo
├── research.md           # Fase 0
├── data-model.md          # Fase 1
├── quickstart.md          # Fase 1
├── contracts/              # Fase 1
│   └── mcp-tools.md
└── tasks.md               # Fase 2 (via /speckit-tasks — ainda não criado)
```

### Source Code (repository root)

```text
src/
└── mcp_fastapi/
    ├── __init__.py
    ├── __main__.py       # entrada `uv run python -m mcp_fastapi`
    ├── server.py          # registro das MCP tools (search_docs, get_document, list_documents)
    ├── corpus.py           # carrega e valida docs/references/*.md em ReferenceDocument
    └── search.py            # tokenização + ranking (stdlib)

tests/
├── contract/
│   └── test_mcp_tools.py    # os 6 cenários de contracts/mcp-tools.md
└── unit/
    ├── test_corpus.py       # carga do corpus, unicidade de id, FR-010
    └── test_search.py       # ranking, empty query, sem match, cap de resultados
```

**Structure Decision**: pacote único em `src/mcp_fastapi/` (Option 1 —
projeto único), sem `backend/`/`frontend/`: a feature não tem frontend nem
persistência (ver `research.md`). Layout `src/` + `tests/` segue o padrão de
scaffolding Python do playbook de stack do projeto (`docs/padroes_de_stack.md`
§3), adaptado para um pacote único em vez do par `api/`+`web/`.

## Complexity Tracking

> Sem violações do Constitution Check — tabela não aplicável.
