import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="Painel BCB", layout="wide")
st.title("Painel - Banco Central do Brasil")

@st.cache_data(ttl=3600)
def get_bcb_series(codigo, nome, escala_bi=False):
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
        if escala_bi:
            df = df / 1000.0
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame(columns=[nome])

def calc_yoy(df):
    if df.empty:
        return df
    df_monthly = df.resample('MS').last()
    yoy = df_monthly.pct_change(12) * 100
    return yoy

def _format_layout(fig, titulo, yaxis_fmt=None, yaxis_title=None):
    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            gridcolor='lightgrey',
            title=yaxis_title,
            ticksuffix="%" if yaxis_fmt == "pct" else "",
        ),
        legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=40, r=20, t=60, b=80)
    )

def make_chart(titulo, series_list, yaxis_fmt=None, yaxis_title=None):
    fig = go.Figure()
    for codigo, nome, cor in series_list:
        df = get_bcb_series(codigo, nome)
        if not df.empty:
            fig.add_trace(go.Scatter(x=df.index, y=df[nome], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig, titulo, yaxis_fmt, yaxis_title)
    return fig

def make_chart_bi(titulo, series_list, yaxis_fmt=None, yaxis_title="R$ bi"):
    fig = go.Figure()
    for codigo, nome, cor in series_list:
        df = get_bcb_series(codigo, nome, escala_bi=True)
        if not df.empty:
            fig.add_trace(go.Scatter(x=df.index, y=df[nome], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig, titulo, yaxis_fmt, yaxis_title)
    return fig

def make_chart_from_dfs(titulo, df_list, yaxis_fmt=None, yaxis_title=None):
    fig = go.Figure()
    for df, nome, cor in df_list:
        if not df.empty:
            col = df.columns[0]
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
    _format_layout(fig, titulo, yaxis_fmt, yaxis_title)
    return fig

def export_button(df_dict, label="Exportar para Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            sn = str(sheet_name)[:31]
            if not df.empty:
                df.to_excel(writer, sheet_name=sn)
    output.seek(0)
    st.download_button(
        label=label,
        data=output,
        file_name=f"{label.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =============================================
# SECAO 1: NPL
# =============================================

st.header("NPL Recursos Livres PJ")

df_npl1_totalpj = get_bcb_series(21086, "Total PJ")
df_npl1_girototal = get_bcb_series(21093, "Capital de giro total")
df_npl1_veic = get_bcb_series(21096, "Aquisicao de veiculos")
df_npl1_bens = get_bcb_series(21098, "Aquisicao de bens total")
df_npl1_arrend = get_bcb_series(21099, "Arrend. mercantil de veiculos")

fig_npl1 = make_chart_from_dfs(
    "NPL Recursos Livres PJ",
    [
        (df_npl1_totalpj, "Total PJ", "#E07B39"),
        (df_npl1_girototal, "Capital de giro total", "#7B3F1E"),
        (df_npl1_veic, "Aquisicao de veiculos", "#1F4E79"),
        (df_npl1_bens, "Aquisicao de bens total", "#5B9BD5"),
        (df_npl1_arrend, "Arrend. mercantil de veiculos", "#70AD47"),
    ],
    yaxis_title="% NPL"
)
st.plotly_chart(fig_npl1, use_container_width=True)
export_button({"Total PJ": df_npl1_totalpj, "Capital giro total": df_npl1_girototal, "Aquis veiculos": df_npl1_veic, "Aquis bens total": df_npl1_bens, "Arrend mercantil": df_npl1_arrend}, "Exportar NPL Recursos Livres PJ")

col1, col2 = st.columns(2)
with col1:
    df_npl2 = get_bcb_series(21092, "Capital de giro rotativo")
    fig_npl2 = make_chart_from_dfs("NPL - Capital de Giro Rotativo", [(df_npl2, "Capital de giro rotativo", "#C0392B")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl2, use_container_width=True)
    export_button({"Capital giro rotativo": df_npl2}, "Exportar Capital Giro Rotativo")
with col2:
    fig_npl3 = make_chart_from_dfs("NPL Recursos Livres PJ - Total PJ", [(df_npl1_totalpj, "Total PJ", "#E07B39")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl3, use_container_width=True)
    export_button({"Total PJ": df_npl1_totalpj}, "Exportar NPL Total PJ")

st.markdown("---")
st.header("NPL Recurso Livre - PF")

df_npl_pf_total = get_bcb_series(21112, "Total PF")
df_npl_cartao_rot = get_bcb_series(21127, "Cartao de credito rotativo")
df_npl_cheque = get_bcb_series(21113, "Cheque especial")
df_npl_cartao_total = get_bcb_series(21129, "Cartao de credito total")
df_npl_cartao_parc = get_bcb_series(21128, "Cartao de credito parcelado")

col3, col4 = st.columns(2)
with col3:
    fig_npl4 = make_chart_from_dfs("NPL Recurso Livre - PF - Total", [(df_npl_pf_total, "Total PF", "#1F4E79")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl4, use_container_width=True)
    export_button({"Total PF": df_npl_pf_total}, "Exportar NPL Total PF")
with col4:
    fig_npl5 = make_chart_from_dfs("NPL Recurso Livre - PF - Cartao rotativo", [(df_npl_cartao_rot, "Cartao de credito rotativo", "#C0392B")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl5, use_container_width=True)
    export_button({"Cartao rotativo": df_npl_cartao_rot}, "Exportar NPL Cartao Rotativo")

fig_npl6 = make_chart_from_dfs(
    "NPL Recurso Livre - PF",
    [(df_npl_cheque, "Cheque especial", "#E07B39"), (df_npl_cartao_total, "Cartao de credito total", "#70AD47"), (df_npl_cartao_parc, "Cartao de credito parcelado", "#1F4E79")],
    yaxis_title="% NPL"
)
st.plotly_chart(fig_npl6, use_container_width=True)
export_button({"Cheque especial": df_npl_cheque, "Cartao total": df_npl_cartao_total, "Cartao parcelado": df_npl_cartao_parc}, "Exportar NPL PF Detalhado")

st.markdown("---")
st.header("NPL Geral")

df_npl_total = get_bcb_series(21085, "Total")
df_npl_pj = get_bcb_series(21086, "Pessoas juridicas")
df_npl_pf = get_bcb_series(21112, "Pessoas fisicas")
df_npl_dir_total = get_bcb_series(21082, "Total Direcionado")
df_npl_dir_pj = get_bcb_series(21083, "PJ Direcionado")
df_npl_dir_pf = get_bcb_series(21084, "PF Direcionado")

col5, col6 = st.columns(2)
with col5:
    fig_npl7 = make_chart_from_dfs("NPL - Total, PJ e PF", [(df_npl_total, "Total", "#1F4E79"), (df_npl_pj, "Pessoas juridicas", "#E07B39"), (df_npl_pf, "Pessoas fisicas", "#808080")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl7, use_container_width=True)
    export_button({"Total": df_npl_total, "Pessoas juridicas": df_npl_pj, "Pessoas fisicas": df_npl_pf}, "Exportar NPL Geral")
with col6:
    fig_npl8 = make_chart_from_dfs("NPL - Recursos Direcionados", [(df_npl_dir_total, "Total", "#E07B39"), (df_npl_dir_pj, "Pessoas juridicas", "#808080"), (df_npl_dir_pf, "Pessoas fisicas", "#1F4E79")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl8, use_container_width=True)
    export_button({"Total": df_npl_dir_total, "PJ": df_npl_dir_pj, "PF": df_npl_dir_pf}, "Exportar NPL Direcionados")

st.markdown("---")
st.header("Inadimplencia por Tipo de Empresa")

df_pmes = get_bcb_series(27703, "PMEs")
df_grandes = get_bcb_series(27704, "Grandes Empresas")
df_cart_pj = get_bcb_series(27705, "PJ")
df_cart_pmes = get_bcb_series(27706, "PMEs EH")
df_cart_grandes = get_bcb_series(27707, "Grandes Empresas EH")

col7, col8 = st.columns(2)
with col7:
    fig_npl9 = make_chart_from_dfs("Inadimplencia por tipo de empresa", [(df_pmes, "PMEs", "#1F4E79"), (df_grandes, "Grandes Empresas", "#E07B39")], yaxis_title="% NPL")
    st.plotly_chart(fig_npl9, use_container_width=True)
    export_button({"PMEs": df_pmes, "Grandes Empresas": df_grandes}, "Exportar Inadimplencia Empresas")
with col8:
    fig_npl10 = make_chart_from_dfs("PJ - % da Carteira em classe E-H", [(df_cart_pj, "PJ", "#808080"), (df_cart_pmes, "PMEs", "#F0C040"), (df_cart_grandes, "Grandes Empresas", "#1F4E79")], yaxis_title="% Carteira")
    st.plotly_chart(fig_npl10, use_container_width=True)
    export_button({"PJ": df_cart_pj, "PMEs": df_cart_pmes, "Grandes Empresas": df_cart_grandes}, "Exportar Carteira E-H")

# =============================================
# SECAO 2: SALDO LIVRE PF
# =============================================

st.markdown("---")
st.header("Saldo Livre PF")

df_cheque = get_bcb_series(20573, "Cheque Especial", escala_bi=True)
df_rotativo = get_bcb_series(20587, "Cartao de Credito Rotativo", escala_bi=True)
df_parcelado = get_bcb_series(20588, "Cartao de Credito Parcelado", escala_bi=True)
df_cc3 = get_bcb_series(20589, "Outros Cartao", escala_bi=True)

fig_s1 = make_chart_from_dfs(
    "Saldo Livre PF",
    [
        (df_rotativo, "Cartao de Credito Rotativo", "#1C1C1C"),
        (df_parcelado, "Cartao de Credito Parcelado", "#1F4E79"),
        (df_cheque, "Cheque Especial", "#70AD47"),
    ],
    yaxis_title="R$ bi"
)
st.plotly_chart(fig_s1, use_container_width=True)
export_button({"Cartao Rotativo": df_rotativo, "Cartao Parcelado": df_parcelado, "Cheque Especial": df_cheque}, "Exportar Saldo Livre PF G1")

df_cc_parts = [df for df in [df_rotativo, df_parcelado, df_cc3] if not df.empty]
if df_cc_parts:
    combined_cc = df_cc_parts[0].copy()
    combined_cc.columns = ["Cartao de Credito total"]
    for dfi in df_cc_parts[1:]:
        dfi2 = dfi.copy()
        dfi2.columns = ["Cartao de Credito total"]
        combined_cc = combined_cc.add(dfi2, fill_value=0)
    df_cc_total = combined_cc
else:
    df_cc_total = pd.DataFrame(columns=["Cartao de Credito total"])

col_s1, col_s2 = st.columns(2)
with col_s1:
    fig_s2 = make_chart_from_dfs(
        "Saldo Livre PF - Cartao de Credito total",
        [(df_cc_total, "Cartao de Credito total", "#E07B39")],
        yaxis_title="R$ bi"
    )
    st.plotly_chart(fig_s2, use_container_width=True)
    export_button({"Cartao Total": df_cc_total}, "Exportar Saldo Cartao Total")

with col_s2:
    fig_s3 = go.Figure()
    yoy_data_s3 = [
        (df_cheque, "Cheque Especial", "#70AD47"),
        (df_rotativo, "Cartao de Credito Rotativo", "#1C1C1C"),
        (df_parcelado, "Cartao de Credito Parcelado", "#1F4E79"),
        (df_cc_total, "Cartao de Credito Total", "#E07B39"),
    ]
    yoy_dfs_s3 = {}
    for df_src, nome, cor in yoy_data_s3:
        yoy = calc_yoy(df_src)
        if not yoy.empty:
            col_name = yoy.columns[0]
            fig_s3.add_trace(go.Scatter(x=yoy.index, y=yoy[col_name], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
            yoy_dfs_s3[nome] = yoy
    _format_layout(fig_s3, "Saldo Livre PF YoY", "pct", "Variacao YoY (%)")
    st.plotly_chart(fig_s3, use_container_width=True)
    if yoy_dfs_s3:
        export_button(yoy_dfs_s3, "Exportar Saldo YoY G3")

df_total_pf = get_bcb_series(20570, "Total PF", escala_bi=True)

col_s3, col_s4 = st.columns(2)
with col_s3:
    fig_s4 = make_chart_from_dfs(
        "Saldo - Total PF",
        [(df_total_pf, "Total PF", "#1F4E79")],
        yaxis_title="R$ bi"
    )
    st.plotly_chart(fig_s4, use_container_width=True)
    export_button({"Total PF": df_total_pf}, "Exportar Saldo Total PF")

with col_s4:
    fig_s5 = go.Figure()
    yoy_total = calc_yoy(df_total_pf)
    if not yoy_total.empty:
        fig_s5.add_trace(go.Scatter(x=yoy_total.index, y=yoy_total["Total PF"], name="Total PF", line=dict(color="#1F4E79", width=1.5), mode='lines'))
    _format_layout(fig_s5, "Saldo YoY - Total PF", "pct", "Variacao YoY (%)")
    st.plotly_chart(fig_s5, use_container_width=True)
    export_button({"Total PF YoY": yoy_total}, "Exportar Saldo YoY Total PF")

df_rot = get_bcb_series(20579, "Rotativo", escala_bi=True)
df_consig = get_bcb_series(20572, "Consignado", escala_bi=True)
df_veic = get_bcb_series(20581, "Veiculos", escala_bi=True)

fig_s6 = make_chart_from_dfs(
    "Saldo",
    [
        (df_rot, "Rotativo", "#E07B39"),
        (df_consig, "Consignado", "#F0C040"),
        (df_veic, "Veiculos", "#1F4E79"),
    ],
    yaxis_title="R$ bi"
)
st.plotly_chart(fig_s6, use_container_width=True)
export_button({"Rotativo": df_rot, "Consignado": df_consig, "Veiculos": df_veic}, "Exportar Saldo G6")

fig_s7 = go.Figure()
yoy_dfs_s7 = {}
for df_src, nome, cor in [(df_rot, "Rotativo", "#E07B39"), (df_consig, "Consignado", "#F0C040"), (df_veic, "Veiculos", "#1F4E79")]:
    yoy = calc_yoy(df_src)
    if not yoy.empty:
        col_name = yoy.columns[0]
        fig_s7.add_trace(go.Scatter(x=yoy.index, y=yoy[col_name], name=nome, line=dict(color=cor, width=1.5), mode='lines'))
        yoy_dfs_s7[nome] = yoy
_format_layout(fig_s7, "Saldo YoY", "pct", "Variacao YoY (%)")
st.plotly_chart(fig_s7, use_container_width=True)
if yoy_dfs_s7:
    export_button(yoy_dfs_s7, "Exportar Saldo YoY G7")
