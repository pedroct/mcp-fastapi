# CHANGELOG


## v1.0.0 (2026-07-12)

### Bug Fixes

- **specs**: Corrigir achados críticos do /speckit-analyze (D1, F1, E1)
  ([`1cd82c0`](https://github.com/pedroct/mcp-fastapi/commit/1cd82c0d4ad4bb020ada704e2182c62c64ce71ba))

- plan.md: corrige a linha V do Constitution Check, que ainda citava a decisão revertida de nomes de
  tool em inglês (contradizia research.md §3) - tasks.md: insere T005-T007 na Setup para CI
  (.github/workflows/ci.yml) e automação de release (python-semantic-release), cobrindo a exigência
  da constituição de que o type-check MUST rodar limpo em CI — antes sem nenhuma tarefa - tasks.md:
  adiciona T024, teste de performance das três tools contra o corpus completo, cobrindo SC-002 (<1s)
  que antes não tinha tarefa - Renumera T005-T020 -> T008-T024 e propaga as referências de
  dependência - Documenta o conflito de arquivo entre T012/T016/T018 (mesmo
  tests/contract/test_mcp_tools.py) na seção de paralelismo

- **specs**: Nomes das MCP tools em pt-BR, não em inglês
  ([`ddb4e6b`](https://github.com/pedroct/mcp-fastapi/commit/ddb4e6b5198fae04e53bf9756d32bc1f00325b27))

Corrige a decisão de research.md §3: a superfície de tool exposta pelo mcp-fastapi
  (buscar_documentos, obter_documento, listar_documentos e seus parâmetros/campos) segue o Princípio
  V (pt-BR) como qualquer outro vocabulário de domínio do projeto — não é "termo técnico de mercado"
  só porque é consumida por um cliente MCP. Propaga a correção para data-model.md,
  contracts/mcp-tools.md, plan.md e quickstart.md.

- **specs**: Resolver achados MEDIUM/LOW do /speckit-analyze (D2, E2, F2, F3)
  ([`fa9ed28`](https://github.com/pedroct/mcp-fastapi/commit/fa9ed28baa5fbe693744c182f57acc352298295b))

- tasks.md: T002 adiciona commitizen às dev deps; T003 configura [tool.commitizen]; T004 adiciona
  hook commitizen-check (stage commit-msg) — fecha a lacuna de enforcement de Conventional Commits -
  contracts/mcp-tools.md + tasks.md (T012): cenário 1 de busca passa a cobrir os 3 termos citados na
  spec (background tasks, websockets, middleware) em vez de só um, mais alinhado à natureza
  estatística de SC-001 (com ressalva de que ainda não é uma amostra estatística completa) -
  plan.md: remove o pin de versão da constituição ("v1.1.0"), que já estava desatualizado;
  referencia "a constituição do projeto" para não ficar obsoleto a cada emenda - spec.md: renomeia
  Key Entities para DocumentoReferencia/ConsultaBusca/ ResultadoBusca, alinhando com data-model.md e
  contracts/mcp-tools.md

### Chores

- Scaffold do projeto (constituição, spec, plan e docs de referência)
  ([`eb21f83`](https://github.com/pedroct/mcp-fastapi/commit/eb21f833e7eda6fa51540eb966199bfe5e64e7c3))

Primeira carga do repositório: constituição v1.1.0, spec/plan/research/ data-model/contracts da
  feature 001-search-fastapi-docs, docs de padrões de stack e o corpus de referência do FastAPI em
  docs/references/.

### Documentation

- Adicionar seção Propósito à constituição (v2.1.0)
  ([`104efff`](https://github.com/pedroct/mcp-fastapi/commit/104efff514b93c6fc46d31c5d7e9bcc7bec93eab))

Explicita que o mcp-fastapi existe para auxiliar uma LLM/agente durante o desenvolvimento real de
  código FastAPI, ancorado nas boas práticas oficiais do FastAPI (docs/references/) — não é um
  mecanismo genérico de busca de documentação. Ajusta o motivo do Princípio I para ecoar esse
  propósito.

- Gerar tasks.md da feature 001-search-fastapi-docs
  ([`d8045a9`](https://github.com/pedroct/mcp-fastapi/commit/d8045a97776fa3b404f5c9fe52fbaeb0182c5dd5))

20 tarefas em 6 fases (Setup, Foundational, US1/US2/US3, Polish), testes mandatórios antes da
  implementação em cada user story (Princípio I - TDD).

- Relaxar exigência de PR na constituição (v2.0.0)
  ([`4f65668`](https://github.com/pedroct/mcp-fastapi/commit/4f65668b78f7a6de708fa42f8cc08c2b7807796b))

Remove a obrigatoriedade de revisão por PR e a proibição de push direto na main (Princípio IV) —
  decisão do mantenedor para um projeto de porte simples. Quality gates automatizados (type-check,
  lint, SAST, testes) continuam obrigatórios independentemente de como a mudança chega à main.

BREAKING CHANGE: Princípio IV não exige mais revisão/PR antes de merge.

### Features

- Implementar servidor MCP de busca em docs do FastAPI
  ([`de00758`](https://github.com/pedroct/mcp-fastapi/commit/de00758ea5746826d94414122f4e78288e11f6c1))

Implementa a feature 001-search-fastapi-docs por completo: as três MCP tools (buscar_documentos,
  obter_documento, listar_documentos) sobre o corpus de docs/references/, com TDD (testes de
  contrato + unitários), mypy --strict, ruff, bandit e pip-audit limpos.

Inclui os ajustes de um code review completo (limpeza de marcação HTML residual no ranqueamento em
  vez de filtro por tamanho de token, título extraído do H1 real do conteúdo, ConsultaBusca conforme
  documentado, fidelidade de schema MCP com minLength, entre outros) e uma auditoria de teste
  unitário por símbolo, garantindo teste dedicado para cada função não-trivial (não só cobertura via
  integração).

Também adiciona scaffold de CI/release (GitHub Actions, pre-commit, semantic-release) e script de
  análise local no SonarQube via pysonar.
