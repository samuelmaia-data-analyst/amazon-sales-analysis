import pandas as pd
import pytest

from src.data_preprocessing import clean_sales_data


def _base_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1],
            "order_date": ["2024-01-15"],
            "product_id": [10],
            "product_category": ["Electronics"],
            "price": [100.0],
            "discount_percent": [10],
            "quantity_sold": [2],
            "customer_region": ["North"],
            "payment_method": ["Card"],
            "rating": [4.8],
            "review_count": [50],
            "discounted_price": [90.0],
            "total_revenue": [180.0],
        }
    )


def test_clean_sales_data_validates_required_columns():
    df = _base_df().drop(columns=["rating"])

    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        clean_sales_data(df)


def test_clean_sales_data_clips_discount_and_rating_and_recalculates_revenue():
    df = _base_df()
    df.loc[0, "discount_percent"] = 120
    df.loc[0, "rating"] = 9.0
    df.loc[0, "total_revenue"] = 1

    cleaned = clean_sales_data(df)

    assert cleaned.loc[0, "discount_percent"] == 100
    assert cleaned.loc[0, "rating"] == 5
    assert cleaned.loc[0, "discounted_price"] == 0
    assert cleaned.loc[0, "total_revenue"] == 0