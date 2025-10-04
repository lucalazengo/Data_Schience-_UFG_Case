# Dashboard de Acidentes — Goiás/Goiânia (Streamlit)

Este projeto entrega um **dashboard analítico** para dados de acidentes em rodovias com foco no **Estado de Goiás (GO)** e na **Região Metropolitana de Goiânia (RMG)**.  
Ele inclui **tendências**, **hotspots/trechos críticos** e **modelagem preditiva de severidade** (acidentes com **vítimas fatais**).

> **Objetivo desta documentação**: explicar **como o código funciona** (de ponta a ponta), detalhar **siglas**, **variáveis**, **features**, **treinos** e **métricas**, para que qualquer avaliador consiga reproduzir e questionar com segurança técnica.

---

## Sumário
1. [Como executar](#como-executar)
2. [Arquitetura e arquivos](#arquitetura-e-arquivos)
3. [Carga e saneamento de dados](#carga-e-saneamento-de-dados)
4. [Filtros: GO e RMG](#filtros-go-e-rmg)
5. [Visões do dashboard](#visões-do-dashboard)
6. [Índice de periculosidade (hotspots)](#índice-de-periculosidade-hotspots)
7. [Modelagem preditiva](#modelagem-preditiva)
   - [Alvo (variável dependente)](#alvo-variável-dependente)
   - [Features](#features)
   - [Pré-processamento](#pré-processamento)
   - [Divisão treino e teste](#divisão-treino-e-teste)
   - [Modelos treinados](#modelos-treinados)
   - [Métricas e curvas](#métricas-e-curvas)
   - [Otimização de limiar (F2)](#otimização-de-limiar-f2)
   - [Importância de features (Permutation)](#importância-de-features-permutation)
8. [Glossário de siglas](#glossário-de-siglas)
9. [Boas práticas e limitações](#boas-práticas-e-limitações)
10. [Personalização](#personalização)

---

## Como executar

Requisitos mínimos (Python 3.9+):
```bash
pip install streamlit pandas numpy plotly scikit-learn
```

Executar localmente (na raiz do projeto):
```bash
streamlit run app.py
```

O caminho padrão do CSV é tentado automaticamente em:
- `./data/processed_data/base_acidente.csv`
- `../data/processed_data/base_acidente.csv`
- `../../data/processed_data/base_acidente.csv`

Você pode **alterar o caminho** no **sidebar** do Streamlit.

> **Observação**: o app é tolerante a CSV “sujos”. Ele **detecta o separador** (`,` ou `;`), usa parser **robusto** e **pula linhas malformadas**, caindo para um parser alternativo se necessário.

---

## Arquitetura e arquivos

- **`app.py`**: aplicativo Streamlit que implementa toda a lógica (ETL leve, visualização e modelagem).
- **`data/processed_data/base_acidente.csv`**: arquivo consolidado de entrada (não versionado aqui).
- (Opcional) `requirements.txt`: dependências do projeto.

**Principais funções no `app.py`:**

- **`load_csv_safe`**: leitura robusta do CSV (detecção de separador, `on_bad_lines='skip'` e fallback de *engine*).  
- **`load_data`**: normalizações, tipagem de colunas, criação de variáveis derivadas (ex.: `HORA`, `PERIODO_DIA`, `TAXA_MORTALIDADE`).  
- **`subset_go_rmg`**: filtra GO e recorta RMG com nomes de municípios **normalizados** (maiúsculo e sem acento).  
- **`kpis_bloco`**, **`plot_tendencias`**, **`indice_periculosidade`**, **`plot_top_brs`**: camadas de visualização e análise.  
- **Seção Modelagem**: `make_splits`, `build_models`, `evaluate_model`, `find_best_threshold`, `show_permutation_importance`.

---

## Carga e saneamento de dados

### Leitura resiliente
1. Detecta o **separador** automaticamente com `csv.Sniffer` (`,` ou `;`).  
2. Tenta ler com **`engine='python'` + `on_bad_lines='skip'`** (tolerante a linhas quebradas).  
3. **Fallback** para `engine='c'` se a leitura falhar.

### Normalizações e tipos
- **Textos**: `uf`, `municipio`, `tipo_acidente`, `causa_acidente`, `tipo_pista`, `tracado_via`, `uso_solo`, `dia_semana`  
  → **maiúsculo**, **sem acento** (NFKD), sem espaços extras.  
- **Datas**: `data_inversa` → `datetime` com `errors='coerce'`. Cria: `year`, `month`, `weekday` (0=Seg … 6=Dom).
- **Horário**: `horario` → `datetime`; cria `HORA` (0–23, `-1` quando ausente).
- **Numéricos**: `km`, `latitude`, `longitude` → troca vírgula por ponto e converte numérico.  
- **Feridos totais**: `TOTAL_FERIDOS = feridos_leves + feridos_graves` (se não existir).
- **Inteiros**: `mortos`, `veiculos`, `pessoas` → `int` com `fillna(0)`.
- **Período do dia** (`PERIODO_DIA`): *bins* por hora → `MADRUGADA (0–4)`, `MANHA (5–11)`, `TARDE (12–17)`, `NOITE (18–23)`; `DESCONHECIDO` quando `HORA` inválida.
- **Taxa de mortalidade** (`TAXA_MORTALIDADE`): `mortos / pessoas` com proteção a divisão por zero.

---

## Filtros: GO e RMG

1. **GO**: `uf == "GO"` (após normalização).
2. **RMG**: subconjunto de GO cujo `municipio_norm` pertence ao conjunto de municípios da **Região Metropolitana de Goiânia**.  
   - A lista é mantida com acento, mas a comparação é feita com **nomes normalizados** (maiúsculo/sem acento) para evitar “zerar RMG” por divergências de ortografia/codificação.

---

## Visões do dashboard

### 1) **Visão Geral**
- **KPIs**: Registros, Mortos, Feridos (L+G), **Taxa bruta por ocorrência** (`mortos / total_ocorrências`).
- **Top municípios (GO)**: ranking por número de ocorrências.

### 2) **Tendências**
- Séries anuais de **ocorrências** e **mortos** para **GO** e **RMG**.
- **Sazonalidade mensal (GO)**: barras de ocorrências e mortes por mês.

### 3) **Hotspots & BRs**
- **Índice de periculosidade** por **BR** (ver fórmula abaixo) e **ranking TOP N**.

---

## Índice de periculosidade (hotspots)

Medida composta que prioriza trechos com **muitos acidentes** e **maior severidade**:

\[
\text{taxa} = \frac{\text{mortos}}{\text{ocorrências}} \quad;\quad
\text{índice} = \Big(0{,}4 \cdot \frac{\text{ocorrências}}{\max(\text{ocorrências})} + 0{,}6 \cdot \frac{\text{mortos}}{\max(\text{mortos})}\Big) \times 10
\]

- Pesos: **0,4** para volume, **0,6** para severidade.  
- Escala: **0–10** (quanto maior, pior).  
- Uso: priorização de fiscalização, engenharia e campanhas.

---

## Modelagem preditiva

### Alvo (variável dependente)
- **`y = 1` se `mortos > 0`**, caso contrário **`0`**.  
- Problema de **classificação binária** com **desbalanceamento** (classe 1 é minoria).

### Features
- **Numéricas** (quando presentes):  
  `km`, `veiculos`, `pessoas`, `TOTAL_FERIDOS`, `HORA`.
- **Categóricas** (quando presentes):  
  `tipo_acidente`, `causa_acidente`, `tipo_pista`, `tracado_via`, `uso_solo`, `PERIODO_DIA`, `dia_semana`, `municipio`, `br`.

> As listas são filtradas dinamicamente para **usar apenas colunas existentes** no CSV.

### Pré-processamento
- `ColumnTransformer`:
  - **Numéricas**: `passthrough` (sem escalonamento obrigatório).
  - **Categóricas**: `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` → matriz densa para compatibilidade com todos os modelos.

### Divisão treino e teste
- `train_test_split(test_size=0.25, random_state=42, stratify=y)`  
  → **25%** para teste, **estratificação** assegura proporção de classes similar nos conjuntos.

### Modelos treinados
1. **LogisticRegression** (`class_weight="balanced"`) → *baseline* linear e interpretável.
2. **HistGradientBoostingClassifier** (HGB) → gradiente de histograma, rápido e performático.
3. **RandomForestClassifier** (`class_weight="balanced"`, 300 árvores) → robusto a ruídos e não linearidades.

> Todos são encapsulados em `Pipeline(prep → modelo)`, garantindo **mesmo pré-processamento** no treino e no teste.

### Métricas e curvas
- **ROC-AUC**: discriminação geral (insensível a limiar).  
- **PR-AUC (AP)**: recomendada em dados **desbalanceados** (foco na classe positiva).  
- **Matriz de confusão** **(limiar 0.5)** e **relatório de classificação** (precision/recall/F1 por classe).  
- **Curvas ROC e Precisão–Recall (Plotly)** por modelo.

### Otimização de limiar (F2)
- Busca por **limiar ótimo** que **maximiza F2** (pesa mais **recall**; salvar vidas é prioridade).
- Exibe **matriz de confusão** com esse limiar e o valor de **F2**.

### Importância de features (Permutation)
- Seleciona o **melhor modelo por AP** (maior **PR-AUC**).  
- Aplica **`permutation_importance`** sobre o conjunto de **teste** para estimar impacto de cada feature.  
- Exibe **TOP 25** (gráfico de barras).

---

## Glossário de siglas

- **GO**: Estado de Goiás.  
- **RMG**: Região Metropolitana de Goiânia.  
- **BR**: Rodovia Federal (ex.: BR-153).  
- **ROC-AUC**: *Area Under ROC Curve*.  
- **PR-AUC (AP)**: *Average Precision* da curva Precisão–Recall.  
- **HGB**: *HistGradientBoostingClassifier*.  
- **OHE / One-Hot**: codificação de categorias em colunas binárias.  
- **F2**: métrica F-Score com **β = 2** (recall tem peso maior).

---

## Boas práticas e limitações

- **Qualidade do CSV** impacta tudo. O app contorna problemas comuns (`on_bad_lines='skip'`), mas **linhas corrompidas** podem ser ignoradas.  
- **Desbalanceamento**: usamos `class_weight="balanced"` e **PR-AUC + F2** para avaliação mais justa.  
- **Sem geolocalização avançada** neste MVP (ex.: *clustering* espacial, mapas interativos) — pode ser incluído depois.
- **Importância por permutação** é computacionalmente mais cara; usar com parcimônia em datasets muito grandes.

---

## Personalização

- **Mudar municípios da RMG**: edite a lista em `RMG_MUNICIPIOS_RAW`. A comparação usa nomes **normalizados** (maiúsculo/sem acento).  
- **Ajustar pesos do índice**: altere `(0.4, 0.6)` em `indice_periculosidade`.  
- **Adicionar modelos**: crie outro estimador em `build_models` e ele aparecerá automaticamente na interface.  
- **Novas visões**: siga o padrão das `tabs` do Streamlit e reutilize os *helpers* existentes.

---

### Referências rápidas a trechos-chave

**Leitura robusta** (detecção de separador + fallback de engine):
```python
df = pd.read_csv(path, sep=sep, encoding="utf-8", engine="python", on_bad_lines="skip")
# fallback: engine="c" se falhar
```

**Normalização de texto** (maiúsculo + sem acento):
```python
ud.normalize("NFKD", x).encode("ASCII","ignore").decode("utf-8")
```

**Alvo da modelagem**:
```python
y = (df_escopo["mortos"] > 0).astype(int)
```

**Pré-processamento**:
```python
ct = ColumnTransformer([
    ("num", "passthrough", num_features),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features)
])
```

**Métricas principais**: roc_auc_score, average_precision_score (PR-AUC/AP).

**Otimização de limiar (F2)**: busca t que maximiza F2 em [0.05, 0.95].

**Importância (Permutation)**: permutation_importance(modelo, X_test, y_test, n_repeats=10).

---

## Dúvidas frequentes (FAQ)

**RMG apareceu zerada. Por quê?**  
→ Geralmente por divergência de acento/caixa. O app já normaliza, mas se os nomes estiverem muito diferentes, ajuste a lista `RMG_MUNICIPIOS_RAW` ou confirme o conteúdo do CSV.

**Por que usar PR-AUC (AP)?**  
→ Em classes desbalanceadas, PR-AUC é mais informativa sobre a qualidade do ranqueamento da classe **positiva** (acidentes fatais).

**Por que F2 e não F1?**  
→ Queremos **maximizar recall** da classe fatal (evitar falsos negativos), aceitando mais falsos positivos.

---
**Exemplos dos BIs**

<img width="1785" height="603" alt="image" src="https://github.com/user-attachments/assets/509991d4-3fc7-4399-a9cb-7cdea5579d1c" />

<img width="1834" height="678" alt="image" src="https://github.com/user-attachments/assets/0ae1dfcb-f195-46f3-904e-47754a902c52" />

<img width="1809" height="459" alt="image" src="https://github.com/user-attachments/assets/ce965f2f-f902-4ab6-aa44-6c24d28f62d1" />

<img width="1801" height="509" alt="image" src="https://github.com/user-attachments/assets/50f84e40-5d13-4f0d-84dc-b07bb42d3b5c" />

<img width="1808" height="598" alt="image" src="https://github.com/user-attachments/assets/46395b66-9526-49e9-a4c2-1fda33b9faee" />

**Exemplos da Modelagem**

<img width="1814" height="845" alt="image" src="https://github.com/user-attachments/assets/ecabb4af-06ed-4bf4-8fc4-4dc8f729e2f2" />

<img width="1762" height="667" alt="image" src="https://github.com/user-attachments/assets/0776eec2-6669-400d-b4df-b99e20562c7a" />

<img width="1795" height="368" alt="image" src="https://github.com/user-attachments/assets/eaf43317-836c-4df2-9bc8-4ec06330e205" />



