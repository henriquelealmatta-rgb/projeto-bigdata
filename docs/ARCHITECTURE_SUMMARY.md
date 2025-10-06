# 📊 Arquitetura de Dados - Movies Big Data Pipeline

## 🏗️ Arquitetura em Camadas (Medallion Architecture)

### **Bronze Layer** (Raw Data) 📦
**Localização:** `data/raw/`

Dados brutos extraídos diretamente do Kaggle sem transformações:
- `movies_metadata.csv` - 32.85 MB
- `credits.csv` - 181.12 MB
- `keywords.csv` - 5.94 MB
- `ratings.csv` - 676.68 MB
- `ratings_small.csv` - 2.33 MB

**Total:** ~900 MB de dados brutos

---

### **Silver Layer** (Processed Data) 🔄
**Localização:** `data/processed/`

Dados limpos, normalizados e convertidos para formato Parquet eficiente:
- `movies.parquet` - Filmes com metadados estruturados (45.379 registros, 30 colunas)
- `credits.parquet` - Créditos com cast e crew parseados (45.476 registros, 5 colunas)
- `keywords.parquet` - Palavras-chave estruturadas (46.419 registros, 3 colunas)
- `ratings.parquet` - Avaliações validadas (100.004 registros, 4 colunas)

**Transformações aplicadas:**
- Parsing de JSON para colunas estruturadas
- Validação de tipos de dados
- Remoção de duplicatas e valores inválidos
- Conversão de formatos (CSV → Parquet)
- Compressão eficiente

---

### **Gold Layer** (Analytics-Ready Data) ✨
**Localização:** `data/refined/`

Dados agregados e otimizados para análise:

#### 1. **yearly_analytics.parquet** (18 KB)
Análises temporais por ano com 120 registros (1900-2020):

**Colunas:**
- `release_year` - Ano de lançamento
- `movie_count` - Número de filmes
- `avg_budget` - Orçamento médio
- `total_budget` - Orçamento total
- `avg_revenue` - **Receita média por filme**
- `total_revenue` - **Receita total do ano**
- `avg_profit` - Lucro médio
- `total_profit` - Lucro total
- `avg_rating` - Avaliação média
- `avg_popularity` - Popularidade média
- `avg_runtime` - Duração média

**Exemplo de dados (2010-2017):**
```
Ano    Filmes  Receita Média      Receita Total
2010     1531   $15.3M            $23.5B
2011     1717   $14.2M            $24.3B
2012     1782   $14.6M            $26.1B
2013     1953   $13.7M            $26.7B
2014     2057   $12.9M            $26.6B
2015     2046   $14.3M            $29.2B
2016     1677   $19.9M            $33.4B
2017      533   $28.3M            $15.1B
```

#### 2. **genre_analytics.parquet** (8 KB)
Análises por gênero com 20 registros:
- Estatísticas de orçamento, receita e avaliação por gênero
- Movie count, rating médio, popularidade

#### 3. **top_movies.parquet** (24 KB)
Top 300 filmes por diferentes métricas:
- Top 100 por receita
- Top 100 por lucro
- Top 100 por avaliação

#### 4. **director_analytics.parquet** (235 KB)
Análises de 4.351 diretores:
- Número de filmes dirigidos
- Receita total e média
- Avaliação média

#### 5. **movies_enriched.parquet** (21.5 MB)
Dataset completo enriquecido com 46.543 filmes:
- Todos os dados de filmes
- Créditos integrados (cast, crew, director)
- Keywords
- Métricas calculadas (ROI, profit margin, etc.)

---

## 🎯 Casos de Uso por Camada

### Bronze (Raw)
- **Quando usar:** Auditoria, reprocessamento completo, backup
- **Características:** Dados imutáveis, formato original

### Silver (Processed)
- **Quando usar:** Análises exploratórias, queries ad-hoc, ML training
- **Características:** Dados limpos, formato otimizado, schema validado

### Gold (Analytics)
- **Quando usar:** Dashboards, relatórios, visualizações, BI
- **Características:** Dados agregados, pré-calculados, otimizados para leitura

---

## 📈 Tendências de Receita Ao Longo dos Anos

### Evolução por Década (dados disponíveis):

**Anos 1990 (1990-1999):**
- Receita média: ~$14M/filme
- Produção: 435-730 filmes/ano
- Crescimento: +68% em número de filmes

**Anos 2000 (2000-2009):**
- Receita média: ~$15M/filme (+7%)
- Produção: 798-1.623 filmes/ano
- Crescimento: +103% em número de filmes

**Anos 2010 (2010-2017):**
- Receita média: ~$16M/filme (+7%)
- Produção: 1.531-2.057 filmes/ano
- Pico de receita: **$33.4B em 2016**

### Insights Principais:
1. ✅ Tendência crescente de receita total (de $5.7B em 1990 para $33.4B em 2016)
2. ✅ Aumento exponencial na produção de filmes
3. ✅ Receita média por filme mantém-se estável (~$14-16M)
4. ⚠️ 2016 teve o maior pico com $19.9M/filme em média
5. 📉 Queda em 2017 devido a dados incompletos

---

## 🔍 Como os Dados São Armazenados

### Formato de Armazenamento
- **Bronze:** CSV (compatibilidade máxima)
- **Silver/Gold:** Parquet (compressão e performance)

### Vantagens do Parquet:
- ✅ Compressão eficiente (~80% redução vs CSV)
- ✅ Leitura columnar (queries mais rápidas)
- ✅ Schema integrado (validação automática)
- ✅ Suporte a tipos complexos
- ✅ Compatível com Spark, Pandas, DuckDB

### Estrutura de Diretórios
```
data/
├── raw/           # Bronze - 900 MB CSV
├── processed/     # Silver - ~50 MB Parquet
└── refined/       # Gold   - ~22 MB Parquet
```

**Redução total de armazenamento:** 900 MB → 72 MB (**92% de economia**)

---

## 🚀 Pipeline de Processamento

1. **Ingestion** → Kaggle API → Bronze Layer
2. **Transformation** → Pandas/Pydantic → Silver Layer
3. **Analytics Loading** → Aggregations → Gold Layer
4. **Visualization** → Streamlit + Gemini AI → Dashboard

**Tempo total de execução:** ~3-4 minutos

