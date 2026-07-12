<!--
Relatório de Impacto de Sincronização
- Mudança de versão: 1.1.0 → 2.0.0
- Princípios modificados:
  - IV. Mudanças Versionadas e Revisáveis → IV. Mudanças Versionadas
    (BACKWARD-INCOMPATIBLE: removida a exigência de revisão por PR e a
    proibição de push direto na branch principal — projeto simples, decisão
    explícita do mantenedor em 2026-07-12; quality gates automatizados
    continuam obrigatórios)
- Seções expandidas:
  - Fluxo de Desenvolvimento & Quality Gates (gates continuam obrigatórios
    antes de qualquer push/merge; aprovação humana vira recomendada, não
    obrigatória)
- Seções removidas: nenhuma
- Templates que precisam de atualização:
  - .specify/templates/plan-template.md ✅ nenhuma mudança necessária
  - .specify/templates/spec-template.md ✅ idem
  - .specify/templates/tasks-template.md ✅ idem
  - .specify/templates/checklist-template.md ✅ idem
- TODOs de acompanhamento: nenhum
-->

# Constituição do mcp-fastapi

## Princípios Fundamentais

### I. Test-First (TDD) — Não Negociável

Toda tool/resource MCP e toda lógica de servidor MUST ter testes escritos e
aprovados antes da implementação começar. O ciclo Red-Green-Refactor é
obrigatório: escreva um teste que falha, confirme que falha pelo motivo
esperado, e só então implemente o mínimo de código para passá-lo. Nenhuma
feature é integrada com implementação commitada antes de, ou sem, seus
testes.

**Motivo**: o valor deste projeto é servir orientação confiável sobre
FastAPI através de tools MCP. Lógica de tool sem teste é o jeito mais rápido
de servir, silenciosamente, orientação errada ou desatualizada a um agente
que não tem como conferir sozinho.

### II. Tipagem Estrita & Simplicidade (YAGNI)

Todo código Python MUST passar em type-checking estrito (`mypy --strict` ou
equivalente), sem supressões, exceto onde uma limitação documentada de
terceiros exigir. Priorize a standard library, os primitivos nativos do MCP
SDK e código já existente neste repo antes de escrever novas abstrações ou
adicionar uma dependência. Nada de configuração especulativa, flexibilidade
não usada, ou código escrito "para depois". A complexidade cognitiva por
função/método MUST se manter baixa o bastante para revisão em uma única
passada; quebre a lógica antes que fique ilegível.

**Motivo**: este é um servidor pequeno e de propósito único. Toda
dependência, camada de abstração ou escape hatch de tipo é custo de
manutenção sem necessidade correspondente de produto — YAGNI vale por
padrão.

### III. Fidelidade de Contrato MCP/API

Todo schema de tool e resource MCP MUST estar em conformidade com a
especificação do protocolo MCP e MUST refletir fielmente seu material de
origem em `docs/references/`. Quando um documento de referência muda, toda
tool/resource construída a partir dele MUST ser revisada e atualizada na
mesma mudança — conteúdo e código não podem divergir. Tools MUST NOT alegar
capacidades, parâmetros ou comportamento do FastAPI que não estejam
amparados pelo material de referência ou verificados contra a versão
instalada do FastAPI.

**Motivo**: agentes que chamam este servidor confiam na saída como fonte de
verdade sobre FastAPI. Um schema que mente sobre suas entradas/saídas, ou
orientação que divergiu da sua origem, é pior do que nenhum servidor.

### IV. Mudanças Versionadas

Os contratos públicos de tool/resource do servidor (nomes, parâmetros,
formatos de retorno) são versionados via versionamento semântico
(MAJOR.MINOR.PATCH). Qualquer mudança que quebre o contrato de uma tool
existente exige um bump de MAJOR e deve ser explicitada na descrição da
mudança. O versionamento do pacote/repositório em si é automático, dirigido
por Conventional Commits (`feat`/`fix`/`feat!`) via **python-semantic-release**
— sem bump manual, sem PR de release. Push direto na branch principal é
permitido — não há exigência de PR/revisão humana para este projeto; os
quality gates automatizados (§ Fluxo de Desenvolvimento) continuam
obrigatórios independentemente de como a mudança chega à branch principal.

**Motivo**: agentes integram com esses contratos de tool de forma
programática; uma quebra silenciosa quebra todo chamador a jusante sem
aviso. Automatizar o versionamento remove o risco de esquecer o bump ou de
escrevê-lo errado à mão. Exigir PR seria ceremonial demais para um projeto
de porte simples e mantenedor único — o que protege a qualidade são os
gates automatizados, não o processo de revisão.

### V. Idioma — Domínio em pt-BR, Técnica em Inglês

