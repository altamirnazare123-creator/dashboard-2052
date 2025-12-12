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
    # Lê apenas o necessário — mais seguro no Streamlit Cloud
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
    # Identificar possível coluna de anos
    year_col = None

    for col in df.columns:
        # Tenta converter — se der certo, é coluna de ano
        try:
            if df[col].dropna().astype(int).between(1900, 2100).all():
                year_col = col
                break
        except:
            pass

    # Se não encontrou, assume formato horizontal e transpõe
    if year_col is None:
        df = df.set_index(df.columns[0]).T.reset_index()
        df.rename(columns={"index": "Year"}, inplace=True)
        df["Year"] = df["Year"].astype(int)
        year_col = "Year"

    # ===============================
    # 3. Seleção de Métricas
    # ===============================
    metric_options = [c for c in df.columns if c != year_col]
    metric = st.sidebar.selectbox("Selecione a métrica para visualizar", metric_options)

    st.subheader(f"📈 Evolução de **{metric}** ao longo do tempo")

    fig = px.line(df, x=year_col, y=metric, title=f"{metric} – {selected_sheet}")
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

        try:
            temp["Year"] = temp["Year"].astype(int)
        except:
            continue

        if metric in temp.columns:
            all_data[sheet] = temp[["Year", metric]]

    combined = pd.concat(
        [d.assign(Region=s) for s, d in all_data.items()],
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
