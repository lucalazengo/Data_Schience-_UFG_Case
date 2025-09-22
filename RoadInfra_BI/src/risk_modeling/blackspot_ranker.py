"""
RoadInfra BI - Módulo de Ranking de Black Spots
===============================================

Este módulo implementa a geração do ranking oficial de black spots
baseado no Índice de Periculosidade e outros critérios relevantes.

Autor: RoadInfra BI Team
Data: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from datetime import datetime
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RankingCriteria:
    """
    Critérios para geração do ranking de black spots.
    """
    min_accidents: int = 3          # Mínimo de acidentes para considerar
    min_years_data: int = 2         # Mínimo de anos com dados
    weight_severity: float = 0.6    # Peso para severidade (índice)
    weight_frequency: float = 0.3   # Peso para frequência
    weight_trend: float = 0.1       # Peso para tendência temporal
    
    def __post_init__(self):
        """Valida critérios após inicialização."""
        total_weight = self.weight_severity + self.weight_frequency + self.weight_trend
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Soma dos pesos deve ser 1.0, atual: {total_weight}")


class BlackSpotRanker:
    """
    Classe responsável pela geração do ranking de black spots.
    """
    
    def __init__(self, criteria: Optional[RankingCriteria] = None):
        """
        Inicializa o rankeador de black spots.
        
        Args:
            criteria (RankingCriteria, optional): Critérios personalizados
        """
        self.criteria = criteria or RankingCriteria()
        logger.info(f"BlackSpotRanker inicializado com critérios: {self.criteria}")
    
    def filter_eligible_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra segmentos elegíveis para o ranking baseado nos critérios.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de risco
            
        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        logger.info("Filtrando segmentos elegíveis para ranking...")
        
        df_filtered = df.copy()
        initial_count = len(df_filtered)
        
        # Filtro 1: Mínimo de acidentes
        if 'total_acidentes' in df_filtered.columns:
            df_filtered = df_filtered[
                df_filtered['total_acidentes'] >= self.criteria.min_accidents
            ]
            logger.info(f"Após filtro de acidentes mínimos: {len(df_filtered)} segmentos")
        
        # Filtro 2: Mínimo de anos com dados (se disponível)
        if 'anos_com_dados' in df_filtered.columns:
            df_filtered = df_filtered[
                df_filtered['anos_com_dados'] >= self.criteria.min_years_data
            ]
            logger.info(f"Após filtro de anos mínimos: {len(df_filtered)} segmentos")
        elif 'ano' in df_filtered.columns:
            # Calcula anos com dados por segmento
            years_per_segment = df_filtered.groupby('segmento_id')['ano'].nunique()
            valid_segments = years_per_segment[
                years_per_segment >= self.criteria.min_years_data
            ].index
            df_filtered = df_filtered[
                df_filtered['segmento_id'].isin(valid_segments)
            ]
            logger.info(f"Após filtro de anos mínimos: {len(df_filtered)} segmentos")
        
        # Remove segmentos com dados incompletos
        required_cols = ['indice_periculosidade', 'segmento_id']
        df_filtered = df_filtered.dropna(subset=required_cols)
        
        logger.info(f"Segmentos elegíveis: {len(df_filtered)} de {initial_count} ({len(df_filtered)/initial_count*100:.1f}%)")
        
        return df_filtered
    
    def calculate_frequency_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score de frequência baseado na densidade de acidentes.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de segmentos
            
        Returns:
            pd.DataFrame: DataFrame com score de frequência
        """
        logger.info("Calculando score de frequência...")
        
        df_freq = df.copy()
        
        if 'total_acidentes' not in df_freq.columns:
            logger.warning("Coluna 'total_acidentes' não encontrada. Score de frequência será 0.")
            df_freq['frequency_score'] = 0
            return df_freq
        
        # Calcula densidade de acidentes (acidentes por km por ano)
        if 'extensao_km' in df_freq.columns and 'anos_com_dados' in df_freq.columns:
            df_freq['densidade_acidentes'] = (
                df_freq['total_acidentes'] / 
                (df_freq['extensao_km'] * df_freq['anos_com_dados'])
            )
        else:
            # Usa total de acidentes como proxy
            df_freq['densidade_acidentes'] = df_freq['total_acidentes']
        
        # Normaliza para score 0-100
        max_density = df_freq['densidade_acidentes'].max()
        if max_density > 0:
            df_freq['frequency_score'] = (
                df_freq['densidade_acidentes'] / max_density * 100
            )
        else:
            df_freq['frequency_score'] = 0
        
        return df_freq
    
    def calculate_trend_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score de tendência temporal.
        
        Args:
            df (pd.DataFrame): DataFrame com dados temporais
            
        Returns:
            pd.DataFrame: DataFrame com score de tendência
        """
        logger.info("Calculando score de tendência...")
        
        df_trend = df.copy()
        
        if 'tendencia_risco' in df_trend.columns:
            # Usa tendência já calculada
            # Tendência positiva (crescente) recebe score maior
            max_trend = df_trend['tendencia_risco'].abs().max()
            if max_trend > 0:
                df_trend['trend_score'] = np.where(
                    df_trend['tendencia_risco'] > 0,
                    df_trend['tendencia_risco'] / max_trend * 100,
                    0  # Tendências decrescentes recebem score 0
                )
            else:
                df_trend['trend_score'] = 50  # Score neutro
        else:
            logger.warning("Dados de tendência não disponíveis. Score de tendência será neutro (50).")
            df_trend['trend_score'] = 50
        
        return df_trend
    
    def calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score composto para ranking final.
        
        Args:
            df (pd.DataFrame): DataFrame com todos os scores
            
        Returns:
            pd.DataFrame: DataFrame com score composto
        """
        logger.info("Calculando score composto...")
        
        df_composite = df.copy()
        
        # Verifica se todas as colunas necessárias existem
        required_scores = ['indice_periculosidade']
        optional_scores = ['frequency_score', 'trend_score']
        
        # Preenche scores opcionais se não existirem
        for score in optional_scores:
            if score not in df_composite.columns:
                if score == 'frequency_score':
                    df_composite = self.calculate_frequency_score(df_composite)
                elif score == 'trend_score':
                    df_composite = self.calculate_trend_score(df_composite)
        
        # Calcula score composto
        df_composite['composite_score'] = (
            df_composite['indice_periculosidade'] * self.criteria.weight_severity +
            df_composite['frequency_score'] * self.criteria.weight_frequency +
            df_composite['trend_score'] * self.criteria.weight_trend
        )
        
        # Garante que o score está entre 0 e 100
        df_composite['composite_score'] = df_composite['composite_score'].clip(0, 100)
        
        return df_composite
    
    def generate_ranking(self, df: pd.DataFrame, top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Gera o ranking oficial de black spots.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de risco
            top_n (int, optional): Número de top segmentos a retornar
            
        Returns:
            pd.DataFrame: DataFrame com ranking
        """
        logger.info(f"Gerando ranking de black spots (top {top_n or 'todos'})...")
        
        # 1. Filtra segmentos elegíveis
        df_eligible = self.filter_eligible_segments(df)
        
        if df_eligible.empty:
            logger.warning("Nenhum segmento elegível encontrado para ranking!")
            return pd.DataFrame()
        
        # 2. Calcula scores
        df_with_scores = self.calculate_composite_score(df_eligible)
        
        # 3. Ordena por score composto
        df_ranked = df_with_scores.sort_values(
            'composite_score', 
            ascending=False
        ).reset_index(drop=True)
        
        # 4. Adiciona posição no ranking
        df_ranked['ranking_position'] = range(1, len(df_ranked) + 1)
        
        # 5. Adiciona classificação de black spot
        df_ranked['blackspot_category'] = df_ranked['ranking_position'].apply(
            self._classify_blackspot_category
        )
        
        # 6. Limita ao top N se especificado
        if top_n:
            df_ranked = df_ranked.head(top_n)
        
        logger.info(f"Ranking gerado com {len(df_ranked)} black spots")
        
        return df_ranked
    
    def _classify_blackspot_category(self, position: int) -> str:
        """
        Classifica categoria do black spot baseado na posição.
        
        Args:
            position (int): Posição no ranking
            
        Returns:
            str: Categoria do black spot
        """
        if position <= 10:
            return 'Crítico - Top 10'
        elif position <= 50:
            return 'Alto Risco - Top 50'
        elif position <= 100:
            return 'Risco Elevado - Top 100'
        elif position <= 500:
            return 'Atenção - Top 500'
        else:
            return 'Monitoramento'
    
    def generate_ranking_by_state(self, df: pd.DataFrame, top_n_per_state: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Gera ranking de black spots por estado.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de risco
            top_n_per_state (int): Top N por estado
            
        Returns:
            Dict[str, pd.DataFrame]: Rankings por estado
        """
        logger.info(f"Gerando ranking por estado (top {top_n_per_state} por UF)...")
        
        if 'uf' not in df.columns:
            logger.error("Coluna 'uf' não encontrada!")
            return {}
        
        rankings_by_state = {}
        
        for uf in df['uf'].unique():
            logger.info(f"Processando ranking para {uf}...")
            
            state_data = df[df['uf'] == uf].copy()
            state_ranking = self.generate_ranking(state_data, top_n_per_state)
            
            if not state_ranking.empty:
                rankings_by_state[uf] = state_ranking
        
        logger.info(f"Rankings gerados para {len(rankings_by_state)} estados")
        
        return rankings_by_state
    
    def generate_ranking_by_highway(self, df: pd.DataFrame, top_n_per_highway: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Gera ranking de black spots por rodovia.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de risco
            top_n_per_highway (int): Top N por rodovia
            
        Returns:
            Dict[str, pd.DataFrame]: Rankings por rodovia
        """
        logger.info(f"Gerando ranking por rodovia (top {top_n_per_highway} por BR)...")
        
        if 'br' not in df.columns:
            logger.error("Coluna 'br' não encontrada!")
            return {}
        
        rankings_by_highway = {}
        
        for br in df['br'].unique():
            logger.info(f"Processando ranking para BR-{br}...")
            
            highway_data = df[df['br'] == br].copy()
            highway_ranking = self.generate_ranking(highway_data, top_n_per_highway)
            
            if not highway_ranking.empty:
                rankings_by_highway[f'BR-{br}'] = highway_ranking
        
        logger.info(f"Rankings gerados para {len(rankings_by_highway)} rodovias")
        
        return rankings_by_highway
    
    def export_ranking_report(self, df_ranking: pd.DataFrame, output_path: str) -> Dict:
        """
        Exporta relatório completo do ranking.
        
        Args:
            df_ranking (pd.DataFrame): DataFrame com ranking
            output_path (str): Caminho para salvar o relatório
            
        Returns:
            Dict: Relatório do ranking
        """
        logger.info(f"Exportando relatório de ranking para {output_path}...")
        
        # Gera relatório
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_blackspots': len(df_ranking),
                'criteria_used': {
                    'min_accidents': self.criteria.min_accidents,
                    'min_years_data': self.criteria.min_years_data,
                    'weight_severity': self.criteria.weight_severity,
                    'weight_frequency': self.criteria.weight_frequency,
                    'weight_trend': self.criteria.weight_trend
                }
            },
            'summary_statistics': {
                'avg_composite_score': df_ranking['composite_score'].mean(),
                'median_composite_score': df_ranking['composite_score'].median(),
                'max_composite_score': df_ranking['composite_score'].max(),
                'min_composite_score': df_ranking['composite_score'].min()
            },
            'category_distribution': df_ranking['blackspot_category'].value_counts().to_dict(),
            'top_10_blackspots': df_ranking.head(10)[[
                'ranking_position', 'segmento_id', 'uf', 'br', 
                'composite_score', 'indice_periculosidade', 'blackspot_category'
            ]].to_dict('records')
        }
        
        # Adiciona estatísticas por UF se disponível
        if 'uf' in df_ranking.columns:
            report['statistics_by_state'] = df_ranking.groupby('uf').agg({
                'composite_score': ['count', 'mean', 'max'],
                'indice_periculosidade': 'mean'
            }).to_dict()
        
        # Salva relatório em JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("Relatório de ranking exportado com sucesso!")
        
        return report
    
    def generate_complete_ranking_analysis(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
        """
        Gera análise completa de ranking com múltiplas perspectivas.
        
        Args:
            df (pd.DataFrame): DataFrame com dados de risco
            
        Returns:
            Tuple: (ranking_geral, rankings_por_estado, rankings_por_rodovia, relatorio)
        """
        logger.info("Gerando análise completa de ranking...")
        
        # 1. Ranking geral
        general_ranking = self.generate_ranking(df)
        
        # 2. Rankings por estado
        state_rankings = self.generate_ranking_by_state(df)
        
        # 3. Rankings por rodovia
        highway_rankings = self.generate_ranking_by_highway(df)
        
        # 4. Relatório consolidado
        consolidated_report = {
            'general_ranking_summary': {
                'total_blackspots': len(general_ranking),
                'critical_spots': len(general_ranking[general_ranking['blackspot_category'] == 'Crítico - Top 10']),
                'high_risk_spots': len(general_ranking[general_ranking['blackspot_category'] == 'Alto Risco - Top 50'])
            },
            'state_analysis': {
                'states_analyzed': len(state_rankings),
                'avg_blackspots_per_state': np.mean([len(ranking) for ranking in state_rankings.values()]) if state_rankings else 0
            },
            'highway_analysis': {
                'highways_analyzed': len(highway_rankings),
                'avg_blackspots_per_highway': np.mean([len(ranking) for ranking in highway_rankings.values()]) if highway_rankings else 0
            }
        }
        
        logger.info("Análise completa de ranking concluída!")
        
        return general_ranking, state_rankings, highway_rankings, consolidated_report


# Exemplo de uso
if __name__ == "__main__":
    # Simula dados para teste
    test_data = pd.DataFrame({
        'segmento_id': [f'SP_BR101_KM{i:04d}_{i+10:04d}' for i in range(0, 100, 10)],
        'uf': ['SP'] * 10,
        'br': [101] * 10,
        'total_acidentes': np.random.poisson(8, 10),
        'mortos': np.random.poisson(0.5, 10),
        'feridos_graves': np.random.poisson(1.2, 10),
        'feridos_leves': np.random.poisson(2.0, 10),
        'indice_periculosidade': np.random.uniform(20, 95, 10),
        'anos_com_dados': np.random.randint(3, 8, 10),
        'extensao_km': [10] * 10
    })
    
    # Gera ranking
    ranker = BlackSpotRanker()
    ranking = ranker.generate_ranking(test_data, top_n=5)
    
    print(f"Top 5 Black Spots:")
    print(ranking[['ranking_position', 'segmento_id', 'composite_score', 'blackspot_category']].to_string(index=False))