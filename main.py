import streamlit as st
import uuid
from datetime import datetime

# Comentário para forçar o Replit a atualizar
# Configuração da Página
st.set_page_config(page_title="RegulaPRO", layout="wide")

# Estilo para o Menu Lateral
st.sidebar.title("🏢 RegulaPRO")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📑 Processos", "🛡️ Licenças", "📁 Documentos", "🎧 Suporte"]
)

# --- CONTEÚDO DAS PÁGINAS ---

if menu == "📊 Dashboard":
    st.title("Painel de Controle")
    st.info("Bem-vindo ao sistema de Gestão Regulatória da ANVISA.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Processos Ativos", "12")
    c2.metric("Vencimentos Próximos", "3")
    c3.metric("Documentos OK", "85%")

elif menu == "📑 Processos":
    st.title("Gestão de Processos")
    with st.expander("Cadastrar Novo Processo"):
        st.text_input("Número do Processo ANVISA")
        st.date_input("Data de Entrada")
        if st.button("Salvar Processo"):
            st.success("Processo registrado no sistema!")

elif menu == "🛡️ Licenças":
    st.title("Licenças e Alvarás")
    st.write("Controle de renovações e documentos legais.")

elif menu == "📁 Documentos":
    st.title("Repositório de Documentos")
    st.file_uploader("Upload de PDFs para análise da IA", type=["pdf"])

elif menu == "🎧 Suporte":
    st.title("Central de Suporte")
    with st.form("chamado"):
        email = st.text_input("Seu E-mail")
        duvida = st.text_area("Descrição da dúvida")
        if st.form_submit_button("Gerar Protocolo"):
            prot = f"REG-{uuid.uuid4().hex[:6].upper()}"
            st.success(f"Chamado aberto! Protocolo: {prot}")
