# Modelo de Dados: Searchable FastAPI Reference Docs

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

Sem banco de dados (ver `research.md` §4) — estas entidades são estruturas
em memória, montadas na inicialização do servidor a partir de
`docs/references/*.md`. Nomes de campo em pt-BR (ver `research.md` §3).

## DocumentoReferencia

Representa um guia de tópico do FastAPI carregado de `docs/references/`.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `id` | `str` | Nome do arquivo sem extensão (ex.: `08 Background Tasks - BackgroundTasks`) | Único dentro do corpus; validado na carga (FR-010) |
| `titulo` | `str` | Título legível do documento | Derivado do nome do arquivo |
| `conteudo` | `str` | Conteúdo markdown completo, sem modificação | Não pode ser truncado (SC-004) |
| `caminho_origem` | `Path` | Caminho do arquivo de origem em `docs/references/` | Somente leitura |

**Invariantes**:
- Todo arquivo em `docs/references/*.md` vira exatamente um
  `DocumentoReferencia` (FR-010) — nenhum é descartado silenciosamente.
- `id` é único; uma colisão na carga é um erro de configuração do corpus,
  não um estado válido em runtime.

## ConsultaBusca

Entrada de uma chamada de busca.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `consulta` | `str` | Texto submetido pelo agente | Não pode ser vazio/só espaço (FR-006) |
| `limite_resultados` | `int` | Teto de resultados retornados | Valor padrão fixo pequeno (ex.: 10); não configurável pelo agente em v1 (FR-008) |

## ResultadoBusca

Um match ranqueado, ligando uma `ConsultaBusca` a um `DocumentoReferencia`.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `id_documento` | `str` | Referência ao `DocumentoReferencia.id` | Deve existir no corpus |
| `titulo` | `str` | Cópia do título do documento | Evita round-trip extra pro agente |
| `trecho` | `str` | Trecho do conteúdo que justifica o match | Curto o bastante para varredura rápida |
| `pontuacao` | `float` | Pontuação de relevância usada para ranquear | Maior = mais relevante; algoritmo é detalhe de implementação (`search.py`) |

**Invariantes**:
- Uma lista de `ResultadoBusca` para uma consulta sem match é uma lista
  vazia, nunca um erro (FR-005).
- O tamanho da lista nunca excede `ConsultaBusca.limite_resultados` (FR-008).
