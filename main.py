import streamlit as st
import uuid
from datetime import datetime

import streamlit as st

# --- INÍCIO DA CUSTOMIZAÇÃO DO FRONTEND ---

# Função para injetar CSS customizado e alcançar o visual da imagem móbile
def layout_customizado_regulapro():
    st.markdown("""
        <style>
            /* --- Customização Geral e Cores de Fundo --- */
            [data-testid="stSidebar"] {
                background-color: #0c111d !important; /* Fundo azul escuro profundo da sidebar */
                color: #ffffff !important;           /* Texto branco para contraste */
            }
            [data-testid="stSidebar"] * {
                color: #ffffff !important;           /* Garante que todo texto interno seja branco */
            }
            [data-testid="stAppViewContainer"] {
                background-color: #0c111d !important; /* Mantém o fundo escuro consistente no app */
            }

            /* --- Título da Sidebar "RegulaPro" --- */
            .sidebar-title {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff !important;           /* Texto branco */
                padding: 10px 0px 20px 0px;
                text-align: left;
            }
            .sidebar-title .green-pro {
                color: #00d084 !important;           /* Verde vibrante para o "Pro" */
            }

            /* --- Itens de Navegação (Menu) --- */
            .nav-item {
                display: flex;
                align-items: center;
                padding: 12px 15px;
                margin-bottom: 5px;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.2s;
                text-decoration: none !important;
            }
            /* Efeito hover nos itens de navegação */
            .nav-item:hover {
                background-color: #1a2333;           /* Fundo ligeiramente mais claro no hover */
            }
            /* Ícones SVG customizados e alinhados */
            .nav-item-icon {
                margin-right: 12px;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .nav-item-label {
                font-size: 16px;
                font-weight: 400;
                color: #ffffff !important;           /* Texto branco para os rótulos */
            }

            /* --- Customização Específica do Item Ativo "Dashboard" --- */
            .active-nav-item {
                background-color: #1a2333 !important; /* Fundo de item ativo */
            }
            /* Texto e ícone do item ativo ficam verdes */
            .active-nav-item .nav-item-label {
                color: #00d084 !important;           /* Verde vibrante */
                font-weight: 500;
            }
            .active-nav-item .nav-item-icon svg {
                fill: #00d084 !important;            /* Ícone verde preenchido */
            }

            /* --- Customização do Botão "Sair" --- */
            .logout-container {
                position: absolute;
                bottom: 20px;
                left: 15px;
                right: 15px;
                border-top: 1px solid #1a2333;      /* Linha divisória fina */
                padding-top: 15px;
            }
            .logout-item {
                display: flex;
                align-items: center;
                padding: 12px 15px;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.2s;
                text-decoration: none !important;
            }
            .logout-item:hover {
                background-color: rgba(255, 255, 255, 0.05); /* Efeito hover suave */
            }
            .logout-item-icon {
                margin-right: 12px;
                width: 20px;
                height: 20px;
                fill: #ffffff !important;            /* Ícone branco */
            }
            .logout-item-label {
                font-size: 16px;
                font-weight: 400;
                color: #ffffff !important;           /* Texto branco */
            }

        </style>
    """, unsafe_allow_html=True)

# Aplica a customização de layout
layout_customizado_regulapro()

# --- FIM DA CUSTOMIZAÇÃO DO FRONTEND ---

# --- ESTRUTURA DE NAVEGAÇÃO DA SIDEBAR ---

# Título da Sidebar
st.sidebar.markdown('<div class="sidebar-title">Regula<span class="green-pro">Pro</span></div>', unsafe_allow_html=True)

# Definição dos itens de navegação (ícones SVG replicam o design)
st.sidebar.markdown("""
    <a href="?page=Dashboard" class="nav-item active-nav-item" target="_self">
        <div class="nav-item-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3H11V11H3V3ZM3 13H11V21H3V13ZM13 3H21V11H13V3ZM13 13H21V21H13V13Z" fill="#00D084"/></svg>
        </div>
        <div class="nav-item-label">Dashboard</div>
    </a>
    <a href="?page=Processos" class="nav-item" target="_self">
        <div class="nav-item-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z" fill="#ffffff"/></svg>
        </div>
        <div class="nav-item-label">Processos</div>
    </a>
    <a href="?page=Licencas" class="nav-item" target="_self">
        <div class="nav-item-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z" fill="#ffffff"/></svg>
        </div>
        <div class="nav-item-label">Licenças</div>
    </a>
    <a href="?page=Documentos" class="nav-item" target="_self">
        <div class="nav-item-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 6H12L10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6Z" fill="#ffffff"/></svg>
        </div>
        <div class="nav-item-label">Documentos</div>
    </a>
    <a href="?page=Suporte" class="nav-item" target="_self">
        <div class="nav-item-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#ffffff"/></svg>
        </div>
        <div class="nav-item-label">Suporte</div>
    </a>
""", unsafe_allow_html=True)

# Botão Sair na parte inferior
st.sidebar.markdown("""
    <div class="logout-container">
        <a href="?page=Sair" class="logout-item" target="_self">
            <div class="logout-item-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10.09 15.59L11.5 17L16.5 12L11.5 7L10.09 8.41L12.67 11H3V13H12.67L10.09 15.59ZM19 3H5C3.9 3 3 3.9 3 5V9H5V5H19V19H5V15H3V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" fill="#ffffff"/></svg>
            </div>
            <div class="logout-item-label">Sair</div>
        </a>
    </div>
""", unsafe_allow_html=True)


# --- CONTEÚDO PRINCIPAL ---

st.title("Gestão Regulatória")
st.write("Selecione uma opção na sidebar para começar.")
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
