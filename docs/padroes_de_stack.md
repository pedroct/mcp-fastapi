# Padrões de Stack & Playbook de Scaffolding

*Documento de referência reutilizável — use ao criar o esqueleto de novos projetos.*
Versão 2.2 · Junho de 2026

> Dois padrões de stack espelhados (backend Python / frontend TypeScript) em
> **repositórios Git separados**, unidos no editor por um **VS Code multi-root
> workspace** e em runtime por **Docker**. Release e changelog são **totalmente
> automáticos** via semantic-release (sem bump manual, sem PR de release).

> **Por que dois repos (e não monorepo)?** Cada app passa a ser um único projeto:
> versionamento, changelog e release ficam **nativos e independentes**, sem a
> limitação do commitizen em monorepo (que não filtra o bump por path e mistura os
> históricos). Bônus: CI menor e focado por repo, e deploy desacoplado. O custo é o
> contrato FE↔BE atravessar a fronteira de repositório — resolvido na §4.

---

## 1. Os dois padrões em uma olhada

| | Backend | Frontend |
|---|---|---|
| **Repositório** | `…/api` (Git próprio) | `…/web` (Git próprio) |
| **Linguagem** | Python (≥3.12) | TypeScript |
| **Framework** | FastAPI · SQLAlchemy 2 (async) · Alembic · asyncpg | Next.js 16 · React 19 · Tailwind v4 · shadcn/ui |
| **Banco** | PostgreSQL 18 | — |
| **Gerenciador** | **uv** | **pnpm** (npm bloqueado) |
| **Release/changelog** | **python-semantic-release** | **semantic-release** |

- **Isolamento de runtime:** Docker (um contêiner por app), igual em ambos.
- **Contrato FE↔BE:** fonte única = schemas do FastAPI → **OpenAPI** → types TS via
  **openapi-typescript**, publicados como o **pacote versionado `@org/contract`**
  (GitHub Packages) e sincronizados no `web/` por **Renovate** (§4). Substitui o
  `workspace:*` que o monorepo dava de graça.
- **Editor:** um arquivo `.code-workspace` abre os dois repos lado a lado (§2).

---

## 2. Estrutura no disco e nos repositórios

Os dois repos vivem em uma pasta de trabalho comum (que **não** é um repositório).
O `.code-workspace` e o `docker-compose.yml` de desenvolvimento ficam nessa pasta-pai
(ou num repo `infra` dedicado, se você versionar a orquestração).

```
<projeto>/                       # pasta de trabalho — NÃO é repo
├── <projeto>.code-workspace     # multi-root: abre api/ + web/ juntos
├── docker-compose.yml           # dev: orquestra db + api + web
├── .env                         # vars de dev compartilhadas (fora dos repos dos apps)
├── api/                         # ── repo Git #1 (backend) ──
│   ├── pyproject.toml           # uv: deps + ferramentas + semantic_release
│   ├── uv.lock
│   ├── .pre-commit-config.yaml
│   ├── Dockerfile · .dockerignore
│   ├── contract/                # pacote @org/contract (gerado/publicado no CI)
│   ├── CHANGELOG.md             # gerado pelo python-semantic-release
│   ├── src/<pkg>_api/
│   └── tests/
└── web/                         # ── repo Git #2 (frontend) ──
    ├── package.json             # pnpm: deps + scripts
    ├── pnpm-lock.yaml
    ├── biome.json · tsconfig.json
    ├── .npmrc · renovate.json    # scope do GitHub Packages + sync do contrato
    ├── .releaserc.json          # config do semantic-release
    ├── .husky/                  # hooks Git (commitlint, lint-staged)
    ├── Dockerfile · .dockerignore
    ├── CHANGELOG.md             # gerado pelo semantic-release
    └── src/
```

