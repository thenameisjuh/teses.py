import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Dissertações UMinho", layout="wide")

# Estilo CSS para tons de azul e aspeto académico
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1, h2, h3 { color: #003366; font-family: 'Helvetica', sans-serif; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border-left: 5px solid #00509E; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    file_path = 'humanidades_digitais_def..csv'
    if not os.path.exists(file_path):
        return None
    
    # Lemos com separador ; conforme o teu ficheiro
    df = pd.read_csv(file_path, sep=';')
    
    # Tratamento básico de dados
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
    df['primary_category_label'] = df['primary_category_label'].fillna('Não Categorizado')
    return df

df = load_data()

if df is None:
    st.error("Erro: Ficheiro CSV não encontrado. Garante que o nome é 'humanidades_digitais_def..csv'")
    st.stop()

# --- SIDEBAR (FILTROS) ---
st.sidebar.image("elach.png", width=150) # Logo genérico se quiseres
st.sidebar.title("Filtros")

# Filtro de Anos (removendo o ano 0 se existir)
anos_disponiveis = sorted([int(a) for a in df['year'].unique() if a > 0])
selected_years = st.sidebar.multiselect("Selecionar Anos", anos_disponiveis, default=anos_disponiveis)

# Filtro de Tipo de Trabalho
tipos = df['document_type_normalized'].unique().tolist()
selected_types = st.sidebar.multiselect("Tipo de Trabalho", tipos, default=tipos)

# Aplicar filtros
df_filtered = df[(df['year'].isin(selected_years)) & (df['document_type_normalized'].isin(selected_types))]

# --- DASHBOARD PRINCIPAL ---
st.title("🎓 Projeto Integrado: Dissertações UMinho")
st.markdown("### Análise de Humanidades Digitais")

# KPIs
m1, m2, m3 = st.columns(3)
m1.metric("Total de Teses", len(df_filtered))
m2.metric("Nº de Autores", df_filtered['primary_author'].nunique())
m3.metric("Idiomas", df_filtered['language'].nunique())

st.write("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Produção por Ano")
    df_year = df_filtered[df_filtered['year'] > 0].groupby('year').size().reset_index(name='Total')
    fig_year = px.line(df_year, x='year', y='Total', markers=True, 
                       color_discrete_sequence=['#003366'])
    fig_year.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_year, use_container_width=True)

with col2:
    st.subheader("📂 Categorias Principais")
    df_cat = df_filtered['primary_category_label'].value_counts().head(8).reset_index()
    fig_cat = px.bar(df_cat, x='count', y='primary_category_label', orientation='h',
                     color_discrete_sequence=['#00509E'])
    fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cat, use_container_width=True)

# Tabela de Dados
st.write("---")
st.subheader("🔍 Listagem de Trabalhos")
st.dataframe(
    df_filtered[['year', 'primary_author', 'title', 'primary_category_label']],
    column_config={
        "year": "Ano",
        "primary_author": "Autor",
        "title": "Título",
        "primary_category_label": "Área"
    },
    hide_index=True,
    use_container_width=True
)

st.info("💡 Dica: Podes filtrar os dados na barra lateral para atualizar os gráficos em tempo real.")