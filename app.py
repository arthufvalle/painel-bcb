import streamlit as st
import pandas as pd
import requests

# Configurações iniciais do app
st.set_page_config(page_title="Painel Macroeconômico - BCB", layout="wide")
st.title("📊 Painel Macroeconômico - Banco Central do Brasil")

# Função para puxar séries do SGS (Banco Central)
def get_bcb_series(codigo, nome):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data:  # se vier vazio
            return pd.DataFrame(columns=[nome])
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        df = df.set_index('data')
        df = df.rename(columns={'valor': nome})
        return df
    except Exception as e:
        st.error(f"Erro ao carregar série {nome}: {e}")
        return pd.DataFrame(columns=[nome])

# Séries do Banco Central (códigos SGS)
series_dict = {
    "Selic Meta (%)": 432,
    "IPCA (%)": 433,
    "Câmbio (R$/US$)": 3697
}

# Seletor de série
opcao = st.selectbox("Selecione a série", list(series_dict.keys()))

# Puxar dados
df = get_bcb_series(series_dict[opcao], opcao)

# Mostrar resultados
if not df.empty:
    st.line_chart(df)
    st.subheader("📌 Últimos Dados")
    st.write(df.tail(5))
    st.metric(opcao, f"{df.iloc[-1,0]:.2f}")
else:
    st.warning("⚠️ Não foi possível carregar dados desta série no momento. Tente novamente mais tarde.")