### `<projeto>.code-workspace`
```json
{
  "folders": [
    { "name": "api (backend)", "path": "api" },
    { "name": "web (frontend)", "path": "web" }
  ],
  "settings": {
    "files.exclude": { "**/.venv": true, "**/node_modules": true },
    "python.defaultInterpreterPath": "api/.venv/bin/python"
  }
}
```

**Regra de localização das ferramentas:** cada repo é autocontido — todas as suas
ferramentas (lint, type-check, testes, SAST, release) vivem **dentro do próprio repo**.
Não há mais "ferramenta repo-wide na raiz"; o que era compartilhado no monorepo agora
é duplicado por repo, com config idiomática de cada lado.

---

## 3. Toolchain do BACKEND (Python) — repo `api/`

| Ferramenta | Versão base | Função | Comando |
|---|---|---|---|
| **uv** | 0.11.x | Gerenciador de pacotes/ambientes | `uv` |
| **ruff** | 0.15.14 | Linter + formatter (substitui black, isort, flake8) | `ruff check` / `ruff format` |
| **mypy** | 2.1.0 | Type checking estático — **modo strict** | `mypy` |
| **pre-commit** | 4.6.0 | Hooks automáticos antes do commit | `pre-commit run` |
| **bandit** | 1.9.4 | SAST de segurança (OWASP Python) | `bandit` |
| **pip-audit** | 2.10.0 | Auditoria de CVEs nas dependências | `pip-audit` |
| **sqlfluff** | 4.2.1 | Lint de SQL / migrations Alembic | `sqlfluff lint` |
| **pytest** | 9.0.3 | Runner de testes (plugins no `pyproject.toml`) | `pytest` |
| **commitizen** | 4.16.2 | Escrever/validar Conventional Commits (`cz commit`/`cz check`) | `cz` |
| **python-semantic-release** | 10.5.x | **Release + changelog automáticos** (CI) | `semantic-release` |
| **semgrep** | 1.165.x | SAST multi-linguagem | `semgrep` |
| **pysonar** | 1.6.x¹ | SonarScanner CLI (um projeto Sonar por repo) | `pysonar` |

¹ *A 1.5.0 pode conflitar com `requires-python`; a 1.6.x resolve. Confirme a última estável.*

> **Nota:** o `commitizen` aqui é só para **escrever/validar** mensagens. O *bump*,
> a tag e o CHANGELOG são do **python-semantic-release** (§9) — não rode `cz bump`.

---

## 4. Toolchain do FRONTEND (TypeScript) e contrato — repo `web/`

| Ferramenta | Versão base | Função | Comando |
|---|---|---|---|
| **pnpm** | 11.x | Gerenciador de pacotes/workspaces (**npm bloqueado**) | `pnpm` |
| **Biome** | 2.4.x | Linter + formatter tudo-em-um | `biome check` / `biome format` |
| **TypeScript** (`tsc`) | 6.x | Type checking estático — **modo strict** | `tsc --noEmit` |
| **Vitest** (+ Testing Library) | 4.x | Runner de testes (`@testing-library/react`) | `vitest run` |
| **pnpm audit** | nativo | Auditoria de CVEs nas dependências | `pnpm audit` |
| **semgrep** | 1.165.x | SAST multi-linguagem (mesmo do backend) | `semgrep` |
| **husky + lint-staged** | 9.x / 16.x | Hooks Git automáticos antes do commit¹ | `husky` / `lint-staged` |
| **commitlint** | 19.x | Validar Conventional Commits (`@commitlint/config-conventional`) | `commitlint` |
| **semantic-release** | 24.x | **Release + changelog automáticos** (CI, §9) | `semantic-release` |
| **pysonar** | — | SonarScanner CLI (um projeto Sonar **por repo**) | `pysonar` |

¹ *Para uniformidade total você pode usar `pre-commit` (Python) também no repo `web/`,
aceitando ter Python instalado lá. O padrão idiomático de Node é husky + lint-staged.*

### Contrato FE↔BE: pacote `@org/contract` versionado + Renovate

