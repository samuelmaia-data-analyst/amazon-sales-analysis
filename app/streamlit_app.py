from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from amazon_sales_analysis.config import PROCESSED_DATA_DIR
from amazon_sales_analysis.data_preprocessing import read_sales_dataset
from amazon_sales_analysis.insights import generate_executive_insights
from amazon_sales_analysis.quality import summarize_quality_gates
from amazon_sales_analysis.sales_analysis import build_executive_report, prepare_sales_frame

ROOT_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = PROCESSED_DATA_DIR / "amazon_sales_clean.csv"

st.set_page_config(page_title="Amazon Commercial Performance Monitor", layout="wide")


@st.cache_data(ttl=3600)
def load_dataset() -> pd.DataFrame:
    frame = read_sales_dataset(DATASET_PATH)
    return prepare_sales_frame(frame)


def format_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def main() -> None:
    st.title("Amazon Commercial Performance Monitor")
    st.caption(
        "Monitoramento de performance comercial com foco em revenue, ticket medio, categorias, "
        "produtos lideres e tendencia temporal."
    )

    try:
        df = load_dataset()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    insights = generate_executive_insights(df)
    report = build_executive_report(df, insights)
    kpi_lookup = dict(zip(report.kpi_summary["metric"], report.kpi_summary["value"], strict=False))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue total", format_currency(float(kpi_lookup["total_revenue"])))
    col2.metric("Ticket medio", format_currency(float(kpi_lookup["avg_order_value"])))
    col3.metric("Pedidos", f"{int(kpi_lookup['total_orders']):,}")
    col4.metric("NRR", f"{float(kpi_lookup['net_revenue_retained']) * 100:.1f}%")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Resumo Executivo", "Drivers de Performance", "Qualidade", "Catalogo de KPIs"]
    )

    with tab1:
        st.subheader("Principais achados")
        st.dataframe(report.insights, use_container_width=True, hide_index=True)

        trend_fig = px.line(
            report.growth_trends,
            x="month_start",
            y="revenue",
            markers=True,
            title="Story 1: Tendencia temporal de revenue",
        )
        st.plotly_chart(trend_fig, use_container_width=True)

        category_fig = px.bar(
            report.category_performance.head(8),
            x="revenue",
            y="product_category",
            orientation="h",
            title="Story 2: Categorias que sustentam o revenue",
            color="discount_pressure",
            color_continuous_scale="Oranges",
        )
        st.plotly_chart(category_fig, use_container_width=True)

    with tab2:
        product_fig = px.bar(
            report.product_contribution,
            x="revenue_share",
            y=report.product_contribution["product_id"].astype(str),
            orientation="h",
            title="Story 3: Produtos com maior contribuicao",
            color="revenue",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(product_fig, use_container_width=True)

        distribution_fig = px.bar(
            report.performance_distribution,
            x="performance_band",
            y="revenue_share",
            title="Story 4: Distribuicao de performance",
            color="avg_discount",
            color_continuous_scale="Teal",
        )
        st.plotly_chart(distribution_fig, use_container_width=True)

        st.dataframe(report.category_performance, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Validacoes de entrada")
        st.dataframe(summarize_quality_gates(df), use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("KPIs definidos")
        st.dataframe(report.kpi_catalog, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
