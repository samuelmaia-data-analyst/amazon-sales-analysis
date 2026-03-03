import pandas as pd

from amazon_sales_analysis.data_preprocessing import clean_sales_data


def _base_fixture() -> pd.DataFrame:
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


def test_invalid_rows_are_removed_and_domain_is_respected() -> None:
    frame = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "order_date": ["2024-01-15", "invalid", "2024-01-17"],
            "product_id": [10, 11, 12],
            "product_category": ["Electronics", "Home", "Books"],
            "price": [100.0, -5.0, 50.0],
            "discount_percent": [10, 5, -20],
            "quantity_sold": [2, 1, 0],
            "customer_region": ["North", "South", "West"],
            "payment_method": ["Card", "Pix", "Boleto"],
            "rating": [4.8, 3.7, 2.0],
            "review_count": [50, 7, 3],
            "discounted_price": [90.0, 4.75, 40.0],
            "total_revenue": [180.0, 4.75, 0.0],
        }
    )

    cleaned = clean_sales_data(frame)

    assert len(cleaned) == 1
    assert cleaned["price"].min() >= 0
    assert cleaned["quantity_sold"].min() > 0
    assert cleaned["discount_percent"].between(0, 100).all()


def test_cleaned_dataset_has_no_null_values() -> None:
    cleaned = clean_sales_data(_base_fixture())
    assert cleaned.isnull().sum().sum() == 0
