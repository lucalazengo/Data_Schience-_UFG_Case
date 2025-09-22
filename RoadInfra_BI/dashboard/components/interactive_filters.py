"""RoadInfra BI - Filtros Interativos para Simulação de Cenários
==============================================================

Componente responsável por criar filtros dinâmicos que permitem ao usuário
simular diferentes cenários e visualizar o impacto em tempo real.

Autor: RoadInfra BI Team
Data: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go


def create_scenario_filters():
    """
    Cria filtros interativos para simulação de cenários.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Simulação de Cenários")
    
    # Filtros temporais
    st.sidebar.markdown("**📅 Período de Análise**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_year = st.selectbox(
            "Ano inicial",
            options=list(range(2017, 2025)),
            index=0,
            key="start_year"
        )
    
    with col2:
        end_year = st.selectbox(
            "Ano final",
            options=list(range(start_year, 2025)),
            index=len(list(range(start_year, 2025))) - 1,
            key="end_year"
        )
    
    # Filtros geográficos
    st.sidebar.markdown("**🗺️ Localização**")
    
    selected_states = st.sidebar.multiselect(
        "Estados (UF)",
        options=['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'ES', 'MT'],
        default=['SP', 'RJ', 'MG'],
        key="selected_states"
    )
    
    selected_brs = st.sidebar.multiselect(
        "Rodovias (BR)",
        options=[101, 116, 381, 40, 50, 153, 262, 324, 356, 393],
        default=[101, 116, 381],
        key="selected_brs"
    )
    
    # Filtros de severidade
    st.sidebar.markdown("**⚠️ Severidade dos Acidentes**")
    
    include_deaths = st.sidebar.checkbox(
        "Incluir acidentes com mortes",
        value=True,
        key="include_deaths"
    )
    
    include_injuries = st.sidebar.checkbox(
        "Incluir acidentes com feridos",
        value=True,
        key="include_injuries"
    )
    
    include_material_damage = st.sidebar.checkbox(
        "Incluir danos materiais",
        value=True,
        key="include_material_damage"
    )
    
    # Filtros de causa
    st.sidebar.markdown("**🎯 Causas de Acidentes**")
    
    selected_causes = st.sidebar.multiselect(
        "Principais causas",
        options=[
            'Velocidade incompatível',
            'Desatenção/distração',
            'Desobediência à sinalização',
            'Defeito mecânico',
            'Condições meteorológicas',
            'Outras'
        ],
        default=['Velocidade incompatível', 'Desatenção/distração'],
        key="selected_causes"
    )
    
    # Filtros de tipo de acidente
    st.sidebar.markdown("**🚗 Tipos de Acidentes**")
    
    selected_types = st.sidebar.multiselect(
        "Tipos de colisão",
        options=[
            'Colisão traseira',
            'Colisão frontal',
            'Colisão lateral',
            'Capotamento',
            'Atropelamento',
            'Outros'
        ],
        default=['Colisão traseira', 'Colisão frontal'],
        key="selected_types"
    )
    
    # Simulação de intervenções
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Simulação de Intervenções")
    
    intervention_enabled = st.sidebar.checkbox(
        "Ativar simulação de intervenções",
        value=False,
        key="intervention_enabled"
    )
    
    intervention_params = {}
    
    if intervention_enabled:
        st.sidebar.markdown("**📉 Redução Esperada (%)**")
        
        intervention_params['speed_reduction'] = st.sidebar.slider(
            "Controle de velocidade",
            min_value=0,
            max_value=50,
            value=25,
            step=5,
            key="speed_reduction"
        )
        
        intervention_params['signaling_improvement'] = st.sidebar.slider(
            "Melhoria da sinalização",
            min_value=0,
            max_value=40,
            value=15,
            step=5,
            key="signaling_improvement"
        )
        
        intervention_params['infrastructure_upgrade'] = st.sidebar.slider(
            "Upgrade de infraestrutura",
            min_value=0,
            max_value=60,
            value=30,
            step=5,
            key="infrastructure_upgrade"
        )
        
        intervention_params['education_campaign'] = st.sidebar.slider(
            "Campanhas educativas",
            min_value=0,
            max_value=30,
            value=10,
            step=5,
            key="education_campaign"
        )
    
    # Botão para aplicar filtros
    st.sidebar.markdown("---")
    apply_filters = st.sidebar.button(
        "🔄 Aplicar Filtros",
        type="primary",
        use_container_width=True,
        key="apply_filters"
    )
    
    # Botão para resetar filtros
    reset_filters = st.sidebar.button(
        "🔄 Resetar Filtros",
        use_container_width=True,
        key="reset_filters"
    )
    
    return {
        'temporal': {
            'start_year': start_year,
            'end_year': end_year
        },
        'geographic': {
            'states': selected_states,
            'brs': selected_brs
        },
        'severity': {
            'deaths': include_deaths,
            'injuries': include_injuries,
            'material_damage': include_material_damage
        },
        'causes': selected_causes,
        'types': selected_types,
        'intervention': {
            'enabled': intervention_enabled,
            'params': intervention_params
        },
        'actions': {
            'apply': apply_filters,
            'reset': reset_filters
        }
    }


def apply_filters_to_data(df, filters):
    """
    Aplica os filtros selecionados aos dados.
    """
    filtered_df = df.copy()
    
    # Filtros temporais
    if 'ano' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['ano'] >= filters['temporal']['start_year']) &
            (filtered_df['ano'] <= filters['temporal']['end_year'])
        ]
    
    # Filtros geográficos
    if 'uf' in filtered_df.columns and filters['geographic']['states']:
        filtered_df = filtered_df[
            filtered_df['uf'].isin(filters['geographic']['states'])
        ]
    
    if 'br' in filtered_df.columns and filters['geographic']['brs']:
        filtered_df = filtered_df[
            filtered_df['br'].isin(filters['geographic']['brs'])
        ]
    
    # Filtros de severidade
    severity_conditions = []
    
    if filters['severity']['deaths'] and 'mortos' in filtered_df.columns:
        severity_conditions.append(filtered_df['mortos'] > 0)
    
    if filters['severity']['injuries'] and 'feridos' in filtered_df.columns:
        severity_conditions.append(filtered_df['feridos'] > 0)
    
    if filters['severity']['material_damage'] and 'danos_materiais' in filtered_df.columns:
        severity_conditions.append(filtered_df['danos_materiais'] > 0)
    
    if severity_conditions:
        combined_condition = severity_conditions[0]
        for condition in severity_conditions[1:]:
            combined_condition = combined_condition | condition
        filtered_df = filtered_df[combined_condition]
    
    return filtered_df


