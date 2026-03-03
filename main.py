import streamlit as st

# 1. CONFIGURAÇÃO (Primeira linha sempre)
st.set_page_config(page_title="RegulaPRO", layout="wide")

# 2. DESIGN CSS (Brilho total e cores mobile)
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
    </style>
""", unsafe_allow_html=True)

# 3. USUÁRIOS
usuarios = {
    "admin": {"senha": "123", "tipo": "admin", "nome": "Administrador"},
    "cliente01": {"senha": "abc", "tipo": "cliente", "nome": "Farmacêutica XPTO"}
}

# 4. SESSÃO
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Dashboard"

# 5. LOGIN
if not st.session_state.logado:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.subheader("Login de Acesso")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u in usuarios and usuarios[u]["senha"] == p:
            st.session_state.logado, st.session_state.user = True, u
            st.session_state.tipo, st.session_state.nome = usuarios[u]["tipo"], usuarios[u]["nome"]
            st.rerun()
        else: st.error("Usuário ou senha incorretos")
    st.stop()

# 6. SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)
    st.write(f"👤 **{st.session_state.nome}**")
    if st.button("📊 Dashboard"): st.session_state.pagina = "Dashboard"
    if st.button("📋 Processos"): st.session_state.pagina = "Processos"
    if st.button("📂 Documentos"): st.session_state.pagina = "Documentos"
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

# 7. PÁGINAS
if st.session_state.pagina == "Dashboard":
    st.title(f"Painel {st.session_state.tipo.capitalize()}")
    if st.session_state.tipo == "admin":
        c1, c2, c3 = st.columns(3)
        c1.metric("Clientes Ativos", "12")
        c2.metric("Petições ANVISA", "28")
        c3.metric("Vencimentos", "5")
        st.table({
            "Cliente": ["Farmacêutica XPTO", "Laboratório Alfa"],
            "Status": ["Em Análise", "Deferido"]
        })
    else:
        st.subheader("Status do seu Processo")
        st.progress(65)
        st.write("65% concluído - Aguardando parecer técnico.")

elif st.session_state.pagina == "Documentos":
    st.title("📂 Repositório de Documentos")
    
    if st.session_state.tipo == "cliente":
        st.subheader("Enviar novos documentos")
        arquivo_enviado = st.file_uploader("Selecione o arquivo", type=["pdf", "png", "jpg"])
        
        if arquivo_enviado:
            st.success(f"Arquivo '{arquivo_enviado.name}' recebido!")

        st.markdown("---")
        st.subheader("Seus Documentos para Download")
        
        # Simulação de um arquivo para o botão funcionar
        documento_exemplo = "Conteúdo do certificado gerado pelo RegulaPRO."
        
        # O BOTÃO REAL DE DOWNLOAD
        st.download_button(
            label="📄 Baixar Licença de Funcionamento (PDF)",
            data=documento_exemplo,
            file_name="licenca_anvisa_exemplo.pdf",
            mime="application/pdf"
        )
        
    else:
        st.subheader("Gestão de Documentos (Admin)")
        st.info("Aqui você poderá ver e baixar os arquivos enviados pelos clientes.")
        st.selectbox("Selecione o cliente para ver os arquivos:", ["Farmacêutica XPTO", "Laboratório Alfa"])
