"""Funções de formatação de dados para o RegulaPRO."""

import re
from datetime import datetime, date
from typing import Optional, Union


def formatar_cnpj(cnpj: str) -> str:
    """Formata string numérica como CNPJ (XX.XXX.XXX/XXXX-XX)."""
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14:
        return cnpj
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def limpar_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ, retornando apenas dígitos."""
    return re.sub(r"\D", "", cnpj)


def formatar_data(valor: Union[str, date, datetime], formato_saida: str = "%d/%m/%Y") -> str:
    """Converte um valor de data para string formatada."""
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime(formato_saida)
    if isinstance(valor, date):
        return valor.strftime(formato_saida)
    # Tenta parsing de string ISO
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(valor), fmt).strftime(formato_saida)
        except ValueError:
            continue
    return str(valor)


def formatar_numero_processo(numero: str) -> str:
    """Formata número de processo ANVISA (XXXXX.XXXXXX/XXXX-XX)."""
    digits = re.sub(r"\D", "", numero)
    if len(digits) == 17:
        return f"{digits[:5]}.{digits[5:11]}/{digits[11:15]}-{digits[15:]}"
    return numero


def formatar_percentual(valor: float, casas: int = 1) -> str:
    """Formata um float como percentual com símbolo %."""
    return f"{valor:.{casas}f}%"


def formatar_prazo_dias(dias: Optional[int]) -> str:
    """Formata quantidade de dias de prazo em texto legível."""
    if dias is None:
        return "—"
    if dias < 0:
        return f"{abs(dias)} dia(s) atrasado"
    if dias == 0:
        return "Vence hoje"
    if dias == 1:
        return "1 dia restante"
    return f"{dias} dias restantes"


def truncar_texto(texto: str, limite: int = 50, sufixo: str = "...") -> str:
    """Trunca texto ao limite de caracteres, adicionando sufixo se necessário."""
    if not texto:
        return ""
    if len(texto) <= limite:
        return texto
    return texto[: limite - len(sufixo)] + sufixo


def capitalizar_palavras(texto: str) -> str:
    """Capitaliza cada palavra do texto."""
    if not texto:
        return ""
    return " ".join(word.capitalize() for word in texto.split())
