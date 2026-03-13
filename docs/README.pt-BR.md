# Amazon Sales Analysis (PT-BR)

## Troca de Idioma
- README principal: [../README.md](../README.md)
- International: [README.en.md](README.en.md)

## Resumo
- Problema de negocio: leakage de desconto reduzindo a receita liquida.
- Publico-alvo: lideranca comercial, gestores de categoria e operacoes.
- North Star Metric: Net Revenue Retained (NRR).
- Potencial financeiro: +$252,3K ao recuperar 5% do leakage.

## Snapshot de Metricas
- Receita Liquida: **$32,87M**
- Leakage de Desconto: **$5,05M**
- North Star (NRR): **86,69%**
- Upside com 5% de recuperacao: **+$252,3K**

## Escopo do Projeto
Este projeto entrega uma stack analitica orientada a negocio para operacoes de vendas no estilo Amazon:
- pipeline reproduzivel com contratos de schema e quality gates;
- feature engineering para KPIs executivos e metricas de leakage;
- endpoints FastAPI para metricas consolidadas e alertas operacionais;
- dashboard Streamlit com selecao de idioma `International` e `PT-BR`;
- simulador de cenarios e alertas de anomalia para revisao executiva.

## Como Executar
```bash
git clone https://github.com/samuelmaia-analytics/amazon-sales-analysis.git
cd amazon-sales-analysis
python -m pip install -e .[dev]
pre-commit install
python -m amazon_sales_analysis.cli.pipeline
uvicorn app.api:app --reload
streamlit run app/streamlit_app.py
```

## Scripts de Console
```bash
python -m pip install .
amazon-sales-pipeline
amazon-sales-alerts
amazon-sales-scenario
```

## Comandos de Qualidade
```bash
python -m pip install -e .[dev]
pre-commit run --all-files
black --check .
isort --check-only src scripts app alerts tests main.py streamlit_app.py scenario_simulation.py
ruff check .
mypy src scripts app alerts tests
pytest
```

## CI e Governanca
- A CI valida formatacao, lint, tipagem, testes e cobertura (`>=70%`).
- O workflow de release verifica consistencia entre versao e changelog antes de publicar.
- Templates de PR e issue estao disponiveis em `.github/`.
- CODEOWNERS foi configurado para governanca do repositorio.

## Exemplos de API
`GET /api/v1/revenue_metrics` (exemplo)
```json
{
  "total_revenue": 32866579.536,
  "gross_revenue": 37913104.54000001,
  "discount_leakage": 5046525.004000008,
  "north_star_nrr": 0.866892330099855,
  "total_orders": 50000.0,
  "avg_ticket": 657.33159072
}
```

`GET /alerts/discount-spikes` (exemplo)
```json
[
  {
    "order_date": "2022-10-31",
    "product_category": "Fashion",
    "z_score": 2.696544107570046,
    "estimated_leakage_usd": 933.6917756183568,
    "severity": "medium"
  }
]
```

## Contato
- GitHub: https://github.com/samuelmaia-analytics
- LinkedIn: https://linkedin.com/in/samuelmaia-analytics
- Email: smaia2@gmail.com
