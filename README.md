# Amazon Commercial Performance Monitor

Projeto analitico em Python que evolui uma exploracao de dataset para um case de monitoramento de performance comercial. A proposta deixa de responder apenas "o que existe no dataset" e passa a responder "onde estao os principais drivers de receita, pressao promocional e oportunidades de acao".

## Problema de negocio

Operacoes de marketplace podem crescer em volume e, ao mesmo tempo, perder eficiencia comercial por descontos pouco controlados, categorias superconcentradas e queda de tendencia em segmentos relevantes.

Este projeto foi estruturado para apoiar perguntas executivas:

- Quanto revenue a operacao gera e qual o ticket medio?
- Quais categorias e produtos sustentam o resultado?
- Onde a politica promocional pressiona margem e receita?
- A tendencia comercial esta acelerando, estavel ou em queda?
- Quais insights acionaveis devem entrar no monitoramento semanal?

## O que foi refatorado

- Estrutura modular para separar ingestao, validacao, transformacao, metricas, analise e visualizacao.
- KPIs centralizados em uma camada unica de negocio.
- Relatorio executivo com storytelling: baseline, categorias, produtos lideres, tendencia e distribuicao de performance.
- Insights automaticos para resumir principais achados.
- Validacoes de qualidade para entrada, schema e dominios criticos.
- Tratamento de erro para leitura e processamento do dataset.
- Ponto unico de execucao via `main.py` e `amazon-sales-pipeline`.
- Testes basicos cobrindo transformacoes, metricas e relatorio executivo.

## Estrutura

```text
src/amazon_sales_analysis/
|-- analytics.py            # wrappers leves para consumo externo
|-- business_metrics.py     # catalogo e definicao dos KPIs
|-- data_preprocessing.py   # leitura, limpeza, auditoria e erros de entrada
|-- insights.py             # resumo automatico dos principais achados
|-- metrics.py              # pacote central de metricas exportaveis
|-- quality.py              # quality gates e sumario de validacao
|-- sales_analysis.py       # analise comercial por categoria, produto e tendencia
|-- table_organization.py   # tabelas executivas para consumo no app e reports
`-- visualization.py        # fluxo de storytelling executivo
```

## KPIs principais

| KPI | Pergunta de negocio | Uso |
|---|---|---|
| Revenue total | Quanto a operacao gerou? | baseline executivo |
| Ticket medio | Qual o valor medio por pedido? | eficiencia comercial |
| Vendas por categoria | Onde o revenue esta concentrado? | priorizacao |
| Produtos com maior contribuicao | Quais itens sustentam o resultado? | portfolio |
| Tendencia temporal | O revenue esta acelerando ou caindo? | monitoramento |
| Distribuicao de performance | O resultado esta pulverizado ou concentrado? | risco comercial |

O catalogo completo fica no modulo [`business_metrics.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/src/amazon_sales_analysis/business_metrics.py).

## Fluxo analitico

1. Leitura segura do dataset com mensagens claras para arquivo ausente, vazio ou invalido.
2. Validacao de schema e colunas obrigatorias.
3. Limpeza e normalizacao das variaveis de receita, desconto e rating.
4. Calculo centralizado de KPIs e visoes de negocio.
5. Geração de tabelas executivas, visual storytelling e insights automaticos.
6. Exportacao de metricas, alertas e artefatos para `reports/`.

## Saidas principais

- `reports/tables/kpi_summary.csv`
- `reports/tables/category_performance.csv`
- `reports/tables/product_contribution.csv`
- `reports/tables/monthly_trend.csv`
- `reports/tables/performance_distribution.csv`
- `reports/tables/executive_insights.csv`
- `reports/metrics/product_metrics.json`
- `reports/figures/sales_trend_over_time.png`
- `reports/figures/top_categories_by_sales.png`
- `reports/figures/product_contribution.png`
- `reports/figures/performance_distribution.png`

## Interface executiva

O app Streamlit foi reorganizado com hierarquia de leitura:

1. Resumo executivo com KPIs e principais achados.
2. Drivers de performance com categorias, produtos lideres e distribuicao.
3. Qualidade dos dados de entrada.
4. Catalogo de KPIs documentado para contexto de negocio.

Arquivo principal do app: [`app/streamlit_app.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/app/streamlit_app.py)

## Como executar

```bash
python -m pip install -e .[dev]
python main.py
```

Ou pelos entry points:

```bash
amazon-sales-pipeline
streamlit run app/streamlit_app.py
pytest
```

## Decisoes de senioridade incorporadas

- O framing foi trocado de "analise exploratoria" para "monitoramento de performance comercial".
- Os KPIs agora estao ligados a perguntas executivas, nao apenas a agregacoes tecnicas.
- Categoria, contribuicao de produtos e tendencia temporal foram modeladas como drivers de decisao.
- O relatorio passou a destacar segmentos e tendencias acionaveis em vez de apenas exibir graficos.

## Testes

Cobertura minima adicionada para:

- limpeza e validacao de dados
- calculo de metricas centrais
- montagem do relatorio executivo
- exportacao de visualizacoes principais

Arquivos de teste relevantes:

- [`tests/test_data_preprocessing.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/tests/test_data_preprocessing.py)
- [`tests/test_metrics.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/tests/test_metrics.py)
- [`tests/test_sales_analysis.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/tests/test_sales_analysis.py)
- [`tests/test_table_organization.py`](/C:/Users/samue/PycharmProjects/amazon-sales-analysis/tests/test_table_organization.py)

## Resultado esperado do case

Um projeto simples de entender, mas com estrutura de portfolio senior:

- reproducivel
- orientado a negocio
- testavel
- com camada analitica centralizada
- com narrativa executiva clara
