# Guia de Uso - RoadInfra BI Dashboard

## Visão Geral

O RoadInfra BI é um sistema de Business Intelligence para análise de acidentes rodoviários baseado nos dados do DATATRAN (PRF). O dashboard oferece duas visões principais:

- **Visão Macro**: Análise geral com filtros, tabelas e mapas
- **Visão Micro**: Análise detalhada por segmento com KPIs específicos

## Acessando o Sistema

1. Certifique-se de que o sistema está executando (veja [Guia de Instalação](installation.md))
2. Abra seu navegador web
3. Acesse: `http://localhost:8501`
4. A página inicial será carregada automaticamente

## Interface Principal

### Barra Lateral (Sidebar)

A barra lateral contém os principais controles de navegação e filtros:

#### Navegação
- **Visão Macro**: Análise geral dos dados
- **Visão Micro**: Análise detalhada por segmento
- **Sobre**: Informações sobre o sistema

#### Filtros Principais
- **Estado (UF)**: Selecione um ou múltiplos estados
- **BR**: Escolha rodovias específicas
- **Ano**: Filtre por período temporal
- **Tipo de Análise**: Diferentes perspectivas dos dados

## Visão Macro

### 1. Filtros e Controles

#### Filtros Básicos
- **Estado**: Use o dropdown para selecionar estados
- **BR**: Escolha rodovias específicas (filtradas por estado)
- **Período**: Selecione anos ou intervalos de anos

#### Filtros Avançados
- **Tipo de Acidente**: Colisão, atropelamento, capotamento, etc.
- **Causa Principal**: Falta de atenção, velocidade, sono, etc.
- **Condições**: Tempo, pista, luminosidade
- **Gravidade**: Sem vítimas, com feridos, com mortos

### 2. Métricas Principais

O dashboard exibe KPIs importantes:

- **Total de Acidentes**: Número absoluto de ocorrências
- **Mortos**: Total de vítimas fatais
- **Feridos**: Vítimas não fatais (graves + leves)
- **Taxa de Letalidade**: Mortos por 100 acidentes
- **Índice de Periculosidade**: Métrica ponderada de risco

### 3. Visualizações

#### Tabela de Dados
- Lista detalhada de acidentes com filtros aplicados
- Colunas ordenáveis e pesquisáveis
- Opção de download em CSV/Excel

#### Mapa Interativo
- Visualização geográfica dos acidentes
- Marcadores coloridos por gravidade
- Zoom e navegação interativa
- Clusters automáticos para grandes volumes

#### Gráficos Temporais
- Evolução dos acidentes ao longo do tempo
- Análise de sazonalidade
- Tendências mensais e anuais

### 4. Exportação de Dados

- **CSV**: Dados tabulares para análise externa
- **Excel**: Planilha formatada com múltiplas abas
- **PDF**: Relatório visual com gráficos
- **Imagem**: Gráficos individuais em PNG/SVG

## Visão Micro

### 1. Seleção de Segmento

#### Método 1: Filtros Hierárquicos
1. Selecione o **Estado**
2. Escolha a **BR**
3. Defina o **Segmento** (km inicial - km final)

#### Método 2: Busca Direta
1. Use a caixa de busca
2. Digite: "BR-XXX km YYY-ZZZ"
3. Selecione da lista de sugestões

### 2. KPIs do Segmento

#### Métricas Básicas
- **Extensão**: Quilometragem do segmento
- **Acidentes/km**: Densidade de acidentes
- **Mortos/km**: Densidade de fatalidades
- **Ranking**: Posição entre segmentos similares

#### Índices Calculados
- **Índice de Periculosidade**: Score ponderado (0-100)
- **Classificação de Risco**: Baixo, Médio, Alto, Crítico
- **Tendência**: Melhora, estável, piora
- **Comparação**: Acima/abaixo da média estadual/nacional

### 3. Análises Detalhadas

#### Análise Temporal
- **Série Histórica**: Evolução dos acidentes
- **Sazonalidade**: Padrões mensais/semanais
- **Horários Críticos**: Distribuição por hora do dia
- **Dias da Semana**: Padrões semanais

#### Análise por Causas
- **Principais Causas**: Ranking das causas mais frequentes
- **Evolução das Causas**: Como as causas mudaram no tempo
- **Correlações**: Relação entre causas e gravidade

#### Análise por Tipos
- **Tipos de Acidente**: Colisão, atropelamento, etc.
- **Gravidade por Tipo**: Letalidade de cada tipo
- **Veículos Envolvidos**: Carros, caminhões, motos, etc.

