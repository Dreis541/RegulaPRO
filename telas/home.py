"""Página Home/Dashboard principal do RegulaPRO."""

from typing import Any

import streamlit as st
from functions.processos import obter_metricas, verificar_e_atualizar_atrasados, listar_processos
from utils.constantes import CORES_STATUS
from utils.formatadores import formatar_data


def main() -> None:
    """Renderiza a página Home."""
    # Atualizar processos atrasados automaticamente
    verificar_e_atualizar_atrasados()

    metricas = obter_metricas()

    st.title("📊 Dashboard Geral")
    st.markdown("---")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📁 Total de Processos", metricas["total"])
    with c2:
        st.metric("🔄 Em Andamento", metricas["em_andamento"])
    with c3:
        st.metric("✅ Concluídos", metricas["concluidos"])
    with c4:
        st.metric("⚠️ Atrasados", metricas["atrasados"])

    st.markdown("---")

    # Gráfico de status
    por_status = metricas.get("por_status", [])
    if por_status:
        import pandas as pd
        import plotly.express as px

        df_status = pd.DataFrame(por_status)
        df_status.columns = ["Status", "Quantidade"]
        cores = [CORES_STATUS.get(s, "#6b7280") for s in df_status["Status"]]

        fig = px.bar(
            df_status,
            x="Status",
            y="Quantidade",
            color="Status",
            color_discrete_sequence=cores,
            title="Processos por Status",
            text="Quantidade",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            showlegend=False,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum processo cadastrado ainda.")

    st.markdown("---")

    # Processos recentes
    st.subheader("📋 Processos Recentes")
    processos = listar_processos()[:5]
    if processos:
        import pandas as pd

        df = pd.DataFrame(processos)[
            ["numero_protocolo", "empresa", "tipo", "status", "data_abertura", "data_prazo"]
        ]
        df.columns = ["Protocolo", "Empresa", "Tipo", "Status", "Abertura", "Prazo"]
        df["Abertura"] = df["Abertura"].apply(formatar_data)
        df["Prazo"] = df["Prazo"].apply(formatar_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum processo cadastrado.")
