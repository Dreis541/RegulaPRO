"""Validações ANVISA para o RegulaPRO."""

import re
from datetime import date
from typing import Dict, List, Optional, Tuple


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo oficial.
    Aceita formatos com ou sem máscara.
    """
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14:
        return False
    if digits == digits[0] * 14:
        return False

    def _calcular_digito(parcial: str, pesos: List[int]) -> int:
        soma = sum(int(d) * p for d, p in zip(parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = _calcular_digito(digits[:12], pesos1)
    d2 = _calcular_digito(digits[:13], pesos2)

    return digits[-2:] == f"{d1}{d2}"


def validar_numero_protocolo(numero: str) -> bool:
    """Valida formato de número de protocolo RegulaPRO (RP-YYYYMMDDHHMMSSuuuuuu)."""
    pattern = r"^RP-\d{20}$"
    return bool(re.match(pattern, numero))


def validar_numero_processo_anvisa(numero: str) -> bool:
    """Valida formato de número de processo ANVISA (XXXXX.XXXXXX/XXXX-XX)."""
    digits = re.sub(r"\D", "", numero)
    return len(digits) == 17


def validar_data_prazo(data_abertura: date, data_prazo: date) -> Tuple[bool, str]:
    """
    Valida que a data de prazo é posterior à data de abertura.
    Retorna (válido, mensagem).
    """
    if data_prazo <= data_abertura:
        return False, "A data de prazo deve ser posterior à data de abertura."
    return True, ""


def validar_campos_obrigatorios(dados: Dict) -> Tuple[bool, List[str]]:
    """
    Valida que os campos obrigatórios estão presentes e não são vazios.
    Retorna (válido, lista_de_erros).
    """
    campos_obrigatorios = ["empresa", "tipo", "data_abertura", "numero_protocolo"]
    erros: List[str] = []
    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if not valor or (isinstance(valor, str) and not valor.strip()):
            erros.append(f"Campo obrigatório ausente: {campo}")
    return len(erros) == 0, erros


def validar_processo(dados: Dict) -> Tuple[bool, List[str]]:
    """
    Validação completa de um processo ANVISA.
    Retorna (válido, lista_de_erros).
    """
    erros: List[str] = []

    valido, erros_obrig = validar_campos_obrigatorios(dados)
    if not valido:
        erros.extend(erros_obrig)

    cnpj = dados.get("cnpj", "")
    if cnpj and not validar_cnpj(cnpj):
        erros.append("CNPJ inválido.")

    data_abertura = dados.get("data_abertura")
    data_prazo = dados.get("data_prazo")
    if data_abertura and data_prazo:
        if isinstance(data_abertura, str):
            try:
                from datetime import datetime
                data_abertura = datetime.strptime(data_abertura, "%Y-%m-%d").date()
            except ValueError:
                erros.append("Formato de data de abertura inválido (use YYYY-MM-DD).")
                data_abertura = None
        if isinstance(data_prazo, str):
            try:
                from datetime import datetime
                data_prazo = datetime.strptime(data_prazo, "%Y-%m-%d").date()
            except ValueError:
                erros.append("Formato de data de prazo inválido (use YYYY-MM-DD).")
                data_prazo = None
        if data_abertura and data_prazo:
            prazo_ok, msg = validar_data_prazo(data_abertura, data_prazo)
            if not prazo_ok:
                erros.append(msg)

    percentual = dados.get("percentual_conclusao", 0)
    if not (0 <= float(percentual) <= 100):
        erros.append("Percentual de conclusão deve estar entre 0 e 100.")

    return len(erros) == 0, erros