def simulate_interventions(df, intervention_params):
    """
    Simula o impacto das intervenções nos dados.
    """
    simulated_df = df.copy()
    
    if not intervention_params:
        return simulated_df
    
    # Calcula redução total baseada nas intervenções
    total_reduction = 0
    
    # Cada intervenção contribui de forma não-linear
    for intervention, reduction in intervention_params.items():
        if reduction > 0:
            # Aplica lei dos rendimentos decrescentes
            effective_reduction = reduction * (1 - total_reduction / 100)
            total_reduction += effective_reduction * 0.8  # Fator de eficácia
    
    # Limita a redução máxima a 70%
    total_reduction = min(total_reduction, 70)
    
    # Aplica a redução aos dados
    reduction_factor = (100 - total_reduction) / 100
    
    numeric_columns = ['total_acidentes', 'mortos', 'feridos_graves', 'feridos_leves']
    
    for col in numeric_columns:
        if col in simulated_df.columns:
            simulated_df[f'{col}_original'] = simulated_df[col]
            simulated_df[col] = (simulated_df[col] * reduction_factor).round().astype(int)
            simulated_df[f'{col}_reduction'] = simulated_df[f'{col}_original'] - simulated_df[col]
    
    return simulated_df, total_reduction


def create_scenario_comparison(original_data, filtered_data, intervention_data=None):
    """
    Cria visualização comparativa dos cenários.
    """
    st.markdown("### 📊 Comparação de Cenários")
    
    # Métricas comparativas
    col1, col2, col3, col4 = st.columns(4)
    
    # Dados originais
    original_accidents = original_data['total_acidentes'].sum() if 'total_acidentes' in original_data.columns else 0
    original_deaths = original_data['mortos'].sum() if 'mortos' in original_data.columns else 0
    
    # Dados filtrados
    filtered_accidents = filtered_data['total_acidentes'].sum() if 'total_acidentes' in filtered_data.columns else 0
    filtered_deaths = filtered_data['mortos'].sum() if 'mortos' in filtered_data.columns else 0
    
    with col1:
        st.metric(
            "Acidentes (Original)",
            f"{original_accidents:,}",
            delta=None
        )
    
    with col2:
        delta_accidents = filtered_accidents - original_accidents
        st.metric(
            "Acidentes (Filtrado)",
            f"{filtered_accidents:,}",
            delta=f"{delta_accidents:+,}"
        )
    
    with col3:
        st.metric(
            "Mortes (Original)",
            f"{original_deaths:,}",
            delta=None
        )
    
    with col4:
        delta_deaths = filtered_deaths - original_deaths
        st.metric(
            "Mortes (Filtrado)",
            f"{filtered_deaths:,}",
            delta=f"{delta_deaths:+,}"
        )
    
    # Se há simulação de intervenção
    if intervention_data is not None:
        simulated_data, reduction_percentage = intervention_data
        
        st.markdown("---")
        st.markdown("### 🛠️ Impacto das Intervenções Simuladas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        simulated_accidents = simulated_data['total_acidentes'].sum()
        simulated_deaths = simulated_data['mortos'].sum()
        
        with col1:
            reduction_accidents = filtered_accidents - simulated_accidents
            st.metric(
                "Acidentes (Pós-Intervenção)",
                f"{simulated_accidents:,}",
                delta=f"-{reduction_accidents:,}",
                delta_color="inverse"
            )
        
        with col2:
            reduction_deaths = filtered_deaths - simulated_deaths
            st.metric(
                "Mortes (Pós-Intervenção)",
                f"{simulated_deaths:,}",
                delta=f"-{reduction_deaths:,}",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Redução Total",
                f"{reduction_percentage:.1f}%",
                delta=None
            )
        
        with col4:
            lives_saved = reduction_deaths
            st.metric(
                "Vidas Poupadas",
                f"{lives_saved:,}",
                delta=None
            )
        
        # Gráfico de comparação
        comparison_data = pd.DataFrame({
            'Cenário': ['Original', 'Filtrado', 'Pós-Intervenção'],
            'Acidentes': [original_accidents, filtered_accidents, simulated_accidents],
            'Mortes': [original_deaths, filtered_deaths, simulated_deaths]
        })
        
        fig = px.bar(
            comparison_data,
            x='Cenário',
            y=['Acidentes', 'Mortes'],
            title="Comparação de Cenários",
            barmode='group',
            color_discrete_sequence=['#1f77b4', '#d62728']
        )
        
        fig.update_layout(
            xaxis_title="Cenário",
            yaxis_title="Quantidade",
            legend_title="Métrica"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def create_filter_summary(filters):
    """
    Cria resumo dos filtros aplicados.
    """
    st.markdown("### 🎛️ Filtros Aplicados")
    
    with st.expander("Ver detalhes dos filtros", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📅 Período:**")
            st.write(f"• {filters['temporal']['start_year']} - {filters['temporal']['end_year']}")
            
            st.markdown("**🗺️ Estados:**")
            if filters['geographic']['states']:
                for state in filters['geographic']['states']:
                    st.write(f"• {state}")
            else:
                st.write("• Todos")
            
            st.markdown("**🛣️ Rodovias:**")
            if filters['geographic']['brs']:
                for br in filters['geographic']['brs']:
                    st.write(f"• BR-{br}")
            else:
                st.write("• Todas")
        
        with col2:
            st.markdown("**⚠️ Severidade:**")
            st.write(f"• Mortes: {'✅' if filters['severity']['deaths'] else '❌'}")
            st.write(f"• Feridos: {'✅' if filters['severity']['injuries'] else '❌'}")
            st.write(f"• Danos materiais: {'✅' if filters['severity']['material_damage'] else '❌'}")
            
            st.markdown("**🎯 Causas:**")
            if filters['causes']:
                for cause in filters['causes'][:3]:  # Mostra apenas as 3 primeiras
                    st.write(f"• {cause}")
                if len(filters['causes']) > 3:
                    st.write(f"• ... e mais {len(filters['causes']) - 3}")
            else:
                st.write("• Todas")
        
        if filters['intervention']['enabled']:
            st.markdown("**🛠️ Intervenções Simuladas:**")
            params = filters['intervention']['params']
            for intervention, value in params.items():
                if value > 0:
                    intervention_name = intervention.replace('_', ' ').title()
                    st.write(f"• {intervention_name}: {value}% redução")


def reset_session_filters():
    """
    Reseta todos os filtros para valores padrão.
    """
    # Lista de chaves de filtros para resetar
    filter_keys = [
        'start_year', 'end_year', 'selected_states', 'selected_brs',
        'include_deaths', 'include_injuries', 'include_material_damage',
        'selected_causes', 'selected_types', 'intervention_enabled',
        'speed_reduction', 'signaling_improvement', 'infrastructure_upgrade',
        'education_campaign'
    ]
    
    # Remove as chaves do session_state
    for key in filter_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()