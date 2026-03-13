import pandas as pd

from .sales_analysis import compute_kpi_summary, prepare_sales_frame


def calculate_business_impact(df: pd.DataFrame, recovery_rate: float = 0.05) -> dict[str, float]:
    summary = compute_kpi_summary(prepare_sales_frame(df))
    lookup = dict(zip(summary["metric"], summary["value"], strict=False))
    total_revenue = float(lookup.get("total_revenue", 0.0))
    gross_revenue = float(prepare_sales_frame(df)["gross_revenue"].sum()) if not df.empty else 0.0
    discount_leakage = float(lookup.get("discount_leakage", 0.0))

    return {
        "total_revenue": total_revenue,
        "gross_revenue": gross_revenue,
        "discount_leakage": discount_leakage,
        "retained_ratio": float(lookup.get("net_revenue_retained", 0.0)),
        "expected_uplift": discount_leakage * recovery_rate,
    }


def build_executive_summary(df: pd.DataFrame) -> pd.DataFrame:
    impact = calculate_business_impact(df)
    return pd.DataFrame(
        {
            "metric": [
                "north_star_net_revenue_retained",
                "total_revenue",
                "gross_revenue",
                "discount_leakage",
                "expected_uplift_5pct_recovery",
            ],
            "value": [
                impact["retained_ratio"],
                impact["total_revenue"],
                impact["gross_revenue"],
                impact["discount_leakage"],
                impact["expected_uplift"],
            ],
        }
    )
