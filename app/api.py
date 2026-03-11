from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import pandas as pd
from fastapi import FastAPI, HTTPException

from amazon_sales_analysis import __version__
from amazon_sales_analysis.analytics import add_derived_metrics, summarize_kpis
from amazon_sales_analysis.anomaly_detection import detect_discount_spikes
from amazon_sales_analysis.config import PROCESSED_DATA_DIR, TABLES_DIR
from amazon_sales_analysis.modeling import rank_discount_opportunities

DATASET_PATH = PROCESSED_DATA_DIR / "amazon_sales_clean.csv"
ALERTS_PATH = TABLES_DIR / "discount_spike_alerts.csv"

app = FastAPI(
    title="Amazon Sales Analytics API",
    version=__version__,
    description="Executive metrics and operational alerts for sales performance.",
)


def _existing_path(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Processed dataset not found. Run: python scripts/run_pipeline.py",
        )
    return path


@lru_cache(maxsize=4)
def _read_processed_data(dataset_path: str, modified_at_ns: int) -> pd.DataFrame:
    del modified_at_ns
    frame = pd.read_csv(dataset_path, parse_dates=["order_date"])
    return add_derived_metrics(frame)


def _load_processed_data() -> pd.DataFrame:
    dataset_path = _existing_path(DATASET_PATH)
    stat = dataset_path.stat()
    return _read_processed_data(str(dataset_path), stat.st_mtime_ns).copy()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics/summary")
def metrics_summary() -> dict[str, float]:
    frame = _load_processed_data()
    kpis = summarize_kpis(frame)
    gross_revenue = float(frame["gross_revenue"].sum()) if "gross_revenue" in frame else 0.0
    total_revenue = float(frame["total_revenue"].sum())

    return {
        "total_revenue": total_revenue,
        "gross_revenue": gross_revenue,
        "discount_leakage": gross_revenue - total_revenue,
        "north_star_nrr": kpis["net_revenue_retained"],
        "total_orders": kpis["total_orders"],
        "avg_ticket": kpis["avg_ticket"],
    }


@app.get("/api/v1/revenue_metrics")
def revenue_metrics_v1() -> dict[str, float]:
    return metrics_summary()


@app.get("/metrics/opportunities")
def category_opportunities() -> list[dict[str, Any]]:
    frame = _load_processed_data()
    opportunities = rank_discount_opportunities(frame)
    return cast(list[dict[str, Any]], opportunities.to_dict(orient="records"))


@app.get("/alerts/discount-spikes")
def discount_spikes() -> list[dict[str, Any]]:
    if ALERTS_PATH.exists():
        alerts = pd.read_csv(ALERTS_PATH, parse_dates=["order_date"])
    else:
        frame = _load_processed_data()
        alerts = detect_discount_spikes(frame)

    if alerts.empty:
        return []
    alerts["order_date"] = pd.to_datetime(alerts["order_date"]).dt.date.astype(str)
    return cast(list[dict[str, Any]], alerts.to_dict(orient="records"))
