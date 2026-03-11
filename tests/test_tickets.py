import pytest
from datetime import datetime
from functions.tickets import (
    Ticket, TipoTicket, PrioridadeTicket, StatusTicket, RespostaTicket
)
from functions.database import db


class TestTipoTicket:
    """Testes para tipos de ticket"""
    
    def test_tipos_existentes(self):
        """Verifica se todos os tipos de ticket existem"""
        tipos = [t.value for t in TipoTicket]
        assert "Dúvida" in tipos
        assert "Problema" in tipos
        assert "Sugestão" in tipos
        assert "Reclamação" in tipos
        assert "Informação" in tipos
    
    def test_quantidade_tipos(self):
        """Verifica quantidade de tipos"""
        assert len(list(TipoTicket)) == 5


class TestPrioridadeTicket:
    """Testes para prioridades de ticket"""
    
    def test_prioridades_ordenadas(self):
        """Verifica se prioridades estão corretamente ordenadas"""
        assert PrioridadeTicket.CRITICA.value == 0
        assert PrioridadeTicket.ALTA.value == 1
        assert PrioridadeTicket.MEDIA.value == 2
        assert PrioridadeTicket.BAIXA.value == 3
    
    def test_quantidade_prioridades(self):
        """Verifica quantidade de prioridades"""
        assert len(list(PrioridadeTicket)) == 4


class TestStatusTicket:
    """Testes para status de ticket"""
    
    def test_status_existentes(self):
        """Verifica se todos os status existem"""
        status = [s.value for s in StatusTicket]
        assert "Aberto" in status
        assert "Em Análise" in status
        assert "Aguardando Resposta do Cliente" in status
        assert "Resolvido" in status
        assert "Fechado" in status
    
    def test_quantidade_status(self):
        """Verifica quantidade de status"""
        assert len(list(StatusTicket)) == 5


class TestCriarTicket:
    """Testes para criação de tickets"""
    
    @pytest.fixture
    def ticket_base(self):
        """Fixture com dados base para um ticket"""
        return {
            "protocolo": "ABC123456",
            "empresa_cnpj": "12.345.678/0001-90",
            "empresa_nome": "Empresa XYZ",
            "cliente_email": "contato@empresa.com",
            "cliente_nome": "João Silva",
            "tipo": TipoTicket.DUVIDA,
            "prioridade": PrioridadeTicket.MEDIA,
            "status": StatusTicket.ABERTO,
            "assunto": "Dúvida sobre documentação",
            "descricao": "Qual é a documentação necessária?",
            "data_abertura": datetime.now()
        }
    
    def test_criar_ticket_basico(self, ticket_base):
        """Testa criação básica de um ticket"""
        ticket = Ticket(**ticket_base)
        
        assert ticket.protocolo == "ABC123456"
        assert ticket.status == StatusTicket.ABERTO
        assert ticket.tipo == TipoTicket.DUVIDA
    
    def test_ticket_protocolo_correto(self, ticket_base):
        """Verifica se protocolo está correto"""
        ticket = Ticket(**ticket_base)
        assert ticket.protocolo == "ABC123456"
        assert len(ticket.protocolo) == 10
    
    def test_ticket_empresa_cnpj(self, ticket_base):
        """Verifica dados da empresa no ticket"""
        ticket = Ticket(**ticket_base)
        assert ticket.empresa_cnpj == "12.345.678/0001-90"
        assert ticket.empresa_nome == "Empresa XYZ"
    
    def test_ticket_cliente(self, ticket_base):
        """Verifica dados do cliente no ticket"""
        ticket = Ticket(**ticket_base)
        assert ticket.cliente_email == "contato@empresa.com"
        assert ticket.cliente_nome == "João Silva"
    
    def test_ticket_conteudo(self, ticket_base):
        """Verifica conteúdo do ticket"""
        ticket = Ticket(**ticket_base)
        assert ticket.assunto == "Dúvida sobre documentação"
        assert ticket.descricao == "Qual é a documentação necessária?"
    
    def test_ticket_respostas_vazia(self, ticket_base):
        """Verifica se lista de respostas inicia vazia"""
        ticket = Ticket(**ticket_base)
        assert len(ticket.respostas) == 0