#### Condições Ambientais
- **Condições Meteorológicas**: Chuva, sol, neblina
- **Estado da Pista**: Seca, molhada, com óleo
- **Luminosidade**: Dia, noite, crepúsculo

### 4. Heatmap de Risco

- **Visualização por Quilômetro**: Risco detalhado por km
- **Escala de Cores**: Verde (baixo) a vermelho (alto)
- **Pontos Críticos**: Identificação automática de black spots
- **Zoom Interativo**: Análise detalhada de trechos específicos

### 5. Recomendações Automáticas

O sistema gera recomendações baseadas nos dados:

#### Infraestrutura
- Melhorias na sinalização
- Instalação de redutores de velocidade
- Iluminação adicional
- Barreiras de proteção

#### Fiscalização
- Intensificar fiscalização em horários críticos
- Foco em causas específicas (velocidade, álcool)
- Campanhas educativas direcionadas

#### Monitoramento
- Pontos para instalação de câmeras
- Locais para postos de fiscalização
- Trechos para monitoramento especial

## Funcionalidades Avançadas

### 1. Comparação de Segmentos

1. Selecione **Modo Comparação** na sidebar
2. Escolha até 5 segmentos diferentes
3. Visualize métricas lado a lado
4. Analise diferenças e semelhanças

### 2. Análise de Tendências

1. Acesse **Análise Temporal**
2. Selecione período de interesse
3. Escolha métrica (acidentes, mortos, índice)
4. Visualize tendência e projeções

### 3. Filtros Personalizados

1. Use **Filtros Avançados**
2. Combine múltiplos critérios
3. Salve filtros frequentes
4. Compartilhe configurações

### 4. Alertas e Notificações

1. Configure **Alertas Automáticos**
2. Defina thresholds para métricas
3. Receba notificações por email
4. Monitore mudanças em tempo real

## Interpretação dos Dados

### Índice de Periculosidade

O índice é calculado usando pesos específicos:
- **Mortos**: Peso 10.0
- **Feridos Graves**: Peso 5.0
- **Feridos Leves**: Peso 2.0
- **Acidentes**: Peso 1.0

**Interpretação**:
- 0-25: Risco Baixo (Verde)
- 26-50: Risco Médio (Amarelo)
- 51-75: Risco Alto (Laranja)
- 76-100: Risco Crítico (Vermelho)

### Taxa de Letalidade

Calculada como: (Mortos / Total de Acidentes) × 100

**Benchmarks**:
- < 5%: Baixa letalidade
- 5-10%: Letalidade média
- 10-15%: Alta letalidade
- > 15%: Letalidade crítica

### Rankings

Os rankings são calculados considerando:
- Segmentos similares (mesmo estado/região)
- Mesmo volume de tráfego
- Características geométricas similares

## Dicas de Uso

### Performance
- Use filtros para reduzir o volume de dados
- Evite carregar todos os anos simultaneamente
- Feche abas não utilizadas do navegador

### Análise Eficiente
- Comece com visão macro para contexto geral
- Use visão micro para análise detalhada
- Compare segmentos similares
- Analise tendências temporais

### Exportação
- Use CSV para análises estatísticas
- Use PDF para relatórios executivos
- Use Excel para compartilhamento
- Salve configurações de filtros frequentes

### Interpretação
- Considere o contexto (volume de tráfego, características da via)
- Analise múltiplas métricas em conjunto
- Observe tendências, não apenas valores absolutos
- Compare com benchmarks regionais/nacionais

## Solução de Problemas

### Dashboard Lento
1. Reduza o período de análise
2. Use menos filtros simultâneos
3. Feche outras aplicações
4. Atualize a página

### Dados Não Aparecem
1. Verifique os filtros aplicados
2. Confirme se há dados para o período
3. Recarregue a página
4. Verifique conexão com internet

### Gráficos Não Carregam
1. Aguarde o processamento
2. Reduza o volume de dados
3. Atualize o navegador
4. Limpe o cache

### Exportação Falha
1. Reduza o volume de dados
2. Tente formato diferente
3. Verifique espaço em disco
4. Use navegador atualizado

## Suporte e Contato

Para dúvidas técnicas ou sugestões:
- Consulte a documentação técnica
- Verifique os logs de erro
- Reporte problemas com detalhes específicos
- Inclua screenshots quando relevante