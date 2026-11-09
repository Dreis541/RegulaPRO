"""Fixtures compartilhadas para os testes do RegulaPRO."""

import os
import sys
import pytest
from datetime import date, timedelta

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def banco_temp(tmp_path, monkeypatch):
    """
    Cada teste roda num banco limpo.

    Por padrão usa um SQLite temporário. Para rodar os mesmos testes contra
    PostgreSQL, defina REGULAPRO_TEST_PG com a URL de um banco de TESTE
    (o schema "regulapro" é apagado antes de cada teste).
    """
    import functions.database as db_mod

    db_temp = str(tmp_path / "test_processos.db")
    monkeypatch.setattr("config.DB_PATH", db_temp)
    monkeypatch.setattr("config.DATA_DIR", str(tmp_path))
    monkeypatch.delenv("REGULAPRO_DATABASE_URL", raising=False)

    url_pg = os.environ.get("REGULAPRO_TEST_PG")
    monkeypatch.setattr("config.DATABASE_URL", url_pg)
    monkeypatch.setattr(db_mod, "_database_url", lambda: url_pg)
    db_mod._inicializados.clear()
    if url_pg:
        with db_mod.get_conexao() as conn:
            conn.execute(f"DROP SCHEMA IF EXISTS {db_mod.SCHEMA} CASCADE")
        db_mod._inicializados.clear()

    yield db_temp


@pytest.fixture
def processo_exemplo():
    """Dados de um processo válido para uso nos testes."""
    return {
        "empresa": "Farmacêutica Teste Ltda",
        "cnpj": "11.222.333/0001-81",
        "tipo": "Registro de Produto",
        "categoria": "Medicamento",
        "produto": "Produto Teste",
        "status": "Em Andamento",
        "prioridade": "Alta",
        "data_abertura": date.today(),
        "data_prazo": date.today() + timedelta(days=90),
        "responsavel": "Dr. Teste",
        "descricao": "Processo de teste",
        "observacoes": "",
        "percentual_conclusao": 0.0,
    }