O FastAPI é a **fonte única** do contrato. Em polyrepo, o `workspace:*` do monorepo
é substituído por um **pacote npm publicado e versionado**, mantido em sincronia
automaticamente. O segredo da garantia "sempre atualizado": **cada mudança de schema
vira um bump de versão do contrato** (pelo mesmo semantic-release), então uma quebra
de contrato fica **visível como `major`** e **revisável** num PR do `web/` — em vez de
latente até alguém regenerar.

**Quem produz (`api/`):** um subprojeto `contract/` empacota os types como `@org/contract`.
No CI de release do `api/`, depois que o python-semantic-release define a versão `X.Y.Z`:
1. exporta `openapi.json` (script `openapi_export.py`);
2. gera os types — `openapi-typescript openapi.json -o contract/index.d.ts`;
3. seta `contract/package.json` na **mesma versão da API** e `npm publish` no
   GitHub Packages.
A versão do contrato **acompanha a da API** (o contrato é a superfície dela). Se quiser
versioná-lo de forma independente, dê a ele seu próprio semantic-release — mas acoplar
é mais simples e semântico.

**Quem consome (`web/`):** declara `@org/contract` como dependência e aponta o scope
para o GitHub Packages via `.npmrc`. O **Renovate** mantém a versão em dia:
- **minor/patch** (compatíveis) → PR + **automerge** se o CI do `web/` passar (zero clique);
- **major** (breaking) → PR **revisável** (sem automerge) — você lê o diff dos types.
> Automerge seguro exige *branch protection* com os checks do `web/` obrigatórios:
> o Renovate só mergeia com o CI verde.

**Fluxo completo (automático ponta a ponta):**
```
schema muda no FastAPI → commit feat/fix → merge na main do api/
   ↓ CI api: gates → python-semantic-release versiona a API (X.Y.Z)
   ↓        → openapi.json → openapi-typescript → @org/contract@X.Y.Z (publish)
Renovate (no web/) detecta @org/contract@X.Y.Z
   ↓ minor/patch: PR → CI verde → automerge ✅
   ↓ major:       PR → revisão humana dos types ✋
web/ sempre na versão certa do contrato
```

**Dev local (iteração rápida, antes de publicar):** gere contra o backend rodando —
`pnpm gen:contract` (`openapi-typescript http://localhost:8000/openapi.json …`) — ou
use `pnpm link @org/contract` apontando para o `contract/` do `api/` clonado ao lado.
A fonte de verdade versionada continua sendo o pacote publicado.

---

## 5. Convenções

- **Idioma — domínio em pt-BR, técnica em inglês:** o vocabulário de **negócio**
  (nomes de módulos, entidades, conceitos e **toda string de UI**) é **português
  brasileiro** e não se traduz nem genericiza — é a *ubiquitous language*, preservada
  inclusive no código (nomes de classes, tabelas, rotas de domínio). Já os **termos
  técnicos padrão de mercado** (padrões de código, identificadores de framework,
  `Repository`/`Service`/`handler`, `feat`/`fix`) seguem a convenção da linguagem —
  em geral **inglês**. Docs e comentários: pt-BR.
- **pnpm, nunca npm** no `web/`. Imposto por `preinstall: "npx -y only-allow pnpm"`.
- **Type checking estrito** dos dois lados: mypy `strict` e tsc `strict`.
- **Versões pinadas** no lock + Dockerfile de cada repo (reprodutibilidade FE/BE/CI).
- **Conventional Commits** em ambos: validados por `cz check` (api) / commitlint (web).
- **Release dirigido por commit:** `feat`/`fix`/`feat!` determinam o bump — nada manual.
- **Changelog gerado, nunca escrito à mão:** semantic-release cuida do `CHANGELOG.md`.
- **Contrato gerado, nunca escrito à mão:** FastAPI → OpenAPI → types TS (§4).
- **Quality gates por repo:** cada repo tem seu `.pre-commit-config.yaml`/husky.

---

