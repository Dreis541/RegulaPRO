"""
Testes unitários para o Sistema de Gerenciamento de Tickets
"""

import unittest
import json
import os
from datetime import datetime
from functions.tickets import Ticket, TicketManager, TicketStatus, TicketPriority


class TestTicket(unittest.TestCase):
    """Testes para a classe Ticket"""
    
    def setUp(self):
        """Prepara cada teste"""
        self.ticket = Ticket(
            titulo="Teste de Ticket",
            descricao="Descrição de teste",
            cliente="Cliente Teste",
            prioridade="media"
        )
    
    def test_criacao_ticket(self):
        """Verifica se um ticket é criado corretamente"""
        self.assertIsNotNone(self.ticket.id)
        self.assertEqual(self.ticket.titulo, "Teste de Ticket")
        self.assertEqual(self.ticket.status, TicketStatus.ABERTO.value)
    
    def test_atualizar_status(self):
        """Testa atualização de status"""
        resultado = self.ticket.atualizar_status("em_progresso")
        self.assertTrue(resultado)
        self.assertEqual(self.ticket.status, "em_progresso")
    
    def test_status_invalido(self):
        """Testa atualização com status inválido"""
        resultado = self.ticket.atualizar_status("status_inexistente")
        self.assertFalse(resultado)
    
    def test_adicionar_comentario(self):
        """Testa adição de comentários"""
        self.ticket.adicionar_comentario("Usuário Teste", "Primeiro comentário")
        self.assertEqual(len(self.ticket.comentarios), 1)
        self.assertEqual(self.ticket.comentarios[0]["autor"], "Usuário Teste")
    
    def test_atribuir_para(self):
        """Testa atribuição de ticket"""
        self.ticket.atribuir_para("Técnico A")
        self.assertEqual(self.ticket.atribuido_para, "Técnico A")
    
    def test_ticket_to_dict(self):
        """Testa conversão para dicionário"""
        ticket_dict = self.ticket.to_dict()
        self.assertEqual(ticket_dict["titulo"], "Teste de Ticket")
        self.assertEqual(ticket_dict["status"], TicketStatus.ABERTO.value)
        self.assertIn("id", ticket_dict)


class TestTicketManager(unittest.TestCase):
    """Testes para o TicketManager"""
    
    def setUp(self):
        """Prepara cada teste"""
        self.arquivo_teste = "tickets_teste.json"
        self.manager = TicketManager(self.arquivo_teste)
    
    def tearDown(self):
        """Limpa após cada teste"""
        if os.path.exists(self.arquivo_teste):
            os.remove(self.arquivo_teste)
    
    def test_criar_ticket(self):
        """Testa criação de um novo ticket"""
        ticket = self.manager.criar_ticket(
            titulo="Novo Ticket",
            descricao="Descrição do novo ticket",
            cliente="Cliente A",
            prioridade="alta"
        )
        self.assertIsNotNone(ticket.id)
        self.assertEqual(len(self.manager.tickets), 1)
    
    def test_obter_ticket(self):
        """Testa obtenção de ticket por ID"""
        ticket = self.manager.criar_ticket(
            titulo="Ticket para Busca",
            descricao="Test",
            cliente="Cliente B"
        )
        ticket_encontrado = self.manager.obter_ticket(ticket.id)
        self.assertIsNotNone(ticket_encontrado)
        self.assertEqual(ticket_encontrado.titulo, "Ticket para Busca")
    
    def test_listar_todos_tickets(self):
        """Testa listagem de todos os tickets"""
        self.manager.criar_ticket("Ticket 1", "Desc 1", "Cliente 1")
        self.manager.criar_ticket("Ticket 2", "Desc 2", "Cliente 2")
        self.manager.criar_ticket("Ticket 3", "Desc 3", "Cliente 1")
        
        todos = self.manager.listar_tickets()
        self.assertEqual(len(todos), 3)
    
    def test_listar_por_cliente(self):
        """Testa filtro por cliente"""
        self.manager.criar_ticket("Ticket 1", "Desc 1", "Cliente A")
        self.manager.criar_ticket("Ticket 2", "Desc 2", "Cliente B")
        self.manager.criar_ticket("Ticket 3", "Desc 3", "Cliente A")
        
        tickets_a = self.manager.listar_tickets(cliente="Cliente A")
        self.assertEqual(len(tickets_a), 2)
    
    def test_listar_por_status(self):
        """Testa filtro por status"""
        ticket1 = self.manager.criar_ticket("T1", "D1", "C1")
        ticket2 = self.manager.criar_ticket("T2", "D2", "C2")
        
        self.manager.atualizar_ticket(ticket1.id, status="resolvido")
        
        abertos = self.manager.listar_tickets(status="aberto")
        self.assertEqual(len(abertos), 1)
    
    def test_atualizar_ticket(self):
        """Testa atualização de ticket"""
        ticket = self.manager.criar_ticket("T", "D", "C")
        resultado = self.manager.atualizar_ticket(
            ticket.id,
            status="em_progresso",
            atribuido_para="Técnico X"
        )
        self.assertTrue(resultado)
        
        ticket_atualizado = self.manager.obter_ticket(ticket.id)
        self.assertEqual(ticket_atualizado.status, "em_progresso")
        self.assertEqual(ticket_atualizado.atribuido_para, "Técnico X")
    
    def test_fechar_ticket(self):
        """Testa fechamento de ticket"""
        ticket = self.manager.criar_ticket("T", "D", "C")
        resultado = self.manager.fechar_ticket(ticket.id, "Problema resolvido")
        
        self.assertTrue(resultado)
        ticket_fechado = self.manager.obter_ticket(ticket.id)
        self.assertEqual(ticket_fechado.status, "fechado")
    
    def test_salvar_e_carregar_tickets(self):
        """Testa persistência de dados"""
        ticket1 = self.manager.criar_ticket("T1", "D1", "C1", "alta")
        ticket1_id = ticket1.id
        
        # Cria novo manager que deve carregar os dados
        manager2 = TicketManager(self.arquivo_teste)
        ticket_carregado = manager2.obter_ticket(ticket1_id)
        
        self.assertIsNotNone(ticket_carregado)
        self.assertEqual(ticket_carregado.titulo, "T1")
        self.assertEqual(ticket_carregado.prioridade, "alta")


class TestTicketPriority(unittest.TestCase):
    """Testes para prioridades"""
    
    def test_prioridades_validas(self):
        """Verifica se todas as prioridades existem"""
        prioridades = [p.value for p in TicketPriority]
        self.assertIn("critica", prioridades)
        self.assertIn("alta", prioridades)
        self.assertIn("media", prioridades)
        self.assertIn("baixa", prioridades)


class TestTicketStatus(unittest.TestCase):
    """Testes para status de tickets"""
    
    def test_status_validos(self):
        """Verifica se todos os status existem"""
        status = [s.value for s in TicketStatus]
        self.assertIn("aberto", status)
        self.assertIn("em_progresso", status)
        self.assertIn("resolvido", status)
        self.assertIn("fechado", status)


if __name__ == "__main__":
    unittest.main()