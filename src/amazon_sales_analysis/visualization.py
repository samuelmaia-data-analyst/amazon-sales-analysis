from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import FIGURES_DIR
from .sales_analysis import (
    analyze_category_performance,
    analyze_growth_trends,
    analyze_performance_distribution,
    analyze_product_contribution,
    prepare_sales_frame,
)

sns.set_theme(style="whitegrid", palette="crest")


def sales_trend_over_time(df: pd.DataFrame) -> None:
    prepared = prepare_sales_frame(df)
    growth = analyze_growth_trends(prepared)

    plt.figure(figsize=(11, 5))
    sns.lineplot(data=growth, x="month_start", y="revenue", marker="o", linewidth=2.5)
    plt.title("Executive Story 1: Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sales_trend_over_time.png")
    plt.close()


def top_categories_by_sales(df: pd.DataFrame, top_n: int = 10) -> None:
    prepared = prepare_sales_frame(df)
    category = analyze_category_performance(prepared).head(top_n)

    plt.figure(figsize=(11, 6))
    sns.barplot(data=category, x="revenue", y="product_category")
    plt.title("Executive Story 2: Category Performance")
    plt.xlabel("Revenue")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "top_categories_by_sales.png")
    plt.close()


def product_contribution_chart(df: pd.DataFrame, top_n: int = 10) -> None:
    prepared = prepare_sales_frame(df)
    products = analyze_product_contribution(prepared, top_n=top_n)

    plt.figure(figsize=(11, 6))
    sns.barplot(data=products, x="revenue_share", y=products["product_id"].astype(str))
    plt.title("Executive Story 3: Product Contribution")
    plt.xlabel("Revenue Share")
    plt.ylabel("Product ID")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "product_contribution.png")
    plt.close()


def performance_distribution_chart(df: pd.DataFrame) -> None:
    prepared = prepare_sales_frame(df)
    distribution = analyze_performance_distribution(prepared)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=distribution, x="performance_band", y="revenue_share")
    plt.title("Executive Story 4: Performance Distribution")
    plt.xlabel("Performance Band")
    plt.ylabel("Revenue Share")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "performance_distribution.png")
    plt.close()


def build_storytelling_visuals(df: pd.DataFrame) -> None:
    sales_trend_over_time(df)
    top_categories_by_sales(df)
    product_contribution_chart(df)
    performance_distribution_chart(df)
