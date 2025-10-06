import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Acidentes em Rodovias Federais",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO E PREPARAÇÃO DE DADOS
# -------------------------------------------------------------------

@st.cache_data(show_spinner="Carregando e processando dados...")
def load_data(path: str) -> pd.DataFrame:
    """
    Carrega e pré-processa os dados de acidentes a partir de um arquivo CSV consolidado.
    """
    if not os.path.exists(path):
        st.error(f"Arquivo de dados não encontrado: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path, encoding='latin-1', sep=';', low_memory=False)

    df['data_inversa'] = pd.to_datetime(df['data_inversa'], errors='coerce')
    df.dropna(subset=['data_inversa'], inplace=True)
    df['year'] = df['data_inversa'].dt.year.astype(int)
    
    df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S', errors='coerce').dt.time

    for col in ['km', 'latitude', 'longitude']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

    df['TOTAL_FERIDOS'] = df['feridos_leves'].fillna(0) + df['feridos_graves'].fillna(0)
    
    for col in ['mortos', 'veiculos', 'pessoas']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    df['br'] = pd.to_numeric(df['br'], errors='coerce').fillna(0).astype(int)
    
    bins = [-1, 5, 11, 17, 23]
    labels = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
    df['periodo_dia'] = pd.cut(df['data_inversa'].dt.hour, bins=bins, labels=labels, include_lowest=True, right=True)
    df['periodo_dia'] = df['periodo_dia'].cat.add_categories(['DESCONHECIDO']).fillna('DESCONHECIDO')
    
    dias_semana_map = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
    df['dia_semana'] = df['data_inversa'].dt.dayofweek.map(dias_semana_map)

    return df

def calcular_indice_periculosidade(df: pd.DataFrame):
    if df.empty or 'br' not in df.columns or 'mortos' not in df.columns:
        return pd.DataFrame(columns=['br', 'indice'])

    g = df.groupby("br").agg(ocorrencias=("br", "size"), mortes=("mortos", "sum")).reset_index()
    if g.empty or g["ocorrencias"].max() == 0 or g["mortes"].max() == 0:
        return g.assign(indice=0.0)
        
    g["indice"] = (0.4 * (g["ocorrencias"] / g["ocorrencias"].max()) + 0.6 * (g["mortes"] / g["mortes"].max())) * 10
    return g.sort_values("indice", ascending=False)

# -------------------------------------------------------------------
# CARREGAMENTO INICIAL DOS DADOS E CACHE DE OPÇÕES DE FILTRO
# -------------------------------------------------------------------
df_original = load_data('base_acidente.csv')

if df_original.empty:
    st.stop()

# Cache das opções para evitar recálculos
@st.cache_data
def get_filter_options(df):
    anos = sorted(df['year'].unique(), reverse=True)
    ufs = ["Todos"] + sorted(df['uf'].unique())
    brs = ["Todas"] + sorted(df['br'].unique())
    causas = ["Todas"] + sorted(df['causa_acidente'].unique())
    tipos = ["Todos"] + sorted(df['tipo_acidente'].unique())
    return anos, ufs, brs, causas, tipos

anos, ufs, brs, causas, tipos = get_filter_options(df_original)

# -------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR) DE FILTROS
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://www.gov.br/prf/pt-br/imagens/brasao-prf-2019-vertical.png", width=120)
    st.title("Filtros da API")
    st.markdown("Filtre os dados de acidentes com base nos parâmetros da API.")

    # Inicializar estado da sessão para os filtros
    if 'clear' in st.session_state and st.session_state.clear:
        st.session_state.ano = anos[0]
        st.session_state.uf = "Todos"
        st.session_state.br = "Todas"
        st.session_state.causa = "Todas"
        st.session_state.tipo = "Todos"
        st.session_state.clear = False

    selected_ano = st.selectbox("Ano", anos, key='ano')
    selected_uf = st.selectbox("Estado (UF)", ufs, key='uf')
    selected_br = st.selectbox("Rodovia (BR)", brs, key='br')
    selected_causa = st.selectbox("Causa do Acidente", causas, key='causa')
    selected_tipo = st.selectbox("Tipo de Acidente", tipos, key='tipo')
    
    st.markdown("---")
    if st.button("Limpar Filtros"):
        st.session_state.clear = True
        st.rerun()

    st.markdown("---")
    st.caption("Dashboard desenvolvido com base na estrutura da API FastAPI.")

# -------------------------------------------------------------------
# APLICAÇÃO DOS FILTROS AO DATAFRAME
# -------------------------------------------------------------------
df_filtered = df_original.copy()

# Aplica filtros sequencialmente
if selected_ano:
    df_filtered = df_filtered[df_filtered['year'] == selected_ano]
if selected_uf != "Todos":
    df_filtered = df_filtered[df_filtered['uf'] == selected_uf]
if selected_br != "Todas":
    df_filtered = df_filtered[df_filtered['br'] == selected_br]
if selected_causa != "Todas":
    df_filtered = df_filtered[df_filtered['causa_acidente'] == selected_causa]
if selected_tipo != "Todos":
    df_filtered = df_filtered[df_filtered['tipo_acidente'] == selected_tipo]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste as opções.")
    st.stop()

# -------------------------------------------------------------------
# CONTEÚDO PRINCIPAL DO DASHBOARD
# -------------------------------------------------------------------
st.title("🚗 Análise Interativa de Acidentes em Rodovias Federais")
st.markdown(f"Exibindo **{len(df_filtered):,}** registros para os filtros selecionados.")

# --- ABAS DE NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs([
    "📊 Estatísticas Gerais",
    "🗺️ Análise Geográfica",
    "⏰ Análise Temporal"
])

