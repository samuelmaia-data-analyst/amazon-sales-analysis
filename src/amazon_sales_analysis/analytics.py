import pandas as pd

from .sales_analysis import compute_kpi_summary, prepare_sales_frame


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    return prepare_sales_frame(df)


def summarize_kpis(df: pd.DataFrame) -> dict[str, float]:
    summary = compute_kpi_summary(prepare_sales_frame(df))
    lookup = dict(zip(summary["metric"], summary["value"], strict=False))
    return {
        "total_revenue": float(lookup.get("total_revenue", 0.0)),
        "total_orders": float(lookup.get("total_orders", 0.0)),
        "total_units": float(lookup.get("total_units", 0.0)),
        "avg_ticket": float(lookup.get("avg_order_value", 0.0)),
        "avg_rating": float(lookup.get("avg_rating", 0.0)),
        "net_revenue_retained": float(lookup.get("net_revenue_retained", 0.0)),
    }
