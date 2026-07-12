---

description: "Task list template for feature implementation"
---

# Tasks: Searchable FastAPI Reference Docs

**Input**: Design documents de `/specs/001-search-fastapi-docs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.md, quickstart.md

**Tests**: MANDATÓRIO — Princípio I (Test-First/TDD, não-negociável) da
constituição exige teste escrito e falhando **antes** de qualquer
implementação de lógica de tool/resource. As tarefas de teste abaixo não
são opcionais.

**Organization**: Tarefas agrupadas por User Story (spec.md) para permitir
implementação e teste independentes de cada uma.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: A qual user story a tarefa pertence (US1, US2, US3)
- Caminho de arquivo exato em cada descrição

## Path Conventions

Projeto único (`src/`, `tests/` na raiz do repo) — ver `plan.md` § Project
Structure. Sem `backend/`/`frontend/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: inicialização do projeto Python

- [ ] T001 Criar a estrutura de diretórios `src/mcp_fastapi/` e
  `tests/{contract,unit}/` conforme `plan.md` § Project Structure
- [ ] T002 Inicializar `pyproject.toml` via `uv` (Python 3.12+), com
  dependência `mcp` (MCP Python SDK — ver `research.md` §1) e dev deps
  `ruff`, `mypy`, `pytest`, `bandit`, `pip-audit`, `pre-commit` conforme
  constituição § Stack Tecnológica
- [ ] T003 [P] Configurar `ruff` (lint + format) e `mypy --strict` em
  `pyproject.toml` conforme constituição § Stack Tecnológica
- [ ] T004 [P] Configurar `.pre-commit-config.yaml` (hooks `ruff-check`,
  `ruff-format`, `mypy`, `bandit`) conforme constituição § Stack Tecnológica

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: carga do corpus e bootstrap do servidor — bloqueia todas as
user stories

**⚠️ CRITICAL**: nenhuma user story pode começar antes desta fase completa

- [ ] T005 [P] Teste unitário de carga do corpus em
  `tests/unit/test_corpus.py` — todo arquivo de `docs/references/*.md` vira
  um `DocumentoReferencia` (FR-010), `id` único validado na carga (ver
  `data-model.md`); escrever e confirmar que falha antes de T006
- [ ] T006 Implementar `DocumentoReferencia` e `carregar_documentos()` em
  `src/mcp_fastapi/corpus.py` — faz T005 passar (ver `research.md` §4-5)
- [ ] T007 Implementar bootstrap do servidor MCP em
  `src/mcp_fastapi/server.py` — instancia o servidor (stdio, ver
  `research.md` §1) e carrega o corpus via T006 na inicialização, ainda sem
  tools registradas (depende de T006)
- [ ] T008 Implementar entrypoint `src/mcp_fastapi/__main__.py`
  (`uv run python -m mcp_fastapi`, ver `quickstart.md`) (depende de T007)

**Checkpoint**: fundação pronta — user stories podem começar

---

## Phase 3: User Story 1 - Busca por tópico (Priority: P1) 🎯 MVP

**Goal**: tool `buscar_documentos` — um agente envia uma consulta e recebe
os documentos de referência mais relevantes, com trecho justificando o
match (FR-001, FR-002, FR-005, FR-006, FR-008)

**Independent Test**: chamar `buscar_documentos` com
`{"consulta": "background tasks"}` e confirmar que o documento correto
aparece entre os 3 primeiros resultados (SC-001)

### Tests for User Story 1 (MANDATÓRIO — ver nota de TDD acima) ⚠️

> Escrever estes testes PRIMEIRO, confirmar que FALHAM antes de implementar

- [ ] T009 [P] [US1] Teste de contrato de `buscar_documentos` em
  `tests/contract/test_mcp_tools.py` — cenários 1-3 de
  `contracts/mcp-tools.md` (match no top-3, sem match → `[]`, consulta
  vazia → erro de validação)
- [ ] T010 [P] [US1] Teste unitário de ranking em
  `tests/unit/test_search.py` — peso maior para match no título vs. corpo,
  cap em `limite_resultados` (FR-008), consulta vazia/só espaço levanta
  erro (FR-006)

### Implementation for User Story 1

- [ ] T011 [US1] Implementar tokenização e ranking em
  `src/mcp_fastapi/search.py` — `ConsultaBusca`, `ResultadoBusca`,
  `ranquear()` (stdlib apenas, ver `research.md` §2) (depende de T010, T006;
  faz T010 passar)
- [ ] T012 [US1] Registrar a tool `buscar_documentos` em
  `src/mcp_fastapi/server.py` — schema de `contracts/mcp-tools.md`, valida
  `consulta` vazia (FR-006), aplica `limite_resultados` (FR-008) (depende de
  T011, T009; faz T009 passar)

**Checkpoint**: US1 funcional e testável isoladamente — MVP entregável

---

## Phase 4: User Story 2 - Obter documento completo (Priority: P2)

**Goal**: tool `obter_documento` — dado um `id_documento` (ex.: retornado
por uma busca), devolve o conteúdo completo e sem modificação do documento
de referência (FR-003, FR-007)

**Independent Test**: pegar um `id_documento` retornado por uma busca da
US1, chamar `obter_documento` com ele e confirmar que o `conteudo` é
idêntico ao arquivo fonte em `docs/references/` (SC-004)

