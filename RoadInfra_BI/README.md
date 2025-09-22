# RoadInfra BI - Sistema de Análise de Acidentes Rodoviários

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Visão Geral

O **RoadInfra BI** é um sistema de Business Intelligence desenvolvido para análise de acidentes rodoviários baseado nos dados do DATATRAN (Polícia Rodoviária Federal). O sistema oferece visualizações interativas, análises estatísticas avançadas e identificação de pontos críticos (black spots) nas rodovias federais brasileiras.

### 🎯 Principais Funcionalidades

- **Dashboard Interativo**: Interface web responsiva com Streamlit
- **Análise Macro**: Visão geral com filtros, mapas e estatísticas gerais
- **Análise Micro**: Análise detalhada por segmento de rodovia
- **Índice de Periculosidade**: Métrica proprietária para classificação de risco
- **Identificação de Black Spots**: Detecção automática de pontos críticos
- **Visualizações Avançadas**: Mapas interativos, gráficos temporais e heatmaps
- **Exportação de Dados**: Relatórios em CSV, Excel e PDF

## 🏗️ Arquitetura do Projeto

```
RoadInfra_BI/
├── 📁 data/                    # Dados do projeto
│   ├── raw/                    # Dados brutos DATATRAN
│   ├── processed/              # Dados processados
│   └── models/                 # Modelos treinados
├── 📁 src/                     # Código fonte
│   ├── data_processing/        # Scripts de processamento
│   ├── risk_modeling/          # Modelagem de risco
│   └── utils/                  # Utilitários
├── 📁 dashboard/               # Dashboard Streamlit
│   ├── pages/                  # Páginas do dashboard
│   ├── components/             # Componentes reutilizáveis
│   └── assets/                 # Recursos estáticos
├── 📁 docs/                    # Documentação
│   ├── technical/              # Documentação técnica
│   └── user_guide/             # Guia do usuário
├── 📁 config/                  # Configurações
└── requirements.txt            # Dependências
```

## 🔬 Metodologia

### Fase 1 - Análise e Modelagem do Risco

1. **Limpeza e Padronização**
   - Padronização de colunas: `br`, `km`, `uf`, `causa_acidente`, `tipo_acidente`
   - Tratamento de valores ausentes e inconsistências

2. **Segmentação**
   - Criação de `segmento_id` combinando `UF + BR + faixa de km`
   - Agrupamento por trechos de 10km

3. **Índice de Periculosidade**
   ```
   Índice = (Mortos × P1) + (Feridos Graves × P2) + (Feridos Leves × P3) + (Acidentes Sem Vítima × P4)
   ```
   - P1 = 10 (Peso para mortos)
   - P2 = 5 (Peso para feridos graves)
   - P3 = 2 (Peso para feridos leves)
   - P4 = 1 (Peso para acidentes sem vítima)

### Fase 2 - Dashboard Interativo

#### Visão Macro
- Filtros por UF, BR, Ano
- Tabela interativa com ranking de segmentos
- Mapa geográfico com intensidade pelo índice

#### Visão Micro
- KPIs principais (acidentes, mortos, índice)
- Análises detalhadas:
  - **O quê?** Top 5 causas de acidentes
  - **Como?** Distribuição por tipo de acidente
  - **Quando?** Sazonalidade anual/mensal

## 🚀 Como Usar

### Pré-requisitos
```bash
Python 3.8+
pip install -r requirements.txt
```

### Executar o Dashboard
```bash
streamlit run dashboard/main.py
```

## 📊 Principais Funcionalidades

- ✅ **Ranking de Black Spots**: Identificação dos trechos mais perigosos
- ✅ **Análise Temporal**: Evolução dos acidentes ao longo do tempo
- ✅ **Análise Causal**: Principais causas de acidentes por segmento
- ✅ **Visualizações Interativas**: Gráficos e mapas dinâmicos
- ✅ **Exportação de Relatórios**: Dados para tomada de decisão

## 🔧 Tecnologias Utilizadas

- **Python**: Linguagem principal
- **Streamlit**: Framework para dashboard
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **Folium**: Mapas geográficos
- **Scikit-learn**: Modelagem preditiva

## 📈 Resultados Esperados

- Redução de **30%** nos acidentes em trechos identificados
- Otimização de investimentos em infraestrutura
- Melhoria na segurança viária nacional
- Suporte data-driven para políticas públicas

## 👥 Equipe

Desenvolvido por especialistas em Ciência de Dados e Segurança Viária.

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**RoadInfra BI** - Transformando dados em vidas salvas 🛡️