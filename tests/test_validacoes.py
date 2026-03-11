"""Testes unitários para as validações ANVISA."""

import pytest
from datetime import date, timedelta
from functions.validacoes import (
    validar_cnpj,
    validar_numero_protocolo,
    validar_numero_processo_anvisa,
    validar_data_prazo,
    validar_campos_obrigatorios,
    validar_processo,
)


class TestValidarCnpj:
    def test_cnpj_valido_formatado(self):
        assert validar_cnpj("11.222.333/0001-81") is True

    def test_cnpj_valido_sem_mascara(self):
        assert validar_cnpj("11222333000181") is True

    def test_cnpj_invalido_digitos_verificadores(self):
        assert validar_cnpj("11.222.333/0001-00") is False

    def test_cnpj_todos_iguais(self):
        assert validar_cnpj("11.111.111/1111-11") is False

    def test_cnpj_tamanho_errado(self):
        assert validar_cnpj("123456") is False

    def test_cnpj_vazio(self):
        assert validar_cnpj("") is False

    def test_cnpj_letras(self):
        assert validar_cnpj("XX.XXX.XXX/XXXX-XX") is False

    def test_cnpj_zeros(self):
        assert validar_cnpj("00.000.000/0000-00") is False


class TestValidarNumeroProtocolo:
    def test_protocolo_valido(self):
        assert validar_numero_protocolo("RP-20260101120000123456") is True

    def test_protocolo_invalido_prefixo(self):
        assert validar_numero_protocolo("XX-20260101120000123456") is False

    def test_protocolo_invalido_tamanho(self):
        assert validar_numero_protocolo("RP-202601011200") is False

    def test_protocolo_vazio(self):
        assert validar_numero_protocolo("") is False


class TestValidarNumeroProcessoAnvisa:
    def test_processo_anvisa_valido(self):
        assert validar_numero_processo_anvisa("25351.123456/2024-01") is True

    def test_processo_anvisa_so_numeros(self):
        assert validar_numero_processo_anvisa("25351123456202401") is True

    def test_processo_anvisa_invalido_curto(self):
        assert validar_numero_processo_anvisa("123456") is False


class TestValidarDataPrazo:
    def test_data_prazo_valida(self):
        abertura = date.today()
        prazo = date.today() + timedelta(days=30)
        ok, msg = validar_data_prazo(abertura, prazo)
        assert ok is True
        assert msg == ""

    def test_data_prazo_igual_abertura(self):
        hoje = date.today()
        ok, msg = validar_data_prazo(hoje, hoje)
        assert ok is False
        assert "posterior" in msg.lower()

    def test_data_prazo_anterior_abertura(self):
        abertura = date.today()
        prazo = date.today() - timedelta(days=5)
        ok, msg = validar_data_prazo(abertura, prazo)
        assert ok is False


class TestValidarCamposObrigatorios:
    def test_todos_campos_presentes(self):
        dados = {
            "empresa": "Empresa X",
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
        }
        ok, erros = validar_campos_obrigatorios(dados)
        assert ok is True
        assert erros == []

    def test_campo_empresa_ausente(self):
        dados = {
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
        }
        ok, erros = validar_campos_obrigatorios(dados)
        assert ok is False
        assert any("empresa" in e for e in erros)

    def test_campo_empresa_vazio(self):
        dados = {
            "empresa": "   ",
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
        }
        ok, erros = validar_campos_obrigatorios(dados)
        assert ok is False


class TestValidarProcesso:
    def test_processo_valido_completo(self):
        dados = {
            "empresa": "Empresa X",
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
            "cnpj": "11.222.333/0001-81",
            "data_prazo": (date.today() + timedelta(days=30)).isoformat(),
            "percentual_conclusao": 50,
        }
        ok, erros = validar_processo(dados)
        assert ok is True
        assert erros == []

    def test_processo_cnpj_invalido(self):
        dados = {
            "empresa": "Empresa X",
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
            "cnpj": "00.000.000/0000-00",
            "percentual_conclusao": 0,
        }
        ok, erros = validar_processo(dados)
        assert ok is False
        assert any("CNPJ" in e for e in erros)

    def test_processo_percentual_invalido(self):
        dados = {
            "empresa": "Empresa X",
            "tipo": "Registro de Produto",
            "data_abertura": date.today().isoformat(),
            "numero_protocolo": "RP-20260101120000",
            "percentual_conclusao": 150,
        }
        ok, erros = validar_processo(dados)
        assert ok is False
        assert any("percentual" in e.lower() for e in erros)
