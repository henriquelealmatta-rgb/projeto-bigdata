# 📚 Movies Big Data Pipeline - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Pipeline de Transformação](#pipeline-de-transformação)
4. [Estrutura de Dados](#estrutura-de-dados)
5. [Como Executar](#como-executar)

---

## 🎯 Visão Geral

Pipeline completo de Big Data para análise do dataset "The Movies Dataset" do Kaggle, implementando:

- **Clean Architecture** (Domain, Application, Infrastructure, Presentation)
- **Medallion Architecture** (Bronze, Silver, Gold)
- **Multi-Cloud Ready** (AWS, Azure, GCP via Terraform)
- **Interface Web com IA** (Streamlit + Google Gemini)

---

## 🏗️ Arquitetura do Sistema

### Estrutura em Camadas (Clean Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                     PRESENTATION                         │
│  ┌────────────────────┐       ┌────────────────────┐   │
│  │   CLI Interface    │       │   Web Interface    │   │
│  │   (pipeline_cli)   │       │   (Streamlit)      │   │
│  └────────────────────┘       └────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                     APPLICATION                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │
│  │ Ingestion  │  │Transformation│ │   Loading      │   │
│  │  (Bronze)  │→ │  (Silver)   │→│   (Gold)       │   │
│  └────────────┘  └────────────┘  └────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   INFRASTRUCTURE                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │
│  │  Kaggle    │  │   Data     │  │  Config &      │   │
│  │  Client    │  │ Repository │  │  Settings      │   │
│  └────────────┘  └────────────┘  └────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                       DOMAIN                             │
│  ┌────────────┐  ┌────────────────────────────────┐   │
│  │  Entities  │  │      Exceptions                │   │
│  │  (Movie)   │  │  (PipelineExceptions)          │   │
│  └────────────┘  └────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Pipeline de Transformação

### Etapa 1: Ingestion (Bronze Layer)

**Objetivo:** Extrair dados brutos do Kaggle sem transformações

**Processo:**
```
Kaggle API → Download ZIP → Extração → data/raw/
```

**Arquivos Baixados:**
- `movies_metadata.csv` (32.85 MB) - Metadados de 45.466 filmes
- `credits.csv` (181.12 MB) - Elenco e equipe
- `keywords.csv` (5.94 MB) - Palavras-chave
- `ratings.csv` (676.68 MB) - Avaliações de usuários
- `ratings_small.csv` (2.33 MB) - Subset de avaliações

**Total:** ~900 MB de dados brutos

**Código:**
```python
# src/application/ingestion/ingest_movies.py
def execute() -> dict:
    # 1. Autenticar com Kaggle API
    # 2. Listar arquivos do dataset
    # 3. Baixar dataset completo
    # 4. Extrair CSV files
    return statistics
```

---

### Etapa 2: Transformation (Silver Layer)

**Objetivo:** Limpar, validar e estruturar dados em formato otimizado

#### 2.1 Transformação de Filmes

**Input:** `movies_metadata.csv`  
**Output:** `movies.parquet`

**Transformações Aplicadas:**

1. **Parsing de JSON:**
   ```python
   # Converter strings JSON para listas
   belongs_to_collection → collection_id, collection_name
   genres → genre_ids, genre_names
   production_companies → company_ids, company_names
   production_countries → country_codes, country_names
   spoken_languages → language_codes
   ```

2. **Limpeza de Dados:**
   ```python
   # Remover valores inválidos
   - Budget = 0 ou NULL → has_budget = False
   - Revenue = 0 ou NULL → has_revenue = False
   - Status != 'Released' → Filtrar
   - Release_date inválida → Filtrar
   ```

3. **Cálculos Derivados:**
   ```python
   profit = revenue - budget
   roi = ((revenue - budget) / budget) * 100
   has_budget = budget > 0
   has_revenue = revenue > 0
   ```

4. **Conversão de Tipos:**
   ```python
   budget → float64
   revenue → float64
   runtime → float64
   vote_average → float64
   vote_count → int64
   release_year → int64
   ```

**Resultado:**
- 45.379 filmes válidos (87 removidos)
- 30 colunas estruturadas
- Formato Parquet comprimido

#### 2.2 Transformação de Créditos

**Input:** `credits.csv`  
**Output:** `credits.parquet`

**Transformações:**

1. **Parsing de Cast:**
   ```python
   # JSON → Lista estruturada
   cast = [
       {"id": int, "name": str, "character": str, "order": int}
   ]
   # Extrair top 5 atores por ordem
   ```

2. **Parsing de Crew:**
   ```python
   # JSON → Lista estruturada
   crew = [
       {"id": int, "name": str, "job": str, "department": str}
   ]
   # Extrair diretor
   director = crew[job == "Director"].name
   ```

3. **Estrutura Final:**
   ```python
   movie_id | cast_ids | cast_names | crew_ids | director
   ```

**Resultado:**
- 45.476 registros
- 5 colunas estruturadas
- Cast e crew parseados

#### 2.3 Transformação de Keywords

**Input:** `keywords.csv`  
**Output:** `keywords.parquet`

**Transformações:**

1. **Parsing de Keywords:**
   ```python
   # JSON → Lista de strings
   keywords = ["action", "hero", "superhero"]
   # Juntar com vírgula
   keywords_str = "action, hero, superhero"
   ```

**Resultado:**
- 46.419 registros
- 3 colunas (movie_id, keyword_ids, keyword_names)

#### 2.4 Transformação de Ratings

**Input:** `ratings_small.csv`  
**Output:** `ratings.parquet`

**Transformações:**

1. **Conversão de Timestamp:**
   ```python
   timestamp → datetime64
   ```

2. **Validação:**
   ```python
   rating ∈ [0.5, 5.0]
   movie_id existe
   ```

**Resultado:**
- 100.004 avaliações válidas
- 4 colunas (userId, movieId, rating, timestamp)

---

### Etapa 3: Analytics Loading (Gold Layer)

**Objetivo:** Criar datasets agregados otimizados para análise

#### 3.1 Yearly Analytics

**Processo:**
```python
movies + credits + keywords → GROUP BY release_year
```

**Agregações:**
```sql
SELECT 
    release_year,
    COUNT(*) as movie_count,
    AVG(budget) as avg_budget,
    SUM(budget) as total_budget,
    AVG(revenue) as avg_revenue,
    SUM(revenue) as total_revenue,
    AVG(profit) as avg_profit,
    SUM(profit) as total_profit,
    AVG(vote_average) as avg_rating,
    AVG(popularity) as avg_popularity,
    AVG(runtime) as avg_runtime
FROM movies_enriched
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year
```

**Output:** `yearly_analytics.parquet`
- 120 registros (anos 1900-2020)
- 11 métricas por ano

#### 3.2 Genre Analytics

**Processo:**
```python
movies → EXPLODE genre_names → GROUP BY genre
```

**Agregações:**
```sql
SELECT 
    genre_name,
    COUNT(*) as movie_count,
    AVG(budget) as avg_budget,
    AVG(revenue) as avg_revenue,
    AVG(profit) as avg_profit,
    AVG(vote_average) as avg_rating,
    AVG(popularity) as avg_popularity,
    SUM(revenue) as total_revenue,
    AVG(roi) as avg_roi
FROM movies_with_genres
GROUP BY genre_name
ORDER BY movie_count DESC
```

**Output:** `genre_analytics.parquet`
- 20 gêneros
- 9 métricas por gênero

#### 3.3 Top Movies

**Processo:**
```python
# Top 100 por cada métrica
top_revenue = movies.nlargest(100, 'revenue')
top_profit = movies.nlargest(100, 'profit')
top_rating = movies.nlargest(100, 'vote_average')
```

**Output:** `top_movies.parquet`
- 300 registros (100 de cada tipo)
- 13 colunas com rank_type indicator

#### 3.4 Director Analytics

**Processo:**
```python
movies + credits → GROUP BY director
```

**Agregações:**
```sql
SELECT 
    director,
    COUNT(*) as movie_count,
    AVG(budget) as avg_budget,
    SUM(revenue) as total_revenue,
    AVG(revenue) as avg_revenue,
    AVG(profit) as avg_profit,
    AVG(vote_average) as avg_rating,
    AVG(popularity) as avg_popularity,
    MAX(vote_average) as best_rating
FROM movies_with_director
WHERE director IS NOT NULL
GROUP BY director
HAVING movie_count >= 2
ORDER BY total_revenue DESC
```

**Output:** `director_analytics.parquet`
- 4.351 diretores
- 9 métricas por diretor

#### 3.5 Movies Enriched

**Processo:**
```python
movies + credits + keywords → LEFT JOIN
```

**Output:** `movies_enriched.parquet`
- 46.543 registros (todos os filmes + créditos + keywords)
- 33 colunas
- Dataset completo para análises exploratórias

---

## 📊 Estrutura de Dados

### Comparação por Camada

| Camada | Formato | Tamanho | Registros | Propósito |
|--------|---------|---------|-----------|-----------|
| **Bronze** | CSV | 900 MB | ~1M | Backup, auditoria |
| **Silver** | Parquet | 50 MB | ~240K | Análises exploratórias |
| **Gold** | Parquet | 22 MB | ~51K | Dashboards, BI |

**Redução de armazenamento:** 900 MB → 72 MB (**92% de economia**)

### Schema por Dataset

#### movies.parquet (Silver)
```
movie_id: int64
title: string
release_year: int64
release_date: date
budget: float64
revenue: float64
profit: float64
roi: float64
runtime: float64
vote_average: float64
vote_count: int64
popularity: float64
status: string
original_language: string
collection_id: int64 (nullable)
collection_name: string (nullable)
genre_ids: string
genre_names: string
company_ids: string
company_names: string
country_codes: string
country_names: string
language_codes: string
has_budget: bool
has_revenue: bool
homepage: string (nullable)
tagline: string (nullable)
overview: string
adult: bool
video: bool
```

#### yearly_analytics.parquet (Gold)
```
release_year: float64
movie_count: int64
avg_budget: float64
total_budget: float64
avg_revenue: float64
total_revenue: float64
avg_profit: float64
total_profit: float64
avg_rating: float64
avg_popularity: float64
avg_runtime: float64
```

---

## 🚀 Como Executar

### Pré-requisitos

1. **Python 3.10+**
2. **Credenciais Kaggle:**
   - Baixe `kaggle.json` de https://www.kaggle.com/settings
   - Coloque em `~/.kaggle/kaggle.json` (Linux/Mac) ou `%USERPROFILE%\.kaggle\kaggle.json` (Windows)

3. **Google Gemini API Key (opcional):**
   - Obtenha em: https://makersuite.google.com/app/apikey
   - Configure no `.env`: `GOOGLE_API_KEY=sua_chave`

### Instalação

```bash
# Clonar repositório
git clone <repo-url>
cd big-data

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Execução do Pipeline

#### Opção 1: Pipeline Completo
```bash
python -m src.main
```

#### Opção 2: Por Etapas
```bash
# Etapa 1: Ingestion (Bronze)
python -m src.main --stage ingestion

# Etapa 2: Transformation (Silver)
python -m src.main --stage transformation

# Etapa 3: Loading (Gold)
python -m src.main --stage loading
```

### Interface Web

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

**Funcionalidades:**
- 📊 Dashboard com 9 gráficos interativos
- 🎬 Explorador de filmes (tabela + cards)
- 🤖 Chat com IA (Google Gemini)
- 📈 Geração de gráficos customizados via linguagem natural

---

## 📁 Estrutura Final de Arquivos

```
big data/
├── data/
│   ├── raw/              # Bronze - 900 MB
│   │   ├── movies_metadata.csv
│   │   ├── credits.csv
│   │   ├── keywords.csv
│   │   └── ratings_small.csv
│   ├── processed/        # Silver - 50 MB
│   │   ├── movies.parquet
│   │   ├── credits.parquet
│   │   ├── keywords.parquet
│   │   └── ratings.parquet
│   └── refined/          # Gold - 22 MB
│       ├── yearly_analytics.parquet
│       ├── genre_analytics.parquet
│       ├── top_movies.parquet
│       ├── director_analytics.parquet
│       └── movies_enriched.parquet
│
├── src/
│   ├── domain/           # Entidades e exceções
│   ├── application/      # Casos de uso (ingestion, transformation, loading)
│   ├── infrastructure/   # Kaggle client, repositories, config
│   └── presentation/     # CLI
│
├── terraform/            # IaC para AWS, Azure, GCP
├── app.py               # Interface Streamlit
├── requirements.txt     # Dependências Python
└── README.md           # Documentação principal
```

---

## 🎯 Métricas de Performance

### Tempo de Execução

| Etapa | Tempo | Descrição |
|-------|-------|-----------|
| Ingestion | ~30s | Download + extração |
| Transformation | ~90s | Parsing + limpeza |
| Loading | ~10s | Agregações |
| **Total** | **~2.5 min** | Pipeline completo |

### Qualidade dos Dados

| Métrica | Valor |
|---------|-------|
| Filmes totais baixados | 45.466 |
| Filmes válidos processados | 45.379 |
| Taxa de sucesso | 99.8% |
| Registros duplicados removidos | 0 |
| Valores inválidos tratados | 87 |

---

## 🔍 Insights dos Dados

### Tendências Temporais (1990-2017)

- **Crescimento de produção:** 435 → 2.057 filmes/ano (+373%)
- **Receita total:** $5.7B (1990) → $33.4B (2016) (+478%)
- **Receita média/filme:** Estável em ~$14-16M

### Top Gêneros
1. Drama - 8.805 filmes
2. Comedy - 5.258 filmes
3. Thriller - 3.210 filmes

### Top Diretores (por receita)
1. Steven Spielberg - $4.1B
2. Peter Jackson - $3.0B
3. Christopher Nolan - $2.9B

---

## 📚 Tecnologias Utilizadas

- **Python 3.12** - Linguagem principal
- **Pandas** - Manipulação de dados
- **PyArrow** - Formato Parquet
- **Pydantic** - Validação de dados
- **Streamlit** - Interface web
- **Plotly** - Visualizações interativas
- **Google Gemini** - IA generativa
- **Terraform** - Infrastructure as Code
- **Kaggle API** - Fonte de dados

---

## ✅ Conclusão

Pipeline completo implementando:
- ✅ Clean Architecture
- ✅ Medallion Architecture (Bronze → Silver → Gold)
- ✅ 92% de redução de armazenamento
- ✅ Validação e limpeza de dados
- ✅ Agregações otimizadas
- ✅ Interface web interativa
- ✅ IA para análises em linguagem natural
- ✅ Multi-cloud ready

**Dados processados:** 900 MB → 72 MB  
**Tempo total:** ~2.5 minutos  
**Qualidade:** 99.8% de dados válidos  
**Visualizações:** 9 gráficos + IA generativa

