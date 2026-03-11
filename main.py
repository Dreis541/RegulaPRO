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
