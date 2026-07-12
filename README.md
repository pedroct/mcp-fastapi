# mcp-fastapi

Servidor [MCP](https://modelcontextprotocol.io/) que expõe os documentos de
referência do FastAPI (`docs/references/`, 39 tópicos) como três tools, para
que um agente/LLM consulte orientação real sobre FastAPI durante o
desenvolvimento — em vez de depender só de conhecimento pré-treinado. Não é
um buscador genérico de documentação: cada tool existe para responder "isso
ajuda o agente a escrever FastAPI correto agora, no meio de uma tarefa de
desenvolvimento?".

## Tools

Nomes e parâmetros em português brasileiro (vocabulário de domínio do
projeto). Schemas completos e cenários de erro em
[`specs/001-search-fastapi-docs/contracts/mcp-tools.md`](specs/001-search-fastapi-docs/contracts/mcp-tools.md).

### `buscar_documentos`

Busca por tópico/palavra-chave. Recebe `consulta` (string, não pode ser
vazia/só espaço) e devolve uma lista ranqueada (máx. 10) com
`id_documento`, `titulo`, `trecho` (excerto que justifica o match) e
`pontuacao`.

### `obter_documento`

Recebe `id_documento` (ex.: o retornado por uma busca) e devolve o conteúdo
markdown completo e sem modificação do documento, ou uma resposta
`encontrado: false` clara se o id não existir.

### `listar_documentos`

Sem parâmetros. Lista todos os documentos do corpus (`id_documento` +
`titulo`), para descoberta de tópicos sem precisar adivinhar um termo de
busca.

## Instalação

Pré-requisitos: Python 3.12+ e [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Rodar o servidor

```bash
uv run python -m mcp_fastapi
```

O servidor fala o protocolo MCP via **stdio** (sem HTTP nesta versão). Para
plugar num cliente MCP (ex. Claude Desktop/Claude Code), aponte para o
comando acima com o diretório do projeto como `cwd`, por exemplo:

```json
{
  "mcpServers": {
    "mcp-fastapi": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_fastapi"],
      "cwd": "/caminho/para/mcp-fastapi"
    }
  }
}
```

Para validar o fluxo completo manualmente (os 3 tools, cenários de sucesso
e erro), veja
[`specs/001-search-fastapi-docs/quickstart.md`](specs/001-search-fastapi-docs/quickstart.md).

## Arquitetura

Pacote único em `src/mcp_fastapi/`, sem banco de dados — o corpus inteiro é
carregado em memória na inicialização a partir de `docs/references/*.md`.

- `corpus.py` — carrega e valida os documentos (`DocumentoReferencia`), um
  por arquivo; id único por nome de arquivo, título extraído do H1 do
  conteúdo.
- `search.py` — tokenização e ranqueamento por frequência de termo (peso
  maior no título), stdlib apenas — sem dependência externa de busca.
- `server.py` — instancia o servidor MCP ([SDK oficial](https://github.com/modelcontextprotocol/python-sdk))
  e registra as três tools.

Detalhes de design e as decisões por trás deles estão em
[`specs/001-search-fastapi-docs/`](specs/001-search-fastapi-docs/) (`plan.md`,
`research.md`, `data-model.md`) e na
[constituição do projeto](.specify/memory/constitution.md).

## Desenvolvimento

```bash
uv run pytest                  # suíte de testes (unit + contract)
uv run pytest --cov            # com relatório de cobertura no terminal
uv run ruff check .            # lint
uv run ruff format --check .   # formatação
uv run mypy                    # type-check estrito
uv run bandit -c pyproject.toml -r src   # SAST
uv run pip-audit               # CVEs nas dependências
```

`pre-commit install` roda essas checagens automaticamente antes de cada
commit (config em [`.pre-commit-config.yaml`](.pre-commit-config.yaml)).

CI (`.github/workflows/ci.yml`) roda as mesmas checagens em PR/push; release
(`.github/workflows/release.yml`) gera versão/changelog/tag automaticamente
via [python-semantic-release](https://python-semantic-release.readthedocs.io/)
a partir de [Conventional Commits](https://www.conventionalcommits.org/) —
sem bump manual.

### Análise local no SonarQube

```bash
cp .env.example .env   # preencher SONAR_TOKEN
scripts/run-sonar-local.sh
```

Roda a suíte com cobertura e envia a análise para o SonarQube configurado em
[`sonar-project.properties`](sonar-project.properties) (só o token fica no
`.env`, gitignored).

## Convenções do projeto

- **Idioma**: domínio de negócio (specs, comentários, nomes de tool/campo)
  em português brasileiro; termos técnicos padrão de mercado (nomes de
  framework, padrões de código, tipos de commit) em inglês.
- **Contrato antes do código**: todo schema de tool deve refletir fielmente
  `docs/references/`; mudanças que quebram um contrato existente exigem bump
  de MAJOR (SemVer).
- **Test-first**: lógica de tool/resource não é implementada sem teste
  escrito e falhando antes.

Regras completas em [`.specify/memory/constitution.md`](.specify/memory/constitution.md).
