"""Integração e utilitários ANVISA para o RegulaPRO."""

from typing import Dict, List, Optional
from utils.constantes import TIPOS_PROCESSO, CATEGORIAS_PRODUTO, PRAZO_REGISTRO, PRAZO_RENOVACAO, PRAZO_LICENCA, PRAZO_AUTORIZACAO, PRAZO_NOTIFICACAO


# Mapa de prazos padrão por tipo de processo
PRAZOS_POR_TIPO: Dict[str, int] = {
    "Registro de Produto": PRAZO_REGISTRO,
    "Renovação de Registro": PRAZO_RENOVACAO,
    "Licença de Funcionamento": PRAZO_LICENCA,
    "Autorização Especial": PRAZO_AUTORIZACAO,
    "Notificação": PRAZO_NOTIFICACAO,
}


def obter_prazo_padrao(tipo_processo: str) -> int:
    """Retorna o prazo padrão (em dias) para um tipo de processo."""
    return PRAZOS_POR_TIPO.get(tipo_processo, 90)


def obter_tipos_processo() -> List[str]:
    """Retorna a lista de tipos de processo ANVISA."""
    return TIPOS_PROCESSO


def obter_categorias() -> List[str]:
    """Retorna a lista de categorias de produto ANVISA."""
    return CATEGORIAS_PRODUTO


def gerar_checklist_documentos(tipo_processo: str, categoria: Optional[str] = None) -> List[str]:
    """
    Retorna checklist de documentos necessários por tipo de processo.
    """
    base = [
        "Requerimento de Petição (original)",
        "Comprovante de pagamento da taxa (GRU)",
        "Documentação do responsável técnico",
        "CNPJ/Contrato Social atualizado",
    ]

    especificos: Dict[str, List[str]] = {
        "Registro de Produto": [
            "Relatório técnico do produto",
            "Laudos de análise laboratorial",
            "Bulas (se aplicável)",
            "Rotulagem proposta",
            "Dados de segurança e eficácia",
        ],
        "Renovação de Registro": [
            "Cópia do registro anterior",
            "Relatório de farmacovigilância (se aplicável)",
            "Dados de comercialização",
        ],
        "Licença de Funcionamento": [
            "Alvará de funcionamento municipal",
            "Laudo de vistoria sanitária",
            "Responsável técnico habilitado",
            "Planta baixa do estabelecimento",
        ],
        "Autorização Especial": [
            "Justificativa técnica detalhada",
            "Parecer do órgão competente",
        ],
        "Notificação": [
            "Ficha técnica completa do produto",
            "Composição qualitativa e quantitativa",
        ],
    }

    return base + especificos.get(tipo_processo, [])


def calcular_taxa_anvisa(tipo_processo: str, porte_empresa: str = "Médio") -> float:
    """
    Retorna uma estimativa de taxa ANVISA para o tipo de processo.
    Valores de referência aproximados (em R$).
    """
    tabela: Dict[str, Dict[str, float]] = {
        "Registro de Produto": {"Micro": 1800.0, "Pequeno": 3600.0, "Médio": 7200.0, "Grande": 14400.0},
        "Renovação de Registro": {"Micro": 900.0, "Pequeno": 1800.0, "Médio": 3600.0, "Grande": 7200.0},
        "Licença de Funcionamento": {"Micro": 500.0, "Pequeno": 1000.0, "Médio": 2000.0, "Grande": 4000.0},
        "Autorização Especial": {"Micro": 300.0, "Pequeno": 600.0, "Médio": 1200.0, "Grande": 2400.0},
        "Notificação": {"Micro": 100.0, "Pequeno": 200.0, "Médio": 400.0, "Grande": 800.0},
        "Certificação": {"Micro": 2000.0, "Pequeno": 4000.0, "Médio": 8000.0, "Grande": 16000.0},
        "Petição": {"Micro": 200.0, "Pequeno": 400.0, "Médio": 800.0, "Grande": 1600.0},
        "Recurso": {"Micro": 150.0, "Pequeno": 300.0, "Médio": 600.0, "Grande": 1200.0},
    }
    tipo_tabela = tabela.get(tipo_processo, {})
    return tipo_tabela.get(porte_empresa, 500.0)
