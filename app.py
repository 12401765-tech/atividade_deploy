from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cuidados", layout="wide", page_icon="📊")

@st.cache_data
def carregar_dados():
    caminho = Path(__file__).resolve().parent / "Tabela 1.1.2.xls"
    
    df = pd.read_excel(caminho, engine = "xlrd")
   
    if "Ano" not in df.columns:
        for i in range(min(len(df), 15)):
            if "Ano" in df.iloc[i].values:
                df.columns = df.iloc[i]
                df = df.iloc[i+1:].reset_index(drop=True)
                break

    df.columns = [str(col).strip() for col in df.columns]

    colunas_obrigatorias = ["Ano", "Localidade", "Total", "Homem", "Mulher"]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            raise KeyError(f"A coluna '{col}' não foi encontrada. Colunas lidas: {list(df.columns)}")

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").fillna(0).astype(int)
    for coluna in ["Total", "Homem", "Mulher"]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
        
    return df

try:
    df = carregar_dados()
    st.sidebar.header("Filtros")
    anos_disponiveis = sorted(df["Ano"].unique().tolist(), reverse=True)
    anos_disponiveis = [ano for ano in anos_disponiveis if ano > 0]
    
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", anos_disponiveis)
    localidades_disponiveis = df["Localidade"].dropna().unique().tolist()
    
    regioes_padrao = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
    default_selecionadas = [r for r in regioes_padrao if r in localidades_disponiveis]
    if not default_selecionadas and localidades_disponiveis:
        default_selecionadas = localidades_disponiveis[:5]

    localidades_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões/UFs:", options=localidades_disponiveis,
        default=default_selecionadas
    )
    
    st.title("Horas Dedicadas a Cuidados e Afazeres Domésticos")
    st.markdown("Análise da média de horas semanais dedicadas por pessoas ocupadas de 14 anos ou mais, por sexo.")
    st.caption("Fonte: IBGE, PNAD Contínua — Tabela 1.1.2. Anos disponíveis: 2016, 2017, 2018, 2019 e 2022. Valores totais por sexo, sem recorte etário.")
    
    df_filtrado = df[(df["Ano"] == ano_selecionado) & (df["Localidade"].isin(localidades_selecionadas))]
    
    if not df_filtrado.empty:
        st.subheader(f"Dados em Tabela ({ano_selecionado})")
        st.dataframe(df_filtrado[["Localidade", "Total", "Homem", "Mulher"]].reset_index(drop=True), use_container_width=True)
        st.markdown("---")
        st.subheader("Gráficos Comparativos")
        col1, col2 = st.columns(2)
        with col1:
            df_melted = df_filtrado.melt(id_vars=["Localidade"], value_vars=["Homem", "Mulher"], var_name="Gênero", value_name="Horas Semanais")
            fig_bar = px.bar(df_melted, x="Localidade", y="Horas Semanais", color="Gênero", barmode="group", title=f"Média de Horas por Gênero ({ano_selecionado})", color_discrete_sequence=["#1f77b4", "#e377c2"], labels={"Horas Semanais": "Horas/Semana", "Localidade": "Região / UF"})
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            df_historico = df[df["Localidade"].isin(localidades_selecionadas)].sort_values("Ano")
            fig_line = px.line(df_historico, x="Ano", y="Total", color="Localidade", markers=True, title="Evolução Temporal do Total de Horas Dedicadas", labels={"Total": "Horas/Semana", "Ano": "Ano"})
            fig_line.update_xaxes(type="category")
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Nenhuma localidade selecionada nos filtros da barra lateral.")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.info("Confira se 'Tabela 1.1.2.xls' está na mesma pasta que 'app.py'.")