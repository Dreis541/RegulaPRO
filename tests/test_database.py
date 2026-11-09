"""Testes da camada de banco (rodam em SQLite e, com REGULAPRO_TEST_PG, em PostgreSQL)."""

from datetime import date, timedelta

from functions.database import _traduzir, executar_query
from functions.processos import (
    adicionar_evento, atualizar_processo, criar_processo, listar_eventos,
    listar_processos, obter_metricas, verificar_e_atualizar_atrasados,
)
from functions.tickets import TicketManager


def test_traducao_para_postgres():
    assert _traduzir("SELECT * FROM t WHERE a = ? AND b LIKE ?") == "SELECT * FROM t WHERE a = %s AND b ILIKE %s"


def test_ciclo_completo_de_processo(processo_exemplo):
    r = criar_processo(processo_exemplo)
    assert r["sucesso"], r
    pid = r["id"]
    assert isinstance(pid, int)

    assert atualizar_processo(pid, {"status": "Concluído", "percentual_conclusao": 100})["sucesso"]
    assert adicionar_evento(pid, "Protocolado", "Enviado à ANVISA")
    assert listar_eventos(pid)[0]["titulo"] == "Protocolado"
    assert obter_metricas()["total"] == 1


def test_busca_por_empresa_ignora_maiusculas(processo_exemplo):
    criar_processo(processo_exemplo)
    assert len(listar_processos(empresa="farmacêutica teste")) == 1


def test_atrasados(processo_exemplo):
    processo_exemplo["data_abertura"] = date.today() - timedelta(days=30)
    processo_exemplo["data_prazo"] = date.today() - timedelta(days=3)
    assert criar_processo(processo_exemplo)["sucesso"]
    assert verificar_e_atualizar_atrasados() == 1
    assert listar_processos()[0]["status"] == "Atrasado"


def test_chamados_no_banco_sobrevivem_a_nova_leitura():
    manager = TicketManager()
    ticket = manager.criar_ticket("Erro no protocolo", "Não salva", "Cliente A", "alta")
    ticket.adicionar_comentario("Suporte", "Verificando")
    manager.salvar_tickets()
    manager.atualizar_ticket(ticket.id, status="em_progresso")

    lido = TicketManager().obter_ticket(ticket.id)
    assert lido.status == "em_progresso"
    assert lido.comentarios[0]["texto"] == "Verificando"
    assert len(executar_query("SELECT * FROM tickets")) == 1