### Tests for User Story 2 (MANDATÓRIO — ver nota de TDD acima) ⚠️

- [ ] T013 [P] [US2] Teste de contrato de `obter_documento` em
  `tests/contract/test_mcp_tools.py` — cenários 4-5 de
  `contracts/mcp-tools.md` (id válido retorna conteúdo completo, id
  inexistente retorna "não encontrado" sem exceção não tratada)

### Implementation for User Story 2

- [ ] T014 [US2] Registrar a tool `obter_documento` em
  `src/mcp_fastapi/server.py` — busca no corpus (T006) por `id_documento`,
  resposta clara de "não encontrado" se ausente (FR-007) (depende de T013,
  T006; faz T013 passar)

**Checkpoint**: US1 e US2 funcionais e testáveis isoladamente

---

## Phase 5: User Story 3 - Listar todos os documentos (Priority: P3)

**Goal**: tool `listar_documentos` — lista todo o corpus (título + id) sem
exigir consulta, para descoberta de tópicos (FR-004, FR-010)

**Independent Test**: chamar `listar_documentos` sem parâmetros e conferir
um item por arquivo em `docs/references/*.md` (SC-003)

### Tests for User Story 3 (MANDATÓRIO — ver nota de TDD acima) ⚠️

- [ ] T015 [P] [US3] Teste de contrato de `listar_documentos` em
  `tests/contract/test_mcp_tools.py` — cenário 6 de `contracts/mcp-tools.md`
  (tamanho da lista = quantidade de arquivos em `docs/references/*.md`)

### Implementation for User Story 3

- [ ] T016 [US3] Registrar a tool `listar_documentos` em
  `src/mcp_fastapi/server.py` — retorna `id_documento` + `titulo` de todo o
  corpus (T006) (depende de T015, T006; faz T015 passar)

**Checkpoint**: as três user stories funcionais e testáveis isoladamente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: qualidade e validação final, cobrindo as três user stories

- [ ] T017 [P] Rodar `mypy --strict` e `ruff check` em `src/` e `tests/`,
  corrigir achados (constituição § Stack Tecnológica)
- [ ] T018 [P] Rodar `bandit` e `pip-audit`, corrigir achados (constituição
  § Stack Tecnológica)
- [ ] T019 Validar manualmente os 6 passos de `quickstart.md` (`mcp dev` ou
  cliente MCP via stdio)
- [ ] T020 [P] Escrever `README.md` mínimo (instalação via `uv`, como rodar
  o servidor, aponta para `quickstart.md` para validação)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente
- **Foundational (Phase 2)**: depende do Setup — BLOQUEIA todas as user
  stories
- **User Stories (Phase 3-5)**: todas dependem do fim do Foundational
  - US1, US2 e US3 são independentes entre si (todas só dependem de T006 —
    carga do corpus); podem rodar em paralelo se houver capacidade
  - Ordem sequencial sugerida: P1 → P2 → P3 (prioridade da spec.md)
- **Polish (Phase 6)**: depende de todas as user stories desejadas estarem
  completas

### User Story Dependencies

- **US1 (P1)**: depende só do Foundational (T006) — sem dependência de
  US2/US3
- **US2 (P2)**: depende só do Foundational (T006) — independente de US1,
  ainda que reutilize `id_documento` que a US1 também produz
- **US3 (P3)**: depende só do Foundational (T006) — independente de US1/US2

### Within Each User Story

- Testes MUST ser escritos e FALHAR antes da implementação (Princípio I)
- `search.py`/registro de tool depois do teste correspondente
- Story completa antes de avançar para a próxima prioridade

### Parallel Opportunities

- T003 e T004 (Setup) podem rodar em paralelo
- T005 (Foundational) é o único [P] da fase — os demais dependem em cadeia
- Depois de T006 (corpus pronto), as três user stories podem ser
  desenvolvidas em paralelo por pessoas diferentes
- Dentro de cada story, as tarefas de teste marcadas [P] rodam em paralelo
- T017, T018 e T020 (Polish) podem rodar em paralelo

---

## Parallel Example: User Story 1

```bash
# Testes da US1 em paralelo:
Task: "Teste de contrato de buscar_documentos em tests/contract/test_mcp_tools.py"
Task: "Teste unitário de ranking em tests/unit/test_search.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 apenas)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO — bloqueia todas as stories)
3. Completar Phase 3: User Story 1 (`buscar_documentos`)
4. **PARAR e VALIDAR**: testar US1 isoladamente (cenário 1 de
   `quickstart.md`)
5. Rodar/demonstrar se pronto

### Incremental Delivery

1. Setup + Foundational → fundação pronta
2. US1 (`buscar_documentos`) → testar isoladamente → MVP
3. US2 (`obter_documento`) → testar isoladamente
4. US3 (`listar_documentos`) → testar isoladamente
5. Cada story agrega valor sem quebrar as anteriores

---

## Notes

- [P] = arquivos diferentes, sem dependência entre si
- [Story] mapeia a tarefa à user story correspondente da spec.md
- Cada user story é completável e testável de forma independente
- Confirmar que os testes falham antes de implementar (TDD, Princípio I)
- Commitar após cada tarefa ou grupo lógico de tarefas (push direto na
  `main` é permitido — Princípio IV — mas os quality gates de T017/T018
  MUST passar antes)
- Parar em qualquer checkpoint para validar a story isoladamente
