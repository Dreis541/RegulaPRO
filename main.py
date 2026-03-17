import sys
import os

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config import APP_TITLE, APP_ICON, LAYOUT, USUARIOS

# 1. CONFIGURAÇÃO (Primeira linha sempre)
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout=LAYOUT)

# 2. DESIGN CSS
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { background-color: #0c111d !important; }
        html, body, [class*="css"], .stMarkdown, p, span, label, .stMetric { color: #ffffff !important; }
        h1, h2, h3 { color: #ffffff !important; font-weight: 700 !important; }
        [data-testid="stMetricValue"] { color: #00d084 !important; font-size: 32px !important; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 16px !important; opacity: 0.9; }
        .stButton > button {
            width: 100%; background-color: #1a2333 !important; color: #ffffff !important;
            border: 1px solid #303746 !important; border-radius: 8px; padding: 10px;
        }
        .stButton > button:hover { border-color: #00d084 !important; color: #00d084 !important; }
        .sidebar-title { font-size: 28px; font-weight: 800; color: #ffffff !important; margin-bottom: 20px; }
        .green-pro { color: #00d084 !important; }
        .stProgress > div > div { background-color: #00d084 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. SESSÃO
if "logado" not in st.session_state:
    st.session_state.logado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

# 4. LOGIN
if not st.session_state.logado:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.subheader("Login de Acesso")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["senha"] == p:
            st.session_state.logado = True
            st.session_state.user = u
            st.session_state.tipo = USUARIOS[u]["tipo"]
            st.session_state.nome = USUARIOS[u]["nome"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# 5. SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.write(f"👤 **{st.session_state.nome}**")
    st.markdown("---")
    if st.button("🏠 Home"):
        st.session_state.pagina = "Home"
    if st.button("📊 Dashboard"):
        st.session_state.pagina = "Dashboard"
    if st.button("📋 Processos"):
        st.session_state.pagina = "Processos"
    if st.button("📈 Acompanhamento"):
        st.session_state.pagina = "Acompanhamento"
    if st.button("📊 Relatórios"):
        st.session_state.pagina = "Relatorios"
    if st.button("📂 Documentos"):
        st.session_state.pagina = "Documentos"
    st.markdown("---")
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

# 6. PÁGINAS
pagina = st.session_state.pagina

if pagina in ("Home", "Dashboard"):
    from pages import home
    home.main()

elif pagina == "Processos":
    from pages import processos as pg_processos
    pg_processos.main()

elif pagina == "Acompanhamento":
    from pages import acompanhamento
    acompanhamento.main()

elif pagina == "Relatorios":
    from pages import relatorios
    relatorios.main()

elif pagina == "Documentos":
    st.title("📂 Repositório de Documentos")

    if st.session_state.tipo == "cliente":
        st.subheader("Enviar novos documentos")
        arquivo_enviado = st.file_uploader("Selecione o arquivo", type=["pdf", "png", "jpg"])
        if arquivo_enviado:
            st.success(f"Arquivo '{arquivo_enviado.name}' recebido!")
        st.markdown("---")
        st.subheader("Seus Documentos para Download")
        documento_exemplo = "Conteúdo do certificado gerado pelo RegulaPRO."
        st.download_button(
            label="📄 Baixar Licença de Funcionamento (PDF)",
            data=documento_exemplo,
            file_name="licenca_anvisa_exemplo.pdf",
            mime="application/pdf",
        )
    else:
        st.subheader("Gestão de Documentos (Admin)")
        st.info("Aqui você poderá ver e baixar os arquivos enviados pelos clientes.")
        st.selectbox("Selecione o cliente para ver os arquivos:", ["Farmacêutica XPTO", "Laboratório Alfa"])



# ===== MÓDULO DE TICKETS =====
# Importar o sistema de tickets
from functions.tickets import TicketManager, TicketStatus

# Inicializar o gerenciador de tickets
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

# ===== SEÇÃO DE TICKETS =====
st.sidebar.markdown("---")
st.sidebar.header("🎫 Sistema de Tickets")

ticket_menu = st.sidebar.radio(
    "Escolha uma opção:",
    ["Criar Ticket", "Visualizar Tickets", "Gerenciar Tickets"]
)

if ticket_menu == "Criar Ticket":
    st.header("🆕 Criar Novo Ticket")
    
    with st.form("form_novo_ticket"):
        titulo = st.text_input("Título do Ticket")
        descricao = st.text_area("Descrição detalhada")
        cliente = st.text_input("Nome do Cliente")
        prioridade = st.selectbox(
            "Prioridade",
            ["baixa", "media", "alta", "critica"]
        )
        
        if st.form_submit_button("📤 Criar Ticket"):
            if titulo and descricao and cliente:
                ticket = st.session_state.ticket_manager.criar_ticket(
                    titulo=titulo,
                    descricao=descricao,
                    cliente=cliente,
                    prioridade=prioridade
                )
                st.success(f"✅ Ticket criado com ID: {ticket.id}")
            else:
                st.error("❌ Preencha todos os campos!")

elif ticket_menu == "Visualizar Tickets":
    st.header("📋 Visualizar Tickets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_status = st.selectbox(
            "Filtrar por Status",
            ["Todos", "aberto", "em_progresso", "resolvido", "fechado"]
        )
    
    with col2:
        filtro_cliente = st.text_input("Filtrar por Cliente")
    
    # Aplicar filtros
    status_filter = None if filtro_status == "Todos" else filtro_status
    cliente_filter = filtro_cliente if filtro_cliente else None
    
    tickets = st.session_state.ticket_manager.listar_tickets(
        status=status_filter,
        cliente=cliente_filter
    )
    
    if tickets:
        for ticket in tickets:
            with st.expander(f"🎫 {ticket.id} - {ticket.titulo}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Status", ticket.status.upper())
                with col2:
                    st.metric("Prioridade", ticket.prioridade.upper())
                with col3:
                    st.metric("Cliente", ticket.cliente)
                
                st.write(f"**Descrição:** {ticket.descricao}")
                st.write(f"**Criado em:** {ticket.data_criacao}")
                
                if ticket.atribuido_para:
                    st.write(f"**Atribuído para:** {ticket.atribuido_para}")
                
                if ticket.comentarios:
                    st.subheader("Comentários")
                    for comentario in ticket.comentarios:
                        st.write(f"**{comentario['autor']}** ({comentario['data']})")
                        st.write(comentario['texto'])
    else:
        st.info("ℹ️ Nenhum ticket encontrado com os filtros aplicados.")

elif ticket_menu == "Gerenciar Tickets":
    st.header("⚙️ Gerenciar Tickets")
    
    ticket_id = st.text_input("ID do Ticket para gerenciar")
    
    if ticket_id:
        ticket = st.session_state.ticket_manager.obter_ticket(ticket_id)
        
        if ticket:
            st.success(f"✅ Ticket encontrado: {ticket.titulo}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                novo_status = st.selectbox(
                    "Novo Status",
                    ["aberto", "em_progresso", "aguardando_cliente", "resolvido", "fechado"],
                    index=0
                )
            
            with col2:
                novo_tecnico = st.text_input("Atribuir para (Técnico)")
            
            if st.button("💾 Atualizar Ticket"):
                st.session_state.ticket_manager.atualizar_ticket(
                    ticket_id,
                    status=novo_status,
                    atribuido_para=novo_tecnico if novo_tecnico else ticket.atribuido_para
                )
                st.success("✅ Ticket atualizado!")
            
            # Adicionar comentário
            st.subheader("💬 Adicionar Comentário")
            with st.form(f"form_comentario_{ticket_id}"):
                autor = st.text_input("Seu nome")
                comentario = st.text_area("Comentário")
                
                if st.form_submit_button("📝 Adicionar Comentário"):
                    if autor and comentario:
                        ticket.adicionar_comentario(autor, comentario)
                        st.session_state.ticket_manager.salvar_tickets()
                        st.success("✅ Comentário adicionado!")
                    else:
                        st.error("❌ Preencha todos os campos!")
        else:
            st.error("❌ Ticket não encontrado!")