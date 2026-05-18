import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Configuração inicial
st.set_page_config(page_title="Painel NPL - BCB", layout="wide")
st.title("📊 Painel NPL - Banco Central do Brasil")

# Função para puxar séries do SGS (Banco Central)
@st.cache_data(ttl=3600)
def get_bcb_series(codigo, nome):
        data_final = datetime.today().strftime("%d/%m/%Y")
        data_inicial = (datetime.today() - timedelta(days=365*15)).strftime("%d/%m/%Y")
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
        st.error(f"Erro ao carregar série {nome} (código {codigo}): {e}")
        return pd.DataFrame(columns=[nome])

def make_chart(titulo, series_list, yaxis_title="% NPL"):
        """series_list: lista de (codigo, nome, cor)"""
        fig = go.Figure()
        for codigo, nome, cor in series_list:
                    df = get_bcb_series(codigo, nome)
                    if not df.empty:
                                    fig.add_trace(go.Scatter(
                                                        x=df.index,
                                                        y=df[nome],
                                                        name=nome,
                                                        line=dict(color=cor, width=1.5),
                                                        mode='lines'
                                    ))
                            fig.update_layout(
                    title=dict(text=titulo, x=0.5, xanchor='center'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(title=yaxis_title, gridcolor='lightgrey'),
                    legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=400,
                    margin=dict(l=40, r=20, t=60, b=80)
                    )
                return fig

# --------------- GRÁFICOS ---------------

st.header("NPL Recursos Livres PJ")

# Gráfico 1 - NPL Recursos Livres PJ (múltiplas linhas)
fig1 = make_chart(
        "NPL Recursos Livres PJ",
        [
                    (21086, "Total PJ", "#E07B39"),
                    (21093, "Capital de giro total", "#7B3F1E"),
                    (21096, "Aquisição de veículos", "#1F4E79"),
                    (21098, "Aquisição de bens total", "#5B9BD5"),
                    (21099, "Arrend. mercantil de veículos", "#70AD47"),
        ]
)
st.plotly_chart(fig1, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
        # Gráfico 2 - Capital de giro rotativo
        fig2 = make_chart(
            "NPL Recursos Livres PJ - Capital de Giro Rotativo",
            [(21092, "Capital de giro rotativo", "#C0392B")]
)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
        # Gráfico 3 - Total PJ
        fig3 = make_chart(
            "NPL Recursos Livres PJ - Total PJ",
            [(21086, "Total PJ", "#E07B39")]
)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.header("NPL Recurso Livre - PF")

col3, col4 = st.columns(2)

with col3:
        # Gráfico 4 - Total PF
        fig4 = make_chart(
            "NPL Recurso Livre - PF",
            [(21112, "Total PF", "#1F4E79")]
)
    st.plotly_chart(fig4, use_container_width=True)

with col4:
        # Gráfico 5 - Cartão de crédito rotativo
        fig5 = make_chart(
            "NPL Recurso Livre - PF",
            [(21127, "Cartão de crédito rotativo", "#C0392B")]
)
    st.plotly_chart(fig5, use_container_width=True)

# Gráfico 6 - Cheque especial, Cartão total, Cartão parcelado
fig6 = make_chart(
        "NPL Recurso Livre - PF",
        [
                    (21113, "Cheque especial", "#E07B39"),
                    (21129, "Cartão de crédito total", "#70AD47"),
                    (21128, "Cartão de crédito parcelado", "#1F4E79"),
        ]
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.header("NPL Geral - Total, PJ e PF")

col5, col6 = st.columns(2)

with col5:
        # Gráfico 7 - Total, Pessoas jurídicas, Pessoas físicas
        fig7 = make_chart(
            "NPL - Total, PJ e PF",
            [
                            (21085, "Total", "#1F4E79"),
                            (21086, "Pessoas jurídicas", "#E07B39"),
                            (21112, "Pessoas físicas", "#808080"),
            ]
)
    st.plotly_chart(fig7, use_container_width=True)

with col6:
        # Gráfico 8 - 21082, 21083, 21084
        fig8 = make_chart(
            "NPL - Total, PJ e PF (Recursos Direcionados)",
            [
                            (21082, "Total", "#E07B39"),
                            (21083, "Pessoas jurídicas", "#808080"),
                            (21084, "Pessoas físicas", "#1F4E79"),
            ]
)
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.header("Inadimplência por Tipo de Empresa e Carteira E-H")

col7, col8 = st.columns(2)

with col7:
        # Gráfico 9 - Inadimplência por tipo de empresa (PMEs e Grandes)
        fig9 = make_chart(
            "Inadimplência por tipo de empresa",
            [
                            (27703, "PMEs", "#1F4E79"),
                            (27704, "Grandes Empresas", "#E07B39"),
            ]
)
    st.plotly_chart(fig9, use_container_width=True)

with col8:
        # Gráfico 10 - PJ % da Carteira em classe E-H
        fig10 = make_chart(
            "PJ - % da Carteira em classe E-H",
            [
                            (27705, "PJ", "#808080"),
                            (27706, "PMEs", "#F0C040"),
                            (27707, "Grandes Empresas", "#1F4E79"),
            ]
)
    st.plotly_chart(fig10, use_container_width=True)
