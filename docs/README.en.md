# Amazon Sales Analysis (International)

## Language Switch
- Main README: [../README.md](../README.md)
- PT-BR: [README.pt-BR.md](README.pt-BR.md)

## Summary
- Business problem: discount leakage reducing net revenue.
- Audience: revenue leaders, category managers, and operations teams.
- North Star Metric: Net Revenue Retained (NRR).
- Value case: +$252.3K at 5% leakage recovery.

## Business Metrics Snapshot
- Net Revenue: **$32.87M**
- Discount Leakage: **$5.05M**
- North Star (NRR): **86.69%**
- Upside at 5% leakage recovery: **+$252.3K**

## Project Scope
This project delivers a business-facing analytics stack for Amazon-like sales operations:
- reproducible data pipeline with schema and quality gates;
- feature engineering for executive KPIs and discount leakage metrics;
- FastAPI endpoints for summary metrics and operational alerts;
- Streamlit dashboard with `International` and `PT-BR` language selection;
- scenario simulator and anomaly alerts for leadership review.

## How to Run
```bash
git clone https://github.com/samuelmaia-analytics/amazon-sales-analysis.git
cd amazon-sales-analysis
python -m pip install -e .[dev]
pre-commit install
python -m amazon_sales_analysis.cli.pipeline
uvicorn app.api:app --reload
streamlit run app/streamlit_app.py
```

## Console Scripts
```bash
amazon-sales-pipeline
amazon-sales-alerts
amazon-sales-scenario
```

## Quality Commands
```bash
python -m pip install -e .[dev]
pre-commit run --all-files
black --check .
isort --check-only src scripts app alerts tests main.py streamlit_app.py scenario_simulation.py
ruff check .
mypy src scripts app alerts tests
pytest
```

## CI and Governance
- CI validates formatting, linting, typing, tests, and coverage (`>=70%`).
- Release workflow checks version/changelog consistency before publishing.
- PR and issue templates are available in `.github/`.
- CODEOWNERS is configured for repository governance.

## API Examples
`GET /api/v1/revenue_metrics` (sample)
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

`GET /alerts/discount-spikes` (sample)
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

## Contact
- GitHub: https://github.com/samuelmaia-analytics
- LinkedIn: https://linkedin.com/in/samuelmaia-analytics
- Email: smaia2@gmail.com