# --- CONTEÚDO DA ABA 1: ESTATÍSTICAS GERAIS ---
with tab1:
    st.header("Visão Geral das Estatísticas")

    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total de Acidentes", f"{len(df_filtered):,}".replace(",", "."))
    kpi2.metric("Total de Mortes", f"{int(df_filtered['mortos'].sum()):,}".replace(",", "."))
    kpi3.metric("Total de Feridos", f"{int(df_filtered['TOTAL_FERIDOS'].sum()):,}".replace(",", "."))

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Causas de Acidentes")
        causa_counts = df_filtered['causa_acidente'].value_counts().nlargest(10)
        fig_causa = px.bar(causa_counts, y=causa_counts.index, x=causa_counts.values, orientation='h',
                           labels={'y': '', 'x': 'Número de Ocorrências'}, template='plotly_white')
        fig_causa.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_causa, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Tipos de Acidentes")
        tipo_counts = df_filtered['tipo_acidente'].value_counts().nlargest(10)
        fig_tipo = px.bar(tipo_counts, y=tipo_counts.index, x=tipo_counts.values, orientation='h',
                          labels={'y': '', 'x': 'Número de Ocorrências'}, template='plotly_white')
        fig_tipo.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_tipo, use_container_width=True)

# --- CONTEÚDO DA ABA 2: ANÁLISE GEOGRÁFICA ---
with tab2:
    st.header("Pontos de Acidente e Trechos Perigosos")
    
    # Mapa de pontos de acidente
    st.subheader("Distribuição Geográfica dos Acidentes (Amostra Aleatória)")
    st.caption("Mostrando uma amostra de até 2000 pontos para melhor performance.")
    map_data = df_filtered[['latitude', 'longitude', 'mortos']].dropna()
    
    if not map_data.empty:
        sample_size = min(len(map_data), 2000)
        map_data_sample = map_data.sample(sample_size, random_state=42)

        fig_map = px.scatter_mapbox(
            map_data_sample,
            lat="latitude",
            lon="longitude",
            color="mortos",
            color_continuous_scale=px.colors.sequential.Reds,
            size_max=15,
            zoom=3.5,
            mapbox_style="carto-positron",
            hover_name=None,
            hover_data={'mortos': True, 'latitude': ':.4f', 'longitude': ':.4f'}
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Sem dados de geolocalização para os filtros atuais.")
        
    st.markdown("---")
    
    # Gráfico de Trechos Perigosos
    st.subheader("Ranking de Rodovias por Índice de Periculosidade")
    indice_br = calcular_indice_periculosidade(df_filtered)
    
    if not indice_br.empty:
        fig_br = px.bar(
            indice_br.head(20), x="indice", y="br",
            orientation='h',
            labels={"indice": "Índice de Periculosidade (0-10)", "br": "Rodovia (BR)"},
            text='indice',
            template='plotly_white'
        )
        fig_br.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_br.update_yaxes(categoryorder="total ascending", tickprefix="BR-")
        st.plotly_chart(fig_br, use_container_width=True)
    else:
        st.info("Não há dados suficientes para calcular o índice de periculosidade com os filtros atuais.")

# --- CONTEÚDO DA ABA 3: ANÁLISE TEMPORAL ---
with tab3:
    st.header("Distribuição de Acidentes ao Longo do Tempo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Acidentes por Dia da Semana")
        dias_ordem = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        weekly_accidents = df_filtered['dia_semana'].value_counts().reindex(dias_ordem)
        fig_weekly = px.bar(weekly_accidents, x=weekly_accidents.index, y=weekly_accidents.values,
                            labels={'x': 'Dia da Semana', 'y': 'Número de Acidentes'}, template='plotly_white')
        st.plotly_chart(fig_weekly, use_container_width=True)

    with col2:
        st.subheader("Acidentes por Período do Dia")
        periodo_ordem = ['Manhã', 'Tarde', 'Noite', 'Madrugada', 'DESCONHECIDO']
        periodo_counts = df_filtered['periodo_dia'].value_counts().reindex(periodo_ordem)
        fig_periodo = px.bar(periodo_counts, y=periodo_counts.values, x=periodo_counts.index,
                             labels={'y': 'Número de Acidentes', 'x': 'Período do Dia'}, template='plotly_white')
        st.plotly_chart(fig_periodo, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Distribuição de Acidentes por Hora")
    hourly_accidents = df_filtered['data_inversa'].dt.hour.value_counts().sort_index()
    fig_hourly = px.bar(hourly_accidents, x=hourly_accidents.index, y=hourly_accidents.values,
                        labels={'x': 'Hora do Dia (0-23)', 'y': 'Número de Acidentes'}, template='plotly_white')
    st.plotly_chart(fig_hourly, use_container_width=True)