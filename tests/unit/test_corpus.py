from pathlib import Path

import pytest

from mcp_fastapi.corpus import DocumentoReferencia, _extrair_titulo, carregar_documentos

REFERENCES_DIR = Path(__file__).parents[2] / "docs" / "references"


def test_carrega_um_documento_por_arquivo() -> None:
    documentos = carregar_documentos(REFERENCES_DIR)

    # rglob (recursivo) para bater com carregar_documentos — FR-010 cobre
    # "todo arquivo sob docs/references/", não só o nível direto
    arquivos = list(REFERENCES_DIR.rglob("*.md"))
    assert len(documentos) == len(arquivos)


def test_documento_tem_id_titulo_e_conteudo_do_arquivo() -> None:
    documentos = carregar_documentos(REFERENCES_DIR)

    alvo = next(d for d in documentos if d.id == "08 Background Tasks - BackgroundTasks")
    caminho = REFERENCES_DIR / "08 Background Tasks - BackgroundTasks.md"

    assert isinstance(alvo, DocumentoReferencia)
    assert alvo.titulo == "Background Tasks - BackgroundTasks"
    assert alvo.conteudo == caminho.read_text(encoding="utf-8")
    assert alvo.caminho_origem == caminho


def test_ids_sao_unicos_no_corpus() -> None:
    documentos = carregar_documentos(REFERENCES_DIR)

    ids = [d.id for d in documentos]
    assert len(ids) == len(set(ids))


def test_id_colidindo_e_erro_de_configuracao(tmp_path: Path) -> None:
    (tmp_path / "sub1").mkdir()
    (tmp_path / "sub2").mkdir()
    (tmp_path / "sub1" / "a.md").write_text("conteudo a", encoding="utf-8")
    (tmp_path / "sub2" / "a.md").write_text("conteudo b", encoding="utf-8")

    with pytest.raises(ValueError):
        carregar_documentos(tmp_path)


def test_diretorio_sem_documentos_e_erro_de_configuracao(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        carregar_documentos(tmp_path)


def test_titulo_vem_do_h1_do_conteudo_nao_do_nome_do_arquivo() -> None:
    # "25 Testing Events lifespan and startup - shutdown.md" está mal
    # numerado/nomeado na fonte: o conteúdo real é sobre outro tópico. O
    # título servido deve refletir o conteúdo, não o nome do arquivo.
    documentos = carregar_documentos(REFERENCES_DIR)

    alvo = next(
        d for d in documentos if d.id == "25 Testing Events lifespan and startup - shutdown"
    )

    assert alvo.titulo == "Testing Dependencies with Overrides"


def test_titulo_cai_para_nome_do_arquivo_sem_h1_no_padrao_esperado(tmp_path: Path) -> None:
    (tmp_path / "01 Sem Titulo Padrao.md").write_text("sem cabeçalho h1 aqui", encoding="utf-8")

    documentos = carregar_documentos(tmp_path)

    assert documentos[0].titulo == "Sem Titulo Padrao"


def test_documentos_com_mesmo_id_sao_iguais_e_tem_mesmo_hash() -> None:
    a = DocumentoReferencia(id="x", titulo="a", conteudo="c1", caminho_origem=Path("a"))
    b = DocumentoReferencia(id="x", titulo="b", conteudo="c2", caminho_origem=Path("b"))

    assert a == b
    assert hash(a) == hash(b)


def test_extrair_titulo_usa_h1_do_padrao_titulo_fastapi() -> None:
    conteudo = "# Meu Título - FastAPI\n\nresto do conteúdo"

    assert _extrair_titulo(conteudo, titulo_fallback="ignorado") == "Meu Título"


def test_extrair_titulo_cai_para_fallback_sem_h1_no_padrao() -> None:
    assert _extrair_titulo("texto sem cabeçalho h1", titulo_fallback="fallback") == "fallback"


def test_extrair_titulo_cai_para_fallback_com_conteudo_vazio() -> None:
    assert _extrair_titulo("", titulo_fallback="fallback") == "fallback"
