# Amazon Sales Analysis

Dashboard estrategico para analise de vendas da Amazon, com pipeline de dados em Python e aplicacao interativa em Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://amazon-sales-analysis-samuelmaia-data-analyst.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-brightgreen)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Plotly](https://img.shields.io/badge/Plotly-5.14+-orange)

## Sumario

- [1. Objetivo](#1-objetivo)
- [2. Funcionalidades](#2-funcionalidades)
- [3. Arquitetura](#3-arquitetura)
- [4. Estrutura do repositorio](#4-estrutura-do-repositorio)
- [5. Como executar localmente](#5-como-executar-localmente)
- [6. Pipeline de dados](#6-pipeline-de-dados)
- [7. Testes](#7-testes)
- [8. Deploy](#8-deploy)
- [9. Contato](#9-contato)

## 1. Objetivo

Transformar dados brutos de vendas em insights acionaveis para tomada de decisao, cobrindo:

- ingestao de dados;
- limpeza e padronizacao;
- analise exploratoria;
- dashboard executivo interativo.

## 2. Funcionalidades

O dashboard possui 4 abas principais:

- **Visao Geral**: KPIs, distribuicao de receita por regiao e pagamento, evolucao diaria.
- **Analise Financeira**: heatmap de receita, impacto de desconto, top produtos.
- **Performance de Produtos**: matriz por categoria e tabela consolidada.
- **Insights Estrategicos**: resumo de descobertas e tendencia mensal.

## 3. Arquitetura

Camadas da solucao:

1. **Ingestao**: `src/data_ingestion.py`
2. **Processamento**: `src/data_preprocessing.py`
3. **Analise**: `src/eda.py`
4. **Visualizacao**: `src/visualization.py` e `streamlit_app.py`

## 4. Estrutura do repositorio

```text
amazon-sales-analysis/
|-- assets/
|   `-- custom.css
|-- data/
|   |-- raw/
|   `-- processed/
|       `-- amazon_sales_clean.csv
|-- notebooks/
|-- reports/
|-- src/
|   |-- config.py
|   |-- data_ingestion.py
|   |-- data_preprocessing.py
|   |-- eda.py
|   |-- modeling.py
|   `-- visualization.py
|-- tests/
|   |-- test_data_preprocessing.py
|   `-- test_data_quality.py
|-- main.py
|-- requirements.txt
|-- streamlit_app.py
`-- README.md
```

## 5. Como executar localmente

### Pre-requisitos

- Python 3.13+
- Git

### Passo a passo

```bash
git clone https://github.com/samuelmaia-data-analyst/amazon-sales-analysis.git
cd amazon-sales-analysis

python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Executar dashboard:

```bash
streamlit run streamlit_app.py
```

## 6. Pipeline de dados

Para baixar/processar os dados novamente:

```bash
python main.py
```

Saida esperada:

- `data/processed/amazon_sales_clean.csv`
- figuras em `reports/figures/`

Observacao: `main.py` usa `kagglehub`. Garanta autenticacao valida da Kaggle no ambiente local.

## 7. Testes

Executar suite:

```bash
pytest tests/ -v
```

Cobertura atual inclui:

- validacao de colunas obrigatorias no preprocessing;
- clipping de limites de dominio (`discount_percent`, `rating`);
- consistencia de calculo de `discounted_price` e `total_revenue`;
- validacao basica de qualidade do dataset processado.

## 8. Deploy

Aplicacao publicada no Streamlit Cloud:

- https://amazon-sales-analysis-samuelmaia-data-analyst.streamlit.app

## 9. Contato

Desenvolvido por Samuel Maia.

- GitHub: https://github.com/samuelmaia-data-analyst
- LinkedIn: https://linkedin.com/in/samuelmaia-data-analyst
- Email: smaia2@gmail.com