## 6. Passo a passo de scaffolding (copiar e rodar)

```bash
# 0. Pasta de trabalho comum (não é repo)
mkdir <projeto> && cd <projeto>

# ───────────────── repo api/ (backend) ─────────────────
mkdir api && cd api && git init && git branch -M main
uv init --package --name <projeto>-api
uv add "fastapi" "sqlalchemy[asyncio]" "alembic" "asyncpg" "uvicorn[standard]"
uv add --dev \
  "ruff==0.15.14" "mypy==2.1.0" "bandit==1.9.4" "pip-audit==2.10.0" \
  "sqlfluff==4.2.1" "pytest==9.0.3" "pre-commit==4.6.0" "commitizen==4.16.2" \
  "python-semantic-release" "semgrep" "pysonar"
uv run pre-commit install --install-hooks
cd ..

# ───────────────── repo web/ (frontend) ─────────────────
pnpm create next-app@latest web   # ou o scaffolding do seu framework
cd web && git init && git branch -M main
pnpm add -D @biomejs/biome typescript vitest jsdom \
  @testing-library/react @testing-library/jest-dom @vitejs/plugin-react \
  semantic-release @semantic-release/changelog @semantic-release/git \
  husky lint-staged @commitlint/cli @commitlint/config-conventional \
  openapi-typescript
pnpm exec husky init
cd ..

# ───────────────── workspace + orquestração ─────────────────
#   crie <projeto>.code-workspace, docker-compose.yml e .env (ver §2 e §7)
code <projeto>.code-workspace
```

> **Dica de versões:** para pegar a última estável, troque `pkg==X` por `pkg` e deixe
> o resolver pinar; depois trave o resultado no lock.

---

## 7. Templates de configuração

### `api/pyproject.toml` (backend)
```toml
[project]
name = "<projeto>-api"
version = "0.1.0"          # gerenciado pelo python-semantic-release
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
package = true

[dependency-groups]
dev = [
  "ruff==0.15.14", "mypy==2.1.0", "bandit==1.9.4", "pip-audit==2.10.0",
  "sqlfluff==4.2.1", "pytest==9.0.3", "pre-commit==4.6.0",
  "commitizen==4.16.2", "python-semantic-release", "semgrep", "pysonar",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "S"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.sqlfluff.core]
dialect = "postgres"
templater = "raw"

[tool.bandit]
exclude_dirs = ["tests"]

# Conventional Commits: só escrever/validar mensagem (NÃO usar cz bump).
[tool.commitizen]
name = "cz_conventional_commits"

# Release + changelog automáticos — roda no CI (ver §9).
[tool.semantic_release]
branch = "main"
version_toml = ["pyproject.toml:project.version"]   # PSR escreve a versão aqui
allow_zero_version = true                            # mantém 0.y.z até a 1ª estável
commit_parser = "conventional"
build_command = "uv build"                           # opcional: artefato no release

[tool.semantic_release.changelog]
mode = "update"                                      # mantém CHANGELOG.md acumulado
```

### `web/package.json` (frontend)
```json
{
  "name": "<projeto>-web",
  "version": "0.1.0",
  "private": true,
  "packageManager": "pnpm@11.5.2",
  "engines": { "node": ">=22", "pnpm": ">=11" },
  "scripts": {
    "preinstall": "npx -y only-allow pnpm",
    "format": "biome format --write .",
    "lint": "biome check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "gen:contract": "openapi-typescript http://localhost:8000/openapi.json -o src/lib/api/schema.d.ts",
    "prepare": "husky"
  },
  "dependencies": {
    "@org/contract": "^1.0.0"
  }
}
```
> O `@org/contract` é a fonte versionada do contrato (Renovate mantém em dia). O
> script `gen:contract` é só um **atalho de dev** contra o backend local — não
> substitui a dependência publicada.

