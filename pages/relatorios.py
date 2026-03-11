"""Página de relatórios do RegulaPRO."""

import streamlit as st
from datetime import date
from typing import Optional

from functions.processos import listar_processos, obter_metricas
from utils.constantes import TODOS_STATUS, TIPOS_PROCESSO
from utils.formatadores import formatar_data, formatar_percentual, formatar_cnpj


def _gerar_csv(processos: list) -> str:
    """Gera string CSV dos processos para download."""
    import csv
    import io

    campos = [
        "numero_protocolo", "empresa", "cnpj", "tipo", "categoria", "produto",
        "status", "prioridade", "data_abertura", "data_prazo", "data_conclusao",
        "responsavel", "descricao", "percentual_conclusao",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=campos, extrasaction="ignore")
    writer.writeheader()
    for p in processos:
        writer.writerow(p)
    return output.getvalue()


def _resumo_metricas(processos: list) -> None:
    """Exibe resumo de métricas dos processos filtrados."""
    total = len(processos)
    concluidos = sum(1 for p in processos if p.get("status") in ("Concluído", "Deferido"))
    atrasados = sum(1 for p in processos if p.get("status") == "Atrasado")
    media_conclusao = (
        sum(float(p.get("percentual_conclusao") or 0) for p in processos) / total
        if total > 0 else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📁 Total Filtrado", total)
    c2.metric("✅ Concluídos", concluidos)
    c3.metric("⚠️ Atrasados", atrasados)
    c4.metric("📊 Média Conclusão", formatar_percentual(media_conclusao))


def _tabela_relatorio(processos: list) -> None:
    """Exibe tabela formatada dos processos para relatório."""
    if not processos:
        st.info("Nenhum processo encontrado com os filtros aplicados.")
        return

    import pandas as pd

    df = pd.DataFrame(processos)
    colunas = [
        "numero_protocolo", "empresa", "cnpj", "tipo", "status", "prioridade",
        "data_abertura", "data_prazo", "percentual_conclusao", "responsavel",
    ]
    colunas_existentes = [c for c in colunas if c in df.columns]
    df = df[colunas_existentes].copy()
    df.rename(columns={
        "numero_protocolo": "Protocolo",
        "empresa": "Empresa",
        "cnpj": "CNPJ",
        "tipo": "Tipo",
        "status": "Status",
        "prioridade": "Prioridade",
        "data_abertura": "Abertura",
        "data_prazo": "Prazo",
        "percentual_conclusao": "Conclusão %",
        "responsavel": "Responsável",
    }, inplace=True)

    if "Abertura" in df.columns:
        df["Abertura"] = df["Abertura"].apply(formatar_data)
    if "Prazo" in df.columns:
        df["Prazo"] = df["Prazo"].apply(formatar_data)
    if "CNPJ" in df.columns:
        df["CNPJ"] = df["CNPJ"].apply(lambda v: formatar_cnpj(v) if v else "")
    if "Conclusão %" in df.columns:
        df["Conclusão %"] = df["Conclusão %"].apply(lambda v: formatar_percentual(float(v or 0)))

    st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    """Renderiza a página de relatórios."""
    st.title("📊 Relatórios")
    st.markdown("---")

    # Filtros
    st.subheader("🔍 Filtros do Relatório")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_empresa = st.text_input("Empresa", key="rel_empresa")
        filtro_status = st.selectbox("Status", ["Todos"] + TODOS_STATUS, key="rel_status")
    with col2:
        filtro_tipo = st.selectbox("Tipo de Processo", ["Todos"] + TIPOS_PROCESSO, key="rel_tipo")
        data_inicio = st.date_input("Data de Início", value=None, key="rel_di")
    with col3:
        data_fim = st.date_input("Data de Fim", value=None, key="rel_df")

    status_p = None if filtro_status == "Todos" else filtro_status
    tipo_p = None if filtro_tipo == "Todos" else filtro_tipo
    data_inicio_str = data_inicio.isoformat() if data_inicio else None
    data_fim_str = data_fim.isoformat() if data_fim else None

    if st.button("🔄 Gerar Relatório", use_container_width=True):
        st.session_state["relatorio_gerado"] = True

    processos = listar_processos(
        empresa=filtro_empresa or None,
        status=status_p,
        tipo=tipo_p,
        data_inicio=data_inicio_str,
        data_fim=data_fim_str,
    )

    st.markdown("---")

    # Métricas resumidas
    st.subheader("📈 Resumo")
    _resumo_metricas(processos)

    st.markdown("---")

    # Tabela
    st.subheader("📋 Dados do Relatório")
    _tabela_relatorio(processos)

    # Botão de download CSV
    if processos:
        csv_data = _gerar_csv(processos)
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_data,
            file_name=f"relatorio_regulapro_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
