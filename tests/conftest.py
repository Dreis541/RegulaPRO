"""Fixtures compartilhadas para os testes do RegulaPRO."""

import os
import sys
import sqlite3
import pytest
from datetime import date, timedelta

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def banco_temp(tmp_path, monkeypatch):
    """
    Substitui o DB_PATH por um banco temporário para cada teste.
    Isolamento total: cada teste tem seu próprio banco SQLite.
    """
    db_temp = str(tmp_path / "test_processos.db")
    monkeypatch.setattr("config.DB_PATH", db_temp)
    monkeypatch.setattr("config.DATA_DIR", str(tmp_path))

    # Também corrige nos módulos já importados
    import functions.database as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", db_temp)
    monkeypatch.setattr(db_mod, "DATA_DIR", str(tmp_path))

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
