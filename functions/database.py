"""Operações com banco de dados SQLite para o RegulaPRO."""

import sqlite3
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from config import DB_PATH, DATA_DIR


def garantir_data_dir() -> None:
    """Cria o diretório data/ se não existir."""
    os.makedirs(DATA_DIR, exist_ok=True)


@contextmanager
def get_conexao() -> Generator[sqlite3.Connection, None, None]:
    """Context manager que abre e fecha a conexão com o banco."""
    garantir_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_banco() -> None:
    """Cria as tabelas necessárias se não existirem."""
    with get_conexao() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_protocolo TEXT UNIQUE NOT NULL,
                empresa TEXT NOT NULL,
                cnpj TEXT,
                tipo TEXT NOT NULL,
                categoria TEXT,
                produto TEXT,
                status TEXT NOT NULL DEFAULT 'Em Andamento',
                prioridade TEXT DEFAULT 'Média',
                data_abertura TEXT NOT NULL,
                data_prazo TEXT,
                data_conclusao TEXT,
                responsavel TEXT,
                descricao TEXT,
                observacoes TEXT,
                percentual_conclusao REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                updated_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                data_evento TEXT NOT NULL,
                tipo_evento TEXT DEFAULT 'Atualização',
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (processo_id) REFERENCES processos(id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_processos_status ON processos(status);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_processos_empresa ON processos(empresa);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_eventos_processo ON eventos(processo_id);
        """)


def executar_query(
    sql: str, params: tuple = (), fetchall: bool = True
) -> List[Dict[str, Any]]:
    """Executa uma query SELECT e retorna lista de dicionários."""
    with get_conexao() as conn:
        cursor = conn.execute(sql, params)
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        row = cursor.fetchone()
        return [dict(row)] if row else []


def executar_insert(sql: str, params: tuple = ()) -> int:
    """Executa INSERT e retorna o lastrowid."""
    with get_conexao() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid


def executar_update(sql: str, params: tuple = ()) -> int:
    """Executa UPDATE/DELETE e retorna rowcount."""
    with get_conexao() as conn:
        cursor = conn.execute(sql, params)
        return cursor.rowcount
