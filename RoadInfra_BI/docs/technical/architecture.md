# Arquitetura do Sistema RoadInfra BI

## Visão Geral

O RoadInfra BI é um sistema de Business Intelligence desenvolvido para análise de acidentes rodoviários baseado nos dados do DATATRAN. O sistema utiliza uma arquitetura modular que permite análises tanto macro (visão geral) quanto micro (segmentos específicos).

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    RoadInfra BI System                     │
├─────────────────────────────────────────────────────────────┤
│  Dashboard Layer (Streamlit)                               │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   Visão Macro   │  │   Visão Micro   │                 │
│  │   - Filtros     │  │   - KPIs        │                 │
│  │   - Tabelas     │  │   - Análises    │                 │
│  │   - Mapas       │  │   - Recomend.   │                 │
│  └─────────────────┘  └─────────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│  Processing Layer                                           │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Data Processing │  │ Risk Modeling   │                 │
│  │ - DataCleaner   │  │ - RiskCalc      │                 │
│  │ - SegmentCreator│  │ - BlackSpotRank │                 │
│  └─────────────────┘  └─────────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   Raw Data      │  │ Processed Data  │                 │
│  │   - DATATRAN    │  │   - Segments    │                 │
│  │   - CSV Files   │  │   - Indices     │                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. Data Processing Layer

#### DataCleaner (`src/data_processing/data_cleaner.py`)
- **Função**: Limpeza e padronização dos dados DATATRAN
- **Responsabilidades**:
  - Carregamento de dados CSV
  - Padronização de nomes de colunas
  - Limpeza de dados de BR, KM, UF
  - Tratamento de valores nulos e duplicatas
  - Validação de qualidade dos dados

#### SegmentCreator (`src/data_processing/segment_creator.py`)
- **Função**: Criação de segmentos de rodovia
- **Responsabilidades**:
  - Combinação UF + BR + faixa de KM
  - Agregação de dados por segmento
  - Criação de metadados dos segmentos
  - Cálculo de estatísticas por segmento

### 2. Risk Modeling Layer

#### RiskCalculator (`src/risk_modeling/risk_calculator.py`)
- **Função**: Cálculo do Índice de Periculosidade
- **Responsabilidades**:
  - Aplicação de pesos documentados
  - Normalização de dados
  - Classificação de níveis de risco
  - Análise de tendências temporais

#### BlackSpotRanker (`src/risk_modeling/blackspot_ranker.py`)
- **Função**: Geração de ranking de black spots
- **Responsabilidades**:
  - Filtragem de segmentos críticos
  - Cálculo de scores compostos
  - Geração de rankings por estado/rodovia
  - Exportação de relatórios

### 3. Dashboard Layer

#### Main Dashboard (`dashboard/main.py`)
- **Função**: Interface principal do sistema
- **Responsabilidades**:
  - Visão macro com filtros
  - Tabelas de ranking
  - Mapas de risco
  - KPIs gerais

#### Micro Analysis (`dashboard/pages/micro_analysis.py`)
- **Função**: Análise detalhada por segmento
- **Responsabilidades**:
  - Seleção de segmentos específicos
  - KPIs detalhados
  - Análises temporais e causais
  - Recomendações de intervenção

#### Components (`dashboard/components/`)
- **charts.py**: Componentes de gráficos reutilizáveis
- **filters.py**: Componentes de filtros e seletores

## Fluxo de Dados

```
1. Raw Data (DATATRAN CSV)
   ↓
2. DataCleaner → Cleaned Data
   ↓
3. SegmentCreator → Segmented Data
   ↓
4. RiskCalculator → Risk Indices
   ↓
5. BlackSpotRanker → Rankings
   ↓
6. Dashboard → Visualizations
```

## Tecnologias Utilizadas

### Core Framework
- **Streamlit**: Framework principal para dashboard web
- **Python 3.8+**: Linguagem de programação

### Data Processing
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **GeoPandas**: Dados geoespaciais
- **Scikit-learn**: Machine learning e normalização

### Visualization
- **Plotly**: Gráficos interativos
- **Folium**: Mapas interativos
- **Streamlit-Folium**: Integração de mapas no Streamlit

### Development Tools
- **Black**: Formatação de código
- **Flake8**: Linting
- **Pytest**: Testes unitários

## Padrões de Design

### 1. Modularidade
- Cada componente tem responsabilidade única
- Interfaces bem definidas entre módulos
- Reutilização de código através de componentes

### 2. Configurabilidade
- Pesos do índice de periculosidade configuráveis
- Filtros flexíveis no dashboard
- Parâmetros ajustáveis nos algoritmos

### 3. Escalabilidade
- Processamento em lotes para grandes volumes
- Cache de dados processados
- Componentes independentes

## Estrutura de Diretórios

```
RoadInfra_BI/
├── src/                    # Código fonte
│   ├── data_processing/    # Processamento de dados
│   ├── risk_modeling/      # Modelagem de risco
│   └── utils/             # Utilitários
├── dashboard/             # Interface web
│   ├── components/        # Componentes reutilizáveis
│   ├── pages/            # Páginas do dashboard
│   └── assets/           # Recursos estáticos
├── data/                 # Dados
│   ├── raw/             # Dados brutos
│   ├── processed/       # Dados processados
│   └── models/          # Modelos salvos
├── docs/                # Documentação
│   ├── technical/       # Documentação técnica
│   └── user_guide/      # Guia do usuário
└── config/              # Configurações
```

## Configurações e Parâmetros

### Índice de Periculosidade
```python
PESOS_PADRAO = {
    'mortos': 10.0,
    'feridos_graves': 5.0,
    'feridos_leves': 2.0,
    'acidentes': 1.0
}
```

### Classificação de Risco
- **Crítico**: Índice > 8.0
- **Alto**: Índice 5.0 - 8.0
- **Moderado**: Índice < 5.0

### Segmentação
- **Tamanho padrão**: 50 km por segmento
- **Formato ID**: `{UF}-BR{BR:03d}-KM{inicio:03d}-{fim:03d}`

## Performance e Otimização

### Estratégias de Cache
- Cache de dados processados em memória
- Persistência de resultados intermediários
- Lazy loading de componentes pesados

### Otimizações de Consulta
- Indexação por segmento_id
- Filtros aplicados antes do processamento
- Agregações pré-calculadas

## Segurança e Validação

### Validação de Dados
- Verificação de tipos de dados
- Validação de ranges de valores
- Detecção de outliers

### Tratamento de Erros
- Logs estruturados
- Fallbacks para dados ausentes
- Mensagens de erro informativas

## Extensibilidade

### Novos Indicadores
- Interface para adicionar novos cálculos de risco
- Sistema de plugins para métricas customizadas

### Novas Visualizações
- Componentes modulares para gráficos
- Templates para novas páginas

### Integração de Dados
- Suporte para múltiplas fontes de dados
- APIs para dados externos