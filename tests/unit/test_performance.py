import time

from mcp_fastapi.server import buscar_documentos, listar_documentos, obter_documento

LIMITE_SEGUNDOS = 1.0


def test_buscar_documentos_responde_em_menos_de_1s() -> None:
    inicio = time.perf_counter()
    buscar_documentos(consulta="background tasks")
    assert time.perf_counter() - inicio < LIMITE_SEGUNDOS


def test_obter_documento_responde_em_menos_de_1s() -> None:
    inicio = time.perf_counter()
    obter_documento(id_documento="08 Background Tasks - BackgroundTasks")
    assert time.perf_counter() - inicio < LIMITE_SEGUNDOS


def test_listar_documentos_responde_em_menos_de_1s() -> None:
    inicio = time.perf_counter()
    listar_documentos()
    assert time.perf_counter() - inicio < LIMITE_SEGUNDOS
