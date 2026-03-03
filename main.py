import streamlit as st

# 1. CONFIGURAÇÃO INICIAL (Sempre a primeira linha)
st.set_page_config(page_title="RegulaPRO", layout="wide")

# 2. DESIGN E CORES (CSS INTEGRADO)
st.markdown("""
    <style>
        /* Fundo principal e da Sidebar */
        [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            background-color: #0c111d !important;
        }

        /* Texto Global: Força o branco puro para não ficar apagado */
        html, body, [class*="css"], .stMarkdown, p, span, label, .stMetric {
            color: #ffffff !important;
        }

        /* Títulos */
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        /* Estilo das Métricas (Números grandes) */
        [data-testid="stMetricValue"] {
            color: #00d084 !important; /* Números em verde neon para destaque */
            font-size: 32px !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-size: 16px !important;
            opacity: 0.9;
        }

        /* Botões do Menu Lateral */
        .stButton > button {
            width: 100%;
            background-color: #1a2333 !important;
            color: #ffffff !important;
            border: 1px solid #303746 !important;
            border-radius: 8px;
            padding: 10px;
            transition: 0.3s;
        }
        
        .stButton > button:hover {
            border-color: #00d084 !important;
            color: #00d084 !important;
            background-color: #0c111d !important;
        }

        /* Título RegulaPro na Sidebar */
        .sidebar-title {
            font-size: 28px;
            font-weight: 800;
            color: #ffffff !important;
            margin-bottom: 20px;
        }
        .green-pro { color: #00d084 !important; }

        /* Esconder elementos desnecessários do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. BANCO DE DADOS DE USUÁRIOS
usuarios = {
    "admin": {"senha": "123", "tipo": "admin", "nome": "Administrador"},
    "cliente01": {"senha": "abc", "tipo": "cliente", "nome": "Farmacêutica XPTO"}
}

# 4. CONTROLE DE SESSÃO
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Dashboard"

# 5. TELA DE LOGIN
if not st.session_state.logado:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.subheader("Login de Acesso")
    
    with st.container():
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

# 6. SIDEBAR (MENU DE NAVEGAÇÃO)
with st.sidebar:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.write(f"👤 Bem-vindo, **{st.session_state.nome}**")
    st.markdown("---")
    
    if st.button("📊 Dashboard"): st.session_state.pagina = "Dashboard"
    if st.button("📋 Processos"): st.session_state.pagina = "Processos"
    if st.button("📂 Documentos"): st.session_state.pagina = "Documentos"
    
    st.markdown("---")
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

# 7. CONTEÚDO DAS PÁGINAS
if st.session_state.pagina == "Dashboard":
    st.title(f"📊 Painel {st.session_state.tipo.capitalize()}")
    
    if st.session_state.tipo == "admin":
        # VISÃO DO ADMINISTRADOR (VOCÊ)
        c1, c2, c3 = st.columns(3)
        c1.metric("Clientes Ativos", "12")
        c2.metric("Petições ANVISA", "28", delta="3")
        c3.metric("Vencimentos/30 dias", "5")
        
        st.subheader("Últimas Atualizações de Clientes")
        st.table({
            "Cliente": ["Farmacêutica XPTO", "Laboratório Alfa", "MedTech"],
            "Processo": ["25351.0001/24", "25351.0042/24", "25351.0099/24"],
            "Status": ["Em Análise", "Deferido
