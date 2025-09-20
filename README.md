# Projeto de Ciência de Dados – Análise de Acidentes de Trânsito (2017–2024)

## 📌 Informações Gerais

* **Disciplina:** Ciência de Dados
* **Especialização:** \[Nome do curso]
* **Equipe:** \[Nomes dos integrantes]
* **Base de dados:** Acidentes de trânsito em rodovias federais do Brasil (DATATRAN – 2017 a 2024).

Este projeto tem como objetivo explorar e analisar dados de acidentes de trânsito nas rodovias federais do Brasil. Através da limpeza, consolidação e análise exploratória, serão obtidos **insights valiosos sobre padrões, tendências e fatores de risco**, visando contribuir para a **conscientização e redução dos acidentes**.

---

## 📂 Estrutura do Projeto

```
src/
│
├── data/
│   ├── processed_data/         # Dados limpos e prontos para análise
│   └── raw_data/               # Dados originais
│       ├── datatran2017.csv
│       ├── datatran2018.csv
│       ├── datatran2019.csv
│       ├── datatran2020.csv
│       ├── datatran2021.csv
│       ├── datatran2022.csv
│       ├── datatran2023.csv
│       └── datatran2024.csv
│
├── Dicionário de Variáveis_ocorrencia_2017.pdf
├── Dicionário de Variáveis_pessoa_2017.pdf
└── Dicionário de Variáveis_pessoa_2017_todas_causas_tipos.pdf
```

---

## 🔎 Etapas do Projeto (Metodologia CRISP-DM)

### 1. Business Understanding

* Pesquisar e descrever o contexto do **DATATRAN** (base oficial da Polícia Rodoviária Federal).
* Entender os **problemas de negócio**: causas de acidentes, impacto social e econômico.
* Identificar **stakeholders** (governo, sociedade civil, órgãos de saúde).

📊 **Recomendação:** Sempre que possível, apresente **gráficos contextuais** (por exemplo: número total de acidentes por ano).

---

### 2. Data Understanding

* Descrever os dados (formato `.csv`, número de registros, colunas disponíveis).
* Verificar tipos de variáveis (numéricas, categóricas, temporais).
* Identificar inconsistências, valores ausentes, duplicados e outliers.

📊 **Recomendação:**

* Gráfico de barras para contagem de registros por ano.
* Histogramas para verificar distribuições.
* Gráficos de linha para evolução temporal.

---

### 3. Data Preparation

* Selecionar variáveis relevantes (ex: tipo de acidente, causa, estado, data, hora, número de vítimas).
* Aplicar rotinas de limpeza:

  * Padronização de nomes.
  * Remoção de duplicatas.
  * Tratamento de valores ausentes (média, mediana, moda).
  * Criação de atributos derivados (ex: mês, dia da semana, horário do acidente).

📊 **Recomendação:**

* Gráficos comparativos antes e depois da limpeza.
* Visualizações iniciais para padrões e tendências (gráficos de linha ou heatmaps).

---

### 4. Análise Exploratória de Dados (AED)

* Estatísticas descritivas: média, mediana, moda.
* Medidas de dispersão: amplitude, variância, desvio padrão.
* Comparar variância x desvio padrão.
* Identificar linearidade vs. não linearidade.
* Correlação e covariância (dados lineares).
* Coeficiente de Spearman (dados não lineares).

📊 **Recomendação:**

* **Boxplot:** detectar outliers.
* **Scatter Plot:** identificar correlações.
* **Heatmap de correlação:** visualizar relações entre variáveis.
* **Series temporais:** avaliar evolução dos acidentes ao longo dos anos.

---

## 🎯 Apresentação Final

* **Duração:** 8 minutos (08/09/2025).
* **Conteúdo esperado:**

  * Impressões críticas sobre os dados.
  * Estatísticas descritivas e dispersão.
  * Correlações e associações.
  * Visualizações relevantes.
  * Recomendações finais.

📊 **Reforço:** Cada etapa deve ser acompanhada de gráficos claros, que auxiliem na interpretação e comunicação dos insights.

---

## 🚀 Requisitos Técnicos

* Linguagem: Python 3.x
* Bibliotecas sugeridas:

  * `pandas`, `numpy` → manipulação de dados
  * `matplotlib`, `seaborn`, `plotly` → visualização
  * `scipy`, `statsmodels` → estatísticas

---

## ✅ Conclusão

Este projeto combina **ciência de dados aplicada** com um problema **real e socialmente relevante**: a segurança no trânsito. A correta aplicação das etapas do CRISP-DM, aliada a **visualizações interativas em todas as fases da AED**, garantirá resultados robustos, interpretáveis e úteis para recomendações práticas.

---
