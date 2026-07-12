from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .corpus import DocumentoReferencia, carregar_documentos
from .search import ConsultaBusca, ResultadoBusca, ranquear

DIRETORIO_CORPUS = Path(__file__).resolve().parents[2] / "docs" / "references"

mcp = FastMCP("mcp-fastapi")
_documentos: list[DocumentoReferencia] = carregar_documentos(DIRETORIO_CORPUS)
_documentos_por_id: dict[str, DocumentoReferencia] = {d.id: d for d in _documentos}


@mcp.tool()
def buscar_documentos(consulta: Annotated[str, Field(min_length=1)]) -> list[ResultadoBusca]:
    """Busca documentos de referência do FastAPI por tópico/palavra-chave."""
    return ranquear(_documentos, ConsultaBusca(consulta=consulta))


class DocumentoObtido(BaseModel):
    encontrado: bool
    id_documento: str
    titulo: str | None = None
    conteudo: str | None = None
    mensagem: str | None = None


@mcp.tool()
def obter_documento(id_documento: Annotated[str, Field(min_length=1)]) -> DocumentoObtido:
    """Obtém o conteúdo completo de um documento de referência pelo seu id."""
    if not id_documento.strip():
        raise ValueError("id_documento não pode ser vazio ou conter apenas espaços")

    documento = _documentos_por_id.get(id_documento)
    if documento is None:
        return DocumentoObtido(
            encontrado=False,
            id_documento=id_documento,
            mensagem=f"documento '{id_documento}' não encontrado",
        )

    return DocumentoObtido(
        encontrado=True,
        id_documento=documento.id,
        titulo=documento.titulo,
        conteudo=documento.conteudo,
    )


class ItemListagem(BaseModel):
    id_documento: str
    titulo: str


@mcp.tool()
def listar_documentos() -> list[ItemListagem]:
    """Lista todos os documentos de referência do FastAPI disponíveis."""
    return [ItemListagem(id_documento=d.id, titulo=d.titulo) for d in _documentos]
