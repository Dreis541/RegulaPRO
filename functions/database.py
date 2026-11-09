"""Banco de dados do RegulaPRO.

Funciona de dois jeitos, sem mudar o resto do código:

- **Supabase / PostgreSQL**: quando existe uma URL de conexão, em
  `.streamlit/secrets.toml` (seção `[database]`, chave `url`) ou na variável
  de ambiente `REGULAPRO_DATABASE_URL`. É o modo usado no Streamlit Cloud,
  onde os arquivos locais são apagados a cada reinício.
- **SQLite local** (`data/processos.db`): quando não há URL. Bom para rodar
  no computador e para os testes.

As consultas são escritas no estilo SQLite (`?` como parâmetro) e traduzidas
automaticamente para PostgreSQL.
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, Iterable, List, Optional
from zoneinfo import ZoneInfo

import config

SCHEMA = "regulapro"
FUSO = ZoneInfo("America/Sao_Paulo")

_pg_conexao = None
_pg_lock = threading.RLock()
_inicializados: set = set()


# ---------------------------------------------------------------------------
# Qual banco usar
# ---------------------------------------------------------------------------

def _database_url() -> Optional[str]:
    """URL do PostgreSQL, se configurada; senão None (usa SQLite)."""
    url = getattr(config, "DATABASE_URL", None) or os.environ.get("REGULAPRO_DATABASE_URL")
    if url:
        return url
    try:
        import streamlit as st

        return st.secrets.get("database", {}).get("url")
    except Exception:
        return None


def usa_postgres() -> bool:
    """True quando o app está ligado ao Supabase/PostgreSQL."""
    return bool(_database_url())


def agora() -> str:
    """Data e hora atuais no fuso de Brasília, no formato usado no banco."""
    return datetime.now(FUSO).strftime("%Y-%m-%d %H:%M:%S")


def garantir_data_dir() -> None:
    """Cria o diretório data/ se não existir."""
    os.makedirs(config.DATA_DIR, exist_ok=True)


def _traduzir(sql: str) -> str:
    """Adapta uma consulta escrita para SQLite ao PostgreSQL."""
    return sql.replace("?", "%s").replace(" LIKE ", " ILIKE ")


# ---------------------------------------------------------------------------
# Conexões
# ---------------------------------------------------------------------------

def _conectar_pg(url: str):
    import psycopg
    from psycopg.rows import dict_row

    # prepare_threshold=None: necessário no pooler do Supabase (modo transação)
    return psycopg.connect(url, row_factory=dict_row, prepare_threshold=None, connect_timeout=15)


def _pg(url: str):
    """Reaproveita uma conexão aberta; reabre se ela caiu."""
    global _pg_conexao
    if _pg_conexao is None or _pg_conexao.closed or _pg_conexao.broken:
        _pg_conexao = _conectar_pg(url)
    return _pg_conexao


class _CursorPG:
    """Deixa o cursor do PostgreSQL com a mesma cara do SQLite."""

    def __init__(self, conn):
        self._conn = conn
        self.lastrowid: Optional[int] = None
        self.rowcount = 0
        self._cur = None

    def execute(self, sql: str, params: Iterable[Any] = ()):
        self._cur = self._conn.execute(_traduzir(sql), tuple(params))
        self.rowcount = self._cur.rowcount
        return self

    def executemany(self, sql: str, lista_params: Iterable[Iterable[Any]]):
        with self._conn.cursor() as cur:
            cur.executemany(_traduzir(sql), [tuple(p) for p in lista_params])
            self.rowcount = cur.rowcount
        return self

    def fetchall(self) -> List[Dict[str, Any]]:
        return self._cur.fetchall() if self._cur and self._cur.description else []

    def fetchone(self) -> Optional[Dict[str, Any]]:
        return self._cur.fetchone() if self._cur and self._cur.description else None


@contextmanager
def get_conexao() -> Generator[Any, None, None]:
    """Abre uma transação no banco ativo; confirma no fim ou desfaz em caso de erro."""
    url = _database_url()
    if not url:
        garantir_data_dir()
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return

    import psycopg

    with _pg_lock:
        conn = _pg(url)
        try:
            conn.execute(f"SET LOCAL search_path TO {SCHEMA}, public")
        except psycopg.OperationalError:
            # Conexão ociosa derrubada pelo servidor: abre outra e segue
            conn = _pg(url)
            conn.execute(f"SET LOCAL search_path TO {SCHEMA}, public")
        try:
            yield _CursorPG(conn)
            conn.commit()
        except Exception:
            if not conn.closed:
                conn.rollback()
            raise


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------

_TABELAS_SQLITE = [
    """CREATE TABLE IF NOT EXISTS processos (
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
    )""",
    """CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT,
        data_evento TEXT NOT NULL,
        tipo_evento TEXT DEFAULT 'Atualização',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (processo_id) REFERENCES processos(id)
    )""",
    """CREATE TABLE IF NOT EXISTS tickets (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao TEXT,
        cliente TEXT NOT NULL,
        prioridade TEXT,
        status TEXT,
        data_criacao TEXT,
        data_atualizacao TEXT,
        atribuido_para TEXT,
        comentarios TEXT DEFAULT '[]'
    )""",
]

_AGORA_PG = "to_char(now() AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS')"

_TABELAS_PG = [
    f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}",
    f"""CREATE TABLE IF NOT EXISTS {SCHEMA}.processos (
        id BIGSERIAL PRIMARY KEY,
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
        percentual_conclusao DOUBLE PRECISION DEFAULT 0.0,
        created_at TEXT DEFAULT {_AGORA_PG},
        updated_at TEXT DEFAULT {_AGORA_PG}
    )""",
    f"""CREATE TABLE IF NOT EXISTS {SCHEMA}.eventos (
        id BIGSERIAL PRIMARY KEY,
        processo_id BIGINT NOT NULL REFERENCES {SCHEMA}.processos(id),
        titulo TEXT NOT NULL,
        descricao TEXT,
        data_evento TEXT NOT NULL,
        tipo_evento TEXT DEFAULT 'Atualização',
        created_at TEXT DEFAULT {_AGORA_PG}
    )""",
    f"""CREATE TABLE IF NOT EXISTS {SCHEMA}.tickets (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao TEXT,
        cliente TEXT NOT NULL,
        prioridade TEXT,
        status TEXT,
        data_criacao TEXT,
        data_atualizacao TEXT,
        atribuido_para TEXT,
        comentarios TEXT DEFAULT '[]'
    )""",
    # Bloqueia o acesso pela API pública do Supabase; o app conecta como dono das tabelas
    f"ALTER TABLE {SCHEMA}.processos ENABLE ROW LEVEL SECURITY",
    f"ALTER TABLE {SCHEMA}.eventos ENABLE ROW LEVEL SECURITY",
    f"ALTER TABLE {SCHEMA}.tickets ENABLE ROW LEVEL SECURITY",
]

_INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_processos_status ON processos(status)",
    "CREATE INDEX IF NOT EXISTS idx_processos_empresa ON processos(empresa)",
    "CREATE INDEX IF NOT EXISTS idx_eventos_processo ON eventos(processo_id)",
    "CREATE INDEX IF NOT EXISTS idx_tickets_cliente ON tickets(cliente)",
]


def inicializar_banco() -> None:
    """Cria as tabelas que faltarem (uma vez por banco a cada execução do app)."""
    url = _database_url()
    chave = url or os.path.abspath(config.DB_PATH)
    if chave in _inicializados and (url or os.path.exists(config.DB_PATH)):
        return
    with get_conexao() as conn:
        for sql in (_TABELAS_PG if url else _TABELAS_SQLITE) + _INDICES:
            conn.execute(sql)
    _inicializados.add(chave)


# ---------------------------------------------------------------------------
# Atalhos usados pelo resto do sistema
# ---------------------------------------------------------------------------

def executar_query(sql: str, params: tuple = (), fetchall: bool = True) -> List[Dict[str, Any]]:
    """Executa uma query SELECT e retorna lista de dicionários."""
    with get_conexao() as conn:
        cursor = conn.execute(sql, params)
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        row = cursor.fetchone()
        return [dict(row)] if row else []


def executar_insert(sql: str, params: tuple = ()) -> int:
    """Executa INSERT e retorna o id da linha criada."""
    with get_conexao() as conn:
        if isinstance(conn, _CursorPG):
            cursor = conn.execute(sql.rstrip().rstrip(";") + " RETURNING id", params)
            return cursor.fetchone()["id"]
        return conn.execute(sql, params).lastrowid


def executar_update(sql: str, params: tuple = ()) -> int:
    """Executa UPDATE/DELETE e retorna quantas linhas foram afetadas."""
    with get_conexao() as conn:
        return conn.execute(sql, params).rowcount


def executar_varios(sql: str, lista_params: List[tuple]) -> None:
    """Executa o mesmo comando para várias linhas, numa única transação."""
    if not lista_params:
        return
    with get_conexao() as conn:
        conn.executemany(sql, lista_params)
