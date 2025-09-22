"""RoadInfra BI - Visão Micro (Análise Detalhada por Segmento)
==========================================================

Página dedicada à análise detalhada de segmentos específicos,
fornecendo diagnóstico completo com KPIs e gráficos explicativos.

Autor: RoadInfra BI Team
Data: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Importar componentes do dashboard
try:
    from dashboard.components.charts import (
        create_kpi_cards, create_temporal_analysis, create_cause_analysis,
        create_accident_type_analysis, create_seasonal_analysis, 
        create_recommendations_panel
    )
    from dashboard.components.filters import create_segment_selector
except ImportError:
    # Fallback para quando os componentes não estão disponíveis
    pass

# Configuração da página
st.set_page_config(
    page_title="RoadInfra BI - Análise Micro",
    page_icon="🔍",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .micro-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .segment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        text-align: center;
        margin-bottom: 1rem;
    }
    .critical-kpi {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .warning-kpi {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .success-kpi {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .info-kpi {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .analysis-section {
        background-color: #fafafa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_sample_segment_data():
    """
    Carrega dados detalhados de exemplo para análise micro.
    """
    np.random.seed(42)
    
    # Simula dados históricos detalhados para um segmento
    segment_id = "SP_BR101_KM0100_0120"
    years = list(range(2017, 2025))
    months = list(range(1, 13))
    
    # Dados anuais
    annual_data = []
    for year in years:
        base_accidents = np.random.poisson(15)
        annual_data.append({
            'ano': year,
            'total_acidentes': base_accidents,
            'mortos': np.random.poisson(base_accidents * 0.08),
            'feridos_graves': np.random.poisson(base_accidents * 0.15),
            'feridos_leves': np.random.poisson(base_accidents * 0.35),
            'danos_materiais': base_accidents - np.random.poisson(base_accidents * 0.58)
        })
    
    # Dados mensais (último ano)
    monthly_data = []
    for month in months:
        # Sazonalidade: mais acidentes no verão e feriados
        seasonal_factor = 1.3 if month in [12, 1, 2, 6, 7] else 1.0
        base_accidents = np.random.poisson(8 * seasonal_factor)
        
        monthly_data.append({
            'mes': month,
            'mes_nome': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month-1],
            'total_acidentes': base_accidents,
            'mortos': np.random.poisson(base_accidents * 0.08),
            'feridos_graves': np.random.poisson(base_accidents * 0.15),
            'feridos_leves': np.random.poisson(base_accidents * 0.35)
        })
    
    # Dados por causa de acidente
    causas_data = [
        {'causa': 'Velocidade incompatível', 'acidentes': 25, 'mortos': 8, 'feridos': 15},
        {'causa': 'Desatenção/distração', 'acidentes': 20, 'mortos': 3, 'feridos': 12},
        {'causa': 'Desobediência à sinalização', 'acidentes': 18, 'mortos': 5, 'feridos': 10},
        {'causa': 'Defeito mecânico', 'acidentes': 12, 'mortos': 2, 'feridos': 8},
        {'causa': 'Condições meteorológicas', 'acidentes': 10, 'mortos': 4, 'feridos': 6},
        {'causa': 'Outras', 'acidentes': 15, 'mortos': 3, 'feridos': 9}
    ]
    
    # Dados por tipo de acidente
    tipos_data = [
        {'tipo': 'Colisão traseira', 'acidentes': 35, 'mortos': 5, 'feridos': 25},
        {'tipo': 'Colisão frontal', 'acidentes': 20, 'mortos': 12, 'feridos': 8},
        {'tipo': 'Colisão lateral', 'acidentes': 18, 'mortos': 3, 'feridos': 15},
        {'tipo': 'Capotamento', 'acidentes': 15, 'mortos': 6, 'feridos': 9},
        {'tipo': 'Atropelamento', 'acidentes': 8, 'mortos': 4, 'feridos': 4},
        {'tipo': 'Outros', 'acidentes': 4, 'mortos': 0, 'feridos': 4}
    ]
    
    # Informações do segmento
    segment_info = {
        'segmento_id': segment_id,
        'uf': 'SP',
        'br': 101,
        'km_inicial': 100,
        'km_final': 120,
        'extensao_km': 20,
        'municipios': ['São Paulo', 'Guarulhos'],
        'caracteristicas': ['Trecho urbano', 'Alto tráfego', 'Múltiplas faixas'],
        'indice_periculosidade': 87.5,
        'nivel_risco': 'Crítico',
        'ranking_position': 3,
        'latitude': -23.5505,
        'longitude': -46.6333
    }
    
    return {
        'segment_info': segment_info,
        'annual_data': pd.DataFrame(annual_data),
        'monthly_data': pd.DataFrame(monthly_data),
        'causas_data': pd.DataFrame(causas_data),
        'tipos_data': pd.DataFrame(tipos_data)
    }


def create_segment_header(segment_info):
    """
    Cria cabeçalho com informações do segmento.
    """
    st.markdown(f"""
    <div class="segment-card">
        <h2>🔍 Análise Detalhada do Segmento</h2>
        <h3>{segment_info['segmento_id']}</h3>
        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
            <div>
                <strong>UF:</strong> {segment_info['uf']}<br>
                <strong>BR:</strong> {segment_info['br']}<br>
                <strong>Extensão:</strong> {segment_info['extensao_km']} km
            </div>
            <div>
                <strong>Ranking:</strong> #{segment_info['ranking_position']}<br>
                <strong>Nível:</strong> {segment_info['nivel_risco']}<br>
                <strong>Índice:</strong> {segment_info['indice_periculosidade']:.1f}
            </div>
            <div>
                <strong>Municípios:</strong> {', '.join(segment_info['municipios'])}<br>
                <strong>Características:</strong> {', '.join(segment_info['caracteristicas'])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_type_analysis(tipos_data):
    """
    Cria análise por tipos (COMO?).
    """
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.subheader("🚗 Análise de Tipos - COMO acontecem os acidentes?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza para tipos
        fig = px.pie(
            tipos_data,
            values='acidentes',
            names='tipo',
            title="Distribuição por Tipo de Acidente",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de severidade por tipo
        tipos_data['letalidade'] = tipos_data['mortos'] / tipos_data['acidentes'] * 100
        
        fig = px.scatter(
            tipos_data,
            x='acidentes',
            y='letalidade',
            size='mortos',
            color='tipo',
            title="Frequência vs Letalidade por Tipo",
            hover_data=['mortos', 'feridos']
        )
        
        fig.update_layout(
            xaxis_title="Número de Acidentes",
            yaxis_title="Taxa de Letalidade (%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """
    Função principal da página de análise micro.
    """
    # Header
    st.markdown('<h1 class="micro-header">🔍 RoadInfra BI - Análise Micro por Segmento</h1>', unsafe_allow_html=True)
    
    # Carrega dados de exemplo
    data = load_sample_segment_data()
    
    # Seletor de segmento (em produção seria dinâmico)
    st.sidebar.markdown("### 🎯 Seleção de Segmento")
    st.sidebar.info("Em produção, você poderia selecionar qualquer segmento do ranking para análise detalhada.")
    
    # Header do segmento
    create_segment_header(data['segment_info'])
    
    # Análise de tipos
    create_type_analysis(data['tipos_data'])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔍 <strong>Análise Micro</strong> - Diagnóstico detalhado para tomada de decisão</p>
        <p>Baseado em dados DATATRAN com metodologia científica de análise de risco</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()