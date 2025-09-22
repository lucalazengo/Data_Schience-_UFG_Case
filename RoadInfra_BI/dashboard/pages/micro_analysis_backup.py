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


def create_kpi_dashboard(annual_data, segment_info):
    """
    Cria dashboard com KPIs principais do segmento.
    """
    st.subheader("📊 KPIs Principais (2017-2024)")
    
    # Calcula totais
    total_acidentes = annual_data['total_acidentes'].sum()
    total_mortos = annual_data['mortos'].sum()
    total_feridos_graves = annual_data['feridos_graves'].sum()
    total_feridos_leves = annual_data['feridos_leves'].sum()
    
    # Calcula médias anuais
    media_acidentes = annual_data['total_acidentes'].mean()
    media_mortos = annual_data['mortos'].mean()
    
    # Calcula tendências
    anos = annual_data['ano'].values
    acidentes = annual_data['total_acidentes'].values
    tendencia_acidentes = np.polyfit(anos, acidentes, 1)[0]
    
    # Primeira linha de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card critical-kpi">
            <h3>💀 Total de Mortos</h3>
            <h2>{total_mortos}</h2>
            <p>Média: {media_mortos:.1f}/ano</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card warning-kpi">
            <h3>🚗 Total de Acidentes</h3>
            <h2>{total_acidentes}</h2>
            <p>Média: {media_acidentes:.1f}/ano</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card info-kpi">
            <h3>🏥 Feridos Graves</h3>
            <h2>{total_feridos_graves}</h2>
            <p>Taxa: {total_feridos_graves/total_acidentes*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        tendencia_icon = "📈" if tendencia_acidentes > 0 else "📉" if tendencia_acidentes < 0 else "➡️"
        tendencia_text = "Crescente" if tendencia_acidentes > 0 else "Decrescente" if tendencia_acidentes < 0 else "Estável"
        
        st.markdown(f"""
        <div class="kpi-card success-kpi">
            <h3>{tendencia_icon} Tendência</h3>
            <h2>{tendencia_text}</h2>
            <p>{tendencia_acidentes:+.1f} acid./ano</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Segunda linha de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        densidade = total_acidentes / (segment_info['extensao_km'] * len(annual_data))
        st.markdown(f"""
        <div class="kpi-card">
            <h3>📏 Densidade</h3>
            <h2>{densidade:.2f}</h2>
            <p>acid./km/ano</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        taxa_mortalidade = total_mortos / total_acidentes * 100 if total_acidentes > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>⚰️ Taxa Mortalidade</h3>
            <h2>{taxa_mortalidade:.1f}%</h2>
            <p>mortos/acidentes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🎯 Índice de Risco</h3>
            <h2>{segment_info['indice_periculosidade']:.1f}</h2>
            <p>Escala 0-100</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_vitimas = total_mortos + total_feridos_graves + total_feridos_leves
        st.markdown(f"""
        <div class="kpi-card">
            <h3>👥 Total Vítimas</h3>
            <h2>{total_vitimas}</h2>
            <p>Todas as categorias</p>
        </div>
        """, unsafe_allow_html=True)


def create_temporal_analysis(annual_data, monthly_data):
    """
    Cria análises temporais (QUANDO?).
    """
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.subheader("📅 Análise Temporal - QUANDO acontecem os acidentes?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Evolução Anual (2017-2024)**")
        
        fig = go.Figure()
        
        # Acidentes totais
        fig.add_trace(go.Scatter(
            x=annual_data['ano'],
            y=annual_data['total_acidentes'],
            mode='lines+markers',
            name='Total Acidentes',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Mortos
        fig.add_trace(go.Scatter(
            x=annual_data['ano'],
            y=annual_data['mortos'],
            mode='lines+markers',
            name='Mortos',
            line=dict(color='#d62728', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Evolução Temporal dos Acidentes",
            xaxis_title="Ano",
            yaxis_title="Número de Acidentes",
            yaxis2=dict(
                title="Número de Mortos",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("**📊 Sazonalidade Mensal (2024)**")
        
        fig = px.bar(
            monthly_data,
            x='mes_nome',
            y='total_acidentes',
            title="Distribuição Mensal de Acidentes",
            color='total_acidentes',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Acidentes",
            showlegend=False
        )
        
        st.plotly_chart(fig, width='stretch')
    
    # Insights temporais
    st.markdown("**🔍 Insights Temporais:**")
    
    # Análise de tendência
    tendencia = np.polyfit(annual_data['ano'], annual_data['total_acidentes'], 1)[0]
    if tendencia > 0.5:
        trend_insight = "📈 **Tendência crescente** de acidentes ao longo dos anos"
    elif tendencia < -0.5:
        trend_insight = "📉 **Tendência decrescente** de acidentes ao longo dos anos"
    else:
        trend_insight = "➡️ **Tendência estável** no número de acidentes"
    
    # Análise sazonal
    max_month = monthly_data.loc[monthly_data['total_acidentes'].idxmax(), 'mes_nome']
    min_month = monthly_data.loc[monthly_data['total_acidentes'].idxmin(), 'mes_nome']
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(trend_insight)
    with col2:
        st.info(f"🗓️ **Pico sazonal** em {max_month}, menor incidência em {min_month}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def create_cause_analysis(causas_data):
    """
    Cria análise por causas (O QUÊ?).
    """
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.subheader("🎯 Análise de Causas - O QUÊ causa os acidentes?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de causas
        fig = px.bar(
            causas_data.sort_values('acidentes', ascending=True),
            x='acidentes',
            y='causa',
            orientation='h',
            title="Top 5 Causas de Acidentes",
            color='mortos',
            color_continuous_scale='Reds',
            text='acidentes'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Número de Acidentes",
            yaxis_title="Causa do Acidente",
            height=400
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("**📋 Ranking de Causas**")
        
        for idx, row in causas_data.head(5).iterrows():
            letalidade = row['mortos'] / row['acidentes'] * 100 if row['acidentes'] > 0 else 0
            
            if letalidade > 20:
                alert_class = "critical-kpi"
                icon = "🔴"
            elif letalidade > 10:
                alert_class = "warning-kpi"
                icon = "🟡"
            else:
                alert_class = "success-kpi"
                icon = "🟢"
            
            st.markdown(f"""
            <div class="kpi-card {alert_class}">
                <strong>{icon} {row['causa']}</strong><br>
                Acidentes: {row['acidentes']}<br>
                Mortos: {row['mortos']}<br>
                Letalidade: {letalidade:.1f}%
            </div>
            """, unsafe_allow_html=True)
    
    # Insights de causas
    st.markdown("**🔍 Insights sobre Causas:**")
    
    principal_causa = causas_data.iloc[0]
    causa_mais_letal = causas_data.loc[causas_data['mortos'].idxmax()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.warning(f"⚠️ **Causa principal:** {principal_causa['causa']} ({principal_causa['acidentes']} acidentes)")
    with col2:
        st.error(f"💀 **Mais letal:** {causa_mais_letal['causa']} ({causa_mais_letal['mortos']} mortos)")
    
    st.markdown('</div>', unsafe_allow_html=True)


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
    
    # Tabela detalhada
    st.markdown("**📊 Detalhamento por Tipo de Acidente**")
    
    tipos_display = tipos_data.copy()
    tipos_display['Taxa Letalidade (%)'] = tipos_display['letalidade'].round(1)
    tipos_display['Taxa Feridos (%)'] = (tipos_display['feridos'] / tipos_display['acidentes'] * 100).round(1)
    
    display_cols = ['tipo', 'acidentes', 'mortos', 'feridos', 'Taxa Letalidade (%)', 'Taxa Feridos (%)']
    tipos_display = tipos_display[display_cols].rename(columns={
        'tipo': 'Tipo de Acidente',
        'acidentes': 'Acidentes',
        'mortos': 'Mortos',
        'feridos': 'Feridos'
    })
    
    st.dataframe(tipos_display, width='stretch')
    
    # Insights de tipos
    st.markdown("**🔍 Insights sobre Tipos:**")
    
    tipo_mais_frequente = tipos_data.iloc[0]
    tipo_mais_letal = tipos_data.loc[tipos_data['letalidade'].idxmax()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📊 **Mais frequente:** {tipo_mais_frequente['tipo']} ({tipo_mais_frequente['acidentes']} casos)")
    with col2:
        st.error(f"⚰️ **Mais letal:** {tipo_mais_letal['tipo']} ({tipo_mais_letal['letalidade']:.1f}% letalidade)")
    
    st.markdown('</div>', unsafe_allow_html=True)


def create_recommendations(segment_info, causas_data, tipos_data):
    """
    Cria seção de recomendações baseadas na análise.
    """
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.subheader("💡 Recomendações de Intervenção")
    
    # Análise do nível de risco
    risk_level = segment_info['nivel_risco']
    
    if risk_level == 'Crítico':
        st.error("🚨 **INTERVENÇÃO URGENTE NECESSÁRIA**")
        urgency_color = "#f44336"
    elif risk_level == 'Alto':
        st.warning("⚠️ **INTERVENÇÃO PRIORITÁRIA RECOMENDADA**")
        urgency_color = "#ff9800"
    else:
        st.info("ℹ️ **MONITORAMENTO E MELHORIAS PREVENTIVAS**")
        urgency_color = "#2196f3"
    
    # Recomendações baseadas nas causas principais
    principal_causa = causas_data.iloc[0]['causa']
    tipo_principal = tipos_data.iloc[0]['tipo']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Intervenções por Causa Principal**")
        
        if 'velocidade' in principal_causa.lower():
            recommendations = [
                "🚧 Instalação de redutores de velocidade",
                "📷 Implementação de radar de velocidade",
                "🛣️ Melhoria da sinalização de limite de velocidade",
                "🚦 Instalação de semáforos inteligentes"
            ]
        elif 'desatenção' in principal_causa.lower() or 'distração' in principal_causa.lower():
            recommendations = [
                "📱 Campanhas contra uso de celular ao volante",
                "🛣️ Melhoria da sinalização visual",
                "🚧 Instalação de tachas refletivas",
                "📢 Campanhas educativas de conscientização"
            ]
        elif 'sinalização' in principal_causa.lower():
            recommendations = [
                "🚦 Modernização da sinalização",
                "💡 Melhoria da iluminação",
                "🛣️ Pintura de faixas e demarcações",
                "📋 Revisão da sinalização vertical"
            ]
        else:
            recommendations = [
                "🔍 Estudo detalhado das causas específicas",
                "🛣️ Melhoria geral da infraestrutura",
                "📊 Monitoramento contínuo",
                "👮 Intensificação da fiscalização"
            ]
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    with col2:
        st.markdown("**🚗 Intervenções por Tipo Principal**")
        
        if 'colisão traseira' in tipo_principal.lower():
            recommendations = [
                "🚦 Instalação de semáforos com tempo adequado",
                "🛣️ Melhoria da sinalização de parada",
                "📏 Criação de faixas de desaceleração",
                "💡 Melhoria da iluminação noturna"
            ]
        elif 'colisão frontal' in tipo_principal.lower():
            recommendations = [
                "🛡️ Instalação de barreiras centrais",
                "🛣️ Criação de canteiro central",
                "🚧 Melhoria das curvas perigosas",
                "📐 Ampliação da pista em pontos críticos"
            ]
        elif 'capotamento' in tipo_principal.lower():
            recommendations = [
                "🛣️ Melhoria do pavimento",
                "🌧️ Drenagem adequada da pista",
                "🚧 Correção de curvas perigosas",
                "🛡️ Instalação de defensas metálicas"
            ]
        else:
            recommendations = [
                "🔍 Análise específica do tipo de acidente",
                "🛣️ Melhoria geral da geometria da via",
                "🚧 Adequação da infraestrutura",
                "📊 Monitoramento especializado"
            ]
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    # Estimativa de impacto
    st.markdown("**📈 Estimativa de Impacto das Intervenções**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card success-kpi">
            <h4>🎯 Redução Esperada</h4>
            <h3>25-40%</h3>
            <p>nos acidentes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card info-kpi">
            <h4>💰 Investimento</h4>
            <h3>R$ 2-5M</h3>
            <p>estimado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card warning-kpi">
            <h4>⏱️ Prazo</h4>
            <h3>6-12 meses</h3>
            <p>implementação</p>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    # Dashboard de KPIs
    create_kpi_dashboard(data['annual_data'], data['segment_info'])
    
    st.markdown("---")
    
    # Análises explicativas
    create_temporal_analysis(data['annual_data'], data['monthly_data'])
    
    create_cause_analysis(data['causas_data'])
    
    create_type_analysis(data['tipos_data'])
    
    # Recomendações
    create_recommendations(data['segment_info'], data['causas_data'], data['tipos_data'])
    
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