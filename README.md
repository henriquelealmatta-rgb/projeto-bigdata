# 📚 Documentação do Projeto

## 📄 Documentos Disponíveis

### 1. [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)
**Documentação Completa do Pipeline**

Contém:
- Arquitetura do Sistema (Clean + Medallion)
- Pipeline de Transformação Detalhado
  - Etapa 1: Ingestion (Bronze)
  - Etapa 2: Transformation (Silver)
  - Etapa 3: Analytics Loading (Gold)
- Estrutura de Dados (schemas, tipos, formatos)
- Métricas de Performance
- Como Executar (guia completo)
- Insights dos Dados

**Este é o documento principal - comece por aqui!**

---

### 2. [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
**Resumo da Arquitetura de Armazenamento**

Contém:
- Arquitetura em Camadas (Medallion)
- Como os dados são armazenados (Bronze, Silver, Gold)
- Estrutura de diretórios
- Formato Parquet vs CSV
- Tendências de receita ao longo dos anos
- Casos de uso por camada

---

### 3. [INTERFACE_IMPROVEMENTS.md](INTERFACE_IMPROVEMENTS.md)
**Melhorias da Interface Web**

Contém:
- Problemas corrigidos (bug da aba IA)
- Novas funcionalidades
- Gráficos implementados (9 gráficos)
- Comparação antes/depois
- Como testar cada funcionalidade

---

## 🎯 Por Onde Começar?

### Se você quer entender o projeto:
1. Leia o [README.md](../README.md) na raiz (visão geral)
2. Leia [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md) (detalhes técnicos)

### Se você quer entender a arquitetura:
1. Leia [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
2. Explore a estrutura em `data/` (Bronze → Silver → Gold)

### Se você quer usar a interface:
1. Execute `streamlit run app.py`
2. Leia [INTERFACE_IMPROVEMENTS.md](INTERFACE_IMPROVEMENTS.md)

---

## 📊 Estrutura do Projeto

```
big data/
├── README.md                 # Quick start
├── app.py                   # Interface Streamlit
├── requirements.txt         # Dependências
│
├── docs/                    # 📚 VOCÊ ESTÁ AQUI
│   ├── README.md
│   ├── PIPELINE_DOCUMENTATION.md      ⭐ Principal
│   ├── ARCHITECTURE_SUMMARY.md
│   └── INTERFACE_IMPROVEMENTS.md
│
├── src/                     # Código fonte
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
│
├── data/                    # Dados processados
│   ├── raw/                 # Bronze
│   ├── processed/           # Silver
│   └── refined/             # Gold
│
└── terraform/               # IaC (AWS, Azure, GCP)
```

---

## 🚀 Links Rápidos

- **Executar Pipeline:** `python -m src.main`
- **Abrir Dashboard:** `streamlit run app.py` → http://localhost:8501
- **Dataset Original:** https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
- **Google Gemini API:** https://makersuite.google.com/app/apikey

---

**Última atualização:** 06/10/2025
