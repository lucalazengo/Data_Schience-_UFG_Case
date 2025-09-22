"""
RoadInfra BI - Módulo de Limpeza e Padronização de Dados DATATRAN
================================================================

Este módulo é responsável pela limpeza, padronização e preparação dos dados
do DATATRAN para análise de segurança viária.

Autor: RoadInfra BI Team
Data: 2024
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTranCleaner:
    """
    Classe responsável pela limpeza e padronização dos dados DATATRAN.
    """
    
    def __init__(self):
        """Inicializa o limpador de dados com configurações padrão."""
        self.required_columns = [
            'br', 'km', 'uf', 'causa_acidente', 'tipo_acidente',
            'mortos', 'feridos_leves', 'feridos_graves', 'data_inversa'
        ]
        
        # Mapeamento de UFs para padronização
        self.uf_mapping = {
            'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPÁ': 'AP', 'AMAZONAS': 'AM',
            'BAHIA': 'BA', 'CEARÁ': 'CE', 'DISTRITO FEDERAL': 'DF',
            'ESPÍRITO SANTO': 'ES', 'GOIÁS': 'GO', 'MARANHÃO': 'MA',
            'MATO GROSSO': 'MT', 'MATO GROSSO DO SUL': 'MS', 'MINAS GERAIS': 'MG',
            'PARÁ': 'PA', 'PARAÍBA': 'PB', 'PARANÁ': 'PR', 'PERNAMBUCO': 'PE',
            'PIAUÍ': 'PI', 'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN',
            'RIO GRANDE DO SUL': 'RS', 'RONDÔNIA': 'RO', 'RORAIMA': 'RR',
            'SANTA CATARINA': 'SC', 'SÃO PAULO': 'SP', 'SERGIPE': 'SE',
            'TOCANTINS': 'TO'
        }
        
    def load_datatran_files(self, data_path: str) -> pd.DataFrame:
        """
        Carrega e consolida todos os arquivos DATATRAN de um diretório.
        
        Args:
            data_path (str): Caminho para o diretório com arquivos DATATRAN
            
        Returns:
            pd.DataFrame: DataFrame consolidado com todos os dados
        """
        logger.info(f"Carregando dados DATATRAN de: {data_path}")
        
        data_dir = Path(data_path)
        csv_files = list(data_dir.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {data_path}")
        
        dataframes = []
        
        for file_path in csv_files:
            try:
                logger.info(f"Processando arquivo: {file_path.name}")
                
                # Tentativa de leitura com diferentes encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, sep=';', low_memory=False)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.warning(f"Não foi possível ler {file_path.name} com encodings padrão")
                    continue
                
                # Adiciona coluna de origem do arquivo
                df['arquivo_origem'] = file_path.name
                dataframes.append(df)
                
            except Exception as e:
                logger.error(f"Erro ao processar {file_path.name}: {str(e)}")
                continue
        
        if not dataframes:
            raise ValueError("Nenhum arquivo foi carregado com sucesso")
        
        # Consolida todos os DataFrames
        consolidated_df = pd.concat(dataframes, ignore_index=True, sort=False)
        logger.info(f"Dados consolidados: {len(consolidated_df)} registros de {len(dataframes)} arquivos")
        
        return consolidated_df
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Padroniza os nomes das colunas do DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame com colunas padronizadas
        """
        logger.info("Padronizando nomes das colunas...")
        
        # Converte nomes para minúsculo e remove acentos
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('ascii')
        df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_')
        
        # Mapeamento de colunas conhecidas
        column_mapping = {
            'br': 'br',
            'km': 'km',
            'uf': 'uf',
            'causa_acidente': 'causa_acidente',
            'tipo_acidente': 'tipo_acidente',
            'classificacao_acidente': 'classificacao_acidente',
            'mortos': 'mortos',
            'feridos_leves': 'feridos_leves',
            'feridos_graves': 'feridos_graves',
            'data_inversa': 'data_inversa',
            'horario': 'horario',
            'dia_semana': 'dia_semana'
        }
        
        # Aplica mapeamento quando possível
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        return df
    
    def clean_br_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e padroniza a coluna BR (rodovia).
        
        Args:
            df (pd.DataFrame): DataFrame com coluna 'br'
            
        Returns:
            pd.DataFrame: DataFrame com coluna BR limpa
        """
        logger.info("Limpando coluna BR...")
        
        if 'br' not in df.columns:
            logger.warning("Coluna 'br' não encontrada")
            return df
        
        # Remove prefixos e sufixos desnecessários
        df['br'] = df['br'].astype(str)
        df['br'] = df['br'].str.replace('BR-', '', regex=False)
        df['br'] = df['br'].str.replace('BR ', '', regex=False)
        df['br'] = df['br'].str.strip()
        
        # Extrai apenas números da BR
        df['br'] = df['br'].str.extract(r'(\d+)')[0]
        
        # Converte para numérico
        df['br'] = pd.to_numeric(df['br'], errors='coerce')
        
        # Remove registros sem BR válida
        initial_count = len(df)
        df = df.dropna(subset=['br'])
        final_count = len(df)
        
        logger.info(f"Registros removidos por BR inválida: {initial_count - final_count}")
        
        return df
    
    def clean_km_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e padroniza a coluna KM.
        
        Args:
            df (pd.DataFrame): DataFrame com coluna 'km'
            
        Returns:
            pd.DataFrame: DataFrame com coluna KM limpa
        """
        logger.info("Limpando coluna KM...")
        
        if 'km' not in df.columns:
            logger.warning("Coluna 'km' não encontrada")
            return df
        
        # Converte para string e limpa
        df['km'] = df['km'].astype(str)
        df['km'] = df['km'].str.replace(',', '.', regex=False)
        
        # Extrai números decimais
        df['km'] = df['km'].str.extract(r'(\d+\.?\d*)')[0]
        
        # Converte para numérico
        df['km'] = pd.to_numeric(df['km'], errors='coerce')
        
        # Remove valores negativos ou muito altos (provavelmente erros)
        df = df[(df['km'] >= 0) & (df['km'] <= 9999)]
        
        return df
    
    def clean_uf_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e padroniza a coluna UF.
        
        Args:
            df (pd.DataFrame): DataFrame com coluna 'uf'
            
        Returns:
            pd.DataFrame: DataFrame com coluna UF limpa
        """
        logger.info("Limpando coluna UF...")
        
        if 'uf' not in df.columns:
            logger.warning("Coluna 'uf' não encontrada")
            return df
        
        # Converte para maiúsculo e remove espaços
        df['uf'] = df['uf'].astype(str).str.upper().str.strip()
        
        # Aplica mapeamento de nomes completos para siglas
        df['uf'] = df['uf'].replace(self.uf_mapping)
        
        # Mantém apenas UFs válidas (2 caracteres)
        valid_ufs = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        initial_count = len(df)
        df = df[df['uf'].isin(valid_ufs)]
        final_count = len(df)
        
        logger.info(f"Registros removidos por UF inválida: {initial_count - final_count}")
        
        return df
    
    def clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa colunas numéricas (mortos, feridos, etc.).
        
        Args:
            df (pd.DataFrame): DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame com colunas numéricas limpas
        """
        logger.info("Limpando colunas numéricas...")
        
        numeric_columns = ['mortos', 'feridos_leves', 'feridos_graves']
        
        for col in numeric_columns:
            if col in df.columns:
                # Converte para numérico, substituindo erros por 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                # Remove valores negativos
                df[col] = df[col].clip(lower=0)
                
                # Converte para inteiro
                df[col] = df[col].astype(int)
        
        return df
    
    def clean_date_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e padroniza a coluna de data.
        
        Args:
            df (pd.DataFrame): DataFrame com coluna de data
            
        Returns:
            pd.DataFrame: DataFrame com coluna de data limpa
        """
        logger.info("Limpando coluna de data...")
        
        date_columns = ['data_inversa', 'data', 'data_acidente']
        date_col = None
        
        # Encontra a coluna de data disponível
        for col in date_columns:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            logger.warning("Nenhuma coluna de data encontrada")
            return df
        
        # Converte para datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        
        # Remove registros sem data válida
        initial_count = len(df)
        df = df.dropna(subset=[date_col])
        final_count = len(df)
        
        logger.info(f"Registros removidos por data inválida: {initial_count - final_count}")
        
        # Cria colunas derivadas
        df['ano'] = df[date_col].dt.year
        df['mes'] = df[date_col].dt.month
        df['dia'] = df[date_col].dt.day
        
        # Padroniza nome da coluna
        if date_col != 'data_acidente':
            df = df.rename(columns={date_col: 'data_acidente'})
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove registros duplicados.
        
        Args:
            df (pd.DataFrame): DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame sem duplicatas
        """
        logger.info("Removendo duplicatas...")
        
        initial_count = len(df)
        
        # Define colunas para identificar duplicatas
        subset_columns = ['br', 'km', 'uf', 'data_acidente']
        subset_columns = [col for col in subset_columns if col in df.columns]
        
        if subset_columns:
            df = df.drop_duplicates(subset=subset_columns, keep='first')
        else:
            df = df.drop_duplicates()
        
        final_count = len(df)
        logger.info(f"Duplicatas removidas: {initial_count - final_count}")
        
        return df
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Valida a qualidade dos dados após limpeza.
        
        Args:
            df (pd.DataFrame): DataFrame limpo
            
        Returns:
            Dict: Relatório de qualidade dos dados
        """
        logger.info("Validando qualidade dos dados...")
        
        report = {
            'total_records': len(df),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict(),
            'unique_brs': df['br'].nunique() if 'br' in df.columns else 0,
            'unique_ufs': df['uf'].nunique() if 'uf' in df.columns else 0,
            'date_range': {
                'min': df['data_acidente'].min() if 'data_acidente' in df.columns else None,
                'max': df['data_acidente'].max() if 'data_acidente' in df.columns else None
            }
        }
        
        return report
    
    def clean_datatran(self, data_path: str, output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Executa o pipeline completo de limpeza dos dados DATATRAN.
        
        Args:
            data_path (str): Caminho para os dados brutos
            output_path (str, optional): Caminho para salvar dados limpos
            
        Returns:
            pd.DataFrame: DataFrame limpo e padronizado
        """
        logger.info("Iniciando pipeline de limpeza DATATRAN...")
        
        # 1. Carrega dados
        df = self.load_datatran_files(data_path)
        
        # 2. Padroniza colunas
        df = self.standardize_columns(df)
        
        # 3. Limpa colunas específicas
        df = self.clean_br_column(df)
        df = self.clean_km_column(df)
        df = self.clean_uf_column(df)
        df = self.clean_numeric_columns(df)
        df = self.clean_date_column(df)
        
        # 4. Remove duplicatas
        df = self.remove_duplicates(df)
        
        # 5. Valida qualidade
        quality_report = self.validate_data_quality(df)
        logger.info(f"Dados limpos: {quality_report['total_records']} registros")
        
        # 6. Salva dados limpos se especificado
        if output_path:
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Dados limpos salvos em: {output_path}")
        
        return df


# Exemplo de uso
if __name__ == "__main__":
    cleaner = DataTranCleaner()
    
    # Caminho para dados brutos
    raw_data_path = "../../data/raw"
    
    # Caminho para dados limpos
    clean_data_path = "../../data/processed/datatran_clean.csv"
    
    # Executa limpeza
    clean_df = cleaner.clean_datatran(raw_data_path, clean_data_path)
    
    print(f"Limpeza concluída! {len(clean_df)} registros processados.")