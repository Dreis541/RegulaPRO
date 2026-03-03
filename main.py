import streamlit as st

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="RegulaPRO", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stAppViewContainer"] { background-color: #0c111d !important; }
        .sidebar-title { font-size: 26px; font-weight: 700; color: #ffffff; padding: 20px 0px; }
        .green-pro { color: #00d084; }
        .nav-link { display: flex; align-items: center; padding: 12px 15px; border-radius: 8px; 
                    text-decoration: none; color: #ffffff !important; margin-bottom: 5px; }
        .active { background-color: #1a2333; color: #00d084 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS DE USUÁRIOS (Simulado)
# Amanhã podemos levar isso para um arquivo externo
usuarios = {
    "admin": {"senha": "123", "tipo": "admin", "nome": "Administrador"},
    "cliente01": {"senha": "abc", "tipo": "cliente", "nome": "Farmacêutica XPTO", "processo": "25351.0001/2024-10"}
}

# 3. LÓGICA DE LOGIN
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    with st.container():
        st.subheader("Login de Acesso")
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user_input in usuarios and usuarios[user_input]["senha"] == pass_input:
                st.session_state.logado = True
                st.session_state.user = user_input
                st.session_state.tipo = usuarios[user_input]["tipo"]
                st.session_state.nome = usuarios[user_input]["nome"]
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    st.stop()

# 4. SIDEBAR E NAVEGAÇÃO
with st.sidebar:
    st.markdown(f'<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.nome}")
    
    query_params = st.query_params
    pagina = query_params.get("p", "Dashboard")

    st.markdown(f"""
        <a href="?p=Dashboard" class="nav-link {'active' if pagina == 'Dashboard' else ''}" target="_self">📊 Dashboard</a>
        <a href="?p=Processos" class="nav-link {'active' if pagina == 'Processos' else ''}" target="_self">📋 Processos</a>
        <a href="?p=Documentos" class="nav-link {'active' if pagina == 'Documentos' else ''}" target="_self">📂 Documentos</a>
    """, unsafe_allow_html=True)
    
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# 5. CONTEÚDO DAS PÁGINAS (ADMIN vs CLIENTE)
if pagina == "Dashboard":
    if st.session_state.tipo == "admin":
        st.title("Painel Administrativo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Clientes Totais", "45")
        col2.metric("Processos em Alerta", "7", delta="-2")
        col3.metric("Faturamento Mensal", "R$ 12k")
    else:
        # VISÃO DO CLIENTE
        st.title(f"Olá, {st.session_state.nome}")
        st.info(f"Acompanhamento do Processo: {usuarios[st.session_state.user]['processo']}")
        
        # Resumo do Cliente
        c1, c2, c3 = st.columns(3)
        c1.metric("Status Atual", "Em Análise 🟡")
        c2.metric("Prazo de Resposta", "12/04/2024")
        c3.metric("Pendências", "0")

        st.markdown("---")
        st.subheader("Linha do Tempo do Processo")
        st.write("✅ Protocolo Realizado (01/03)")
        st.write("🟡 Aguardando Triagem Técnica")

elif pagina == "Processos":
    st.title("Gerenciamento de Processos")
    if st.session_state.tipo == "admin":
        st.write("Aqui você cadastra e edita processos de todos os clientes.")
        # Espaço para formulário de cadastro
    else:
        st.write("Detalhamento técnico das suas petições na ANVISA.")
