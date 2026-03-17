"""Funções auxiliares do RegulaPRO."""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


def calcular_dias_restantes(data_prazo: Optional[date]) -> Optional[int]:
    """Retorna a diferença em dias entre hoje e a data de prazo."""
    if data_prazo is None:
        return None
    hoje = date.today()
    if isinstance(data_prazo, datetime):
        data_prazo = data_prazo.date()
    return (data_prazo - hoje).days


def calcular_percentual_conclusao(etapas_concluidas: int, total_etapas: int) -> float:
    """Calcula percentual de conclusão com base em etapas."""
    if total_etapas <= 0:
        return 0.0
    return min(100.0, (etapas_concluidas / total_etapas) * 100)


def agrupar_por_campo(lista: List[Dict[str, Any]], campo: str) -> Dict[str, List[Dict]]:
    """Agrupa uma lista de dicionários por um campo específico."""
    resultado: Dict[str, List[Dict]] = {}
    for item in lista:
        chave = str(item.get(campo, ""))
        resultado.setdefault(chave, []).append(item)
    return resultado


def contar_por_campo(lista: List[Dict[str, Any]], campo: str) -> Dict[str, int]:
    """Conta ocorrências de cada valor de um campo na lista."""
    contagem: Dict[str, int] = {}
    for item in lista:
        chave = str(item.get(campo, ""))
        contagem[chave] = contagem.get(chave, 0) + 1
    return contagem


def filtrar_lista(
    lista: List[Dict[str, Any]],
    filtros: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Filtra uma lista de dicionários com base em um dicionário de filtros."""
    resultado = []
    for item in lista:
        match = True
        for campo, valor in filtros.items():
            if valor is None or valor == "" or valor == []:
                continue
            item_val = item.get(campo)
            if isinstance(valor, list):
                if item_val not in valor:
                    match = False
                    break
            else:
                if item_val != valor:
                    match = False
                    break
        if match:
            resultado.append(item)
    return resultado


def data_iso_para_date(valor: Optional[str]) -> Optional[date]:
    """Converte string ISO (YYYY-MM-DD) para objeto date."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return None


def gerar_numero_protocolo(prefixo: str = "RP") -> str:
    """Gera um número de protocolo baseado em timestamp com microsegundos."""
    agora = datetime.now()
    return f"{prefixo}-{agora.strftime('%Y%m%d%H%M%S')}{agora.microsecond:06d}"
