"""Página de listagem, criação e edição de processos."""

import streamlit as st
from datetime import date, timedelta
from typing import Optional

from functions.processos import (
    listar_processos,
    criar_processo,
    atualizar_processo,
    excluir_processo,
    adicionar_evento,
    buscar_processo_por_id,
)
from functions.anvisa import (
    obter_tipos_processo,
    obter_categorias,
    obter_prazo_padrao,
    gerar_checklist_documentos,
)
from utils.constantes import TODOS_STATUS, PRIORIDADES
from utils.formatadores import formatar_cnpj, formatar_data, formatar_prazo_dias
from utils.helpers import calcular_dias_restantes, gerar_numero_protocolo


def _form_novo_processo() -> None:
    """Formulário para criar um novo processo."""
    st.subheader("➕ Novo Processo")
    with st.form("form_novo_processo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa *", placeholder="Nome da empresa")
            cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
            tipo = st.selectbox("Tipo de Processo *", obter_tipos_processo())
            categoria = st.selectbox("Categoria do Produto", obter_categorias())
            produto = st.text_input("Produto", placeholder="Nome do produto")
        with col2:
            prioridade = st.selectbox("Prioridade", PRIORIDADES)
            responsavel = st.text_input("Responsável", placeholder="Nome do responsável")
            data_abertura = st.date_input("Data de Abertura *", value=date.today())
            dias_prazo = obter_prazo_padrao(tipo)
            data_prazo = st.date_input(
                "Data de Prazo",
                value=date.today() + timedelta(days=dias_prazo),
            )
        descricao = st.text_area("Descrição", placeholder="Descreva o processo...")
        observacoes = st.text_area("Observações", placeholder="Observações adicionais...")

        submitted = st.form_submit_button("💾 Criar Processo", use_container_width=True)
        if submitted:
            if not empresa.strip():
                st.error("O campo Empresa é obrigatório.")
                return
            dados = {
                "empresa": empresa.strip(),
                "cnpj": cnpj.strip(),
                "tipo": tipo,
                "categoria": categoria,
                "produto": produto.strip(),
                "status": "Em Andamento",
                "prioridade": prioridade,
                "responsavel": responsavel.strip(),
                "data_abertura": data_abertura,
                "data_prazo": data_prazo,
                "descricao": descricao.strip(),
                "observacoes": observacoes.strip(),
                "percentual_conclusao": 0.0,
            }
            resultado = criar_processo(dados)
            if resultado["sucesso"]:
                st.success(f"✅ Processo criado! Protocolo: {dados.get('numero_protocolo', '')}")
                st.rerun()
            else:
                for erro in resultado["erros"]:
                    st.error(erro)


def _checklist_documentos(tipo: str) -> None:
    """Exibe checklist de documentos para o tipo de processo."""
    with st.expander("📋 Checklist de Documentos Necessários"):
        docs = gerar_checklist_documentos(tipo)
        for doc in docs:
            st.checkbox(doc, key=f"doc_{doc}")


def _tabela_processos(processos: list) -> None:
    """Exibe a tabela de processos com ações."""
    if not processos:
        st.info("Nenhum processo encontrado com os filtros aplicados.")
        return

    import pandas as pd

    df = pd.DataFrame(processos)
    colunas = ["id", "numero_protocolo", "empresa", "tipo", "status", "prioridade", "data_abertura", "data_prazo", "percentual_conclusao"]
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_exib = df[colunas_existentes].copy()
    df_exib.rename(columns={
        "id": "ID",
        "numero_protocolo": "Protocolo",
        "empresa": "Empresa",
        "tipo": "Tipo",
        "status": "Status",
        "prioridade": "Prioridade",
        "data_abertura": "Abertura",
        "data_prazo": "Prazo",
        "percentual_conclusao": "Conclusão %",
    }, inplace=True)

    if "Abertura" in df_exib.columns:
        df_exib["Abertura"] = df_exib["Abertura"].apply(formatar_data)
    if "Prazo" in df_exib.columns:
        df_exib["Prazo"] = df_exib["Prazo"].apply(formatar_data)
    if "Conclusão %" in df_exib.columns:
        df_exib["Conclusão %"] = df_exib["Conclusão %"].apply(lambda v: f"{float(v):.0f}%")

    st.dataframe(df_exib, use_container_width=True, hide_index=True)


def _painel_editar_processo(processo_id: int) -> None:
    """Painel lateral para editar um processo existente."""
    processo = buscar_processo_por_id(processo_id)
    if not processo:
        st.error("Processo não encontrado.")
        return

    st.subheader(f"✏️ Editar Processo #{processo_id}")
    with st.form(f"form_editar_{processo_id}"):
        novo_status = st.selectbox("Status", TODOS_STATUS, index=TODOS_STATUS.index(processo["status"]) if processo["status"] in TODOS_STATUS else 0)
        novo_percentual = st.slider("% de Conclusão", 0, 100, int(processo.get("percentual_conclusao") or 0))
        nova_obs = st.text_area("Observações", value=processo.get("observacoes", ""))
        novo_responsavel = st.text_input("Responsável", value=processo.get("responsavel", ""))

        col_salvar, col_excluir = st.columns(2)
        salvar = col_salvar.form_submit_button("💾 Salvar")
        excluir = col_excluir.form_submit_button("🗑️ Excluir")

        if salvar:
            resultado = atualizar_processo(processo_id, {
                "status": novo_status,
                "percentual_conclusao": novo_percentual,
                "observacoes": nova_obs,
                "responsavel": novo_responsavel,
            })
            if resultado["sucesso"]:
                adicionar_evento(processo_id, f"Status atualizado para: {novo_status}", tipo_evento="Atualização")
                st.success("Processo atualizado!")
                st.rerun()
            else:
                for e in resultado["erros"]:
                    st.error(e)

        if excluir:
            excluir_processo(processo_id)
            st.success("Processo excluído.")
            st.rerun()


def main() -> None:
    """Renderiza a página de processos."""
    st.title("📋 Processos ANVISA")
    st.markdown("---")

    aba_listar, aba_novo = st.tabs(["📄 Listar Processos", "➕ Novo Processo"])

    with aba_listar:
        # Filtros
        with st.expander("🔍 Filtros", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_empresa = st.text_input("Empresa", key="f_empresa")
            with col2:
                filtro_status = st.selectbox("Status", ["Todos"] + TODOS_STATUS, key="f_status")
            with col3:
                filtro_tipo = st.selectbox("Tipo", ["Todos"] + obter_tipos_processo(), key="f_tipo")

        status_param = None if filtro_status == "Todos" else filtro_status
        tipo_param = None if filtro_tipo == "Todos" else filtro_tipo
        processos = listar_processos(empresa=filtro_empresa or None, status=status_param, tipo=tipo_param)

        _tabela_processos(processos)

        if processos:
            ids_disponiveis = [p["id"] for p in processos]
            processo_id_sel = st.number_input(
                "ID do processo para editar",
                min_value=1,
                step=1,
                key="sel_processo_id",
            )
            if st.button("✏️ Editar Processo Selecionado") and processo_id_sel in ids_disponiveis:
                _painel_editar_processo(int(processo_id_sel))

    with aba_novo:
        _form_novo_processo()
