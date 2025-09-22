# Guia de Instalação - RoadInfra BI

## Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS 10.14+, ou Linux Ubuntu 18.04+
- Mínimo 4GB RAM (recomendado 8GB+)
- 2GB de espaço livre em disco

### Software Necessário
- Python 3.8 ou superior
- Git (opcional, para clonagem do repositório)

## Instalação

### 1. Obter o Código

#### Opção A: Download Direto
1. Baixe o arquivo ZIP do projeto
2. Extraia para um diretório de sua escolha
3. Navegue até o diretório `RoadInfra_BI`

#### Opção B: Git Clone
```bash
git clone <repository-url>
cd RoadInfra_BI
```

### 2. Configurar Ambiente Virtual (Recomendado)

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Verificar Instalação

Execute o comando para verificar se tudo foi instalado corretamente:

```bash
python -c "import streamlit, pandas, plotly; print('Instalação OK!')"
```

## Configuração Inicial

### 1. Estrutura de Dados

Certifique-se de que a estrutura de diretórios está correta:

```
RoadInfra_BI/
├── data/
│   ├── raw/          # Coloque aqui os arquivos CSV do DATATRAN
│   ├── processed/    # Dados processados (gerado automaticamente)
│   └── models/       # Modelos salvos (gerado automaticamente)
├── dashboard/        # Interface do usuário
├── src/             # Código fonte
└── docs/            # Documentação
```

### 2. Dados DATATRAN

1. Baixe os dados do DATATRAN do site oficial da PRF
2. Coloque os arquivos CSV na pasta `data/raw/`
3. Os arquivos devem seguir o padrão: `datatran_YYYY.csv`

### 3. Configurações Opcionais

Crie um arquivo `.env` na raiz do projeto para configurações personalizadas:

```env
# Configurações do Dashboard
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost

# Configurações de Processamento
CHUNK_SIZE=10000
CACHE_ENABLED=true

# Configurações do Índice de Periculosidade
PESO_MORTOS=10.0
PESO_FERIDOS_GRAVES=5.0
PESO_FERIDOS_LEVES=2.0
PESO_ACIDENTES=1.0
```

## Executando o Sistema

### 1. Iniciar o Dashboard

```bash
streamlit run dashboard/main.py
```

O sistema estará disponível em: `http://localhost:8501`

### 2. Processamento de Dados (Primeira Execução)

Na primeira execução, o sistema irá:
1. Detectar automaticamente os arquivos CSV em `data/raw/`
2. Processar e limpar os dados
3. Criar segmentos de rodovia
4. Calcular índices de periculosidade
5. Gerar rankings de black spots

Este processo pode levar alguns minutos dependendo do volume de dados.

## Solução de Problemas

### Erro: "ModuleNotFoundError"

**Problema**: Dependências não instaladas corretamente.

**Solução**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro: "Permission denied"

**Problema**: Permissões insuficientes para criar arquivos.

**Solução**:
- Windows: Execute o terminal como administrador
- macOS/Linux: Use `sudo` se necessário ou ajuste permissões da pasta

### Erro: "Port already in use"

**Problema**: Porta 8501 já está sendo usada.

**Solução**:
```bash
streamlit run dashboard/main.py --server.port 8502
```

### Dashboard não carrega dados

**Problema**: Arquivos CSV não encontrados ou formato incorreto.

**Solução**:
1. Verifique se os arquivos estão em `data/raw/`
2. Confirme que são arquivos CSV válidos do DATATRAN
3. Verifique os logs no terminal para erros específicos

### Performance lenta

**Problema**: Sistema lento com grandes volumes de dados.

**Soluções**:
1. Aumente a RAM disponível
2. Processe dados em lotes menores
3. Use filtros para reduzir o conjunto de dados
4. Ative o cache no arquivo `.env`

## Atualizações

### Atualizar Dependências

```bash
pip install --upgrade -r requirements.txt
```

### Atualizar Código

Se usando Git:
```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

## Configurações Avançadas

### Personalizar Pesos do Índice

Edite o arquivo `src/risk_modeling/risk_calculator.py`:

```python
PESOS_PADRAO = {
    'mortos': 15.0,        # Aumentar peso de mortes
    'feridos_graves': 7.0,  # Aumentar peso de feridos graves
    'feridos_leves': 2.0,
    'acidentes': 1.0
}
```

### Configurar Segmentação

Edite o arquivo `src/data_processing/segment_creator.py`:

```python
TAMANHO_SEGMENTO_KM = 25  # Segmentos de 25km em vez de 50km
```

### Adicionar Novos Estados/BRs

Edite os filtros no dashboard para incluir novos estados ou rodovias:

```python
# Em dashboard/main.py
estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'ES', 'MT', 'CE']  # Adicionar CE
brs = [101, 116, 381, 40, 50, 153, 262, 277, 290, 324, 230]  # Adicionar BR-230
```

## Backup e Manutenção

### Backup de Dados Processados

```bash
# Criar backup
cp -r data/processed/ backup/processed_$(date +%Y%m%d)/

# Restaurar backup
cp -r backup/processed_YYYYMMDD/ data/processed/
```

### Limpeza de Cache

```bash
# Limpar dados processados (forçar reprocessamento)
rm -rf data/processed/*

# Limpar cache do Streamlit
streamlit cache clear
```

## Suporte

### Logs do Sistema

Os logs são exibidos no terminal onde o Streamlit está executando. Para salvar logs:

```bash
streamlit run dashboard/main.py > logs/app.log 2>&1
```

### Informações do Sistema

Para obter informações de debug:

```python
import streamlit as st
st.write("Versão do Streamlit:", st.__version__)
st.write("Versão do Python:", sys.version)
```

### Contato

Para suporte técnico ou dúvidas:
- Consulte a documentação em `docs/`
- Verifique os logs de erro
- Reporte problemas com informações detalhadas do erro