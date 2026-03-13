import pandas as pd

from amazon_sales_analysis.insights import generate_executive_insights
from amazon_sales_analysis.sales_analysis import (
    analyze_category_performance,
    analyze_growth_trends,
    analyze_product_contribution,
    build_executive_report,
    prepare_sales_frame,
)


def _fixture_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "order_date": ["2024-01-15", "2024-02-10", "2024-02-18", "2024-03-03"],
            "product_id": [10, 11, 10, 12],
            "product_category": ["Electronics", "Home", "Electronics", "Beauty"],
            "price": [100.0, 120.0, 80.0, 50.0],
            "discount_percent": [10, 20, 5, 0],
            "quantity_sold": [2, 1, 3, 4],
            "customer_region": ["North", "South", "North", "East"],
            "payment_method": ["Card", "Pix", "Card", "Cash"],
            "rating": [4.8, 4.1, 4.6, 4.9],
            "review_count": [50, 20, 15, 12],
            "discounted_price": [90.0, 96.0, 76.0, 50.0],
            "total_revenue": [180.0, 96.0, 228.0, 200.0],
        }
    )


def test_sales_analysis_builds_business_views() -> None:
    prepared = prepare_sales_frame(_fixture_df())

    category = analyze_category_performance(prepared)
    products = analyze_product_contribution(prepared)
    growth = analyze_growth_trends(prepared)

    assert category.iloc[0]["product_category"] == "Electronics"
    assert "discount_pressure" in category.columns
    assert "revenue_share" in products.columns
    assert "revenue_growth_rate" in growth.columns


def test_executive_report_contains_storytelling_assets() -> None:
    prepared = prepare_sales_frame(_fixture_df())
    insights = generate_executive_insights(prepared)
    report = build_executive_report(prepared, insights)

    assert not report.insights.empty
    assert not report.kpi_catalog.empty
    assert not report.performance_distribution.empty
