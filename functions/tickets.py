"""
Sistema de Gerenciamento de Tickets - RegulaPRO
Módulo para criar, atualizar e gerenciar tickets de suporte
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def _agora_iso() -> str:
    """Data e hora atuais no fuso de Brasília (sem o sufixo de fuso)."""
    return datetime.now(FUSO).replace(tzinfo=None).isoformat()


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
        self.data_criacao = _agora_iso()
        self.data_atualizacao = _agora_iso()
        self.atribuido_para = None
        self.comentarios = []
    
    def atualizar_status(self, novo_status: str) -> bool:
        """Atualiza o status do ticket"""
        try:
            TicketStatus(novo_status)
            self.status = novo_status
            self.data_atualizacao = _agora_iso()
            return True
        except ValueError:
            return False
    
    def adicionar_comentario(self, autor: str, texto: str) -> None:
        """Adiciona um comentário ao ticket"""
        comentario = {
            "id": str(uuid.uuid4())[:8],
            "autor": autor,
            "texto": texto,
            "data": _agora_iso()
        }
        self.comentarios.append(comentario)
        self.data_atualizacao = _agora_iso()
    
    def atribuir_para(self, usuario: str) -> None:
        """Atribui o ticket para um usuário"""
        self.atribuido_para = usuario
        self.data_atualizacao = _agora_iso()
    
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


_COLUNAS = ("id", "titulo", "descricao", "cliente", "prioridade", "status",
            "data_criacao", "data_atualizacao", "atribuido_para", "comentarios")


def _ticket_de_dict(ticket_id: str, info: Dict) -> "Ticket":
    """Monta um Ticket a partir dos dados salvos (arquivo ou banco)."""
    ticket = Ticket(
        info.get("titulo", ""),
        info.get("descricao", ""),
        info.get("cliente", ""),
        info.get("prioridade", "media"),
    )
    ticket.id = info.get("id") or ticket_id
    ticket.status = info.get("status") or ticket.status
    ticket.data_criacao = info.get("data_criacao") or ticket.data_criacao
    ticket.data_atualizacao = info.get("data_atualizacao") or ticket.data_atualizacao
    ticket.atribuido_para = info.get("atribuido_para")
    comentarios = info.get("comentarios") or []
    ticket.comentarios = json.loads(comentarios) if isinstance(comentarios, str) else comentarios
    return ticket


class TicketManager:
    """Gerenciador central de tickets.

    Sem argumento, guarda os chamados no banco do sistema (Supabase em produção,
    SQLite local). Com `arquivo_dados`, usa um arquivo JSON (útil em testes).
    """

    def __init__(self, arquivo_dados: Optional[str] = None):
        self.arquivo_dados = arquivo_dados
        self.tickets: Dict[str, Ticket] = {}
        self.carregar_tickets()

    @property
    def usa_banco(self) -> bool:
        return self.arquivo_dados is None
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
        """Grava todos os tickets no banco ou no arquivo JSON."""
        if self.usa_banco:
            from functions.database import executar_varios, inicializar_banco

            inicializar_banco()
            linhas = []
            for ticket in self.tickets.values():
                d = ticket.to_dict()
                d["comentarios"] = json.dumps(d.get("comentarios", []), ensure_ascii=False)
                linhas.append(tuple(d.get(c) for c in _COLUNAS))
            atualizar = ", ".join(f"{c} = excluded.{c}" for c in _COLUNAS[1:])
            executar_varios(
                f"INSERT INTO tickets ({', '.join(_COLUNAS)}) "
                f"VALUES ({', '.join('?' for _ in _COLUNAS)}) "
                f"ON CONFLICT (id) DO UPDATE SET {atualizar}",
                linhas,
            )
            return

        dados = {ticket_id: ticket.to_dict() for ticket_id, ticket in self.tickets.items()}
        pasta = os.path.dirname(self.arquivo_dados)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(self.arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def carregar_tickets(self) -> None:
        """Carrega os tickets do banco ou do arquivo JSON."""
        if self.usa_banco:
            from functions.database import executar_query, inicializar_banco

            inicializar_banco()
            linhas = executar_query("SELECT * FROM tickets")
            self.tickets = {linha["id"]: _ticket_de_dict(linha["id"], linha) for linha in linhas}
            return

        try:
            with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tickets = {}
            return
        self.tickets = {tid: _ticket_de_dict(tid, info) for tid, info in dados.items()}