### `web/.npmrc` (aponta o scope para o GitHub Packages)
```ini
@org:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```
> Em CI, exporte `NODE_AUTH_TOKEN` (um `GITHUB_TOKEN` com `packages: read`). O Renovate
> precisa de credencial equivalente via `hostRules` (token de leitura do registry).

### `web/renovate.json`
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchPackageNames": ["@org/contract"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true,
      "automergeType": "branch"
    },
    {
      "matchPackageNames": ["@org/contract"],
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "addLabels": ["breaking-contract"]
    }
  ]
}
```
> Automerge só ocorre com os checks do `web/` verdes — exige *branch protection* na
> `main` com o job `quality` (e o que mais você marcar como obrigatório).

### `api/contract/package.json` (o pacote publicado pelo backend)
```json
{
  "name": "@org/contract",
  "version": "0.0.0",
  "description": "Tipos TS gerados do OpenAPI do <projeto>-api",
  "types": "index.d.ts",
  "files": ["index.d.ts"],
  "publishConfig": { "registry": "https://npm.pkg.github.com" }
}
```
> A `version` é sobrescrita no CI com a versão da release da API (ver §8) antes do
> `npm publish`. Geração: `openapi-typescript openapi.json -o index.d.ts`.

### `web/.releaserc.json` (semantic-release — pacote privado, sem publish npm)
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    "@semantic-release/github",
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
    }]
  ]
}
```
> Sem `@semantic-release/npm`: não publica no registry, mas ainda calcula a versão,
> grava o `CHANGELOG.md`, comita `package.json` e cria a tag + GitHub Release.

### `web/commitlint.config.js`
```js
export default { extends: ["@commitlint/config-conventional"] };
```

### `web/.husky/commit-msg` e `web/.husky/pre-commit`
```bash
# .husky/commit-msg
pnpm exec commitlint --edit "$1"
# .husky/pre-commit
pnpm exec lint-staged
```

### `web/biome.json`
```json
{
  "$schema": "https://biomejs.dev/schemas/2.4.16/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "ignoreUnknown": true },
  "formatter": { "enabled": true, "indentStyle": "space", "indentWidth": 2, "lineWidth": 100 },
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "javascript": { "formatter": { "quoteStyle": "double" } },
  "assist": { "actions": { "source": { "organizeImports": "on" } } }
}
```

### `web/tsconfig.json` (base strict)
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "jsx": "preserve"
  },
  "exclude": ["node_modules", "dist", ".next"]
}
```

### `api/.pre-commit-config.yaml`
```yaml
minimum_pre_commit_version: "4.0.0"
default_install_hook_types: [pre-commit, commit-msg, pre-push]
default_stages: [pre-commit]
exclude: ^(uv\.lock)$
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=1024"]
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff (lint + autofix)
        entry: uv run ruff check --fix --force-exclude
        language: system
        types_or: [python, pyi]
      - id: ruff-format
        name: ruff (format)
        entry: uv run ruff format --force-exclude
        language: system
        types_or: [python, pyi]
      - id: mypy
        name: mypy (strict)
        entry: uv run mypy --config-file pyproject.toml src
        language: system
        types_or: [python, pyi]
        pass_filenames: false
      - id: bandit
        name: bandit (SAST Python)
        entry: uv run bandit -c pyproject.toml -q
        language: system
        types: [python]
      - id: sqlfluff
        name: sqlfluff (lint SQL)
        entry: uv run sqlfluff lint
        language: system
        types: [sql]
      - id: semgrep
        name: semgrep (SAST)
        entry: uv run semgrep --error --skip-unknown-extensions --config p/security-audit --config p/secrets
        language: system
        pass_filenames: false
        stages: [pre-push]
      - id: commitizen-check
        name: commitizen (Conventional Commits)
        entry: uv run cz check --commit-msg-file
        language: system
        stages: [commit-msg]
