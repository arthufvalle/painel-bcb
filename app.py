import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="Painel BCB", layout="wide")
st.title("Painel - Banco Central do Brasil")

@st.cache_data(ttl=3600)
def get_bcb_series(codigo, nome):
    data_final = datetime.today().strftime("%d/%m/%Y")
    data_inicial = (datetime.today() - timedelta(days=365*20)).strftime("%d/%m/%Y")
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) == 0:
            return pd.DataFrame(columns=[nome])
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors="coerce")
        df['valor'] = pd.to_numeric(df['valor'], errors="coerce")
        df = df.dropna()
        df = df.set_index('data')
        df = df.rename(columns={'valor': nome})
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame(columns=[nome])

def calc_yoy(df):
    return df.pct_change(12) * 100

def make_chart(titulo, series_list, yaxis_fmt=None):
    fig = go.Figure()
    for codigo, nome, cor in series_list:
        df = get_bcb_series(codigo, nome)
        if not df.empty:
            fig.add_trace(go.Scatter(x=df.index, y=df[nome], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig, titulo, yaxis_fmt)
    return fig

def make_chart_from_dfs(titulo, df_list, yaxis_fmt=None):
    fig = go.Figure()
    for df, nome, cor in df_list:
        if not df.empty:
            col = df.columns[0]
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig, titulo, yaxis_fmt)
    return fig

def _format_layout(fig, titulo, yaxis_fmt=None):
    tickformat = ".1%" if yaxis_fmt == "pct" else None
    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='lightgrey', tickformat=tickformat),
        legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=40, r=20, t=60, b=80)
    )

# =============================================
# SECAO 1: NPL
# =============================================