O vocabulário de negócio deste projeto — conceitos de domínio, documentação,
comentários de código e toda comunicação sobre o projeto (specs, PRs,
issues, conversas com o mantenedor) — é em **português brasileiro (pt-BR)**
e não se traduz nem se genericiza. Termos técnicos padrão de mercado (nomes
de framework, padrões de código como `Repository`/`Service`/`handler`, tipos
de commit `feat`/`fix`, siglas como MCP/API/TDD/YAGNI/SemVer) seguem a
convenção usual — em geral inglês.

**Motivo**: mantém o projeto acessível ao mantenedor e a quem revisar o
trabalho, sem abrir mão da terminologia técnica padrão, que teria tradução
forçada e confusa.

## Stack Tecnológica & Fidelidade de Conteúdo

- **Linguagem/Runtime**: Python 3.12+.
- **Gerenciador de pacotes**: **uv** — único gerenciador de dependências e
  ambientes do projeto.
- **Servidor**: MCP Python SDK para a implementação do protocolo; FastAPI
  MAY ser usado onde um transporte HTTP/SSE ou um servidor de exemplo
  demonstrável for necessário.
- **Fonte de verdade**: o diretório `docs/references/` (excertos da documentação
  oficial do FastAPI) é a fonte canônica de conteúdo para qualquer
  tool/resource que sirva orientação sobre FastAPI. Conteúdo não rastreável
  a um arquivo de referência ou a uma versão verificada do FastAPI MUST ser
  sinalizado como tal, nunca apresentado como equivalente a orientação com
  fonte.
- **Fora de escopo desta stack** (não se aplicam a este projeto): banco de
  dados/SQLAlchemy/Alembic/PostgreSQL — não há necessidade de persistência,
  o conteúdo já vive como markdown em `docs/references/`; e o par `web/` +
  contrato OpenAPI-TS — este projeto não tem frontend.
- **Qualidade de código**:
  - **ruff** — lint e formatação (substitui flake8/black/isort).
  - **mypy --strict** (ou equivalente estrito configurado) MUST rodar limpo
    em CI.
  - **bandit** — SAST de segurança para Python.
  - **pip-audit** — auditoria de CVEs nas dependências.
  - **pytest** — runner de testes.
  - **pre-commit** — hooks automáticos antes do commit, rodando as
    ferramentas acima.
- **Commits e versionamento**: Conventional Commits, validados via
  commitizen (`cz check`); versão, changelog, tag e release são gerados
  automaticamente pelo **python-semantic-release** a cada push na branch
  principal — nunca à mão.
- **Versões pinadas**: dependências e ferramentas de dev MUST ser fixadas no
  lockfile (`uv.lock`); a versão exata de cada ferramenta é decisão de
  scaffold/manutenção, não de constituição.

## Fluxo de Desenvolvimento & Quality Gates

- **Antes de qualquer push/merge**: type-check, lint (ruff), SAST (bandit) e
  a suíte de testes completa MUST passar. Revisão por PR é recomendada, mas
  não obrigatória — push direto na `main` é permitido (Princípio IV).
- **Test-first continua obrigatório** (Princípio I) mesmo sem PR: o autor
  garante o commit prévio somente-de-teste antes de commitar a
  implementação. Se houver revisão, a ausência dessa evidência é motivo de
  devolução.
- **Mudanças de contrato**: toda mudança que toca um schema de tool/resource
  MUST declarar o impacto de semver (PATCH/MINOR/MAJOR) na mensagem de
  commit ou no PR, quando houver um.
- **Mensagens de commit**: MUST seguir Conventional Commits; o tipo
  (`feat`/`fix`/`feat!`/etc.) é o que dispara o bump automático de versão —
  é o único trabalho manual do processo de release.

## Governança

Esta constituição prevalece sobre qualquer outra prática ou convenção do
projeto. Emendas exigem: (1) justificativa documentada da mudança, (2) bump
de versão conforme a política abaixo, e (3) propagação da mudança para
qualquer template ou arquivo de workflow dependente em `.specify/` na mesma
emenda.

**Política de versionamento**:
- **MAJOR**: remoção ou redefinição, incompatível com o anterior, de um
  princípio ou regra de governança.
- **MINOR**: um novo princípio é adicionado ou uma orientação existente é
  expandida de forma material.
- **PATCH**: esclarecimentos de texto, correções de digitação, refinamentos
  não semânticos.

Toda mudança MUST honrar os Princípios Fundamentais acima, revisada em PR ou
não (Princípio IV). Qualquer desvio MUST ser justificado por escrito (ex.:
na seção Complexity Tracking do plano) ou a mudança MUST ser rejeitada.
Complexidade que não possa ser justificada contra o Princípio II é motivo
de rejeição por si só.

**Versão**: 2.0.0 | **Ratificada em**: 2026-07-12 | **Última Emenda**: 2026-07-12
