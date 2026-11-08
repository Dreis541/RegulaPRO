"""Página de chamados de suporte do RegulaPRO.

Clientes abrem e acompanham só os próprios chamados.
Administradores veem todos e podem atualizar status, técnico e comentários.
"""

import streamlit as st

from functions.tickets import TicketManager

STATUS = ["aberto", "em_progresso", "aguardando_cliente", "resolvido", "fechado"]
PRIORIDADES = ["baixa", "media", "alta", "critica"]


def _manager() -> TicketManager:
    if "ticket_manager" not in st.session_state:
        st.session_state.ticket_manager = TicketManager()
    return st.session_state.ticket_manager


def _criar(manager: TicketManager, eh_admin: bool) -> None:
    st.subheader("🆕 Abrir novo chamado")
    with st.form("form_novo_ticket", clear_on_submit=True):
        titulo = st.text_input("Título")
        descricao = st.text_area("Descrição detalhada")
        if eh_admin:
            cliente = st.text_input("Nome do cliente")
        else:
            cliente = st.session_state.nome
            st.caption(f"Cliente: **{cliente}**")
        prioridade = st.selectbox("Prioridade", PRIORIDADES, index=1)
        if st.form_submit_button("📤 Abrir chamado"):
            if titulo and descricao and cliente:
                ticket = manager.criar_ticket(titulo=titulo, descricao=descricao, cliente=cliente, prioridade=prioridade)
                st.success(f"✅ Chamado aberto com o código {ticket.id}")
            else:
                st.error("❌ Preencha todos os campos!")


def _listar(manager: TicketManager, eh_admin: bool) -> None:
    st.subheader("📋 Chamados")
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox("Status", ["Todos"] + STATUS)
    with col2:
        filtro_cliente = st.text_input("Cliente") if eh_admin else st.session_state.nome

    tickets = manager.listar_tickets(
        status=None if filtro_status == "Todos" else filtro_status,
        cliente=filtro_cliente or None,
    )
    if not tickets:
        st.info("ℹ️ Nenhum chamado encontrado.")
        return

    for ticket in sorted(tickets, key=lambda t: t.data_criacao, reverse=True):
        with st.expander(f"🎫 {ticket.id} - {ticket.titulo}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", ticket.status.upper())
            c2.metric("Prioridade", ticket.prioridade.upper())
            c3.metric("Cliente", ticket.cliente)
            st.write(f"**Descrição:** {ticket.descricao}")
            st.write(f"**Aberto em:** {ticket.data_criacao[:16].replace('T', ' ')}")
            if ticket.atribuido_para:
                st.write(f"**Técnico:** {ticket.atribuido_para}")
            for comentario in ticket.comentarios:
                st.write(f"**{comentario['autor']}** ({comentario['data'][:16].replace('T', ' ')}): {comentario['texto']}")


def _gerenciar(manager: TicketManager) -> None:
    st.subheader("⚙️ Gerenciar chamado")
    ticket_id = st.text_input("Código do chamado")
    if not ticket_id:
        return
    ticket = manager.obter_ticket(ticket_id.strip())
    if not ticket:
        st.error("❌ Chamado não encontrado!")
        return

    st.success(f"✅ {ticket.titulo} — {ticket.cliente}")
    col1, col2 = st.columns(2)
    with col1:
        indice = STATUS.index(ticket.status) if ticket.status in STATUS else 0
        novo_status = st.selectbox("Novo status", STATUS, index=indice)
    with col2:
        novo_tecnico = st.text_input("Técnico responsável", value=ticket.atribuido_para or "")
    if st.button("💾 Atualizar chamado"):
        manager.atualizar_ticket(ticket.id, status=novo_status, atribuido_para=novo_tecnico or ticket.atribuido_para)
        st.success("✅ Chamado atualizado!")

    with st.form(f"form_comentario_{ticket.id}", clear_on_submit=True):
        comentario = st.text_area("Adicionar comentário")
        if st.form_submit_button("📝 Comentar"):
            if comentario:
                ticket.adicionar_comentario(st.session_state.nome, comentario)
                manager.salvar_tickets()
                st.success("✅ Comentário adicionado!")
            else:
                st.error("❌ Escreva o comentário.")


def main() -> None:
    """Renderiza a página de chamados."""
    st.title("🎫 Chamados de suporte")
    manager = _manager()
    eh_admin = st.session_state.get("tipo") == "admin"

    opcoes = ["Abrir chamado", "Meus chamados"] if not eh_admin else ["Abrir chamado", "Todos os chamados", "Gerenciar"]
    aba = st.radio("Opção", opcoes, horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if aba == "Abrir chamado":
        _criar(manager, eh_admin)
    elif aba == "Gerenciar" and eh_admin:
        _gerenciar(manager)
    else:
        _listar(manager, eh_admin)