st.header("NPL Recursos Livres PJ")
fig1 = make_chart("NPL Recursos Livres PJ", [(21086, "Total PJ", "#E07B39"), (21093, "Capital de giro total", "#7B3F1E"), (21096, "Aquisicao de veiculos", "#1F4E79"), (21098, "Aquisicao de bens total", "#5B9BD5"), (21099, "Arrend. mercantil de veiculos", "#70AD47")])
st.plotly_chart(fig1, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig2 = make_chart("NPL Recursos Livres PJ - Capital de Giro Rotativo", [(21092, "Capital de giro rotativo", "#C0392B")])
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    fig3 = make_chart("NPL Recursos Livres PJ - Total PJ", [(21086, "Total PJ", "#E07B39")])
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.header("NPL Recurso Livre - PF")
col3, col4 = st.columns(2)
with col3:
    fig4 = make_chart("NPL Recurso Livre - PF - Total", [(21112, "Total PF", "#1F4E79")])
    st.plotly_chart(fig4, use_container_width=True)
with col4:
    fig5 = make_chart("NPL Recurso Livre - PF - Cartao rotativo", [(21127, "Cartao de credito rotativo", "#C0392B")])
    st.plotly_chart(fig5, use_container_width=True)

fig6 = make_chart("NPL Recurso Livre - PF", [(21113, "Cheque especial", "#E07B39"), (21129, "Cartao de credito total", "#70AD47"), (21128, "Cartao de credito parcelado", "#1F4E79")])
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.header("NPL Geral")
col5, col6 = st.columns(2)
with col5:
    fig7 = make_chart("NPL - Total, PJ e PF", [(21085, "Total", "#1F4E79"), (21086, "Pessoas juridicas", "#E07B39"), (21112, "Pessoas fisicas", "#808080")])
    st.plotly_chart(fig7, use_container_width=True)
with col6:
    fig8 = make_chart("NPL - Recursos Direcionados", [(21082, "Total", "#E07B39"), (21083, "Pessoas juridicas", "#808080"), (21084, "Pessoas fisicas", "#1F4E79")])
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.header("Inadimplencia por Tipo de Empresa")
col7, col8 = st.columns(2)
with col7:
    fig9 = make_chart("Inadimplencia por tipo de empresa", [(27703, "PMEs", "#1F4E79"), (27704, "Grandes Empresas", "#E07B39")])
    st.plotly_chart(fig9, use_container_width=True)
with col8:
    fig10 = make_chart("PJ - % da Carteira em classe E-H", [(27705, "PJ", "#808080"), (27706, "PMEs", "#F0C040"), (27707, "Grandes Empresas", "#1F4E79")])
    st.plotly_chart(fig10, use_container_width=True)

# =============================================
# SECAO 2: SALDO LIVRE PF
# =============================================

st.markdown("---")
st.header("Saldo Livre PF")

# G1: Cheque Especial, Cartao Rotativo, Cartao Parcelado (nivel)
df_cheque = get_bcb_series(20573, "Cheque Especial")
df_rotativo = get_bcb_series(20587, "Cartao de Credito Rotativo")
df_parcelado = get_bcb_series(20588, "Cartao de Credito Parcelado")

fig_s1 = make_chart_from_dfs(
    "Saldo Livre PF",
    [
        (df_rotativo, "Cartao de Credito Rotativo", "#1C1C1C"),
        (df_parcelado, "Cartao de Credito Parcelado", "#1F4E79"),
        (df_cheque, "Cheque Especial", "#70AD47"),
    ]
)
st.plotly_chart(fig_s1, use_container_width=True)

# G2: Cartao de Credito Total (soma rotativo + parcelado + 20589)
df_cc3 = get_bcb_series(20589, "Outros Cartao")
df_cc_total = pd.DataFrame()
if not df_rotativo.empty and not df_parcelado.empty and not df_cc3.empty:
    combined = df_rotativo.join(df_parcelado, how='outer').join(df_cc3, how='outer').fillna(0)
    df_cc_total = pd.DataFrame(combined.sum(axis=1), columns=["Cartao de Credito total"])
elif not df_rotativo.empty and not df_parcelado.empty:
    combined = df_rotativo.join(df_parcelado, how='outer').fillna(0)
    df_cc_total = pd.DataFrame(combined.sum(axis=1), columns=["Cartao de Credito total"])

col_s1, col_s2 = st.columns(2)
with col_s1:
    fig_s2 = make_chart_from_dfs(
        "Saldo Livre PF - Cartao de Credito total",
        [(df_cc_total, "Cartao de Credito total", "#E07B39")]
    )
    st.plotly_chart(fig_s2, use_container_width=True)

# G3: YoY de G1 (cheque, rotativo, parcelado) e G2 (cartao total)
with col_s2:
    fig_s3 = go.Figure()
    yoy_data = [
        (df_cheque, "Cheque Especial", "#70AD47"),
        (df_rotativo, "Cartao de Credito Rotativo", "#1C1C1C"),
        (df_parcelado, "Cartao de Credito Parcelado", "#1F4E79"),
        (df_cc_total, "Cartao de Credito Total", "#E07B39"),
    ]
    for df_src, nome, cor in yoy_data:
        if not df_src.empty:
            yoy = calc_yoy(df_src)
            col_name = df_src.columns[0]
            fig_s3.add_trace(go.Scatter(x=yoy.index, y=yoy[col_name], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig_s3, "Saldo Livre PF YoY", "pct")
    st.plotly_chart(fig_s3, use_container_width=True)

# G4: Total PF Saldo (20570)
df_total_pf = get_bcb_series(20570, "Total PF")

col_s3, col_s4 = st.columns(2)
with col_s3:
    fig_s4 = make_chart_from_dfs(
        "Saldo - Total PF",
        [(df_total_pf, "Total PF", "#1F4E79")]
    )
    st.plotly_chart(fig_s4, use_container_width=True)

# G5: YoY de G4
with col_s4:
    fig_s5 = go.Figure()
    if not df_total_pf.empty:
        yoy_total = calc_yoy(df_total_pf)
        fig_s5.add_trace(go.Scatter(x=yoy_total.index, y=yoy_total["Total PF"], name="Total PF", line=dict(color="#1F4E79", width=1.5), mode='lines'))
    _format_layout(fig_s5, "Saldo YoY - Total PF", "pct")
    st.plotly_chart(fig_s5, use_container_width=True)

# G6: Rotativo, Consignado, Veiculos (nivel)
df_rot = get_bcb_series(20579, "Rotativo")
df_consig = get_bcb_series(20572, "Consignado")
df_veic = get_bcb_series(20581, "Veiculos")

fig_s6 = make_chart_from_dfs(
    "Saldo",
    [
        (df_rot, "Rotativo", "#E07B39"),
        (df_consig, "Consignado", "#F0C040"),
        (df_veic, "Veiculos", "#1F4E79"),
    ]
)
st.plotly_chart(fig_s6, use_container_width=True)

# G7: YoY de G6
fig_s7 = go.Figure()
for df_src, nome, cor in [(df_rot, "Rotativo", "#E07B39"), (df_consig, "Consignado", "#F0C040"), (df_veic, "Veiculos", "#1F4E79")]:
    if not df_src.empty:
        yoy = calc_yoy(df_src)
        col_name = df_src.columns[0]
        fig_s7.add_trace(go.Scatter(x=yoy.index, y=yoy[col_name], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
_format_layout(fig_s7, "Saldo YoY", "pct")
st.plotly_chart(fig_s7, use_container_width=True)
