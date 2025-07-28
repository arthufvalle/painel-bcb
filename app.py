import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Painel Macroeconômico - BCB", layout="wide")
st.title("📊 Painel Macroeconômico - Banco Central do Brasil")

# Função para puxar séries do SGS (Banco Central)
def get_bcb_series(codigo, nome):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    r = requests.get(url)
    df = pd.DataFrame(r.json())
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df['valor'] = df['valor'].astype(float)
    df = df.set_index('data')
    df = df.rename(columns={'valor': nome})
    return df

# Séries do Banco Central (códigos SGS)
series_dict = {
    "Selic Meta (%)": 432,
    "IPCA (%)": 433,
    "Câmbio (R$/US$)": 3697
}

# Selecionar série
opcao = st.selectbox("Selecione a série", list(series_dict.keys()))

# Puxar dados
df = get_bcb_series(series_dict[opcao], opcao)

# Mostrar gráfico
st.line_chart(df)

# Mostrar últimos valores
st.subheader("📌 Últimos Dados")
st.write(df.tail(5))

# Mostrar métrica do último valor
st.metric(opcao, f"{df.iloc[-1,0]:.2f}")
