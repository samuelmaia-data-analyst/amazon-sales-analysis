from pathlib import Path
import pandas as pd

from .config import RAW_DATA_DIR, PROCESSED_DATA_DIR


RAW_SUBDIR = "amazon_sales"
RAW_FILENAME = "amazon_sales_dataset.csv"
PROCESSED_FILENAME = "amazon_sales_clean.csv"

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "product_id",
    "product_category",
    "price",
    "discount_percent",
    "quantity_sold",
    "customer_region",
    "payment_method",
    "rating",
    "review_count",
    "discounted_price",
    "total_revenue",
}


def load_raw_sales_data() -> pd.DataFrame:
    """
    Carrega o arquivo principal de vendas da pasta data/raw/amazon_sales.
    """
    dataset_dir = RAW_DATA_DIR / RAW_SUBDIR
    sales_file = dataset_dir / RAW_FILENAME
    if not sales_file.exists():
        raise FileNotFoundError(f"Arquivo bruto não encontrado em {sales_file}")
    print(f"Carregando dados de: {sales_file}")
    df = pd.read_csv(sales_file)
    return df


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza específica para o schema do dataset Amazon:

    Colunas:
    - order_id (int)
    - order_date (datetime)
    - product_id (int)
    - product_category (str)
    - price (float)
    - discount_percent (int)
    - quantity_sold (int)
    - customer_region (str)
    - payment_method (str)
    - rating (float)
    - review_count (int)
    - discounted_price (float)
    - total_revenue (float)
    """
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {missing}")

    df = df.copy()

    # Garantir tipos adequados
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    numeric_cols = [
        "order_id",
        "product_id",
        "price",
        "discount_percent",
        "quantity_sold",
        "rating",
        "review_count",
        "discounted_price",
        "total_revenue",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remover linhas sem data ou sem receita total
    df = df.dropna(subset=["order_date", "total_revenue"])
    # Remover linhas sem data, preço ou quantidade
    df = df.dropna(subset=["order_date", "price", "discount_percent", "quantity_sold"])

    # Remover vendas com quantidade <= 0
    df = df[df["quantity_sold"] > 0]
    # Corrigir limites conhecidos do domínio
    df = df[(df["quantity_sold"] > 0) & (df["price"] >= 0)]
    df["discount_percent"] = df["discount_percent"].clip(lower=0, upper=100)
    df["rating"] = df["rating"].clip(lower=0, upper=5)

    # Recalcular total_revenue e discounted_price para consistência
    df["discounted_price_calc"] = df["price"] * (1 - df["discount_percent"] / 100)
    df["total_revenue_calc"] = df["discounted_price_calc"] * df["quantity_sold"]

    # Se a diferença for pequena, substitui pelos valores calculados
    # Priorizar valores calculados para garantir consistência
    df["total_revenue"] = df["total_revenue_calc"]
    df["discounted_price"] = df["discounted_price_calc"]

    df = df.drop(columns=["discounted_price_calc", "total_revenue_calc"])

    # Reset index
    df = df.reset_index(drop=True)

    return df


def save_processed_data(df: pd.DataFrame, filename: str = PROCESSED_FILENAME) -> Path:
    """
    Salva o DataFrame limpo na pasta data/processed.
    """
    output_path = PROCESSED_DATA_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"Dados processados salvos em: {output_path}")
    return output_path


if __name__ == "__main__":
    raw_df = load_raw_sales_data()
    clean_df = clean_sales_data(raw_df)
    save_processed_data(clean_df)
