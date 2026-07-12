import unicodedata
from pathlib import Path

import pytest

from mcp_fastapi.corpus import DocumentoReferencia
from mcp_fastapi.search import (
    LIMITE_RESULTADOS_PADRAO,
    PESO_CORPO,
    PESO_TITULO,
    TAMANHO_TRECHO,
    ConsultaBusca,
    _extrair_trecho,
    _limpar_marcacao_residual,
    _pontuar,
    _tokenizar,
    ranquear,
)

_CAMINHO_FALSO = Path("doc.md")


def _documento(id_: str, titulo: str, conteudo: str) -> DocumentoReferencia:
    return DocumentoReferencia(
        id=id_, titulo=titulo, conteudo=conteudo, caminho_origem=_CAMINHO_FALSO
    )


def test_match_no_titulo_pontua_mais_que_match_no_corpo() -> None:
    doc_titulo = _documento("A", "websockets", "nada relevante aqui")
    doc_corpo = _documento("B", "outro assunto", "fala sobre websockets uma vez")

    resultados = ranquear([doc_titulo, doc_corpo], ConsultaBusca(consulta="websockets"))

    assert [r.id_documento for r in resultados] == ["A", "B"]
    assert resultados[0].pontuacao > resultados[1].pontuacao


def test_sem_match_retorna_lista_vazia() -> None:
    doc = _documento("A", "middleware", "conteúdo sobre middleware")

    resultados = ranquear(
        [doc], ConsultaBusca(consulta="termo-que-nao-existe-em-nenhuma-referencia")
    )

    assert resultados == []


def test_cap_em_limite_resultados() -> None:
    documentos = [_documento(str(i), "background tasks", "background tasks") for i in range(5)]

    resultados = ranquear(
        documentos, ConsultaBusca(consulta="background tasks", limite_resultados=3)
    )

    assert len(resultados) == 3


@pytest.mark.parametrize("consulta", ["", "   ", "\t\n"])
def test_consulta_vazia_ou_so_espaco_levanta_erro(consulta: str) -> None:
    doc = _documento("A", "middleware", "conteúdo sobre middleware")

    with pytest.raises(ValueError):
        ranquear([doc], ConsultaBusca(consulta=consulta))


def test_termo_curto_e_real_encontra_documento() -> None:
    # termos curtos (ex.: "API") não podem ser descartados por tamanho —
    # só a marcação HTML residual deve ser filtrada, não termos legítimos
    doc = _documento("A", "FastAPI class", "The title of the API.")

    resultados = ranquear([doc], ConsultaBusca(consulta="API"))

    assert [r.id_documento for r in resultados] == ["A"]


def test_limpar_marcacao_residual_remove_code_vazio_e_desembrulha_span() -> None:
    bruto = (
        'Antes <code class=\\"doc-symbol doc-symbol-heading doc-symbol-class\\"></code> '
        'depois <span class=\\"doc doc-object-name doc-class-name\\">APIKey</span> fim'
    )

    limpo = _limpar_marcacao_residual(bruto)

    assert "doc-symbol" not in limpo
    assert "doc-object-name" not in limpo
    assert "APIKey" in limpo


def test_marcacao_residual_nao_infla_pontuacao_de_termo_generico() -> None:
    # antes da limpeza, "doc-symbol-class" (fragmentado em "doc"/"symbol"/
    # "class") inflava a pontuação de "class" em qualquer documento com a
    # marcação residual, mesmo sem "class" no título
    ruido = 'x <code class=\\"doc-symbol doc-symbol-heading doc-symbol-class\\"></code> ' * 50
    doc_com_ruido = _documento("ruido", "OpenAPI models", ruido)
    doc_no_titulo = _documento("titulo", "FastAPI class", "conteúdo qualquer")

    resultados = ranquear([doc_com_ruido, doc_no_titulo], ConsultaBusca(consulta="class"))

    assert [r.id_documento for r in resultados] == ["titulo"]


def test_tokenizar_normaliza_nfd_para_nfc() -> None:
    palavra = "cafe" + chr(0x301)  # "e" + acento agudo combinante (NFD)
    nfd = unicodedata.normalize("NFD", palavra)
    nfc = unicodedata.normalize("NFC", palavra)
    assert nfc != nfd  # confirma que os dois têm codificação diferente

    assert _tokenizar(nfc) == _tokenizar(nfd)


def test_pontuar_soma_peso_titulo_e_peso_corpo() -> None:
    doc = _documento("A", "websockets tutorial", "websockets aparece aqui e websockets de novo")

    pontuacao = _pontuar(doc, _tokenizar("websockets"))

    # 1 match no título (peso 3) + 2 matches no corpo (peso 1 cada)
    assert pontuacao == pytest.approx(PESO_TITULO * 1 + PESO_CORPO * 2)


def test_pontuar_sem_match_e_zero() -> None:
    doc = _documento("A", "middleware", "conteúdo qualquer")

    assert _pontuar(doc, _tokenizar("termo-inexistente-aqui")) == pytest.approx(0.0)


def test_extrair_trecho_contem_o_termo_buscado_e_respeita_tamanho_maximo() -> None:
    doc = _documento("A", "titulo qualquer", "x" * 200 + " websockets " + "y" * 200)

    trecho = _extrair_trecho(doc, _tokenizar("websockets"))

    assert "websockets" in trecho.lower()
    assert len(trecho) <= TAMANHO_TRECHO


def test_extrair_trecho_sem_match_comeca_no_inicio_do_texto() -> None:
    doc = _documento("A", "titulo", "conteúdo qualquer sem o termo buscado")

    trecho = _extrair_trecho(doc, ("inexistente",))

    assert trecho.startswith("titulo")


def test_extrair_trecho_remove_marcacao_residual() -> None:
    doc = _documento(
        "A",
        "titulo",
        'x <code class=\\"doc-symbol doc-symbol-heading doc-symbol-class\\"></code> websockets',
    )

    trecho = _extrair_trecho(doc, _tokenizar("websockets"))

    assert "doc-symbol" not in trecho


def test_consulta_busca_usa_limite_padrao_quando_omitido() -> None:
    assert ConsultaBusca(consulta="x").limite_resultados == LIMITE_RESULTADOS_PADRAO


def test_ranquear_usa_limite_padrao_quando_nao_informado() -> None:
    documentos = [
        _documento(str(i), "background tasks", "background tasks")
        for i in range(LIMITE_RESULTADOS_PADRAO + 5)
    ]

    resultados = ranquear(documentos, ConsultaBusca(consulta="background tasks"))

    assert len(resultados) == LIMITE_RESULTADOS_PADRAO
