import asyncio

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from mcp_fastapi.server import (
    DIRETORIO_CORPUS,
    buscar_documentos,
    listar_documentos,
    mcp,
    obter_documento,
)

_CASOS_SC001 = [
    ("background tasks", {"08 Background Tasks - BackgroundTasks"}),
    ("websockets", {"10 WebSockets", "21 WebSockets"}),
    ("middleware", {"14 Middleware"}),
    ("class", {"01 FastAPI class", "07 APIRouter class"}),
]


@pytest.mark.parametrize("termo, ids_aceitos", _CASOS_SC001)
def test_busca_encontra_documento_esperado_no_top_3(termo: str, ids_aceitos: set[str]) -> None:
    resultados = buscar_documentos(consulta=termo)

    ids_top3 = {r.id_documento for r in resultados[:3]}
    assert ids_top3 & ids_aceitos


def test_busca_sem_match_retorna_lista_vazia() -> None:
    assert buscar_documentos(consulta="termo-que-nao-existe-em-nenhuma-referencia") == []


def test_busca_consulta_vazia_levanta_erro_de_validacao() -> None:
    with pytest.raises(ValueError):
        buscar_documentos(consulta="")


def test_obter_documento_retorna_conteudo_identico_ao_arquivo_fonte() -> None:
    id_documento = "08 Background Tasks - BackgroundTasks"
    caminho = DIRETORIO_CORPUS / f"{id_documento}.md"

    resultado = obter_documento(id_documento=id_documento)

    assert resultado.encontrado is True
    assert resultado.conteudo == caminho.read_text(encoding="utf-8")


def test_obter_documento_inexistente_retorna_nao_encontrado_sem_excecao() -> None:
    resultado = obter_documento(id_documento="nao-existe")

    assert resultado.encontrado is False
    assert resultado.conteudo is None


def test_obter_documento_id_vazio_levanta_erro_de_validacao() -> None:
    with pytest.raises(ValueError):
        obter_documento(id_documento="")


def test_listar_documentos_tem_um_item_por_arquivo_do_corpus() -> None:
    # rglob (recursivo) para bater com carregar_documentos — FR-010 cobre
    # "todo arquivo sob docs/references/", não só o nível direto
    arquivos = list(DIRETORIO_CORPUS.rglob("*.md"))

    resultado = listar_documentos()

    assert len(resultado) == len(arquivos)


def test_listar_documentos_item_tem_id_e_titulo_corretos() -> None:
    resultado = listar_documentos()

    alvo = next(i for i in resultado if i.id_documento == "08 Background Tasks - BackgroundTasks")
    assert alvo.titulo == "Background Tasks - BackgroundTasks"


def test_busca_invalida_via_dispatch_real_do_mcp_levanta_toolerror() -> None:
    # tests acima chamam a tool direto em Python (bypassa o dispatch do
    # protocolo); aqui confirmamos o que um cliente MCP real recebe:
    # Tool.run() do SDK envolve toda exceção em ToolError
    async def chamar() -> None:
        await mcp.call_tool("buscar_documentos", {"consulta": ""})

    with pytest.raises(ToolError):
        asyncio.run(chamar())