```

### `.gitignore` (compartilhe o relevante em cada repo)
```gitignore
# Python (api/)
__pycache__/
*.py[cod]
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/
# Node / pnpm (web/)
node_modules/
.pnpm-store/
dist/
.next/
coverage/
# Env / segredos (ambos)
.env
.env.*
!.env.example
# SonarQube
.scannerwork/
```

### Docker

**Todas as imagens são fixadas** (nunca `:latest`). Centralize os pins aqui e, para
reprodutibilidade total, prenda também o **digest** `@sha256:…` — obtenha com
`docker buildx imagetools inspect <imagem:tag>`.

| Imagem | Pin base | Usada em |
|---|---|---|
| `python` | `3.12-slim-bookworm` | `api/Dockerfile` (builder + runtime) |
| `ghcr.io/astral-sh/uv` | `0.11.21` | `api/Dockerfile` (copia o binário `uv`) |
| `node` | `22-alpine3.20` | `web/Dockerfile` (base) |
| `postgres` | `18.4` | `docker-compose.yml` (db) |

> As tags acima são a **linha de base**; confirme a última patch estável no scaffold e
> prenda por digest. Mantenha o pin do `uv` igual ao usado fora do Docker (§3).

#### `api/Dockerfile` (backend — polyrepo, contexto = repo `api/`)
```dockerfile
# ── Stage: builder ──────────────────────────────────────────────────────────────
# Pin por digest p/ reprodutibilidade: FROM python:3.12-slim-bookworm@sha256:<digest>
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# Cache de camada: lock/manifests mudam menos que o código
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-install-project
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen

