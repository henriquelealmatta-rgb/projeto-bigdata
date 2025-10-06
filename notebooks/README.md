# 📓 Jupyter Notebooks

## 📁 Notebooks Disponíveis

### 🎬 movies_pipeline_colab.ipynb

**Pipeline completo de Big Data para Google Colab**

#### 🎯 Objetivo
Executar todo o pipeline de transformação de dados do projeto no Google Colab, desde a ingestão até visualizações finais.

#### 📋 Conteúdo

**1. Configuração Inicial** ⚙️
- Instalação de dependências (kaggle, pandas, pyarrow, plotly)
- Upload de credenciais Kaggle
- Criação de estrutura de diretórios

**2. Ingestion (Bronze Layer)** 📥
- Download do dataset do Kaggle (~900 MB)
- Extração de 7 arquivos CSV

**3. Transformation (Silver Layer)** 🔄
- **Movies**: Parse de JSON, conversão de tipos, cálculo de métricas
- **Credits**: Extração de cast e diretor
- **Keywords**: Parse de palavras-chave
- **Ratings**: Conversão de timestamps
- **Resultado**: 4 arquivos Parquet (~50 MB, redução de 94%)

**4. Analytics Loading (Gold Layer)** 📊
- **Movies Enriched**: Dataset completo com merge de todas as fontes
- **Yearly Analytics**: Agregações por ano (1900-2020)
- **Genre Analytics**: Estatísticas por gênero (20 gêneros)
- **Top Movies**: Rankings de top 100 (receita, lucro, avaliação)
- **Director Analytics**: Análise de 4.351 diretores
- **Resultado**: 5 arquivos Parquet (~22 MB, redução de 98%)

**5. Visualizações** 📈
- 7 gráficos interativos com Plotly:
  1. 📅 Evolução da Produção de Filmes (1990+)
  2. 💰 Evolução de Receita (Dual Axis)
  3. 🎭 Top 10 Gêneros por Número de Filmes
  4. 💵 Top 10 Gêneros por Receita Média
  5. 🎬 Top 10 Diretores por Receita Total
  6. 💎 Scatter Plot: Orçamento vs Receita
  7. 🏆 Top 20 Filmes por Receita

**6. Resumo Final** ✅
- Estatísticas completas do pipeline
- Insights principais
- Top 3 de cada categoria

---

## 🚀 Como Usar no Google Colab

### 1. Abrir no Colab

**Opção A - Upload Manual:**
```
1. Acesse: https://colab.research.google.com/
2. File → Upload notebook
3. Selecione: movies_pipeline_colab.ipynb
```

**Opção B - GitHub (após push):**
```
1. Acesse: https://colab.research.google.com/
2. File → Open notebook → GitHub
3. Cole a URL do repositório
```

### 2. Preparar Credenciais Kaggle

```bash
# Baixe suas credenciais:
# https://www.kaggle.com/settings → API → Create New Token
# Isso baixará o arquivo kaggle.json
```

### 3. Executar o Notebook

**Método 1: Executar Tudo**
```
Runtime → Run all (Ctrl+F9)
```

**Método 2: Célula por Célula**
```
Shift+Enter em cada célula
```

### 4. Fazer Upload do kaggle.json

Quando solicitado pela célula de upload:
```python
uploaded = files.upload()
```
Clique em "Choose Files" e selecione seu `kaggle.json`

---

## ⏱️ Tempo de Execução

| Etapa | Tempo Estimado | GPU Necessária? |
|-------|----------------|-----------------|
| Setup | 1-2 min | ❌ |
| Ingestion | 30-60 seg | ❌ |
| Transformation | 2-3 min | ❌ |
| Analytics | 30 seg | ❌ |
| Visualizações | 10 seg | ❌ |
| **Total** | **~5 min** | ❌ |

> 💡 **Dica**: Não é necessário GPU. O notebook roda perfeitamente na CPU gratuita do Colab.

---

## 📊 Dados Gerados

Após execução completa, você terá:

```
data/
├── raw/              # Bronze Layer (CSVs - 900 MB)
│   ├── movies_metadata.csv
│   ├── credits.csv
│   ├── keywords.csv
│   └── ratings_small.csv
│
├── processed/        # Silver Layer (Parquet - 50 MB)
│   ├── movies.parquet
│   ├── credits.parquet
│   ├── keywords.parquet
│   └── ratings.parquet
│
└── refined/          # Gold Layer (Parquet - 22 MB)
    ├── movies_enriched.parquet
    ├── yearly_analytics.parquet
    ├── genre_analytics.parquet
    ├── top_movies.parquet
    └── director_analytics.parquet
```

---

## 💾 Download dos Resultados

Para baixar os dados processados do Colab:

```python
# Adicione no final do notebook:
from google.colab import files

# Baixar arquivo específico
files.download('data/refined/movies_enriched.parquet')

# Ou compactar tudo
!zip -r results.zip data/refined/
files.download('results.zip')
```

---

## 🔧 Troubleshooting

### Erro: "Kaggle credentials not found"
**Solução**: Certifique-se de fazer upload do `kaggle.json` na célula correta.

### Erro: "Memory limit exceeded"
**Solução**: O notebook usa ~3-4 GB de RAM. Se necessário:
- Runtime → Change runtime type → High-RAM

### Erro: "Dataset download timeout"
**Solução**: Execute novamente a célula de download. A conexão pode ter caído.

### Gráficos não aparecem
**Solução**: Certifique-se de que Plotly está instalado:
```python
!pip install plotly
```

---

## 📝 Modificações Sugeridas

### Filtrar por período específico
```python
# Na etapa de transformation, adicione:
df_movies = df_movies[df_movies['release_year'] >= 2000]
```

### Analisar mais filmes nos rankings
```python
# Altere de 100 para 200:
top_revenue = movies_enriched.nlargest(200, 'revenue')
```

### Adicionar novos gráficos
```python
# Exemplo: Distribuição de duração dos filmes
fig = px.histogram(
    movies_enriched,
    x='runtime',
    title='Distribuição de Duração dos Filmes',
    nbins=50
)
fig.show()
```

---

## 🎓 Conceitos Aplicados

- ✅ **Medallion Architecture** (Bronze, Silver, Gold)
- ✅ **ETL Pipeline** (Extract, Transform, Load)
- ✅ **Data Cleaning** (parsing, validation, filtering)
- ✅ **Data Aggregation** (groupby, joins, explode)
- ✅ **Data Compression** (CSV → Parquet, 98% reduction)
- ✅ **Data Visualization** (Plotly interactive charts)

---

## 📚 Referências

- **Dataset**: [The Movies Dataset - Kaggle](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)
- **Documentação**: [`docs/PIPELINE_DOCUMENTATION.md`](../docs/PIPELINE_DOCUMENTATION.md)
- **Google Colab**: https://colab.research.google.com/

---

**Desenvolvido para Fundamentos de Big Data** 🎓

