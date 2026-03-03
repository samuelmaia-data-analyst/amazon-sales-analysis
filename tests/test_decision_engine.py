import pandas as pd

from amazon_sales_analysis.decision_engine import build_actionable_recommendations
from amazon_sales_analysis.feature_engineering import build_features


def _fixture_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "order_date": ["2024-01-15", "2024-01-20", "2024-02-10", "2024-02-18"],
            "product_id": [10, 11, 12, 13],
            "product_category": ["Electronics", "Home", "Electronics", "Beauty"],
            "price": [100.0, 120.0, 80.0, 150.0],
            "discount_percent": [10, 20, 5, 25],
            "quantity_sold": [2, 1, 3, 2],
            "customer_region": ["North", "South", "North", "West"],
            "payment_method": ["Card", "Pix", "Card", "Boleto"],
            "rating": [4.8, 4.1, 4.6, 4.4],
            "review_count": [50, 20, 15, 30],
            "discounted_price": [90.0, 96.0, 76.0, 112.5],
            "total_revenue": [180.0, 96.0, 228.0, 225.0],
        }
    )


def test_actionable_recommendations_returns_expected_columns() -> None:
    featured = build_features(_fixture_df())
    recommendations = build_actionable_recommendations(featured)

    expected_columns = {
        "priority",
        "decision_rule",
        "recommended_action",
        "expected_impact_usd",
        "owner_area",
    }
    assert set(recommendations.columns) == expected_columns
    assert len(recommendations) >= 1
