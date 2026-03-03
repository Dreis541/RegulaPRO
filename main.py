import streamlit as st

# 1. CONFIGURAÇÃO (Sempre no topo)
st.set_page_config(page_title="RegulaPRO", layout="wide")

# 2. DESIGN CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stAppViewContainer"] { background-color: #0c111d !important; }
        .sidebar-title { font-size: 26px; font-weight: 700; color: #ffffff; padding: 20px 0px; }
        .green-pro { color: #00d084; }
        div[data-testid="stVerticalBlock"] > div:has(div.stButton) > button {
            width: 100%; background-color: #1a2333; color: white; border: none;
        }
    </style>
""", unsafe_allow_html=True)

# 3. BANCO DE DADOS E ESTADO DA SESSÃO
usuarios = {
    "admin": {"senha": "123", "tipo": "admin", "nome": "Administrador"},
    "cliente01": {"senha": "abc", "tipo": "cliente", "nome": "Farmacêutica XPTO"}
}

if 'logado' not in st.session_state:
    st.session_state.logado = False

# 4. TELA DE LOGIN
if not st.session_state.logado:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
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
            st.error("Usuário ou senha incorretos")
    st.stop()

# 5. SIDEBAR COM BOTÕES (Mais estável que links de URL)
with st.sidebar:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.nome}")
    st.markdown("---")
    
    # Navegação por botões (evita erro de URL)
    if st.button("📊 Dashboard"): st.session_state.pagina = "Dashboard"
    if st.button("📋 Processos"): st.session_state.pagina = "Processos"
    if st.button("📂 Documentos"): st.session_state.pagina = "Documentos"
    
    st.markdown("---")
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

# Define a página inicial se não houver nenhuma selecionada
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Dashboard"

# 6. CONTEÚDO DAS PÁGINAS
if st.session_state.pagina == "Dashboard":
    if st.session_state.tipo == "admin":
        st.title("Painel Administrativo")
        st.write("Visão Geral de todos os clientes")
        # Adicione aqui seus cards e tabelas de Admin
    else:
        st.title(f"Bem-vindo, {st.session_state.nome}")
        st.subheader("Resumo do seu Processo ANVISA")
        col1, col2 = st.columns(2)
        col1.metric("Status", "Em Análise 🟡")
        col2.metric("Prazo Previsto", "15/05/2026")

elif st.session_state.pagina == "Processos":
    st.title("📋 Meus Processos")
    st.write("Aqui aparecem os detalhes técnicos das petições.")
