from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .business_metrics import build_kpi_catalog
from .feature_engineering import build_features


@dataclass(frozen=True)
class ExecutiveReport:
    kpi_summary: pd.DataFrame
    category_performance: pd.DataFrame
    product_contribution: pd.DataFrame
    growth_trends: pd.DataFrame
    performance_distribution: pd.DataFrame
    insights: pd.DataFrame
    kpi_catalog: pd.DataFrame


def prepare_sales_frame(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    if "order_date" not in base.columns:
        base["order_date"] = pd.Timestamp("1970-01-01")
    frame = build_features(base)
    if "order_id" not in frame.columns:
        frame["order_id"] = range(1, len(frame) + 1)
    if "product_id" not in frame.columns:
        frame["product_id"] = range(1, len(frame) + 1)
    if "product_category" not in frame.columns:
        frame["product_category"] = "Unknown"
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce")
    frame["month_start"] = frame["order_date"].dt.to_period("M").dt.to_timestamp()
    frame["order_revenue_share"] = frame["total_revenue"] / frame["total_revenue"].sum()
    return frame.fillna({"order_revenue_share": 0.0})


def compute_kpi_summary(df: pd.DataFrame) -> pd.DataFrame:
    total_revenue = float(df["total_revenue"].sum()) if not df.empty else 0.0
    total_orders = float(df["order_id"].nunique()) if "order_id" in df else 0.0
    gross_revenue = float(df["gross_revenue"].sum()) if "gross_revenue" in df else 0.0
    total_units = float(df["quantity_sold"].sum()) if "quantity_sold" in df else 0.0
    avg_ticket = total_revenue / total_orders if total_orders else 0.0
    discount_leakage = gross_revenue - total_revenue
    rating = float(df["rating"].mean()) if "rating" in df and not df.empty else 0.0
    return pd.DataFrame(
        [
            {"metric": "total_revenue", "value": total_revenue, "unit": "currency"},
            {"metric": "avg_order_value", "value": avg_ticket, "unit": "currency"},
            {"metric": "total_orders", "value": total_orders, "unit": "orders"},
            {"metric": "total_units", "value": total_units, "unit": "units"},
            {"metric": "discount_leakage", "value": discount_leakage, "unit": "currency"},
            {
                "metric": "net_revenue_retained",
                "value": (total_revenue / gross_revenue) if gross_revenue else 0.0,
                "unit": "ratio",
            },
            {"metric": "avg_rating", "value": rating, "unit": "score"},
        ]
    )


def analyze_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    total_revenue = float(df["total_revenue"].sum()) if not df.empty else 0.0
    grouped = (
        df.groupby("product_category", as_index=False)
        .agg(
            revenue=("total_revenue", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity_sold", "sum"),
            avg_order_value=("total_revenue", "mean"),
            discount_value=("discount_value", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    grouped["revenue_share"] = grouped["revenue"] / total_revenue if total_revenue else 0.0
    grouped["discount_pressure"] = grouped["discount_value"] / grouped["revenue"].replace(0, pd.NA)
    return grouped.fillna({"discount_pressure": 0.0}).reset_index(drop=True)


def analyze_product_contribution(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    total_revenue = float(df["total_revenue"].sum()) if not df.empty else 0.0
    grouped = (
        df.groupby(["product_id", "product_category"], as_index=False)
        .agg(
            revenue=("total_revenue", "sum"),
            units=("quantity_sold", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
        .head(top_n)
    )
    grouped["revenue_share"] = grouped["revenue"] / total_revenue if total_revenue else 0.0
    grouped["rank"] = range(1, len(grouped) + 1)
    return grouped


def analyze_growth_trends(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("month_start", as_index=False)
        .agg(
            revenue=("total_revenue", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity_sold", "sum"),
        )
        .sort_values("month_start")
    )
    monthly["avg_order_value"] = monthly["revenue"] / monthly["orders"].replace(0, pd.NA)
    monthly["revenue_growth_rate"] = monthly["revenue"].pct_change().fillna(0.0)
    monthly["momentum"] = monthly["revenue_growth_rate"].apply(classify_growth_momentum)
    return monthly.fillna({"avg_order_value": 0.0})


def analyze_performance_distribution(df: pd.DataFrame) -> pd.DataFrame:
    order_perf = (
        df.groupby("order_id", as_index=False)
        .agg(
            order_revenue=("total_revenue", "sum"),
            units=("quantity_sold", "sum"),
            avg_discount=("discount_percent", "mean"),
        )
        .sort_values("order_revenue", ascending=False)
    )
    if order_perf.empty:
        return pd.DataFrame(
            columns=["performance_band", "orders", "revenue", "avg_order_value", "avg_discount"]
        )

    quantiles = min(4, len(order_perf))
    labels = ["Low", "Mid-Low", "Mid-High", "High"][-quantiles:]
    order_perf["performance_band"] = pd.qcut(
        order_perf["order_revenue"].rank(method="first"),
        q=quantiles,
        labels=labels,
    )
    distribution = (
        order_perf.groupby("performance_band", as_index=False, observed=False)
        .agg(
            orders=("order_id", "count"),
            revenue=("order_revenue", "sum"),
            avg_order_value=("order_revenue", "mean"),
            avg_discount=("avg_discount", "mean"),
        )
        .sort_values("avg_order_value", ascending=False)
    )
    total_revenue = float(order_perf["order_revenue"].sum()) if not order_perf.empty else 0.0
    distribution["revenue_share"] = (
        distribution["revenue"] / total_revenue if total_revenue else 0.0
    )
    return distribution


def classify_growth_momentum(value: float) -> str:
    if value >= 0.08:
        return "Accelerating"
    if value <= -0.05:
        return "Declining"
    return "Stable"


def build_executive_report(df: pd.DataFrame, insights: pd.DataFrame) -> ExecutiveReport:
    prepared = prepare_sales_frame(df)
    return ExecutiveReport(
        kpi_summary=compute_kpi_summary(prepared),
        category_performance=analyze_category_performance(prepared),
        product_contribution=analyze_product_contribution(prepared),
        growth_trends=analyze_growth_trends(prepared),
        performance_distribution=analyze_performance_distribution(prepared),
        insights=insights,
        kpi_catalog=build_kpi_catalog(),
    )
