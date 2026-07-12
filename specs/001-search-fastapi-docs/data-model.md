# Modelo de Dados: Searchable FastAPI Reference Docs

**Feature**: `001-search-fastapi-docs` | **Data**: 2026-07-12

Sem banco de dados (ver `research.md` §4) — estas entidades são estruturas
em memória, montadas na inicialização do servidor a partir de
`docs/references/*.md`.

## ReferenceDocument (Documento de Referência)

Representa um guia de tópico do FastAPI carregado de `docs/references/`.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `id` | `str` | Nome do arquivo sem extensão (ex.: `08 Background Tasks - BackgroundTasks`) | Único dentro do corpus; validado na carga (FR-010) |
| `title` | `str` | Título legível do documento | Derivado do nome do arquivo |
| `content` | `str` | Conteúdo markdown completo, sem modificação | Não pode ser truncado (SC-004) |
| `source_path` | `Path` | Caminho do arquivo de origem em `docs/references/` | Somente leitura |

**Invariantes**:
- Todo arquivo em `docs/references/*.md` vira exatamente um `ReferenceDocument`
  (FR-010) — nenhum é descartado silenciosamente.
- `id` é único; uma colisão na carga é um erro de configuração do corpus,
  não um estado válido em runtime.

## SearchQuery (Consulta de Busca)

Entrada de uma chamada de busca.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `text` | `str` | Texto submetido pelo agente | Não pode ser vazio/só espaço (FR-006) |
| `max_results` | `int` | Teto de resultados retornados | Valor padrão fixo pequeno (ex.: 10); não configurável pelo agente em v1 (FR-008) |

## SearchResult (Resultado de Busca)

Um match ranqueado, ligando uma `SearchQuery` a um `ReferenceDocument`.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `document_id` | `str` | Referência ao `ReferenceDocument.id` | Deve existir no corpus |
| `title` | `str` | Cópia do título do documento | Evita round-trip extra pro agente |
| `excerpt` | `str` | Trecho do conteúdo que justifica o match | Curto o bastante para varredura rápida |
| `score` | `float` | Pontuação de relevância usada para ranquear | Maior = mais relevante; algoritmo é detalhe de implementação (`search.py`) |

**Invariantes**:
- Uma lista de `SearchResult` para uma query sem match é uma lista vazia,
  nunca um erro (FR-005).
- O tamanho da lista nunca excede `SearchQuery.max_results` (FR-008).
