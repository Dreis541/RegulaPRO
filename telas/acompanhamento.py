"""Dashboard de acompanhamento dos processos ANVISA."""

import streamlit as st
from typing import List, Dict, Any, Optional

from functions.processos import (
    listar_processos,
    listar_eventos,
    obter_metricas,
    verificar_e_atualizar_atrasados,
)
from utils.constantes import TODOS_STATUS, CORES_STATUS, TIPOS_PROCESSO
from utils.formatadores import formatar_data, formatar_prazo_dias, formatar_percentual
from utils.helpers import calcular_dias_restantes, data_iso_para_date


def _grafico_pizza_status(por_status: List[Dict]) -> None:
    """Gráfico de pizza com distribuição de status."""
    if not por_status:
        st.info("Sem dados para exibir.")
        return
    import plotly.express as px
    import pandas as pd

    df = pd.DataFrame(por_status)
    df.columns = ["Status", "Quantidade"]
    cores = [CORES_STATUS.get(s, "#6b7280") for s in df["Status"]]
    fig = px.pie(
        df,
        names="Status",
        values="Quantidade",
        color="Status",
        color_discrete_sequence=cores,
        title="Distribuição por Status",
        hole=0.4,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
    )
    st.plotly_chart(fig, use_container_width=True)


def _grafico_barras_tipo(processos: List[Dict]) -> None:
    """Gráfico de barras com processos por tipo."""
    if not processos:
        return
    import plotly.express as px
    import pandas as pd
    from utils.helpers import contar_por_campo

    contagem = contar_por_campo(processos, "tipo")
    df = pd.DataFrame(list(contagem.items()), columns=["Tipo", "Quantidade"])
    df = df.sort_values("Quantidade", ascending=False)
    fig = px.bar(
        df,
        x="Tipo",
        y="Quantidade",
        title="Processos por Tipo",
        color="Quantidade",
        color_continuous_scale="tealgrn",
        text="Quantidade",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        coloraxis_showscale=False,
        xaxis_tickangle=-30,
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def _grafico_linha_abertura(processos: List[Dict]) -> None:
    """Gráfico de linha com volume de aberturas por mês."""
    if not processos:
        return
    import plotly.express as px
    import pandas as pd

    df = pd.DataFrame(processos)
    if "data_abertura" not in df.columns:
        return
    df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    df["mes"] = df["data_abertura"].dt.to_period("M").astype(str)
    contagem = df.groupby("mes").size().reset_index(name="Processos")
    fig = px.line(
        contagem,
        x="mes",
        y="Processos",
        title="Novos Processos por Mês",
        markers=True,
        color_discrete_sequence=["#00d084"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        xaxis_title="Mês",
    )
    st.plotly_chart(fig, use_container_width=True)


def _timeline_eventos(processo_id: int) -> None:
    """Exibe timeline de eventos de um processo."""
    eventos = listar_eventos(processo_id)
    if not eventos:
        st.info("Nenhum evento registrado para este processo.")
        return
    for ev in eventos:
        data_str = formatar_data(ev.get("data_evento", ""), "%d/%m/%Y %H:%M")
        tipo = ev.get("tipo_evento", "Atualização")
        icon_map = {
            "Atualização": "🔄",
            "Criação": "🆕",
            "Alerta": "⚠️",
            "Conclusão": "✅",
            "Documento": "📄",
        }
        icone = icon_map.get(tipo, "📌")
        with st.container():
            st.markdown(f"**{icone} {ev['titulo']}** — _{data_str}_")
            if ev.get("descricao"):
                st.caption(ev["descricao"])
            st.divider()


def _card_processo(p: Dict) -> None:
    """Renderiza um card de processo com barra de progresso."""
    dias_restantes = calcular_dias_restantes(data_iso_para_date(p.get("data_prazo")))
    prazo_texto = formatar_prazo_dias(dias_restantes)
    percentual = float(p.get("percentual_conclusao") or 0)
    cor_status = CORES_STATUS.get(p.get("status", ""), "#6b7280")

    with st.container():
        col_info, col_prog = st.columns([3, 1])
        with col_info:
            st.markdown(
                f"**{p.get('empresa', '')}** — `{p.get('numero_protocolo', '')}`"
            )
            st.caption(
                f"📂 {p.get('tipo', '')} &nbsp;|&nbsp; "
                f"🏷️ <span style='color:{cor_status}'>{p.get('status', '')}</span> &nbsp;|&nbsp; "
                f"📅 {prazo_texto}",
                unsafe_allow_html=True,
            )
        with col_prog:
            st.metric("Conclusão", formatar_percentual(percentual))
        st.progress(int(percentual))
        st.divider()


def main() -> None:
    """Renderiza o dashboard de acompanhamento."""
    verificar_e_atualizar_atrasados()

    st.title("📈 Dashboard de Acompanhamento")
    st.markdown("---")

    # Filtros no topo
    with st.expander("🔍 Filtros", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_empresa = st.text_input("Empresa", key="ac_empresa")
        with col2:
            filtro_status = st.selectbox("Status", ["Todos"] + TODOS_STATUS, key="ac_status")
        with col3:
            filtro_tipo = st.selectbox("Tipo", ["Todos"] + TIPOS_PROCESSO, key="ac_tipo")
        with col4:
            col_data1, col_data2 = st.columns(2)
            data_inicio = col_data1.date_input("De", value=None, key="ac_di")
            data_fim = col_data2.date_input("Até", value=None, key="ac_df")

    status_p = None if filtro_status == "Todos" else filtro_status
    tipo_p = None if filtro_tipo == "Todos" else filtro_tipo
    di_str = data_inicio.isoformat() if data_inicio else None
    df_str = data_fim.isoformat() if data_fim else None

    processos = listar_processos(
        empresa=filtro_empresa or None,
        status=status_p,
        tipo=tipo_p,
        data_inicio=di_str,
        data_fim=df_str,
    )

    metricas = obter_metricas()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📁 Total", metricas["total"])
    c2.metric("🔄 Em Andamento", metricas["em_andamento"])
    c3.metric("✅ Concluídos", metricas["concluidos"])
    c4.metric("⚠️ Atrasados", metricas["atrasados"])

    st.markdown("---")

    # Gráficos
    col_pizza, col_barras = st.columns(2)
    with col_pizza:
        _grafico_pizza_status(metricas.get("por_status", []))
    with col_barras:
        _grafico_barras_tipo(processos)

    _grafico_linha_abertura(processos)

    st.markdown("---")

    # Cards de processos
    st.subheader(f"📋 Processos ({len(processos)} encontrados)")
    if processos:
        for p in processos:
            _card_processo(p)
    else:
        st.info("Nenhum processo encontrado com os filtros aplicados.")

    st.markdown("---")

    # Timeline por processo
    st.subheader("⏱️ Timeline de Eventos")
    if processos:
        ids = {f"{p['numero_protocolo']} — {p['empresa']}": p["id"] for p in processos}
        sel = st.selectbox("Selecione um processo", list(ids.keys()), key="timeline_sel")
        if sel:
            _timeline_eventos(ids[sel])
    else:
        st.info("Sem processos para exibir timeline.")
