"""Testes de gerenciamento de processos."""

import pytest
from datetime import date, timedelta

from functions.processos import (
    criar_processo,
    listar_processos,
    buscar_processo_por_id,
    buscar_processo_por_protocolo,
    atualizar_processo,
    excluir_processo,
    adicionar_evento,
    listar_eventos,
    obter_metricas,
    verificar_e_atualizar_atrasados,
)
from functions.database import inicializar_banco


class TestCriarProcesso:
    def test_criar_processo_valido(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        assert resultado["sucesso"] is True
        assert resultado["id"] is not None
        assert resultado["erros"] == []

    def test_criar_processo_sem_empresa(self, processo_exemplo):
        processo_exemplo["empresa"] = ""
        resultado = criar_processo(processo_exemplo)
        assert resultado["sucesso"] is False
        assert len(resultado["erros"]) > 0

    def test_criar_processo_gera_protocolo_automatico(self, processo_exemplo):
        processo_exemplo.pop("numero_protocolo", None)
        resultado = criar_processo(processo_exemplo)
        assert resultado["sucesso"] is True

    def test_criar_processo_cnpj_invalido(self, processo_exemplo):
        processo_exemplo["cnpj"] = "00.000.000/0000-00"
        resultado = criar_processo(processo_exemplo)
        assert resultado["sucesso"] is False

    def test_criar_processo_percentual_invalido(self, processo_exemplo):
        processo_exemplo["percentual_conclusao"] = 200
        resultado = criar_processo(processo_exemplo)
        assert resultado["sucesso"] is False


class TestListarProcessos:
    def test_listar_vazio(self):
        inicializar_banco()
        processos = listar_processos()
        assert processos == []

    def test_listar_apos_criar(self, processo_exemplo):
        criar_processo(processo_exemplo)
        processos = listar_processos()
        assert len(processos) == 1

    def test_filtrar_por_empresa(self, processo_exemplo):
        criar_processo(processo_exemplo)
        resultados = listar_processos(empresa="Farmacêutica Teste")
        assert len(resultados) == 1
        resultados_sem = listar_processos(empresa="Empresa Inexistente")
        assert len(resultados_sem) == 0

    def test_filtrar_por_status(self, processo_exemplo):
        criar_processo(processo_exemplo)
        resultados = listar_processos(status="Em Andamento")
        assert len(resultados) == 1
        resultados_outro = listar_processos(status="Concluído")
        assert len(resultados_outro) == 0

    def test_filtrar_por_tipo(self, processo_exemplo):
        criar_processo(processo_exemplo)
        resultados = listar_processos(tipo="Registro de Produto")
        assert len(resultados) == 1


class TestBuscarProcesso:
    def test_buscar_por_id_existente(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        processo = buscar_processo_por_id(resultado["id"])
        assert processo is not None
        assert processo["empresa"] == processo_exemplo["empresa"]

    def test_buscar_por_id_inexistente(self):
        inicializar_banco()
        processo = buscar_processo_por_id(9999)
        assert processo is None

    def test_buscar_por_protocolo(self, processo_exemplo):
        processo_exemplo["numero_protocolo"] = "RP-20260101120000000000"
        criar_processo(processo_exemplo)
        processo = buscar_processo_por_protocolo("RP-20260101120000000000")
        assert processo is not None
        assert processo["numero_protocolo"] == "RP-20260101120000000000"

    def test_buscar_por_protocolo_inexistente(self):
        inicializar_banco()
        processo = buscar_processo_por_protocolo("RP-99999999999999")
        assert processo is None


class TestAtualizarProcesso:
    def test_atualizar_status(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        pid = resultado["id"]
        upd = atualizar_processo(pid, {"status": "Concluído", "percentual_conclusao": 100})
        assert upd["sucesso"] is True
        processo = buscar_processo_por_id(pid)
        assert processo["status"] == "Concluído"
        assert float(processo["percentual_conclusao"]) == 100.0

    def test_atualizar_processo_inexistente(self):
        inicializar_banco()
        upd = atualizar_processo(9999, {"status": "Concluído"})
        assert upd["sucesso"] is False

    def test_atualizar_sem_campos(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        upd = atualizar_processo(resultado["id"], {})
        assert upd["sucesso"] is False


class TestExcluirProcesso:
    def test_excluir_processo_existente(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        pid = resultado["id"]
        sucesso = excluir_processo(pid)
        assert sucesso is True
        assert buscar_processo_por_id(pid) is None

    def test_excluir_processo_inexistente(self):
        inicializar_banco()
        sucesso = excluir_processo(9999)
        assert sucesso is False


class TestEventos:
    def test_adicionar_e_listar_eventos(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        pid = resultado["id"]
        adicionar_evento(pid, "Documento enviado", "PDF recebido", tipo_evento="Documento")
        adicionar_evento(pid, "Status atualizado", tipo_evento="Atualização")
        eventos = listar_eventos(pid)
        assert len(eventos) == 2

    def test_listar_eventos_processo_sem_eventos(self, processo_exemplo):
        resultado = criar_processo(processo_exemplo)
        eventos = listar_eventos(resultado["id"])
        assert eventos == []


class TestObterMetricas:
    def test_metricas_banco_vazio(self):
        inicializar_banco()
        metricas = obter_metricas()
        assert metricas["total"] == 0
        assert metricas["em_andamento"] == 0
        assert metricas["concluidos"] == 0
        assert metricas["atrasados"] == 0

    def test_metricas_com_processos(self, processo_exemplo):
        criar_processo(processo_exemplo)
        metricas = obter_metricas()
        assert metricas["total"] == 1
        assert metricas["em_andamento"] == 1


class TestVerificarAtrasados:
    def test_processo_sem_prazo_nao_fica_atrasado(self, processo_exemplo):
        processo_exemplo["data_prazo"] = None
        criar_processo(processo_exemplo)
        count = verificar_e_atualizar_atrasados()
        assert count == 0

    def test_processo_com_prazo_vencido_fica_atrasado(self, processo_exemplo):
        processo_exemplo["data_abertura"] = date.today() - timedelta(days=30)
        processo_exemplo["data_prazo"] = date.today() - timedelta(days=1)
        criar_processo(processo_exemplo)
        count = verificar_e_atualizar_atrasados()
        assert count == 1
        processos = listar_processos(status="Atrasado")
        assert len(processos) == 1

    def test_processo_com_prazo_futuro_nao_fica_atrasado(self, processo_exemplo):
        processo_exemplo["data_prazo"] = date.today() + timedelta(days=30)
        criar_processo(processo_exemplo)
        count = verificar_e_atualizar_atrasados()
        assert count == 0
