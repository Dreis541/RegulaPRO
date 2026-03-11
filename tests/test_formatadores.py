"""Testes para funções de formatação de dados."""

import pytest
from datetime import date, datetime
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


class TestFormatarCnpj:
    def test_cnpj_14_digitos(self):
        assert formatar_cnpj("11222333000181") == "11.222.333/0001-81"

    def test_cnpj_ja_formatado(self):
        assert formatar_cnpj("11.222.333/0001-81") == "11.222.333/0001-81"

    def test_cnpj_tamanho_errado_retorna_original(self):
        assert formatar_cnpj("123456") == "123456"

    def test_cnpj_vazio(self):
        assert formatar_cnpj("") == ""


class TestLimparCnpj:
    def test_remove_formatacao(self):
        assert limpar_cnpj("11.222.333/0001-81") == "11222333000181"

    def test_ja_limpo(self):
        assert limpar_cnpj("11222333000181") == "11222333000181"

    def test_vazio(self):
        assert limpar_cnpj("") == ""


class TestFormatarData:
    def test_string_iso(self):
        assert formatar_data("2024-01-15") == "15/01/2024"

    def test_objeto_date(self):
        assert formatar_data(date(2024, 1, 15)) == "15/01/2024"

    def test_objeto_datetime(self):
        assert formatar_data(datetime(2024, 1, 15, 10, 30)) == "15/01/2024"

    def test_none_retorna_vazio(self):
        assert formatar_data(None) == ""

    def test_formato_personalizado(self):
        assert formatar_data("2024-01-15", "%Y/%m/%d") == "2024/01/15"

    def test_string_invalida_retorna_original(self):
        resultado = formatar_data("data-invalida")
        assert resultado == "data-invalida"


class TestFormatarNumeroProcesso:
    def test_17_digitos(self):
        resultado = formatar_numero_processo("25351123456202401")
        assert resultado == "25351.123456/2024-01"

    def test_tamanho_diferente_retorna_original(self):
        assert formatar_numero_processo("12345") == "12345"


class TestFormatarPercentual:
    def test_valor_inteiro(self):
        assert formatar_percentual(75.0) == "75.0%"

    def test_casas_decimais(self):
        assert formatar_percentual(33.333, 2) == "33.33%"

    def test_zero(self):
        assert formatar_percentual(0) == "0.0%"

    def test_cem(self):
        assert formatar_percentual(100) == "100.0%"


class TestFormatarPrazoDias:
    def test_dias_negativos(self):
        resultado = formatar_prazo_dias(-5)
        assert "5" in resultado
        assert "atrasado" in resultado.lower()

    def test_dia_zero(self):
        assert "hoje" in formatar_prazo_dias(0).lower()

    def test_um_dia(self):
        assert "1 dia" in formatar_prazo_dias(1)

    def test_multiplos_dias(self):
        resultado = formatar_prazo_dias(30)
        assert "30" in resultado
        assert "restante" in resultado.lower()

    def test_none_retorna_traco(self):
        assert formatar_prazo_dias(None) == "—"


class TestTruncarTexto:
    def test_texto_dentro_do_limite(self):
        assert truncar_texto("Texto curto", 20) == "Texto curto"

    def test_texto_acima_do_limite(self):
        resultado = truncar_texto("Texto muito longo que ultrapassa o limite", 15)
        assert len(resultado) <= 15
        assert resultado.endswith("...")

    def test_texto_vazio(self):
        assert truncar_texto("") == ""

    def test_limite_exato(self):
        texto = "Exato123456789012"
        assert truncar_texto(texto, len(texto)) == texto


class TestCapitalizarPalavras:
    def test_minusculas(self):
        assert capitalizar_palavras("farmácia central") == "Farmácia Central"

    def test_ja_capitalizado(self):
        assert capitalizar_palavras("Farmácia Central") == "Farmácia Central"

    def test_texto_vazio(self):
        assert capitalizar_palavras("") == ""

    def test_uma_palavra(self):
        assert capitalizar_palavras("anvisa") == "Anvisa"