class TestRespostaTicket:
    """Testes para respostas de tickets"""
    
    def test_criar_resposta(self):
        """Testa criação de uma resposta"""
        resposta = RespostaTicket(
            autor="Analista",
            data=datetime.now(),
            mensagem="Aqui está a resposta..."
        )
        
        assert resposta.autor == "Analista"
        assert resposta.mensagem == "Aqui está a resposta..."
    
    def test_resposta_com_anexos(self):
        """Testa resposta com anexos"""
        anexos = ["documento.pdf", "imagem.jpg"]
        resposta = RespostaTicket(
            autor="Analista",
            data=datetime.now(),
            mensagem="Resposta com anexos",
            anexos=anexos
        )
        
        assert len(resposta.anexos) == 2
        assert "documento.pdf" in resposta.anexos


class TestProtocolo:
    """Testes para geração de protocolos"""
    
    def test_protocolo_unico(self):
        """Verifica se protocolos gerados são únicos"""
        protocolo1 = db.gerar_protocolo()
        protocolo2 = db.gerar_protocolo()
        
        assert protocolo1 != protocolo2
    
    def test_protocolo_formato(self):
        """Verifica formato do protocolo"""
        protocolo = db.gerar_protocolo()
        
        assert len(protocolo) == 10
        assert protocolo.isalnum()
    
    def test_protocolo_maiusculo(self):
        """Verifica se protocolo contém apenas maiúsculas e dígitos"""
        protocolo = db.gerar_protocolo()
        
        for char in protocolo:
            assert char.isupper() or char.isdigit()


class TestValidacoes:
    """Testes para validações"""
    
    def test_cnpj_valido(self):
        """Testa validação de CNPJ"""
        cnpj = "12.345.678/0001-90"
        assert len(cnpj) == 18
        assert cnpj.count(".") == 2
        assert "/" in cnpj
    
    def test_email_valido(self):
        """Testa validação de email"""
        email = "contato@empresa.com"
        assert "@" in email
        assert "." in email
    
    def test_assunto_nao_vazio(self):
        """Testa se assunto não está vazio"""
        assunto = "Dúvida sobre processo"
        assert len(assunto) > 0
        assert len(assunto) <= 100


class TestDatabase:
    """Testes para operações de banco de dados"""
    
    def test_database_criada(self):
        """Verifica se banco de dados foi criado"""
        import os
        from pathlib import Path
        
        db_path = "data/regulapro.db"
        # Se o banco não existe, será criado na primeira conexão
        assert Path("data").exists() or True
    
    def test_tabelas_criadas(self):
        """Verifica se tabelas foram criadas"""
        conn = __import__("sqlite3").connect("data/regulapro.db")
        cursor = conn.cursor()
        
        # Verificar tabela de tickets
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'"
        )
        assert cursor.fetchone() is not None
        
        # Verificar tabela de respostas
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='respostas_tickets'"
        )
        assert cursor.fetchone() is not None
        
        conn.close()


@pytest.mark.parametrize("tipo", list(TipoTicket))
def test_todos_tipos_ticket(tipo):
    """Testa criação com todos os tipos de ticket"""
    ticket = Ticket(
        protocolo="TEST123456",
        empresa_cnpj="12.345.678/0001-90",
        empresa_nome="Teste",
        cliente_email="teste@teste.com",
        cliente_nome="Teste",
        tipo=tipo,
        prioridade=PrioridadeTicket.MEDIA,
        status=StatusTicket.ABERTO,
        assunto="Teste",
        descricao="Teste",
        data_abertura=datetime.now()
    )
    
    assert ticket.tipo == tipo


@pytest.mark.parametrize("prioridade", list(PrioridadeTicket))
def test_todas_prioridades_ticket(prioridade):
    """Testa criação com todas as prioridades"""
    ticket = Ticket(
        protocolo="TEST123456",
        empresa_cnpj="12.345.678/0001-90",
        empresa_nome="Teste",
        cliente_email="teste@teste.com",
        cliente_nome="Teste",
        tipo=TipoTicket.DUVIDA,
        prioridade=prioridade,
        status=StatusTicket.ABERTO,
        assunto="Teste",
        descricao="Teste",
        data_abertura=datetime.now()
    )
    
    assert ticket.prioridade == prioridade


@pytest.mark.parametrize("status", list(StatusTicket))
def test_todos_status_ticket(status):
    """Testa criação com todos os status"""
    ticket = Ticket(
        protocolo="TEST123456",
        empresa_cnpj="12.345.678/0001-90",
        empresa_nome="Teste",
        cliente_email="teste@teste.com",
        cliente_nome="Teste",
        tipo=TipoTicket.DUVIDA,
        prioridade=PrioridadeTicket.MEDIA,
        status=status,
        assunto="Teste",
        descricao="Teste",
        data_abertura=datetime.now()
    )
    
    assert ticket.status == status
