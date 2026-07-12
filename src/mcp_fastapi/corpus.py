import re
from dataclasses import dataclass, field
from pathlib import Path

_PREFIXO_NUMERICO = re.compile(r"^\d+\s+")
_TITULO_H1 = re.compile(r"^# (.+) - FastAPI$")


@dataclass(frozen=True)
class DocumentoReferencia:
    id: str
    # id já garante unicidade no corpus; demais campos ficam fora de eq/hash
    # para não comparar/hashear o conteúdo inteiro do documento
    titulo: str = field(compare=False)
    conteudo: str = field(compare=False)
    caminho_origem: Path = field(compare=False)


def _extrair_titulo(conteudo: str, titulo_fallback: str) -> str:
    primeira_linha = conteudo.splitlines()[0] if conteudo else ""
    m = _TITULO_H1.match(primeira_linha)
    return m.group(1) if m else titulo_fallback


def carregar_documentos(diretorio: Path) -> list[DocumentoReferencia]:
    documentos: list[DocumentoReferencia] = []
    ids_vistos: dict[str, Path] = {}

    for caminho in sorted(diretorio.rglob("*.md")):
        id_documento = caminho.stem
        if id_documento in ids_vistos:
            raise ValueError(
                f"id de documento duplicado: '{id_documento}' "
                f"({ids_vistos[id_documento]} e {caminho})"
            )
        ids_vistos[id_documento] = caminho

        conteudo = caminho.read_text(encoding="utf-8")
        titulo_fallback = _PREFIXO_NUMERICO.sub("", id_documento)

        documentos.append(
            DocumentoReferencia(
                id=id_documento,
                titulo=_extrair_titulo(conteudo, titulo_fallback),
                conteudo=conteudo,
                caminho_origem=caminho,
            )
        )

    if not documentos:
        raise ValueError(f"nenhum documento .md encontrado em {diretorio}")

    return documentos
