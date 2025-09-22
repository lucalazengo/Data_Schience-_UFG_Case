"""
Componentes de filtros para o dashboard RoadInfra BI
"""

import streamlit as st
import pandas as pd

def create_main_filters(df):
    """Cria os filtros principais na sidebar"""
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por UF
    ufs_disponiveis = sorted(df['uf'].unique())
    uf_selecionada = st.sidebar.multiselect(
        "Estados (UF)",
        options=ufs_disponiveis,
        default=ufs_disponiveis[:5],  # Primeiros 5 estados por padrão
        help="Selecione os estados para análise"
    )
    
    # Filtro por BR
    brs_disponiveis = sorted(df['br'].unique())
    br_selecionada = st.sidebar.multiselect(
        "Rodovias (BR)",
        options=brs_disponiveis,
        default=brs_disponiveis[:10],  # Primeiras 10 BRs por padrão
        help="Selecione as rodovias federais"
    )
    
    # Filtro por Ano
    anos_disponiveis = sorted(df['ano'].unique())
    ano_range = st.sidebar.select_slider(
        "Período (Anos)",
        options=anos_disponiveis,
        value=(anos_disponiveis[0], anos_disponiveis[-1]),
        help="Selecione o período de análise"
    )
    
    # Filtro por Índice de Periculosidade
    indice_min, indice_max = st.sidebar.slider(
        "Índice de Periculosidade",
        min_value=float(df['indice_periculosidade'].min()),
        max_value=float(df['indice_periculosidade'].max()),
        value=(float(df['indice_periculosidade'].min()), 
               float(df['indice_periculosidade'].max())),
        step=0.1,
        help="Filtre por faixa de índice de periculosidade"
    )
    
    return {
        'uf': uf_selecionada,
        'br': br_selecionada,
        'ano_inicio': ano_range[0],
        'ano_fim': ano_range[1],
        'indice_min': indice_min,
        'indice_max': indice_max
    }

