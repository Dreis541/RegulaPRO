"""Pacote utils do RegulaPRO."""

from utils.constantes import (
    TODOS_STATUS,
    STATUS_ATIVOS,
    STATUS_FINALIZADOS,
    TIPOS_PROCESSO,
    CATEGORIAS_PRODUTO,
    PRIORIDADES,
    CORES_STATUS,
)
from utils.formatadores import (
    formatar_cnpj,
    limpar_cnpj,
    formatar_data,
    formatar_numero_processo,
    formatar_percentual,
    formatar_prazo_dias,
    truncar_texto,
    capitalizar_palavras,
)
from utils.helpers import (
    calcular_dias_restantes,
    calcular_percentual_conclusao,
    agrupar_por_campo,
    contar_por_campo,
    filtrar_lista,
    data_iso_para_date,
    gerar_numero_protocolo,
)

__all__ = [
    "TODOS_STATUS",
    "STATUS_ATIVOS",
    "STATUS_FINALIZADOS",
    "TIPOS_PROCESSO",
    "CATEGORIAS_PRODUTO",
    "PRIORIDADES",
    "CORES_STATUS",
    "formatar_cnpj",
    "limpar_cnpj",
    "formatar_data",
    "formatar_numero_processo",
    "formatar_percentual",
    "formatar_prazo_dias",
    "truncar_texto",
    "capitalizar_palavras",
    "calcular_dias_restantes",
    "calcular_percentual_conclusao",
    "agrupar_por_campo",
    "contar_por_campo",
    "filtrar_lista",
    "data_iso_para_date",
    "gerar_numero_protocolo",
]
