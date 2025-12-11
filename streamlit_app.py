import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Global 2052",
    layout="wide"
)

st.title("🌍 Dashboard Global 2052 – Projeções Mundiais")
st.markdown("Dados originais do relatório *2052 - Ulrich Golüke*. Dashboard criado por **Altamir Filgueiras**.")

# ===============================
# 1. Carregamento dos Dados
# ===============================
uploaded_file = st.file_uploader("📂 Envie a planilha 2052 (arquivo XLSX)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheets = xls.sheet_names

    st.sidebar.header("Configurações")
    selected_sheet = st.sidebar.selectbox("Escolha uma região", sheets)

    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    st.subheader(f"📑 Aba selecionada: **{selected_sheet}**")
    st.dataframe(df.head())

    # ===============================
    # 2. Processamento Automático
    # ===============================
    # Busca coluna com anos (normalmente algo como 'Year', 'Ano', ou primeira coluna numérica)
    year_col_candidates = [c for c in df.columns if df[c].dtype in [int, float]]
    year_col = year_col_candidates[0]

    # Transforma o dataframe se estiver no formato horizontal
    if df[year_col].count() < 10:  
        df = df.set_index(df.columns[0]).T.reset_index()
        df.rename(columns={"index": "Year"}, inplace=True)

    # ===============================
    # 3. Seleção de Métricas
    # ===============================
    metric = st.sidebar.selectbox("Selecione a métrica para visualizar", df.columns[1:])
    st.subheader(f"📈 Evolução de **{metric}** ao longo do tempo")

    fig = px.line(df, x="Year", y=metric, title=f"{metric} – {selected_sheet}")
    st.plotly_chart(fig, use_container_width=True)

    # ===============================
    # 4. Comparação Entre Regiões
    # ===============================
    st.subheader("🌎 Comparação entre Regiões")

    all_data = {}
    for sheet in sheets:
        temp = pd.read_excel(uploaded_file, sheet_name=sheet)
        temp = temp.set_index(temp.columns[0]).T.reset_index()
        temp.rename(columns={"index": "Year"}, inplace=True)
        if metric in temp.columns:
            all_data[sheet] = temp[["Year", metric]]

    combined = pd.concat(
        [df.assign(Region=sheet) for sheet, df in all_data.items()],
        ignore_index=True
    )

    fig2 = px.line(
        combined,
        x="Year",
        y=metric,
        color="Region",
        title=f"Comparação Global – {metric}"
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("☝️ Envie o arquivo XLSX para iniciar o dashboard.")
