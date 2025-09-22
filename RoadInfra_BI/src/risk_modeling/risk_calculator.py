"""
RoadInfra BI - Módulo de Cálculo do Índice de Periculosidade
===========================================================

Este módulo implementa o cálculo do Índice de Periculosidade para
identificação de black spots em rodovias federais.

Fórmula: Índice = (Mortos × P1) + (Feridos Graves × P2) + (Feridos Leves × P3) + (Acidentes Sem Vítima × P4)

Autor: RoadInfra BI Team
Data: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskWeights:
    """
    Classe para armazenar os pesos do Índice de Periculosidade.
    
    Pesos baseados em:
    - Impacto social e econômico
    - Severidade das consequências
    - Literatura científica em segurança viária
    """
    mortos: float = 10.0          # Peso máximo - impacto irreversível
    feridos_graves: float = 5.0   # Alto impacto - sequelas permanentes
    feridos_leves: float = 2.0    # Impacto moderado - recuperação possível
    sem_vitimas: float = 1.0      # Impacto mínimo - apenas danos materiais
    
    def __post_init__(self):
        """Valida os pesos após inicialização."""
        if not all(peso > 0 for peso in [self.mortos, self.feridos_graves, self.feridos_leves, self.sem_vitimas]):
            raise ValueError("Todos os pesos devem ser positivos")
        
        if not (self.mortos >= self.feridos_graves >= self.feridos_leves >= self.sem_vitimas):
            logger.warning("Recomenda-se que os pesos sigam ordem decrescente de severidade")


class RiskCalculator:
    """
    Classe responsável pelo cálculo do Índice de Periculosidade.
    """
    
    def __init__(self, weights: Optional[RiskWeights] = None):
        """
        Inicializa o calculador de risco.
        
        Args:
            weights (RiskWeights, optional): Pesos personalizados. Se None, usa pesos padrão.
        """
        self.weights = weights or RiskWeights()
        logger.info(f"RiskCalculator inicializado com pesos: {self.weights}")
    
    def calculate_base_risk_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o Índice de Periculosidade base para cada segmento.
        
        Args:
            df (pd.DataFrame): DataFrame com dados agregados por segmento
            
        Returns:
            pd.DataFrame: DataFrame com índice de risco calculado
        """
        logger.info("Calculando Índice de Periculosidade base...")
        
        # Verifica colunas necessárias
        required_cols = ['mortos', 'feridos_graves', 'feridos_leves', 'total_acidentes']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias não encontradas: {missing_cols}")
        
        df_risk = df.copy()
        
        # Preenche valores ausentes com 0
        for col in required_cols:
            df_risk[col] = df_risk[col].fillna(0)
        
        # Calcula acidentes sem vítimas
        df_risk['acidentes_sem_vitimas'] = (
            df_risk['total_acidentes'] - 
            (df_risk['mortos'] > 0).astype(int) - 
            (df_risk['feridos_graves'] > 0).astype(int) - 
            (df_risk['feridos_leves'] > 0).astype(int)
        ).clip(lower=0)
        
        # Calcula o índice base
        df_risk['indice_periculosidade_bruto'] = (
            df_risk['mortos'] * self.weights.mortos +
            df_risk['feridos_graves'] * self.weights.feridos_graves +
            df_risk['feridos_leves'] * self.weights.feridos_leves +
            df_risk['acidentes_sem_vitimas'] * self.weights.sem_vitimas
        )
        
        logger.info(f"Índice base calculado para {len(df_risk)} segmentos")
        
        return df_risk
    
    def normalize_risk_index(self, df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """
        Normaliza o Índice de Periculosidade para escala 0-100.
        
        Args:
            df (pd.DataFrame): DataFrame com índice bruto
            method (str): Método de normalização ('minmax', 'zscore', 'robust')
            
        Returns:
            pd.DataFrame: DataFrame com índice normalizado
        """
        logger.info(f"Normalizando índice usando método: {method}")
        
        df_normalized = df.copy()
        
        if 'indice_periculosidade_bruto' not in df.columns:
            raise ValueError("Coluna 'indice_periculosidade_bruto' não encontrada")
        
        # Remove valores infinitos ou NaN
        df_normalized = df_normalized[
            np.isfinite(df_normalized['indice_periculosidade_bruto'])
        ]
        
        if method == 'minmax':
            # Normalização Min-Max (0-100)
            scaler = MinMaxScaler(feature_range=(0, 100))
            df_normalized['indice_periculosidade'] = scaler.fit_transform(
                df_normalized[['indice_periculosidade_bruto']]
            ).flatten()
            
        elif method == 'zscore':
            # Normalização Z-Score convertida para 0-100
            mean_val = df_normalized['indice_periculosidade_bruto'].mean()
            std_val = df_normalized['indice_periculosidade_bruto'].std()
            
            z_scores = (df_normalized['indice_periculosidade_bruto'] - mean_val) / std_val
            
            # Converte Z-scores para escala 0-100
            min_z, max_z = z_scores.min(), z_scores.max()
            df_normalized['indice_periculosidade'] = (
                (z_scores - min_z) / (max_z - min_z) * 100
            )
            
        elif method == 'robust':
            # Normalização robusta usando percentis
            q25 = df_normalized['indice_periculosidade_bruto'].quantile(0.25)
            q75 = df_normalized['indice_periculosidade_bruto'].quantile(0.75)
            median = df_normalized['indice_periculosidade_bruto'].median()
            
            # Normalização robusta
            df_normalized['indice_periculosidade'] = (
                (df_normalized['indice_periculosidade_bruto'] - median) / (q75 - q25)
            )
            
            # Converte para escala 0-100
            min_val = df_normalized['indice_periculosidade'].min()
            max_val = df_normalized['indice_periculosidade'].max()
            df_normalized['indice_periculosidade'] = (
                (df_normalized['indice_periculosidade'] - min_val) / (max_val - min_val) * 100
            )
        
        else:
            raise ValueError(f"Método de normalização não suportado: {method}")
        
        # Garante que o índice está entre 0 e 100
        df_normalized['indice_periculosidade'] = df_normalized['indice_periculosidade'].clip(0, 100)
        
        logger.info(f"Normalização concluída. Índice varia de {df_normalized['indice_periculosidade'].min():.2f} a {df_normalized['indice_periculosidade'].max():.2f}")
        
        return df_normalized
    
    def classify_risk_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica segmentos em níveis de risco baseado no índice.
        
        Args:
            df (pd.DataFrame): DataFrame com índice normalizado
            
        Returns:
            pd.DataFrame: DataFrame com classificação de risco
        """
        logger.info("Classificando níveis de risco...")
        
        df_classified = df.copy()
        
        if 'indice_periculosidade' not in df.columns:
            raise ValueError("Coluna 'indice_periculosidade' não encontrada")
        
        # Define thresholds para classificação
        def classify_risk(index_value):
            if index_value >= 80:
                return 'Crítico'
            elif index_value >= 60:
                return 'Alto'
            elif index_value >= 40:
                return 'Moderado'
            elif index_value >= 20:
                return 'Baixo'
            else:
                return 'Muito Baixo'
        
        # Aplica classificação
        df_classified['nivel_risco'] = df_classified['indice_periculosidade'].apply(classify_risk)
        
        # Adiciona código numérico para ordenação
        risk_codes = {
            'Crítico': 5,
            'Alto': 4,
            'Moderado': 3,
            'Baixo': 2,
            'Muito Baixo': 1
        }
        
        df_classified['codigo_risco'] = df_classified['nivel_risco'].map(risk_codes)
        
        # Estatísticas da classificação
        risk_distribution = df_classified['nivel_risco'].value_counts()
        logger.info(f"Distribuição de risco: {risk_distribution.to_dict()}")
        
        return df_classified
    
    def calculate_temporal_risk_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula tendências temporais do risco por segmento.
        
        Args:
            df (pd.DataFrame): DataFrame com dados temporais
            
        Returns:
            pd.DataFrame: DataFrame com tendências de risco
        """
        logger.info("Calculando tendências temporais de risco...")
        
        if 'ano' not in df.columns:
            logger.warning("Coluna 'ano' não encontrada. Pulando análise temporal.")
            return df
        
        df_trends = df.copy()
        
        # Calcula índice por ano para cada segmento
        yearly_risk = []
        
        for segment_id in df_trends['segmento_id'].unique():
            segment_data = df_trends[df_trends['segmento_id'] == segment_id]
            
            for year in segment_data['ano'].unique():
                year_data = segment_data[segment_data['ano'] == year]
                
                # Calcula índice para o ano específico
                yearly_index = (
                    year_data['mortos'].sum() * self.weights.mortos +
                    year_data['feridos_graves'].sum() * self.weights.feridos_graves +
                    year_data['feridos_leves'].sum() * self.weights.feridos_leves +
                    (year_data['total_acidentes'].sum() - 
                     year_data[['mortos', 'feridos_graves', 'feridos_leves']].sum().sum()) * self.weights.sem_vitimas
                )
                
                yearly_risk.append({
                    'segmento_id': segment_id,
                    'ano': year,
                    'indice_anual': yearly_index
                })
        
        df_yearly = pd.DataFrame(yearly_risk)
        
        # Calcula tendência (slope) para cada segmento
        segment_trends = []
        
        for segment_id in df_yearly['segmento_id'].unique():
            segment_years = df_yearly[df_yearly['segmento_id'] == segment_id]
            
            if len(segment_years) > 1:
                # Calcula regressão linear simples
                x = segment_years['ano'].values
                y = segment_years['indice_anual'].values
                
                # Slope da regressão linear
                slope = np.polyfit(x, y, 1)[0]
                
                segment_trends.append({
                    'segmento_id': segment_id,
                    'tendencia_risco': slope,
                    'tendencia_categoria': 'Crescente' if slope > 0.1 else 'Decrescente' if slope < -0.1 else 'Estável'
                })
        
        df_trends_summary = pd.DataFrame(segment_trends)
        
        # Merge com dados principais
        if not df_trends_summary.empty:
            df_trends = df_trends.merge(df_trends_summary, on='segmento_id', how='left')
        
        return df_trends
    
    def generate_risk_report(self, df: pd.DataFrame) -> Dict:
        """
        Gera relatório completo de análise de risco.
        
        Args:
            df (pd.DataFrame): DataFrame com análise de risco completa
            
        Returns:
            Dict: Relatório de risco
        """
        logger.info("Gerando relatório de risco...")
        
        report = {
            'resumo_geral': {
                'total_segmentos': len(df),
                'indice_medio': df['indice_periculosidade'].mean(),
                'indice_mediano': df['indice_periculosidade'].median(),
                'desvio_padrao': df['indice_periculosidade'].std()
            },
            'distribuicao_risco': df['nivel_risco'].value_counts().to_dict(),
            'top_10_mais_perigosos': df.nlargest(10, 'indice_periculosidade')[
                ['segmento_id', 'uf', 'br', 'indice_periculosidade', 'nivel_risco']
            ].to_dict('records'),
            'estatisticas_por_uf': df.groupby('uf')['indice_periculosidade'].agg([
                'count', 'mean', 'median', 'max'
            ]).to_dict(),
            'pesos_utilizados': {
                'mortos': self.weights.mortos,
                'feridos_graves': self.weights.feridos_graves,
                'feridos_leves': self.weights.feridos_leves,
                'sem_vitimas': self.weights.sem_vitimas
            }
        }
        
        # Adiciona análise temporal se disponível
        if 'tendencia_risco' in df.columns:
            report['tendencias_temporais'] = df['tendencia_categoria'].value_counts().to_dict()
        
        return report
    
    def calculate_risk_pipeline(self, df: pd.DataFrame, normalization_method: str = 'minmax') -> Tuple[pd.DataFrame, Dict]:
        """
        Executa o pipeline completo de cálculo de risco.
        
        Args:
            df (pd.DataFrame): DataFrame com dados agregados por segmento
            normalization_method (str): Método de normalização
            
        Returns:
            Tuple[pd.DataFrame, Dict]: DataFrame com risco calculado e relatório
        """
        logger.info("Executando pipeline completo de cálculo de risco...")
        
        # 1. Calcula índice base
        df_with_base_risk = self.calculate_base_risk_index(df)
        
        # 2. Normaliza índice
        df_normalized = self.normalize_risk_index(df_with_base_risk, normalization_method)
        
        # 3. Classifica níveis de risco
        df_classified = self.classify_risk_levels(df_normalized)
        
        # 4. Calcula tendências temporais (se dados disponíveis)
        df_with_trends = self.calculate_temporal_risk_trends(df_classified)
        
        # 5. Gera relatório
        report = self.generate_risk_report(df_with_trends)
        
        logger.info("Pipeline de cálculo de risco concluído com sucesso!")
        
        return df_with_trends, report


# Exemplo de uso
if __name__ == "__main__":
    # Simula dados para teste
    test_data = pd.DataFrame({
        'segmento_id': [f'SP_BR101_KM{i:04d}_{i+10:04d}' for i in range(0, 100, 10)],
        'uf': ['SP'] * 10,
        'br': [101] * 10,
        'total_acidentes': np.random.poisson(5, 10),
        'mortos': np.random.poisson(0.3, 10),
        'feridos_graves': np.random.poisson(0.8, 10),
        'feridos_leves': np.random.poisson(1.5, 10),
        'ano': [2023] * 10
    })
    
    # Calcula risco
    calculator = RiskCalculator()
    risk_df, report = calculator.calculate_risk_pipeline(test_data)
    
    print(f"Análise de risco concluída para {len(risk_df)} segmentos")
    print(f"Índice médio: {report['resumo_geral']['indice_medio']:.2f}")
    print(f"Distribuição de risco: {report['distribuicao_risco']}")
    print(risk_df[['segmento_id', 'indice_periculosidade', 'nivel_risco']].head())