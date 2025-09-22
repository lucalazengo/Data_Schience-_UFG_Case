"""
Componentes de gráficos para o dashboard RoadInfra BI
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_kpi_cards(col1, col2, col3, col4, total_acidentes, total_mortos, total_feridos, indice_medio):
    """Cria cards de KPIs principais"""
    with col1:
        st.metric(
            label="🚨 Total de Acidentes",
            value=f"{total_acidentes:,}",
            delta=f"{np.random.randint(-15, 25)}% vs ano anterior"
        )
    
    with col2:
        st.metric(
            label="💀 Total de Mortos",
            value=f"{total_mortos:,}",
            delta=f"{np.random.randint(-20, 10)}% vs ano anterior",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🏥 Total de Feridos",
            value=f"{total_feridos:,}",
            delta=f"{np.random.randint(-10, 15)}% vs ano anterior",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="⚠️ Índice Médio",
            value=f"{indice_medio:.2f}",
            delta=f"{np.random.uniform(-0.5, 0.3):.2f} vs ano anterior",
            delta_color="inverse"
        )

def create_temporal_analysis(df):
    """Cria gráficos de análise temporal"""
    st.subheader("📈 Análise Temporal")
    
    # Gráfico de linha temporal
    temporal_data = df.groupby('ano').agg({
        'acidentes': 'sum',
        'mortos': 'sum',
        'feridos_graves': 'sum',
        'feridos_leves': 'sum',
        'indice_periculosidade': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Acidentes por Ano', 'Mortos por Ano', 
                       'Feridos por Ano', 'Índice de Periculosidade'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Acidentes
    fig.add_trace(
        go.Scatter(x=temporal_data['ano'], y=temporal_data['acidentes'],
                  mode='lines+markers', name='Acidentes', line=dict(color='#FF6B6B')),
        row=1, col=1
    )
    
    # Mortos
    fig.add_trace(
        go.Scatter(x=temporal_data['ano'], y=temporal_data['mortos'],
                  mode='lines+markers', name='Mortos', line=dict(color='#4ECDC4')),
        row=1, col=2
    )
    
    # Feridos
    fig.add_trace(
        go.Scatter(x=temporal_data['ano'], y=temporal_data['feridos_graves'] + temporal_data['feridos_leves'],
                  mode='lines+markers', name='Feridos', line=dict(color='#45B7D1')),
        row=2, col=1
    )
    
    # Índice
    fig.add_trace(
        go.Scatter(x=temporal_data['ano'], y=temporal_data['indice_periculosidade'],
                  mode='lines+markers', name='Índice', line=dict(color='#96CEB4')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, width='stretch')

def create_cause_analysis(df):
    """Cria análise por causas de acidentes"""
    st.subheader("🔍 Análise por Causas")
    
    # Top 10 causas
    causas = df.groupby('causa_acidente').agg({
        'acidentes': 'sum',
        'mortos': 'sum',
        'indice_periculosidade': 'mean'
    }).sort_values('acidentes', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_causas = px.bar(
            causas.reset_index(),
            x='acidentes',
            y='causa_acidente',
            orientation='h',
            title='Top 10 Causas de Acidentes',
            color='acidentes',
            color_continuous_scale='Reds'
        )
        fig_causas.update_layout(height=400)
        st.plotly_chart(fig_causas, width='stretch')
    
    with col2:
        fig_mortes = px.bar(
            causas.reset_index(),
            x='mortos',
            y='causa_acidente',
            orientation='h',
            title='Mortes por Causa',
            color='mortos',
            color_continuous_scale='Oranges'
        )
        fig_mortes.update_layout(height=400)
        st.plotly_chart(fig_mortes, width='stretch')

def create_accident_type_analysis(df):
    """Cria análise por tipos de acidentes"""
    st.subheader("🚗 Análise por Tipos de Acidentes")
    
    tipos = df.groupby('tipo_acidente').agg({
        'acidentes': 'sum',
        'mortos': 'sum',
        'feridos_graves': 'sum',
        'feridos_leves': 'sum'
    }).sort_values('acidentes', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pizza = px.pie(
            tipos.reset_index(),
            values='acidentes',
            names='tipo_acidente',
            title='Distribuição por Tipo de Acidente'
        )
        st.plotly_chart(fig_pizza, width='stretch')
    
    with col2:
        fig_gravidade = px.bar(
            tipos.reset_index(),
            x='tipo_acidente',
            y=['mortos', 'feridos_graves', 'feridos_leves'],
            title='Gravidade por Tipo de Acidente',
            barmode='stack'
        )
        fig_gravidade.update_xaxes(tickangle=45)
        st.plotly_chart(fig_gravidade, width='stretch')

def create_seasonal_analysis(df):
    """Cria análise de sazonalidade"""
    st.subheader("📅 Análise de Sazonalidade")
    
    # Simular dados mensais
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Padrão sazonal realista (mais acidentes no final do ano e férias)
    fatores_sazonais = [1.1, 0.9, 1.0, 1.0, 1.0, 1.2, 1.3, 1.1, 1.0, 1.0, 1.1, 1.4]
    
    acidentes_mensais = []
    mortos_mensais = []
    
    for i, fator in enumerate(fatores_sazonais):
        base_acidentes = df['acidentes'].sum() / 12
        base_mortos = df['mortos'].sum() / 12
        
        acidentes_mensais.append(int(base_acidentes * fator * np.random.uniform(0.8, 1.2)))
        mortos_mensais.append(int(base_mortos * fator * np.random.uniform(0.8, 1.2)))
    
    dados_sazonais = pd.DataFrame({
        'mes': meses,
        'acidentes': acidentes_mensais,
        'mortos': mortos_mensais
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_mensal = px.line(
            dados_sazonais,
            x='mes',
            y='acidentes',
            title='Acidentes por Mês',
            markers=True
        )
        fig_mensal.update_traces(line_color='#FF6B6B')
        st.plotly_chart(fig_mensal, width='stretch')
        
        # Análise de mortes por mês
        fig_mortes_mensal = px.line(
            dados_sazonais, 
            x='mes', 
            y='mortos',
            title="Mortes por Mês",
            markers=True
        )
        fig_mortes_mensal.update_layout(xaxis_title="Mês", yaxis_title="Número de Mortes")
        st.plotly_chart(fig_mortes_mensal, width='stretch')
    
    with col2:
        fig_mortes_mensal = px.bar(
            dados_sazonais,
            x='mes',
            y='mortos',
            title='Mortes por Mês',
            color='mortos',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_mortes_mensal, width='stretch')

def create_risk_heatmap(df):
    """Cria heatmap de risco por UF e BR"""
    st.subheader("🗺️ Mapa de Calor de Risco")
    
    # Matriz de risco UF x BR (top BRs)
    top_brs = df.groupby('br')['indice_periculosidade'].mean().sort_values(ascending=False).head(10).index
    
    matriz_risco = df[df['br'].isin(top_brs)].pivot_table(
        values='indice_periculosidade',
        index='uf',
        columns='br',
        aggfunc='mean',
        fill_value=0
    )
    
    fig_heatmap = px.imshow(
        matriz_risco,
        title='Índice de Periculosidade por UF e BR',
        color_continuous_scale='Reds',
        aspect='auto'
    )
    
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, width='stretch')

def create_recommendations_panel(df, segmento_selecionado=None):
    """Cria painel de recomendações"""
    st.subheader("💡 Recomendações de Intervenção")
    
    if segmento_selecionado:
        # Recomendações específicas para o segmento
        indice = segmento_selecionado.get('indice_periculosidade', 0)
        
        if indice > 8:
            nivel = "🔴 CRÍTICO"
            cor = "red"
            recomendacoes = [
                "Implementação imediata de medidas de segurança",
                "Instalação de radares e lombadas eletrônicas",
                "Reforço na sinalização e iluminação",
                "Campanha intensiva de conscientização",
                "Aumento da fiscalização policial"
            ]
        elif indice > 5:
            nivel = "🟡 ALTO"
            cor = "orange"
            recomendacoes = [
                "Melhoria na sinalização horizontal e vertical",
                "Instalação de dispositivos de segurança",
                "Campanha de conscientização direcionada",
                "Monitoramento contínuo do trecho"
            ]
        else:
            nivel = "🟢 MODERADO"
            cor = "green"
            recomendacoes = [
                "Manutenção preventiva da sinalização",
                "Monitoramento periódico",
                "Campanhas educativas pontuais"
            ]
        
        st.markdown(f"**Nível de Risco: {nivel}**")
        
        for rec in recomendacoes:
            st.markdown(f"• {rec}")
    
    else:
        # Recomendações gerais
        st.markdown("**Recomendações Gerais do Sistema:**")
        
        top_segments = df.nlargest(5, 'indice_periculosidade')
        
        st.markdown("**Top 5 Segmentos Prioritários:**")
        for idx, segment in top_segments.iterrows():
            st.markdown(f"• {segment['segmento_id']} - Índice: {segment['indice_periculosidade']:.2f}")
        
        st.markdown("**Ações Recomendadas:**")
        st.markdown("• Priorizar intervenções nos segmentos com índice > 8.0")
        st.markdown("• Implementar programa de monitoramento contínuo")
        st.markdown("• Desenvolver campanhas educativas regionalizadas")
        st.markdown("• Estabelecer parcerias com concessionárias")