def create_advanced_filters(df):
    """Cria filtros avançados"""
    with st.expander("🔧 Filtros Avançados"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por causa do acidente
            causas_disponiveis = sorted(df['causa_acidente'].unique())
            causas_selecionadas = st.multiselect(
                "Causas de Acidentes",
                options=causas_disponiveis,
                default=causas_disponiveis,
                help="Filtre por causas específicas"
            )
            
            # Filtro por tipo de acidente
            tipos_disponiveis = sorted(df['tipo_acidente'].unique())
            tipos_selecionados = st.multiselect(
                "Tipos de Acidentes",
                options=tipos_disponiveis,
                default=tipos_disponiveis,
                help="Filtre por tipos específicos"
            )
        
        with col2:
            # Filtro por número mínimo de acidentes
            min_acidentes = st.number_input(
                "Mínimo de Acidentes",
                min_value=0,
                max_value=int(df['acidentes'].max()),
                value=0,
                help="Segmentos com pelo menos X acidentes"
            )
            
            # Filtro por número mínimo de mortos
            min_mortos = st.number_input(
                "Mínimo de Mortos",
                min_value=0,
                max_value=int(df['mortos'].max()),
                value=0,
                help="Segmentos com pelo menos X mortos"
            )
    
    return {
        'causas': causas_selecionadas,
        'tipos': tipos_selecionados,
        'min_acidentes': min_acidentes,
        'min_mortos': min_mortos
    }

def create_segment_selector(df_filtrado):
    """Cria seletor de segmento específico"""
    st.subheader("🎯 Análise de Segmento Específico")
    
    # Ordenar por índice de periculosidade
    df_ordenado = df_filtrado.sort_values('indice_periculosidade', ascending=False)
    
    # Criar lista de opções formatadas
    opcoes_segmentos = []
    for idx, row in df_ordenado.head(50).iterrows():  # Top 50 segmentos
        opcao = f"{row['segmento_id']} | Índice: {row['indice_periculosidade']:.2f} | Acidentes: {row['acidentes']}"
        opcoes_segmentos.append(opcao)
    
    segmento_selecionado = st.selectbox(
        "Selecione um segmento para análise detalhada:",
        options=["Nenhum"] + opcoes_segmentos,
        help="Escolha um segmento específico para análise micro"
    )
    
    if segmento_selecionado != "Nenhum":
        # Extrair o ID do segmento da string formatada
        segmento_id = segmento_selecionado.split(" | ")[0]
        segmento_data = df_filtrado[df_filtrado['segmento_id'] == segmento_id].iloc[0]
        return segmento_data.to_dict()
    
    return None

def apply_filters(df, filtros_principais, filtros_avancados=None):
    """Aplica todos os filtros ao dataframe"""
    df_filtrado = df.copy()
    
    # Aplicar filtros principais
    if filtros_principais['uf']:
        df_filtrado = df_filtrado[df_filtrado['uf'].isin(filtros_principais['uf'])]
    
    if filtros_principais['br']:
        df_filtrado = df_filtrado[df_filtrado['br'].isin(filtros_principais['br'])]
    
    df_filtrado = df_filtrado[
        (df_filtrado['ano'] >= filtros_principais['ano_inicio']) &
        (df_filtrado['ano'] <= filtros_principais['ano_fim'])
    ]
    
    df_filtrado = df_filtrado[
        (df_filtrado['indice_periculosidade'] >= filtros_principais['indice_min']) &
        (df_filtrado['indice_periculosidade'] <= filtros_principais['indice_max'])
    ]
    
    # Aplicar filtros avançados se fornecidos
    if filtros_avancados:
        if filtros_avancados['causas']:
            df_filtrado = df_filtrado[df_filtrado['causa_acidente'].isin(filtros_avancados['causas'])]
        
        if filtros_avancados['tipos']:
            df_filtrado = df_filtrado[df_filtrado['tipo_acidente'].isin(filtros_avancados['tipos'])]
        
        df_filtrado = df_filtrado[df_filtrado['acidentes'] >= filtros_avancados['min_acidentes']]
        df_filtrado = df_filtrado[df_filtrado['mortos'] >= filtros_avancados['min_mortos']]
    
    return df_filtrado

def create_export_options(df_filtrado):
    """Cria opções de exportação dos dados filtrados"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Exportar Dados")
    
    if st.sidebar.button("📥 Baixar CSV"):
        csv = df_filtrado.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"roadinfra_dados_filtrados.csv",
            mime="text/csv"
        )
    
    # Mostrar estatísticas dos dados filtrados
    st.sidebar.markdown("**Dados Filtrados:**")
    st.sidebar.metric("Segmentos", len(df_filtrado))
    st.sidebar.metric("Total Acidentes", df_filtrado['acidentes'].sum())
    st.sidebar.metric("Total Mortos", df_filtrado['mortos'].sum())
    st.sidebar.metric("Índice Médio", f"{df_filtrado['indice_periculosidade'].mean():.2f}")

def create_comparison_mode():
    """Cria modo de comparação entre períodos"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Modo Comparação")
    
    comparacao_ativa = st.sidebar.checkbox(
        "Ativar Comparação",
        help="Compare dados entre dois períodos diferentes"
    )
    
    if comparacao_ativa:
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.markdown("**Período 1:**")
            periodo1_inicio = st.selectbox("Ano Início", [2017, 2018, 2019, 2020], key="p1_inicio")
            periodo1_fim = st.selectbox("Ano Fim", [2019, 2020, 2021, 2022], key="p1_fim")
        
        with col2:
            st.markdown("**Período 2:**")
            periodo2_inicio = st.selectbox("Ano Início", [2020, 2021, 2022, 2023], key="p2_inicio")
            periodo2_fim = st.selectbox("Ano Fim", [2022, 2023, 2024], key="p2_fim")
        
        return {
            'ativo': True,
            'periodo1': (periodo1_inicio, periodo1_fim),
            'periodo2': (periodo2_inicio, periodo2_fim)
        }
    
    return {'ativo': False}