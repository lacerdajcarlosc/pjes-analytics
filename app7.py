# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import os
from io import BytesIO

from app5 import formatar_valor, mostrar_tabela_download

st.set_page_config(page_title="PJES Dashboard", page_icon="📊", layout="wide")

# =====================
# FUNÇÕES
# =====================

@st.cache_data
def load_data():
    return pd.read_excel("PJES.xlsx")

def moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def numero(v):
    return f"{int(v):,}".replace(",", ".")

def filtro_texto(col):
    return ["Todos"] + sorted(
        df[col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

# =====================
# DADOS
# =====================

df = load_data()

mapa_meses = {
    "January": "JANEIRO", "February": "FEVEREIRO", "March": "MARÇO",
    "April": "ABRIL", "May": "MAIO", "June": "JUNHO",
    "July": "JULHO", "August": "AGOSTO", "September": "SETEMBRO",
    "October": "OUTUBRO", "November": "NOVEMBRO", "December": "DEZEMBRO"
}

meses_ordem = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

# 1. Traduz e padroniza para maiúsculo
df["COMPETÊNCIA"] = df["COMPETÊNCIA"].astype(str).str.capitalize().map(mapa_meses)

# 2. Transforma em categoria ordenada (essencial para o gráfico de linha e filtros)
df["COMPETÊNCIA"] = pd.Categorical(df["COMPETÊNCIA"], categories=meses_ordem, ordered=True)

# =====================
# LOGO + TÍTULO
# =====================

col1, col2 = st.columns([1, 9])

with col1:
    if os.path.exists("logo_sds.png"):
        st.image("logo_sds.png", width=90)

with col2:
    st.markdown("<center><h1>📊 Dashboard PJES</h1></center>", unsafe_allow_html=True)

# =====================
# SIDEBAR FILTROS
# =====================

st.sidebar.header("🔍 Filtros")

exercicio = st.sidebar.selectbox(
    "Exercício",
    filtro_texto("EXERCÍCIO"),
    key="filtro_exercicio"
)

lista_competencia = ["Todos"] + sorted(df["COMPETÊNCIA"].dropna().unique().tolist(), key=lambda x: meses_ordem.index(x))

min_exercicio = df["EXERCÍCIO"].min()
max_exercicio = df["EXERCÍCIO"].max()


# Pega apenas os meses que realmente existem no Excel, mas mantendo a ordem cronológica
meses_no_df = sorted(df["COMPETÊNCIA"].dropna().unique(), key=lambda x: meses_ordem.index(x))

lista_competencia = ["Todos"] + meses_no_df

competencia = st.sidebar.selectbox(
    "Competência",
    lista_competencia,
    key="filtro_competencia"
)

operativa = st.sidebar.selectbox(
    "Operativa",
    filtro_texto("OPERATIVA QUE PRESTOU SERVIÇO"),
    key="filtro_operativa"
)

local = st.sidebar.selectbox(
    "Local",
    filtro_texto("LOCAL DA PRESTAÇÃO DO SERVIÇO"),
    key="filtro_local"
)

verba = st.sidebar.selectbox(
    "Verba",
    ["Todos"] + sorted(df["VERBA"].dropna().unique()),
    key="filtro_verba"
)

# =====================
# APLICAR FILTROS
# =====================

df_f = df.copy()

if exercicio != "Todos":
    df_f = df_f[df_f["EXERCÍCIO"] == exercicio]

if competencia != "Todos":
    df_f = df_f[df_f["COMPETÊNCIA"] == competencia]

if operativa != "Todos":
    df_f = df_f[df_f["OPERATIVA QUE PRESTOU SERVIÇO"] == operativa]

if local != "Todos":
    df_f = df_f[df_f["LOCAL DA PRESTAÇÃO DO SERVIÇO"] == local]

if verba != "Todos":
    df_f = df_f[df_f["VERBA"] == verba]

# =====================
# KPIs
# =====================

valor_total = df_f["TOTAL"].sum()
cotas = df_f["COTA"].sum()
c223 = df_f[df_f["VERBA"] == 223]["COTA"].sum()
c423 = df_f[df_f["VERBA"] == 423]["COTA"].sum()
pessoas = df_f["MATRICULA"].nunique()
locais = df_f["LOCAL DA PRESTAÇÃO DO SERVIÇO"].nunique()
media = valor_total / pessoas if pessoas else 0

st.subheader("📈 Indicadores")

k1, k2, k3, k4 = st.columns(4)
k5, k6, k7, k8 = st.columns(4)

k1.metric("💰 Valor Total", moeda(valor_total))
k2.metric("📊 Cotas", numero(cotas))
k3.metric("🔴 Cotas 223", numero(c223))
k4.metric("🔵 Cotas 423", numero(c423))

k5.metric("👥 Pessoas", numero(pessoas))
k6.metric("🏢 Locais", numero(locais))
k7.metric("📈 Média / Pessoa", moeda(media))
k8.metric("📋 Registros", numero(len(df_f)))

st.divider()

# =====================
# GRÁFICOS
# =====================

st.subheader("📊 Visualizações")

por_local = (
    df_f.groupby("LOCAL DA PRESTAÇÃO DO SERVIÇO", as_index=False)["TOTAL"]
    .sum()
    .sort_values("TOTAL", ascending=False)
    .head(10)
)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        por_local,
        x="LOCAL DA PRESTAÇÃO DO SERVIÇO",
        y="TOTAL",
        title="Top 10 Locais"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(
        por_local,
        values="TOTAL",
        names="LOCAL DA PRESTAÇÃO DO SERVIÇO",
        hole=.3
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    evolucao = df_f.groupby("COMPETÊNCIA", as_index=False)["TOTAL"].sum().sort_values("COMPETÊNCIA")
    
    fig3 = px.line(
        evolucao,
        x="COMPETÊNCIA",
        y="TOTAL",
        markers=True,
        title="Evolução Mensal"
    )
    # Formata o eixo Y para moeda no gráfico
    fig3.update_layout(yaxis_tickformat="R$ ,.2f")
    st.plotly_chart(fig3, use_container_width=True)

    # Para a tabela de download, aí sim você usa o formatar_valor
    evolucao_display = evolucao.copy()
    evolucao_display["TOTAL"] = evolucao_display["TOTAL"].apply(formatar_valor)
    mostrar_tabela_download(evolucao_display, "Evolucao.csv", " EVOLUÇÃO MENSAL")

with col4:
    # ==============================
    # GRÁFICO - TOTAL POR CARGO
    # ==============================
    if not df_f.empty and "CARGO" in df_f.columns:
        df_cargo = df_f.dropna(subset=["CARGO", "TOTAL"], how="all")
        df_cargo["TOTAL"] = pd.to_numeric(df_cargo["TOTAL"], errors="coerce")
        df_cargo = df_cargo.dropna(subset=["CARGO", "TOTAL"])

        if not df_cargo.empty:
            result_cargo = (
                df_cargo.groupby("CARGO", as_index=False)["TOTAL"]
                .sum()
                .sort_values(by="TOTAL", ascending=False)
            )

            result_cargo_display = result_cargo.copy()
            result_cargo_display["TOTAL"] = result_cargo_display["TOTAL"].apply(formatar_valor)

            fig_cargo = px.bar(
                result_cargo,
                x="CARGO",
                y="TOTAL",
                title="Total por Cargo",
                labels={"TOTAL": "TOTAL (R$)", "CARGO": "Cargo"},
                template="gridon"
            )
            fig_cargo.update_layout(xaxis=dict(tickangle=45))
            st.plotly_chart(fig_cargo, use_container_width=True)

            mostrar_tabela_download(result_cargo_display, "Cargo.csv", "👮 CARGO POR OPERATIVA")

st.divider()

# =====================
# TABELA DETALHADA
# =====================

st.subheader("📋 Dados Detalhados")

cols = [
    "MATRICULA",
    "NOME",
    "CARGO",
    "OPERATIVA QUE PRESTOU SERVIÇO",
    "LOCAL DA PRESTAÇÃO DO SERVIÇO",
    "COMPETÊNCIA",
    "COTA",
    "VERBA",
    "TOTAL",
]

df_tab = df_f[cols].sort_values("TOTAL", ascending=False)

st.dataframe(df_tab, use_container_width=True, height=400,hide_index=True)

buf = BytesIO()
df_tab.to_excel(buf, index=False)

st.download_button(
    "📥 Baixar Dados Filtrados",
    buf.getvalue(),
    "dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =====================
# TABELA DINÂMICA VERBA 223
# =====================

st.divider()
st.subheader("📊 Tabela Dinâmica – VERBA 223 por Local")

df_223 = df_f[df_f["VERBA"] == 223]

if not df_223.empty:
    pivot223 = pd.pivot_table(
        df_223,
        index=["MATRICULA", "NOME"],
        columns="LOCAL DA PRESTAÇÃO DO SERVIÇO",
        values="COTA",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    pivot223.columns.name = None
    pivot223["TOTAL GERAL"] = pivot223.iloc[:, 2:].sum(axis=1)
    pivot223 = pivot223.sort_values("TOTAL GERAL", ascending=False)

    st.dataframe(pivot223, use_container_width=True, height=400, hide_index=True)

    buf223 = BytesIO()
    pivot223.to_excel(buf223, index=False)

    st.download_button(
        "📥 Baixar Tabela Dinâmica VERBA 223",
        buf223.getvalue(),
        "tabela_dinamica_223.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Nenhum registro para VERBA 223.")

# =====================
# RODAPÉ
# =====================

st.caption(f"Dashboard PJES | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
