"""CRUD e lógica de negócio para processos ANVISA."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from functions.database import executar_query, executar_insert, executar_update, inicializar_banco
from functions.validacoes import validar_processo
from utils.helpers import gerar_numero_protocolo, calcular_dias_restantes
from utils.constantes import STATUS_ATRASADO, STATUS_ATIVOS


def criar_processo(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria um novo processo no banco de dados.
    Retorna {'sucesso': bool, 'id': int|None, 'erros': list}.
    """
    inicializar_banco()

    if "numero_protocolo" not in dados or not dados["numero_protocolo"]:
        dados["numero_protocolo"] = gerar_numero_protocolo()

    valido, erros = validar_processo(dados)
    if not valido:
        return {"sucesso": False, "id": None, "erros": erros}

    sql = """
        INSERT INTO processos (
            numero_protocolo, empresa, cnpj, tipo, categoria, produto,
            status, prioridade, data_abertura, data_prazo, data_conclusao,
            responsavel, descricao, observacoes, percentual_conclusao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        dados.get("numero_protocolo"),
        dados.get("empresa"),
        dados.get("cnpj", ""),
        dados.get("tipo"),
        dados.get("categoria", ""),
        dados.get("produto", ""),
        dados.get("status", "Em Andamento"),
        dados.get("prioridade", "Média"),
        _to_str(dados.get("data_abertura")),
        _to_str(dados.get("data_prazo")),
        _to_str(dados.get("data_conclusao")),
        dados.get("responsavel", ""),
        dados.get("descricao", ""),
        dados.get("observacoes", ""),
        float(dados.get("percentual_conclusao", 0)),
    )
    novo_id = executar_insert(sql, params)
    return {"sucesso": True, "id": novo_id, "erros": []}


def listar_processos(
    empresa: Optional[str] = None,
    status: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    tipo: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lista processos com filtros opcionais."""
    inicializar_banco()
    sql = "SELECT * FROM processos WHERE 1=1"
    params: List[Any] = []

    if empresa:
        sql += " AND empresa LIKE ?"
        params.append(f"%{empresa}%")
    if status:
        sql += " AND status = ?"
        params.append(status)
    if data_inicio:
        sql += " AND data_abertura >= ?"
        params.append(data_inicio)
    if data_fim:
        sql += " AND data_abertura <= ?"
        params.append(data_fim)
    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo)

    sql += " ORDER BY created_at DESC"
    return executar_query(sql, tuple(params))


def buscar_processo_por_id(processo_id: int) -> Optional[Dict[str, Any]]:
    """Retorna um processo pelo ID ou None se não encontrado."""
    inicializar_banco()
    rows = executar_query("SELECT * FROM processos WHERE id = ?", (processo_id,), fetchall=False)
    return rows[0] if rows else None


def buscar_processo_por_protocolo(numero: str) -> Optional[Dict[str, Any]]:
    """Retorna um processo pelo número de protocolo."""
    inicializar_banco()
    rows = executar_query(
        "SELECT * FROM processos WHERE numero_protocolo = ?", (numero,), fetchall=False
    )
    return rows[0] if rows else None


def atualizar_processo(processo_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
    """Atualiza campos de um processo existente."""
    inicializar_banco()
    campos_permitidos = [
        "empresa", "cnpj", "tipo", "categoria", "produto", "status",
        "prioridade", "data_prazo", "data_conclusao", "responsavel",
        "descricao", "observacoes", "percentual_conclusao",
    ]
    sets = []
    params: List[Any] = []
    for campo in campos_permitidos:
        if campo in dados:
            sets.append(f"{campo} = ?")
            params.append(dados[campo])

    if not sets:
        return {"sucesso": False, "erros": ["Nenhum campo para atualizar."]}

    sets.append("updated_at = datetime('now','localtime')")
    params.append(processo_id)
    sql = f"UPDATE processos SET {', '.join(sets)} WHERE id = ?"
    rowcount = executar_update(sql, tuple(params))
    if rowcount == 0:
        return {"sucesso": False, "erros": ["Processo não encontrado."]}
    return {"sucesso": True, "erros": []}


def excluir_processo(processo_id: int) -> bool:
    """Exclui um processo e seus eventos. Retorna True se excluiu."""
    inicializar_banco()
    executar_update("DELETE FROM eventos WHERE processo_id = ?", (processo_id,))
    rowcount = executar_update("DELETE FROM processos WHERE id = ?", (processo_id,))
    return rowcount > 0


def adicionar_evento(
    processo_id: int,
    titulo: str,
    descricao: str = "",
    tipo_evento: str = "Atualização",
    data_evento: Optional[str] = None,
) -> int:
    """Adiciona um evento/timeline a um processo. Retorna o ID do evento."""
    inicializar_banco()
    if data_evento is None:
        data_evento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO eventos (processo_id, titulo, descricao, data_evento, tipo_evento)
        VALUES (?, ?, ?, ?, ?)
    """
    return executar_insert(sql, (processo_id, titulo, descricao, data_evento, tipo_evento))


def listar_eventos(processo_id: int) -> List[Dict[str, Any]]:
    """Lista todos os eventos de um processo em ordem cronológica."""
    inicializar_banco()
    return executar_query(
        "SELECT * FROM eventos WHERE processo_id = ? ORDER BY data_evento DESC",
        (processo_id,),
    )


def obter_metricas() -> Dict[str, Any]:
    """Retorna métricas agregadas para o dashboard."""
    inicializar_banco()
    total = executar_query("SELECT COUNT(*) as total FROM processos", fetchall=False)
    total_count = total[0]["total"] if total else 0

    por_status = executar_query(
        "SELECT status, COUNT(*) as quantidade FROM processos GROUP BY status"
    )

    atrasados = executar_query(
        "SELECT COUNT(*) as total FROM processos WHERE status = 'Atrasado'",
        fetchall=False,
    )
    atrasados_count = atrasados[0]["total"] if atrasados else 0

    em_andamento = sum(
        r["quantidade"] for r in por_status if r["status"] in STATUS_ATIVOS
    )
    concluidos = sum(
        r["quantidade"] for r in por_status
        if r["status"] in ("Concluído", "Deferido")
    )

    return {
        "total": total_count,
        "em_andamento": em_andamento,
        "concluidos": concluidos,
        "atrasados": atrasados_count,
        "por_status": por_status,
    }


def verificar_e_atualizar_atrasados() -> int:
    """
    Marca como 'Atrasado' os processos com prazo vencido e status ativo.
    Retorna quantos foram atualizados.
    """
    inicializar_banco()
    hoje = date.today().isoformat()
    placeholders = ", ".join("?" for _ in STATUS_ATIVOS)
    sql = f"""
        UPDATE processos
        SET status = ?, updated_at = datetime('now','localtime')
        WHERE data_prazo IS NOT NULL
          AND data_prazo < ?
          AND status IN ({placeholders})
    """
    return executar_update(sql, (STATUS_ATRASADO, hoje) + tuple(STATUS_ATIVOS))


def _to_str(valor: Any) -> Optional[str]:
    """Converte date/datetime para ISO string ou retorna None."""
    if valor is None:
        return None
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return str(valor) if valor else None
