import re
import unicodedata
from collections.abc import Sequence
from functools import lru_cache

from pydantic import BaseModel

from .corpus import DocumentoReferencia

_TOKEN_RE = re.compile(r"\w+")

# marcação HTML residual do scrape original (ex.: `<code class="doc-symbol
# doc-symbol-heading doc-symbol-class"></code>`, `<span class="doc
# doc-object-name doc-class-name">Nome</span>`) — sem isso, fragmentos como
# "doc"/"class"/"symbol" aparecem em quase todo documento e distorcem o
# ranqueamento; o `<span>` preserva o texto interno (ex.: "Nome"), só remove
# a marcação
_ARTEFATO_CODE_VAZIO = re.compile(r'<code class=\\?"doc-symbol[^"]*\\?"></code>')
_ARTEFATO_SPAN_DOC = re.compile(r'<span class=\\?"doc[^"]*\\?">(.*?)</span>')

PESO_TITULO = 3.0
PESO_CORPO = 1.0
LIMITE_RESULTADOS_PADRAO = 10
TAMANHO_TRECHO = 160


class ConsultaBusca(BaseModel):
    consulta: str
    limite_resultados: int = LIMITE_RESULTADOS_PADRAO


class ResultadoBusca(BaseModel):
    id_documento: str
    titulo: str
    trecho: str
    pontuacao: float


def _limpar_marcacao_residual(texto: str) -> str:
    texto = _ARTEFATO_CODE_VAZIO.sub("", texto)
    return _ARTEFATO_SPAN_DOC.sub(r"\1", texto)


@lru_cache(maxsize=256)
def _tokenizar(texto: str) -> tuple[str, ...]:
    texto_limpo = unicodedata.normalize("NFC", _limpar_marcacao_residual(texto))
    return tuple(_TOKEN_RE.findall(texto_limpo.lower()))


def _pontuar(documento: DocumentoReferencia, termos: tuple[str, ...]) -> float:
    titulo_tokens = _tokenizar(documento.titulo)
    corpo_tokens = _tokenizar(documento.conteudo)
    pontos_titulo = sum(titulo_tokens.count(termo) for termo in termos)
    pontos_corpo = sum(corpo_tokens.count(termo) for termo in termos)
    return PESO_TITULO * pontos_titulo + PESO_CORPO * pontos_corpo


def _extrair_trecho(documento: DocumentoReferencia, termos: tuple[str, ...]) -> str:
    conteudo_limpo = _limpar_marcacao_residual(documento.conteudo)
    texto = f"{documento.titulo}\n\n{conteudo_limpo}"
    texto_lower = texto.lower()

    posicoes = [texto_lower.find(termo) for termo in termos if termo in texto_lower]
    posicao = min(posicoes) if posicoes else 0

    inicio = max(0, posicao - TAMANHO_TRECHO // 2)
    fim = min(len(texto), inicio + TAMANHO_TRECHO)
    return texto[inicio:fim].strip()


def ranquear(
    documentos: Sequence[DocumentoReferencia],
    consulta_busca: ConsultaBusca,
) -> list[ResultadoBusca]:
    if not consulta_busca.consulta.strip():
        raise ValueError("consulta não pode ser vazia ou conter apenas espaços")

    termos = _tokenizar(consulta_busca.consulta)
    candidatos = [(_pontuar(documento, termos), documento) for documento in documentos]
    candidatos = [(pontuacao, documento) for pontuacao, documento in candidatos if pontuacao > 0]
    # DocumentoReferencia não define ordenação — a key= explícita é obrigatória
    # (sem ela, um empate de pontuação levaria a comparar os documentos e
    # estourar TypeError)
    candidatos.sort(key=lambda item: item[0], reverse=True)

    return [
        ResultadoBusca(
            id_documento=documento.id,
            titulo=documento.titulo,
            trecho=_extrair_trecho(documento, termos),
            pontuacao=pontuacao,
        )
        for pontuacao, documento in candidatos[: consulta_busca.limite_resultados]
    ]
