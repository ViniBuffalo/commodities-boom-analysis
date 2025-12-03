import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Econômico", layout="wide")

st.title("Dashboard Econômico - Vários Países")
st.markdown(
    "Compare indicadores de diferentes países (PIB, inflação e desemprego). "
    "Escolha o país, ajuste o intervalo de anos e o indicador para analisar."
)

# --- Mapeia nomes de arquivos ---
arquivos = {
    "Brasil": "tabela_brasil.csv",
    "Colômbia": "tabela_colombia.csv",
    "Equador": "tabela_equador.csv",
    "Chile": "tabela_chile.csv",
}

# Escolha do dataset por dropbox
pais = st.sidebar.selectbox("Selecione o país", list(arquivos.keys()))

# Carrega o CSV escolhido
df = pd.read_csv(arquivos[pais])

# limpeza básica de colunas e tipos
df.columns = df.columns.str.strip()

# Conversão do Ano para inteiro
df["Ano"] = pd.to_numeric(df["Ano"].astype(str).str.strip(), errors="coerce").astype("Int64")
df = df.dropna(subset=["Ano"])
df["Ano"] = df["Ano"].astype(int)

# Converte explicitamente todas as colunas numéricas esperadas
for col in ["Cresc Pib em %", "Inflação em %", "Desemprego em %"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".").str.strip(), errors="coerce")

# --- Filtros na barra lateral ---
st.sidebar.header("Filtros")

min_ano, max_ano = int(df["Ano"].min()), int(df["Ano"].max())
anos_sel = st.sidebar.slider(
    "Selecione o intervalo de anos",
    min_value=min_ano,
    max_value=max_ano,
    value=(min_ano, max_ano),
    step=1,
)

map_colunas = {
    "Crescimento do PIB (%)": "Cresc Pib em %",
    "Inflação (%)": "Inflação em %",
    "Desemprego (%)": "Desemprego em %",
}
indicador_legivel = st.sidebar.selectbox(
    "Indicador para análise",
    options=list(map_colunas.keys()),
    index=0,
)
coluna_indicador = map_colunas[indicador_legivel]

tipo_grafico = st.sidebar.radio(
    "Tipo de gráfico",
    options=["Linha", "Barras"],
    index=0,
)

# --- Filtragem por ano e limpeza final ---
df_filtrado = df[(df["Ano"] >= anos_sel[0]) & (df["Ano"] <= anos_sel[1])].copy()
df_filtrado = df_filtrado.sort_values("Ano").reset_index(drop=True)

if coluna_indicador in df_filtrado.columns:
    df_filtrado[coluna_indicador] = pd.to_numeric(df_filtrado[coluna_indicador], errors="coerce")

# --- KPIs ---
st.subheader(f"Indicadores de destaque - {pais} (período filtrado)")

col1, col2, col3 = st.columns(3)

# Calcula médias
media_pib = pd.to_numeric(df_filtrado.get("Cresc Pib em %", pd.Series(dtype=float)), errors="coerce").mean()
media_inflacao = pd.to_numeric(df_filtrado.get("Inflação em %", pd.Series(dtype=float)), errors="coerce").mean()
media_desemprego = pd.to_numeric(df_filtrado.get("Desemprego em %", pd.Series(dtype=float)), errors="coerce").mean()

col1.metric("PIB médio (%)", f"{media_pib:.2f}" if pd.notna(media_pib) else "N/A")
col2.metric("Inflação média (%)", f"{media_inflacao:.2f}" if pd.notna(media_inflacao) else "N/A")
col3.metric("Desemprego médio (%)", f"{media_desemprego:.2f}" if pd.notna(media_desemprego) else "N/A")

# --- Tabela e gráfico ---
st.subheader(f"Tabela de dados filtrados - {pais}")
st.dataframe(df_filtrado, width="stretch")

st.subheader(f"Evolução de {indicador_legivel} - {pais}")

if coluna_indicador in df_filtrado.columns:
    df_plot = df_filtrado[["Ano", coluna_indicador]].copy()
    df_plot["Ano"] = df_plot["Ano"].astype(str)
    df_plot = df_plot.set_index("Ano")
else:
    df_plot = pd.DataFrame(
        {coluna_indicador: []},
        index=df_filtrado["Ano"].astype(str).unique()
    ).sort_index()

# Mostra gráficos com base no tipo selecionado
if tipo_grafico == "Linha":
    st.line_chart(df_plot, width="stretch")
else:
    st.bar_chart(df_plot, width="stretch")

st.caption("Dados carregados automaticamente a partir dos arquivos CSV do diretório.")