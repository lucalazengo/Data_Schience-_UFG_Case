"""RoadInfra BI - Dashboard Principal
===================================

Dashboard interativo para análise de acidentes rodoviários no Brasil,
baseado em dados do DATATRAN com foco em segmentos críticos.

Autor: RoadInfra BI Team
Data: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar componentes do dashboard
try:
    from dashboard.components.charts import (
        create_kpi_cards, create_temporal_analysis, create_cause_analysis,
        create_accident_type_analysis, create_seasonal_analysis, 
        create_recommendations_panel
    )
    from dashboard.components.interactive_filters import (
        create_scenario_filters, apply_filters_to_data, simulate_interventions,
        create_scenario_comparison, create_filter_summary, reset_session_filters
    )
    from dashboard.components.user_experience import enhance_user_experience, add_notification
except ImportError:
    # Fallback para quando os componentes não estão disponíveis
    pass

# Imports dos módulos do projeto
try:
    from data_processing.data_cleaner import DataCleaner
    from data_processing.segment_creator import SegmentCreator
    from risk_modeling.risk_calculator import RiskCalculator, RiskWeights
    from risk_modeling.blackspot_ranker import BlackSpotRanker, RankingCriteria
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="RoadInfra BI - Dashboard de Segurança Viária",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .danger-card {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .warning-card {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
    }
    .success-card {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    .sidebar-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_sample_data():
    """
    Carrega dados de exemplo para demonstração.
    Em produção, isso seria substituído pela carga dos dados reais do DATATRAN.
    """
    np.random.seed(42)
    
    # Estados e BRs mais relevantes
    estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'ES', 'MT']
    brs = [101, 116, 381, 40, 50, 153, 262, 277, 290, 324]
    anos = list(range(2017, 2025))
    
    # Gera dados sintéticos realistas
    data = []
    segment_id = 0
    
    for uf in estados:
        for br in np.random.choice(brs, size=3, replace=False):
            for km_start in range(0, 500, 20):  # Segmentos de 20km
                segment_id += 1
                km_end = km_start + 20
                
                # Simula dados por ano
                for ano in anos:
                    # Fatores de risco baseados em características reais
                    urban_factor = 1.5 if km_start < 100 else 1.0  # Trechos urbanos mais perigosos
                    br_factor = 1.3 if br in [101, 116, 40] else 1.0  # BRs mais movimentadas
                    
                    # Gera acidentes com distribuição realista
                    base_accidents = np.random.poisson(3 * urban_factor * br_factor)
                    
                    mortos = np.random.poisson(base_accidents * 0.08)
                    feridos_graves = np.random.poisson(base_accidents * 0.15)
                    feridos_leves = np.random.poisson(base_accidents * 0.35)
                    total_acidentes = base_accidents
                    
                    # Coordenadas aproximadas (para demonstração)
                    lat_base = {'SP': -23.5, 'RJ': -22.9, 'MG': -19.9, 'RS': -30.0, 'PR': -25.4,
                               'SC': -27.6, 'BA': -12.9, 'GO': -16.7, 'ES': -20.3, 'MT': -15.6}
                    lng_base = {'SP': -46.6, 'RJ': -43.2, 'MG': -43.9, 'RS': -51.2, 'PR': -49.3,
                               'SC': -48.5, 'BA': -38.5, 'GO': -49.2, 'ES': -40.3, 'MT': -56.1}
                    
                    lat = lat_base[uf] + np.random.uniform(-2, 2)
                    lng = lng_base[uf] + np.random.uniform(-2, 2)
                    
                    data.append({
                        'segmento_id': f'{uf}_BR{br:03d}_KM{km_start:04d}_{km_end:04d}',
                        'uf': uf,
                        'br': br,
                        'km_inicial': km_start,
                        'km_final': km_end,
                        'ano': ano,
                        'total_acidentes': total_acidentes,
                        'mortos': mortos,
                        'feridos_graves': feridos_graves,
                        'feridos_leves': feridos_leves,
                        'latitude': lat,
                        'longitude': lng,
                        'extensao_km': 20,
                        'anos_com_dados': len(anos)
                    })
    
    return pd.DataFrame(data)


@st.cache_data
def process_data(df):
    """
    Processa os dados aplicando limpeza, criação de segmentos e cálculo de risco.
    """
    # Simula o processamento (em produção usaria os módulos reais)
    df_processed = df.copy()
    
    # Calcula índice de periculosidade
    calculator = RiskCalculator()
    
    # Agrega dados por segmento
    df_agg = df_processed.groupby(['segmento_id', 'uf', 'br', 'km_inicial', 'km_final', 'latitude', 'longitude']).agg({
        'total_acidentes': 'sum',
        'mortos': 'sum',
        'feridos_graves': 'sum',
        'feridos_leves': 'sum',
        'extensao_km': 'first',
        'anos_com_dados': 'first'
    }).reset_index()
    
    # Calcula risco
    df_with_risk, risk_report = calculator.calculate_risk_pipeline(df_agg)
    
    # Gera ranking
    ranker = BlackSpotRanker()
    df_ranked = ranker.generate_ranking(df_with_risk)
    
    return df_processed, df_ranked, risk_report


def create_sidebar_filters(df):
    """
    Cria filtros na sidebar.
    """
    st.sidebar.markdown('<div class="sidebar-info"><h3>🎛️ Filtros de Análise</h3></div>', unsafe_allow_html=True)
    
    # Filtro de UF
    ufs_available = sorted(df['uf'].unique())
    selected_ufs = st.sidebar.multiselect(
        "Estados (UF)",
        options=ufs_available,
        default=ufs_available[:5],
        help="Selecione os estados para análise"
    )
    
    # Filtro de BR
    brs_available = sorted(df['br'].unique())
    selected_brs = st.sidebar.multiselect(
        "Rodovias (BR)",
        options=brs_available,
        default=brs_available[:5],
        help="Selecione as rodovias federais"
    )
    
    # Filtro de Ano
    if 'ano' in df.columns:
        anos_available = sorted(df['ano'].unique())
        selected_years = st.sidebar.slider(
            "Período de Análise",
            min_value=min(anos_available),
            max_value=max(anos_available),
            value=(min(anos_available), max(anos_available)),
            help="Selecione o período para análise"
        )
    else:
        selected_years = None
    
    # Filtro de Nível de Risco
    if 'nivel_risco' in df.columns:
        risk_levels = df['nivel_risco'].unique()
        selected_risk_levels = st.sidebar.multiselect(
            "Níveis de Risco",
            options=risk_levels,
            default=risk_levels,
            help="Filtre por nível de risco"
        )
    else:
        selected_risk_levels = None
    
    return {
        'ufs': selected_ufs,
        'brs': selected_brs,
        'years': selected_years,
        'risk_levels': selected_risk_levels
    }


def apply_filters(df, filters):
    """
    Aplica filtros ao DataFrame.
    """
    df_filtered = df.copy()
    
    # Filtro UF
    if filters['ufs']:
        df_filtered = df_filtered[df_filtered['uf'].isin(filters['ufs'])]
    
    # Filtro BR
    if filters['brs']:
        df_filtered = df_filtered[df_filtered['br'].isin(filters['brs'])]
    
    # Filtro Anos
    if filters['years'] and 'ano' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['ano'] >= filters['years'][0]) & 
            (df_filtered['ano'] <= filters['years'][1])
        ]
    
    # Filtro Nível de Risco
    if filters['risk_levels'] and 'nivel_risco' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['nivel_risco'].isin(filters['risk_levels'])]
    
    return df_filtered


def create_kpi_cards(df):
    """
    Cria cards com KPIs principais.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_segments = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛣️ Segmentos Analisados</h3>
            <h2>{total_segments:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_accidents = df['total_acidentes'].sum() if 'total_acidentes' in df.columns else 0
        st.markdown(f"""
        <div class="warning-card">
            <h3>🚗 Total de Acidentes</h3>
            <h2>{total_accidents:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_deaths = df['mortos'].sum() if 'mortos' in df.columns else 0
        st.markdown(f"""
        <div class="danger-card">
            <h3>💀 Total de Mortos</h3>
            <h2>{total_deaths:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if 'indice_periculosidade' in df.columns:
            avg_risk = df['indice_periculosidade'].mean()
            st.markdown(f"""
            <div class="success-card">
                <h3>📊 Índice Médio</h3>
                <h2>{avg_risk:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Índice Médio</h3>
                <h2>N/A</h2>
            </div>
            """, unsafe_allow_html=True)


def create_ranking_table(df):
    """
    Cria tabela interativa com ranking de segmentos.
    """
    st.subheader("🏆 Ranking de Black Spots")
    
    if 'ranking_position' in df.columns:
        # Prepara dados para exibição
        display_columns = [
            'ranking_position', 'segmento_id', 'uf', 'br', 
            'indice_periculosidade', 'total_acidentes', 'mortos', 
            'nivel_risco', 'blackspot_category'
        ]
        
        available_columns = [col for col in display_columns if col in df.columns]
        df_display = df[available_columns].copy()
        
        # Renomeia colunas para exibição
        column_names = {
            'ranking_position': 'Posição',
            'segmento_id': 'Segmento',
            'uf': 'UF',
            'br': 'BR',
            'indice_periculosidade': 'Índice',
            'total_acidentes': 'Acidentes',
            'mortos': 'Mortos',
            'nivel_risco': 'Nível de Risco',
            'blackspot_category': 'Categoria'
        }
        
        df_display = df_display.rename(columns=column_names)
        
        # Formata valores numéricos
        if 'Índice' in df_display.columns:
            df_display['Índice'] = df_display['Índice'].round(1)
        
        # Exibe tabela
        st.dataframe(
            df_display,
            width='stretch',
            height=400
        )
        
        # Opção de download
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Ranking (CSV)",
            data=csv,
            file_name=f"ranking_blackspots_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Dados de ranking não disponíveis. Execute o processamento completo.")


def create_risk_map(df):
    """
    Cria mapa interativo com intensidade de risco.
    """
    st.subheader("🗺️ Mapa de Risco")
    
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # Cria mapa base
        center_lat = df['latitude'].mean()
        center_lng = df['longitude'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Adiciona marcadores coloridos por risco
        for idx, row in df.head(100).iterrows():  # Limita a 100 pontos para performance
            # Define cor baseada no índice de periculosidade
            if 'indice_periculosidade' in row:
                risk_index = row['indice_periculosidade']
                if risk_index >= 80:
                    color = 'red'
                elif risk_index >= 60:
                    color = 'orange'
                elif risk_index >= 40:
                    color = 'yellow'
                else:
                    color = 'green'
            else:
                color = 'blue'
            
            # Cria popup com informações
            popup_text = f"""
            <b>Segmento:</b> {row.get('segmento_id', 'N/A')}<br>
            <b>UF:</b> {row.get('uf', 'N/A')}<br>
            <b>BR:</b> {row.get('br', 'N/A')}<br>
            <b>Acidentes:</b> {row.get('total_acidentes', 0)}<br>
            <b>Mortos:</b> {row.get('mortos', 0)}<br>
            <b>Índice:</b> {row.get('indice_periculosidade', 0):.1f}
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=popup_text,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
        
        # Adiciona legenda
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Nível de Risco</b></p>
        <p><i class="fa fa-circle" style="color:red"></i> Crítico (80+)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Alto (60-80)</p>
        <p><i class="fa fa-circle" style="color:yellow"></i> Moderado (40-60)</p>
        <p><i class="fa fa-circle" style="color:green"></i> Baixo (<40)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Exibe mapa
        st_folium(m, width=700, height=500)
    else:
        st.warning("Dados de coordenadas não disponíveis para criação do mapa.")


def create_analysis_charts(df):
    """
    Cria gráficos de análise.
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por UF")
        if 'uf' in df.columns and 'total_acidentes' in df.columns:
            uf_stats = df.groupby('uf')['total_acidentes'].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=uf_stats.index,
                y=uf_stats.values,
                labels={'x': 'Estado', 'y': 'Total de Acidentes'},
                title="Acidentes por Estado"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Dados não disponíveis para análise por UF")
    
    with col2:
        st.subheader("🎯 Distribuição de Risco")
        if 'nivel_risco' in df.columns:
            risk_dist = df['nivel_risco'].value_counts()
            
            fig = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Distribuição por Nível de Risco"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Dados de nível de risco não disponíveis")


def main():
    """
    Função principal do dashboard.
    """
    # Aplica melhorias de experiência do usuário
    try:
        enhance_user_experience()
        add_notification("Dashboard carregado com sucesso!", "success")
    except (ImportError, NameError):
        pass  # Continua sem as melhorias se não disponíveis
    
    # Header
    st.markdown('<h1 class="main-header">🛣️ RoadInfra BI - Dashboard de Segurança Viária</h1>', unsafe_allow_html=True)
    
    # Informações do projeto
    with st.expander("ℹ️ Sobre o Projeto"):
        st.markdown("""
        **RoadInfra BI** transforma dados do DATATRAN (2017-2024) em inteligência acionável 
        para gestão de segurança viária em rodovias federais.
        
        **Funcionalidades:**
        - 🔍 Identificação de black spots baseada em Índice de Periculosidade
        - 📊 Análise interativa com filtros por UF, BR e período
        - 🗺️ Visualização geográfica dos pontos críticos
        - 📈 Rankings e estatísticas detalhadas
        
        **Metodologia:**
        - Índice = (Mortos × 10) + (Feridos Graves × 5) + (Feridos Leves × 2) + (Sem Vítimas × 1)
        - Normalização 0-100 e classificação em níveis de risco
        - Ranking multi-critério considerando severidade, frequência e tendência
        """)
    
    # Carrega dados
    with st.spinner("Carregando dados..."):
        raw_data = load_sample_data()
        processed_data, ranked_data, risk_report = process_data(raw_data)
        original_data = ranked_data.copy()
    
    # === FILTROS INTERATIVOS ===
    try:
        filters = create_scenario_filters()
        
        # Processa ações dos filtros
        if filters['actions']['reset']:
            reset_session_filters()
            try:
                add_notification("Filtros resetados com sucesso!", "info")
            except:
                pass
            st.rerun()
        
        # Aplica filtros aos dados
        filtered_data = apply_filters_to_data(ranked_data, filters)
        
        # Simula intervenções se habilitado
        intervention_data = None
        if filters['intervention']['enabled']:
            intervention_data = simulate_interventions(filtered_data, filters['intervention']['params'])
            try:
                add_notification(
                    f"Simulação aplicada: {filters['intervention']['params']['type']}", 
                    "success"
                )
            except:
                pass
        
        # === RESUMO DOS FILTROS ===
        if filters['actions']['apply'] or any([
            len(filters['geographic']['states']) != 3,
            len(filters['geographic']['brs']) != 3,
            filters['temporal']['start_year'] != 2017,
            filters['temporal']['end_year'] != 2024,
            filters['intervention']['enabled']
        ]):
            create_filter_summary(filters)
            
            # Alerta de cenário ativo
            st.markdown("""
            <div class="scenario-alert">
                <strong>🎛️ Cenário Personalizado Ativo</strong><br>
                Os dados exibidos refletem os filtros aplicados. Use o botão "Resetar Filtros" para voltar à visão completa.
                <br><small>💡 Dica: Use Ctrl+R para resetar rapidamente</small>
            </div>
            """, unsafe_allow_html=True)
        
        # === COMPARAÇÃO DE CENÁRIOS ===
        if intervention_data or len(filtered_data) != len(original_data):
            create_scenario_comparison(original_data, filtered_data, intervention_data)
            st.markdown("---")
        
        # Usa dados simulados se disponível, senão usa dados filtrados
        display_data = intervention_data[0] if intervention_data else filtered_data
        
    except (ImportError, NameError):
        # Fallback para filtros básicos se componentes avançados não estão disponíveis
        filters = create_sidebar_filters(ranked_data)
        display_data = apply_filters(ranked_data, filters)
        
        if display_data.empty:
            st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros.")
            return
    
    # KPIs principais
    create_kpi_cards(display_data)
    
    st.markdown("---")
    
    # Layout principal em duas colunas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Tabela de ranking
        create_ranking_table(display_data)
    
    with col2:
        # Informações do filtro atual
        st.subheader("🎛️ Filtros Ativos")
        if 'filters' in locals() and isinstance(filters, dict) and 'geographic' in filters:
            # Filtros avançados
            st.info(f"""
            **Estados:** {', '.join(filters['geographic']['states']) if filters['geographic']['states'] else 'Todos'}
            
            **Rodovias:** {', '.join(map(str, filters['geographic']['brs'])) if filters['geographic']['brs'] else 'Todas'}
            
            **Período:** {filters['temporal']['start_year']}-{filters['temporal']['end_year']}
            
            **Segmentos:** {len(display_data):,}
            """)
        else:
            # Filtros básicos
            st.info(f"""
            **Estados:** {', '.join(filters['ufs']) if filters['ufs'] else 'Todos'}
            
            **Rodovias:** {', '.join(map(str, filters['brs'])) if filters['brs'] else 'Todas'}
            
            **Período:** {f"{filters['years'][0]}-{filters['years'][1]}" if filters['years'] else 'Todos os anos'}
            
            **Segmentos:** {len(display_data):,}
            """)
    
    st.markdown("---")
    
    # Mapa de risco
    create_risk_map(display_data)
    
    st.markdown("---")
    
    # Gráficos de análise
    create_analysis_charts(display_data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🛣️ <strong>RoadInfra BI</strong> - Transformando dados em segurança viária</p>
        <p>Desenvolvido para apoiar concessionárias e órgãos de trânsito na redução de acidentes</p>
        <p><em>Use os filtros na barra lateral para simular diferentes cenários e intervenções</em></p>
    </div>
    """, unsafe_allow_html=True)


def create_recommendations_panel_enhanced(data, filters=None):
    """
    Cria painel de recomendações baseado nos dados e filtros aplicados.
    """
    st.subheader("💡 Recomendações Inteligentes")
    
    # Análise dos dados atuais
    total_accidents = len(data)
    fatal_accidents = len(data[data['classificacao_acidente'] == 'Com Vítimas Fatais'])
    fatal_rate = (fatal_accidents / total_accidents * 100) if total_accidents > 0 else 0
    
    # Principais causas
    top_causes = data['causa_acidente'].value_counts().head(3)
    
    # Principais tipos
    top_types = data['tipo_acidente'].value_counts().head(3)
    
    # Estados mais críticos
    critical_states = data.groupby('uf')['classificacao_acidente'].apply(
        lambda x: (x == 'Com Vítimas Fatais').sum()
    ).sort_values(ascending=False).head(3)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Recomendações Prioritárias")
        
        recommendations = []
        
        # Recomendações baseadas na taxa de fatalidade
        if fatal_rate > 15:
            recommendations.append({
                'priority': 'CRÍTICA',
                'action': 'Implementar medidas de segurança imediatas',
                'description': f'Taxa de fatalidade de {fatal_rate:.1f}% está acima do aceitável (>15%)',
                'icon': '🚨'
            })
        elif fatal_rate > 10:
            recommendations.append({
                'priority': 'ALTA',
                'action': 'Reforçar fiscalização e sinalização',
                'description': f'Taxa de fatalidade de {fatal_rate:.1f}% requer atenção',
                'icon': '⚠️'
            })
        
        # Recomendações baseadas nas principais causas
        if len(top_causes) > 0:
            main_cause = top_causes.index[0]
            cause_count = top_causes.iloc[0]
            
            if 'velocidade' in main_cause.lower():
                recommendations.append({
                    'priority': 'ALTA',
                    'action': 'Instalar radares e redutores de velocidade',
                    'description': f'{cause_count} acidentes por excesso de velocidade',
                    'icon': '📡'
                })
            elif 'sono' in main_cause.lower() or 'fadiga' in main_cause.lower():
                recommendations.append({
                    'priority': 'MÉDIA',
                    'action': 'Criar áreas de descanso e campanhas educativas',
                    'description': f'{cause_count} acidentes por fadiga/sono',
                    'icon': '😴'
                })
            elif 'álcool' in main_cause.lower():
                recommendations.append({
                    'priority': 'CRÍTICA',
                    'action': 'Intensificar operações Lei Seca',
                    'description': f'{cause_count} acidentes relacionados ao álcool',
                    'icon': '🍺'
                })
        
        # Recomendações baseadas nos filtros aplicados
        if filters and filters.get('intervention', {}).get('enabled'):
            intervention_type = filters['intervention']['params']['type']
            if intervention_type == 'speed_cameras':
                recommendations.append({
                    'priority': 'SIMULAÇÃO',
                    'action': 'Resultado da simulação: Radares',
                    'description': f'Redução estimada de {filters["intervention"]["params"]["effectiveness"]*100:.0f}% nos acidentes',
                    'icon': '🎯'
                })
            elif intervention_type == 'road_improvement':
                recommendations.append({
                    'priority': 'SIMULAÇÃO',
                    'action': 'Resultado da simulação: Melhorias viárias',
                    'description': f'Redução estimada de {filters["intervention"]["params"]["effectiveness"]*100:.0f}% nos acidentes',
                    'icon': '🛣️'
                })
        
        # Exibe recomendações
        for rec in recommendations:
            priority_color = {
                'CRÍTICA': '#f44336',
                'ALTA': '#ff9800',
                'MÉDIA': '#2196f3',
                'SIMULAÇÃO': '#4caf50'
            }.get(rec['priority'], '#666')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color}; padding: 1rem; margin: 1rem 0; background-color: #f8f9fa; border-radius: 0.5rem;">
                <strong>{rec['icon']} {rec['action']}</strong><br>
                <small style="color: {priority_color};">PRIORIDADE {rec['priority']}</small><br>
                {rec['description']}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Análise de Impacto")
        
        # Métricas de impacto
        st.metric(
            "Taxa de Fatalidade",
            f"{fatal_rate:.1f}%",
            delta=f"{fatal_rate - 12:.1f}%" if fatal_rate != 12 else None,
            delta_color="inverse"
        )
        
        if len(critical_states) > 0:
            st.markdown("**Estados Críticos:**")
            for state, fatal_count in critical_states.items():
                st.write(f"• {state}: {fatal_count} acidentes fatais")
        
        if len(top_causes) > 0:
            st.markdown("**Principais Causas:**")
            for cause, count in top_causes.items():
                percentage = (count / total_accidents * 100)
                st.write(f"• {cause}: {count} ({percentage:.1f}%)")
        
        # Estimativa de ROI para intervenções
        if filters and filters.get('intervention', {}).get('enabled'):
            st.markdown("### 💰 Estimativa de ROI")
            effectiveness = filters['intervention']['params']['effectiveness']
            accidents_prevented = int(total_accidents * effectiveness)
            cost_per_accident = 150000  # Custo médio estimado por acidente
            savings = accidents_prevented * cost_per_accident
            
            st.success(f"""
            **Acidentes Evitados:** {accidents_prevented}
            
            **Economia Estimada:** R$ {savings:,.0f}
            
            **ROI Projetado:** {(savings / 1000000):.1f}x o investimento
            """)
    
    # Plano de ação sugerido
    st.markdown("### 📋 Plano de Ação Sugerido")
    
    action_plan = []
    
    if fatal_rate > 15:
        action_plan.extend([
            "1. **IMEDIATO (0-30 dias)**: Implementar sinalização de emergência nos pontos críticos",
            "2. **CURTO PRAZO (1-3 meses)**: Instalar equipamentos de monitoramento",
            "3. **MÉDIO PRAZO (3-6 meses)**: Executar melhorias na infraestrutura"
        ])
    else:
        action_plan.extend([
            "1. **CURTO PRAZO (1-3 meses)**: Reforçar campanhas educativas",
            "2. **MÉDIO PRAZO (3-6 meses)**: Implementar melhorias preventivas",
            "3. **LONGO PRAZO (6-12 meses)**: Monitorar e ajustar estratégias"
        ])
    
    for action in action_plan:
        st.markdown(action)
    
    # Botão para exportar relatório
    if st.button("📄 Gerar Relatório Completo", type="primary"):
        st.success("Relatório gerado! (Funcionalidade em desenvolvimento)")
        st.balloons()


if __name__ == "__main__":
    main()