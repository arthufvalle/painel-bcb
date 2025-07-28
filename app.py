import streamlit as st
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

# Configuração inicial
st.set_page_config(page_title="Painel Macroeconômico - BCB", layout="wide")
st.title("📊 Painel Macroeconômico - Banco Central do Brasil")

# Função para puxar séries do SGS via pandas_datareader
def get_bcb_series(codigo, nome):
    try:
        start = datetime(2000, 1, 1)  # início da série
        df = web.DataReader(f"SGS{codigo}", "sgs", start)
        df = df.rename(columns={f"SGS{codigo}": nome})
        return df
    except Exception as e:
        st.error(f"Erro ao carregar série {nome}: {e}")
        return pd.DataFrame(columns=[nome])

# Séries do Banco Central
series_dict = {
    "Selic Meta (%)": 432,
    "IPCA (%)": 433,
    "Câmbio (R$/US$)": 3697
}

# Caixa de seleção
opcao = st.selectbox("Selecione a série", list(series_dict.keys()))

# Buscar dados
df = get_bcb_series(series_dict[opcao], opcao)

# Mostrar resultados
if not df.empty:
    st.line_chart(df)
    st.subheader("📌 Últimos Dados")
    st.write(df.tail(5))
    st.metric(opcao, f"{df.iloc[-1,0]:.2f}")
else:
    st.warning("⚠️ Não foi possível carregar dados desta série no momento. Tente novamente mais tarde.")



