"""
RoadInfra BI - Módulo de Criação de Segmentos de Rodovia
=======================================================

Este módulo é responsável pela criação de segmentos de rodovia
combinando UF + BR + faixa de km para análise de black spots.

Autor: RoadInfra BI Team
Data: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentCreator:
    """
    Classe responsável pela criação de segmentos de rodovia para análise.
    """
    
    def __init__(self, segment_length: int = 10):
        """
        Inicializa o criador de segmentos.
        
        Args:
            segment_length (int): Comprimento do segmento em km (padrão: 10km)
        """
        self.segment_length = segment_length
        logger.info(f"SegmentCreator inicializado com segmentos de {segment_length}km")
    
    def create_segment_id(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria identificadores únicos para segmentos de rodovia.
        
        Args:
            df (pd.DataFrame): DataFrame com colunas 'uf', 'br', 'km'
            
        Returns:
            pd.DataFrame: DataFrame com coluna 'segmento_id' adicionada
        """
        logger.info("Criando identificadores de segmento...")
        
        # Verifica se as colunas necessárias existem
        required_cols = ['uf', 'br', 'km']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias não encontradas: {missing_cols}")
        
        # Cria uma cópia do DataFrame
        df_segments = df.copy()
        
        # Calcula a faixa de km para cada registro
        df_segments['km_inicio'] = (df_segments['km'] // self.segment_length) * self.segment_length
        df_segments['km_fim'] = df_segments['km_inicio'] + self.segment_length
        
        # Cria o identificador do segmento
        df_segments['segmento_id'] = (
            df_segments['uf'].astype(str) + '_' +
            'BR' + df_segments['br'].astype(str).str.zfill(3) + '_' +
            'KM' + df_segments['km_inicio'].astype(int).astype(str).str.zfill(4) + '_' +
            df_segments['km_fim'].astype(int).astype(str).str.zfill(4)
        )
        
        logger.info(f"Criados {df_segments['segmento_id'].nunique()} segmentos únicos")
        
        return df_segments
    
    def aggregate_by_segment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados por segmento de rodovia.
        
        Args:
            df (pd.DataFrame): DataFrame com segmentos criados
            
        Returns:
            pd.DataFrame: DataFrame agregado por segmento
        """
        logger.info("Agregando dados por segmento...")
        
        if 'segmento_id' not in df.columns:
            raise ValueError("Coluna 'segmento_id' não encontrada. Execute create_segment_id() primeiro.")
        
        # Define colunas para agregação
        agg_dict = {
            'uf': 'first',
            'br': 'first',
            'km_inicio': 'first',
            'km_fim': 'first',
        }
        
        # Adiciona colunas numéricas se existirem
        numeric_cols = ['mortos', 'feridos_leves', 'feridos_graves']
        for col in numeric_cols:
            if col in df.columns:
                agg_dict[col] = 'sum'
        
        # Adiciona contagem de acidentes
        agg_dict['total_acidentes'] = ('segmento_id', 'count')
        
        # Adiciona informações temporais se existirem
        if 'ano' in df.columns:
            agg_dict['anos_dados'] = ('ano', lambda x: sorted(x.unique()))
            agg_dict['ano_min'] = ('ano', 'min')
            agg_dict['ano_max'] = ('ano', 'max')
        
        # Executa agregação
        df_aggregated = df.groupby('segmento_id').agg(agg_dict).reset_index()
        
        # Renomeia colunas se necessário
        if ('segmento_id', 'count') in df_aggregated.columns:
            df_aggregated = df_aggregated.rename(columns={('segmento_id', 'count'): 'total_acidentes'})
        
        # Achata colunas multi-nível se existirem
        if isinstance(df_aggregated.columns, pd.MultiIndex):
            df_aggregated.columns = [col[1] if col[1] else col[0] for col in df_aggregated.columns]
        
        # Calcula estatísticas adicionais
        df_aggregated['total_feridos'] = 0
        if 'feridos_leves' in df_aggregated.columns and 'feridos_graves' in df_aggregated.columns:
            df_aggregated['total_feridos'] = (
                df_aggregated['feridos_leves'].fillna(0) + 
                df_aggregated['feridos_graves'].fillna(0)
            )
        
        # Calcula densidade de acidentes (acidentes por km)
        df_aggregated['densidade_acidentes'] = (
            df_aggregated['total_acidentes'] / self.segment_length
        )
        
        logger.info(f"Agregação concluída: {len(df_aggregated)} segmentos")
        
        return df_aggregated
    
    def create_segment_metadata(self, df_segments: pd.DataFrame) -> pd.DataFrame:
        """
        Cria metadados dos segmentos para análise.
        
        Args:
            df_segments (pd.DataFrame): DataFrame agregado por segmento
            
        Returns:
            pd.DataFrame: DataFrame com metadados dos segmentos
        """
        logger.info("Criando metadados dos segmentos...")
        
        metadata = df_segments.copy()
        
        # Adiciona informações geográficas
        metadata['regiao'] = metadata['uf'].map(self._get_region_mapping())
        
        # Classifica BR por tipo
        metadata['tipo_br'] = metadata['br'].apply(self._classify_br_type)
        
        # Calcula comprimento do segmento
        metadata['comprimento_km'] = self.segment_length
        
        # Adiciona coordenadas aproximadas (se disponível)
        # Nota: Em implementação real, seria necessário um serviço de geocodificação
        metadata['latitude_aprox'] = None
        metadata['longitude_aprox'] = None
        
        return metadata
    
    def _get_region_mapping(self) -> Dict[str, str]:
        """
        Retorna mapeamento de UF para região.
        
        Returns:
            Dict[str, str]: Mapeamento UF -> Região
        """
        return {
            # Norte
            'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte',
            'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
            
            # Nordeste
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
            'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste',
            'SE': 'Nordeste',
            
            # Centro-Oeste
            'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
            'DF': 'Centro-Oeste',
            
            # Sudeste
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            
            # Sul
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
    
    def _classify_br_type(self, br_number: int) -> str:
        """
        Classifica o tipo de BR baseado na numeração.
        
        Args:
            br_number (int): Número da BR
            
        Returns:
            str: Tipo da BR
        """
        if pd.isna(br_number):
            return 'Indefinido'
        
        br_num = int(br_number)
        
        if br_num < 100:
            return 'Radial'  # BRs que partem de Brasília
        elif br_num < 200:
            return 'Longitudinal'  # BRs no sentido Norte-Sul
        elif br_num < 300:
            return 'Transversal'  # BRs no sentido Leste-Oeste
        elif br_num < 400:
            return 'Diagonal'  # BRs em sentido diagonal
        else:
            return 'Ligação'  # BRs de ligação
    
    def get_segment_statistics(self, df_segments: pd.DataFrame) -> Dict:
        """
        Calcula estatísticas gerais dos segmentos.
        
        Args:
            df_segments (pd.DataFrame): DataFrame com segmentos
            
        Returns:
            Dict: Estatísticas dos segmentos
        """
        logger.info("Calculando estatísticas dos segmentos...")
        
        stats = {
            'total_segmentos': len(df_segments),
            'total_brs': df_segments['br'].nunique(),
            'total_ufs': df_segments['uf'].nunique(),
            'comprimento_total_km': len(df_segments) * self.segment_length,
            'acidentes_por_segmento': {
                'media': df_segments['total_acidentes'].mean(),
                'mediana': df_segments['total_acidentes'].median(),
                'maximo': df_segments['total_acidentes'].max(),
                'minimo': df_segments['total_acidentes'].min(),
                'desvio_padrao': df_segments['total_acidentes'].std()
            }
        }
        
        # Estatísticas por região se disponível
        if 'regiao' in df_segments.columns:
            stats['segmentos_por_regiao'] = df_segments['regiao'].value_counts().to_dict()
        
        # Estatísticas por tipo de BR se disponível
        if 'tipo_br' in df_segments.columns:
            stats['segmentos_por_tipo_br'] = df_segments['tipo_br'].value_counts().to_dict()
        
        return stats
    
    def create_segments_pipeline(self, df: pd.DataFrame, include_metadata: bool = True) -> Tuple[pd.DataFrame, Dict]:
        """
        Executa o pipeline completo de criação de segmentos.
        
        Args:
            df (pd.DataFrame): DataFrame limpo com dados DATATRAN
            include_metadata (bool): Se deve incluir metadados
            
        Returns:
            Tuple[pd.DataFrame, Dict]: DataFrame com segmentos e estatísticas
        """
        logger.info("Executando pipeline de criação de segmentos...")
        
        # 1. Cria identificadores de segmento
        df_with_segments = self.create_segment_id(df)
        
        # 2. Agrega por segmento
        df_aggregated = self.aggregate_by_segment(df_with_segments)
        
        # 3. Adiciona metadados se solicitado
        if include_metadata:
            df_aggregated = self.create_segment_metadata(df_aggregated)
        
        # 4. Calcula estatísticas
        statistics = self.get_segment_statistics(df_aggregated)
        
        logger.info("Pipeline de segmentos concluído com sucesso!")
        
        return df_aggregated, statistics


# Exemplo de uso
if __name__ == "__main__":
    # Simula dados para teste
    test_data = pd.DataFrame({
        'uf': ['SP', 'SP', 'RJ', 'RJ', 'MG'] * 20,
        'br': [101, 101, 116, 116, 381] * 20,
        'km': np.random.uniform(0, 500, 100),
        'mortos': np.random.poisson(0.5, 100),
        'feridos_leves': np.random.poisson(1.2, 100),
        'feridos_graves': np.random.poisson(0.3, 100),
        'ano': np.random.choice([2020, 2021, 2022, 2023], 100)
    })
    
    # Cria segmentos
    creator = SegmentCreator(segment_length=10)
    segments_df, stats = creator.create_segments_pipeline(test_data)
    
    print(f"Segmentos criados: {len(segments_df)}")
    print(f"Estatísticas: {stats}")
    print(segments_df.head())