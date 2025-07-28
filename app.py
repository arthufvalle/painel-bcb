import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Painel Macroeconômico - BCB", layout="wide")
st.title("📊 Painel Macroeconômico - Banco Central do Brasil")

def get_bcb_series(codigo, nome, start="01/01/2000"):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={start}&dataFinal=31/12/2099"
    headers = {"User-Agent": "Mozilla/5.0"}  # para evitar erro 406
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
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
        st.error(f"Erro ao carregar série {nome}: {e}")
        return pd.DataFrame(columns=[nome])

# Séries SGS
series_dict = {
    "Selic Meta (%)": 432,
    "IPCA (%)": 433,
    "Câmbio (R$/US$)": 3697
}

opcao = st.selectbox("Selecione a série", list(series_dict.keys()))
df = get_bcb_series(series_dict[opcao], opcao)

if not df.empty:
    st.line_chart(df)
    st.subheader("📌 Últimos Dados")
    st.write(df.tail(5))
    st.metric(opcao, f"{df.iloc[-1,0]:.2f}")
else:
    st.warning("⚠️ Não foi possível carregar dados desta série no momento. Tente novamente mais tarde.")