# ── Stage: runtime ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src ./src           # mesmo caminho do install editable
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
ENV PATH="/app/.venv/bin:$PATH"
# Non-root com UID/GID explícito (skill: nunca o user default)
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1
CMD ["uvicorn", "<pkg>_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `web/Dockerfile` (frontend — polyrepo, contexto = repo `web/`)
Requer `output: "standalone"` no `next.config`. O `@org/contract` vem do GitHub
Packages → o token entra como **secret de build** (nunca `ENV`/camada).
```dockerfile
# ── Stage: base ─────────────────────────────────────────────────────────────────
# Pin por digest: FROM node:22-alpine3.20@sha256:<digest>
FROM node:22-alpine3.20 AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# ── Stage: deps ─────────────────────────────────────────────────────────────────
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
# Token do registry como secret de build:
#   docker build --secret id=npm_token,env=NODE_AUTH_TOKEN ...
RUN --mount=type=secret,id=npm_token \
    NODE_AUTH_TOKEN="$(cat /run/secrets/npm_token)" \
    pnpm install --frozen-lockfile

# ── Stage: builder ──────────────────────────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# ── Stage: runner ───────────────────────────────────────────────────────────────
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs \
    && chown -R nextjs:nodejs /app
USER nextjs
# Next standalone usa HOSTNAME como bind address; sem isto escuta só na IP interna.
ENV HOSTNAME="0.0.0.0"
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget -qO- http://0.0.0.0:3000/ || exit 1
CMD ["node", "server.js"]
```

#### `docker-compose.yml` (dev — na pasta-pai do workspace)
```yaml
services:
  db:
    image: postgres:18.4
    environment:
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
      POSTGRES_DB: "${POSTGRES_DB:-app}"
      POSTGRES_USER: "${POSTGRES_USER:-app}"
    volumes:
      - pg_data:/var/lib/postgresql      # PG18+ usa /var/lib/postgresql/<v>/main
    networks: [backend]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app}"]
      interval: 5s
      timeout: 3s
      retries: 10
    restart: unless-stopped

  migrate:                               # one-shot: aplica as migrations e sai
    build: { context: ./api }
    command: sh -c "alembic upgrade head"
    environment:
      DATABASE_URL: "${DATABASE_URL}"
    networks: [backend]
    depends_on:
      db: { condition: service_healthy }

  api:
    build: { context: ./api }
    environment:
      DATABASE_URL: "${DATABASE_URL}"
      SECRET_KEY: "${SECRET_KEY}"
    ports: ["8000:8000"]
    networks: [backend, frontend]
    depends_on:
      migrate: { condition: service_completed_successfully }
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')\""]
      interval: 30s
      timeout: 5s
      start_period: 15s
      retries: 3
    restart: unless-stopped

  web:
    build:
      context: ./web
      secrets: [npm_token]               # token p/ baixar @org/contract no build
    environment:
      API_URL: "http://api:8000"         # service discovery pela rede Docker
    ports: ["3000:3000"]
    networks: [frontend]
    depends_on:
      api: { condition: service_healthy }
    restart: unless-stopped

networks:
  backend:  { driver: bridge, internal: true }   # db nunca exposto fora do Docker
  frontend: { driver: bridge }

volumes:
  pg_data:

secrets:
  npm_token:
    environment: NODE_AUTH_TOKEN
```

> **Hardening de produção (override):** num `docker-compose.prod.yml` adicione
> `security_opt: [no-new-privileges:true]`, `read_only: true` (+ `tmpfs`),
> `cap_drop: [ALL]` e `deploy.resources.limits` (cpu/memória). Para multi-container
> em produção real, prefira um orquestrador (Kubernetes/Swarm/ECS) ao compose.

#### `api/.dockerignore`
```gitignore
.venv/
__pycache__/
*.py[cod]
.mypy_cache/
.ruff_cache/
.pytest_cache/
*.egg-info/
.coverage
coverage.xml
tests/
contract/node_modules/
.git/
.github/
.env
.env.*
!.env.example
*.log
```

#### `web/.dockerignore`
```gitignore
node_modules/
.pnpm-store/
.next/
coverage/
.git/
.github/
.env
.env.*
!.env.example
*.log
*.tsbuildinfo
README.md
```

---

## 8. CI (GitHub Actions) — um pipeline por repo

Cada repo tem seus próprios workflows; o release roda **só na `main`**, após os gates.

### `api/` (backend)
| Job | O que roda | Quando |
|---|---|---|
| `quality` | ruff → mypy (strict) → bandit → pytest (`--cov`) | PR + push |
| `sast` | semgrep (security-audit + secrets) | PR + push |
| `sonar` | SonarQube scan (pysonar, `SONAR_TOKEN`) | PR + push |
| `release` | **python-semantic-release** (version + CHANGELOG + tag + GitHub Release) | push na `main` |
| `publish-contract` | gera types + publica `@org/contract` na versão da release | após `release`, se houve release |

```yaml
# api/.github/workflows/release.yml
name: release
on:
  push:
    branches: [main]
permissions:
  contents: write          # push de commit/tag + criar release
  id-token: write          # trusted publisher (se for publicar)
  packages: write          # publicar @org/contract no GitHub Packages
jobs:
  release:
    runs-on: ubuntu-latest
    concurrency: release-${{ github.ref }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # histórico completo p/ analisar commits
      - id: release
        uses: python-semantic-release/python-semantic-release@v10.5.3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      # Publica o contrato SÓ quando houve release (nova versão da API).
      - if: steps.release.outputs.released == 'true'
        uses: astral-sh/setup-uv@v5
      - if: steps.release.outputs.released == 'true'
        uses: actions/setup-node@v4
        with: { node-version: 22, registry-url: https://npm.pkg.github.com }
      - if: steps.release.outputs.released == 'true'
        run: |
          uv run python -m <pkg>_api.openapi_export > contract/openapi.json
          npx -y openapi-typescript contract/openapi.json -o contract/index.d.ts
          npm --prefix contract version "${{ steps.release.outputs.version }}" --no-git-tag-version
          npm --prefix contract publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### `web/` (frontend)
| Job | O que roda | Quando |
|---|---|---|
| `quality` | Biome → tsc (`--noEmit`) → Vitest | PR + push |
| `sast` | semgrep | PR + push |
| `sonar` | SonarQube scan | PR + push |
| `release` | **semantic-release** (version + CHANGELOG + tag + GitHub Release) | push na `main` |

```yaml
# web/.github/workflows/release.yml
name: release
on:
  push:
    branches: [main]
permissions:
  contents: write
  issues: write
  pull-requests: write
jobs:
  release:
    runs-on: ubuntu-latest
    concurrency: release-${{ github.ref }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec semantic-release
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
```

> **Sincronização do contrato:** habilite o **Renovate** (GitHub App) no `web/` com o
> `renovate.json` da §7. Ele abre os PRs de `@org/contract` automaticamente —
> automerge em minor/patch (CI verde) e PR revisável em major. Proteja a `main` do
> `web/` exigindo o job `quality`, senão o automerge entra sem gate.

**Rulesets semgrep recomendados:** `p/python`, `p/javascript`, `p/typescript`,
`p/security-audit`, `p/secrets`, `p/owasp-top-ten`.

---

## 9. Versionamento e changelog automáticos (SemVer)

**Modelo: cada repositório se versiona sozinho, 100% automático no CI.** Não há bump
manual, nem PR de release, nem comando local. Você só escreve Conventional Commits;
ao mergear na `main`, o CI calcula a versão, gera o changelog, cria a tag e a release.

**Semântica** (derivada das mensagens de commit, igual nos dois repos):

| Bump | Dispara com | Significado |
|---|---|---|
| **MAJOR** (`x`) | `feat!:` / `BREAKING CHANGE:` | quebra de contrato/comportamento |
| **MINOR** (`y`) | `feat:` | funcionalidade compatível |
| **PATCH** (`z`) | `fix:` (e `perf:`) | correção compatível |

- **Pré-1.0:** `allow_zero_version = true` (backend) — enquanto em `0.y.z`, breaking
  changes sobem o **minor**. O semantic-release (frontend) tem comportamento análogo
  partindo de `0.1.0`. Promova para `1.0.0` na primeira release estável.
- **Tags:** cada repo usa `vX.Y.Z` no seu próprio espaço — sem prefixo, porque não há
  ambiguidade entre repos (era o que forçava `api-v`/`web-v` no monorepo).
- **Changelog:** `CHANGELOG.md` na raiz de cada repo, escrito e commitado pela própria
  ferramenta — nunca à mão.

**O que acontece a cada push na `main` (totalmente automático):**

```
push na main
   ↓  CI rota os gates (quality + sast + sonar)
   ↓  job de release
analisa commits desde a última tag  →  decide o bump (ou nenhum)
   ↓
escreve a versão no manifesto  +  gera/atualiza CHANGELOG.md
   ↓
commit "chore(release): X.Y.Z [skip ci]"  +  tag vX.Y.Z  +  GitHub Release
```

- **Backend:** `python-semantic-release` lê `[tool.semantic_release]` do `pyproject.toml`,
  escreve a versão via `version_toml` e mantém o `CHANGELOG.md`.
- **Frontend:** `semantic-release` lê `.releaserc.json`; sem `@semantic-release/npm`
  não publica no registry, mas grava versão, changelog, tag e GitHub Release.
- **Sem commits relevantes** (`feat`/`fix`) desde a última tag → nenhuma release é
  criada. Commits `chore`/`docs`/`test`/`refactor` não disparam versão por padrão.
- **Escrever bem o commit é o único trabalho manual:** use `cz commit` (api) para ser
  guiado; o commitlint (web) rejeita mensagens fora do padrão no `commit-msg`.

> **Por que isto é mais automático que o commitizen:** com `cz bump` você rodava o
> comando à mão, num repo certo, e cuidava do push da tag. Aqui o gatilho é o próprio
> merge na `main` — zero intervenção, e como cada app é um repo, o histórico nunca se
> mistura (a limitação de path-filtering do monorepo deixa de existir).

---

*Fim do playbook. Mantenha as versões e este documento sincronizados quando atualizar o padrão.*
