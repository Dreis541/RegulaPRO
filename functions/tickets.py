"""
Sistema de Gerenciamento de Tickets - RegulaPRO
Módulo para criar, atualizar e gerenciar tickets de suporte
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class TicketStatus(Enum):
    """Estados possíveis de um ticket"""
    ABERTO = "aberto"
    EM_PROGRESSO = "em_progresso"
    AGUARDANDO_CLIENTE = "aguardando_cliente"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"


class TicketPriority(Enum):
    """Níveis de prioridade"""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Ticket:
    """Classe para representar um ticket de suporte"""
    
    def __init__(self, titulo: str, descricao: str, cliente: str, 
                 prioridade: str = "media"):
        self.id = str(uuid.uuid4())[:8]
        self.titulo = titulo
        self.descricao = descricao
        self.cliente = cliente
        self.prioridade = prioridade
        self.status = TicketStatus.ABERTO.value
        self.data_criacao = datetime.now().isoformat()
        self.data_atualizacao = datetime.now().isoformat()
        self.atribuido_para = None
        self.comentarios = []
    
    def atualizar_status(self, novo_status: str) -> bool:
        """Atualiza o status do ticket"""
        try:
            TicketStatus(novo_status)
            self.status = novo_status
            self.data_atualizacao = datetime.now().isoformat()
            return True
        except ValueError:
            return False
    
    def adicionar_comentario(self, autor: str, texto: str) -> None:
        """Adiciona um comentário ao ticket"""
        comentario = {
            "id": str(uuid.uuid4())[:8],
            "autor": autor,
            "texto": texto,
            "data": datetime.now().isoformat()
        }
        self.comentarios.append(comentario)
        self.data_atualizacao = datetime.now().isoformat()
    
    def atribuir_para(self, usuario: str) -> None:
        """Atribui o ticket para um usuário"""
        self.atribuido_para = usuario
        self.data_atualizacao = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Converte o ticket para dicionário"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "cliente": self.cliente,
            "prioridade": self.prioridade,
            "status": self.status,
            "data_criacao": self.data_criacao,
            "data_atualizacao": self.data_atualizacao,
            "atribuido_para": self.atribuido_para,
            "comentarios": self.comentarios
        }


class TicketManager:
    """Gerenciador central de tickets"""
    
    def __init__(self, arquivo_dados: str = "tickets.json"):
        self.arquivo_dados = arquivo_dados
        self.tickets: Dict[str, Ticket] = {}
        self.carregar_tickets()
    
    def criar_ticket(self, titulo: str, descricao: str, cliente: str,
                    prioridade: str = "media") -> Ticket:
        """Cria um novo ticket"""
        ticket = Ticket(titulo, descricao, cliente, prioridade)
        self.tickets[ticket.id] = ticket
        self.salvar_tickets()
        return ticket
    
    def obter_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Obtém um ticket pelo ID"""
        return self.tickets.get(ticket_id)
    
    def listar_tickets(self, status: Optional[str] = None,
                      cliente: Optional[str] = None) -> List[Ticket]:
        """Lista tickets com filtros opcionais"""
        resultados = list(self.tickets.values())
        
        if status:
            resultados = [t for t in resultados if t.status == status]
        
        if cliente:
            resultados = [t for t in resultados if t.cliente == cliente]
        
        return resultados
    
    def atualizar_ticket(self, ticket_id: str, **kwargs) -> bool:
        """Atualiza propriedades de um ticket"""
        ticket = self.obter_ticket(ticket_id)
        if not ticket:
            return False
        
        if "status" in kwargs:
            ticket.atualizar_status(kwargs["status"])
        if "prioridade" in kwargs:
            ticket.prioridade = kwargs["prioridade"]
        if "atribuido_para" in kwargs:
            ticket.atribuir_para(kwargs["atribuido_para"])
        
        self.salvar_tickets()
        return True
    
    def fechar_ticket(self, ticket_id: str, motivo: str = "") -> bool:
        """Fecha um ticket"""
        ticket = self.obter_ticket(ticket_id)
        if not ticket:
            return False
        
        ticket.atualizar_status(TicketStatus.FECHADO.value)
        if motivo:
            ticket.adicionar_comentario("sistema", f"Fechado: {motivo}")
        
        self.salvar_tickets()
        return True
    
    def salvar_tickets(self) -> None:
        """Salva tickets em arquivo JSON"""
        dados = {
            ticket_id: ticket.to_dict()
            for ticket_id, ticket in self.tickets.items()
        }
        with open(self.arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def carregar_tickets(self) -> None:
        """Carrega tickets do arquivo JSON"""
        try:
            with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for**
