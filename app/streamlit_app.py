from pathlib import Path
from typing import Any, cast

import pandas as pd
import plotly.express as px
import streamlit as st

from amazon_sales_analysis.analytics import add_derived_metrics, summarize_kpis
from amazon_sales_analysis.anomaly_detection import detect_discount_spikes
from amazon_sales_analysis.config import PROCESSED_DATA_DIR
from amazon_sales_analysis.decision_engine import build_actionable_recommendations
from amazon_sales_analysis.scenario_simulator import simulate_leakage_recovery
from amazon_sales_analysis.table_organization import build_executive_tables

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_CSS = ROOT_DIR / "assets" / "custom.css"
DATASET_PATH = PROCESSED_DATA_DIR / "amazon_sales_clean.csv"
LOGO_LOCAL_PATH = ROOT_DIR / "assets" / "amazon_logo.svg"
LOGO_FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"

st.set_page_config(
    page_title="Amazon Sales Analytics",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

if ASSETS_CSS.exists():
    st.markdown(f"<style>{ASSETS_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

I18N = {
    "pt-BR": {
        "language_label": "Idioma",
        "language_options": ["PT-BR", "International"],
        "decision_controls": "### Controles de Decisão",
        "period": "Período",
        "region": "Região",
        "category": "Categoria",
        "payment": "Pagamento",
        "all": "Todos",
        "range": "Intervalo",
        "header_sub": "Portfólio de dados com foco executivo: pipeline reproduzível, qualidade e impacto de negócio.",
        "dataset_missing": "Dataset processado não encontrado. Execute: python -m amazon_sales_analysis.cli.pipeline",
        "kpi_revenue": "Receita Total",
        "kpi_orders": "Pedidos",
        "kpi_units": "Unidades",
        "kpi_ticket": "Ticket Médio",
        "kpi_rating": "Rating Médio",
        "kpi_nrr": "North Star NRR",
        "of_total": "do total",
        "no_data_cut": "Sem dados para o recorte selecionado.",
        "revenue_by_region": "Receita por Região",
        "revenue_by_payment": "Receita por Método de Pagamento",
        "monthly_trend": "Tendência Mensal de Receita",
        "recruiter_signals": "Sinais de Senioridade Técnica",
        "recruiter_md": """
- Arquitetura orientada a domínio (`src/amazon_sales_analysis`) com separação clara de responsabilidades.
- Pipeline empacotada com CLIs (`amazon-sales-pipeline`, `amazon-sales-alerts`, `amazon-sales-scenario`).
- Padrão de qualidade com testes automatizados, type checking e governança de repositório.
- Dashboard orientado à decisão: KPI, segmentação, tendência e leitura executiva.
        """,
        "top_10_categories": "Top 10 Categorias por Receita",
        "action_layer": "Camada de Decisão Acionável",
        "dq_indicator": "Indicador",
        "dq_value": "Valor",
        "dq_rows": "Total de linhas",
        "dq_nulls": "Nulos totais",
        "dq_dup": "Pedidos duplicados",
        "dq_discount": "Desconto fora de 0-100",
        "dq_rating": "Rating fora de 0-5",
        "tab_exec": "Dashboard Executivo",
        "tab_recruiter": "Perfil para Recrutadores",
        "tab_dq": "Qualidade dos Dados",
        "tab_tables": "Tabelas Executivas",
        "tab_scenario": "Simulador de Cenários",
        "kpi_summary": "Resumo de KPIs",
        "category_perf": "Performance por Categoria",
        "regional_perf": "Performance Regional",
        "payment_perf": "Performance por Pagamento",
        "trend_table": "Tendência Mensal",
        "dq_audit": "Auditoria de Qualidade",
        "no_records": "Nenhum registro encontrado para os filtros selecionados.",
        "scenario_title": "Simulador de Cenários: Recuperação de Leakage por Categoria",
        "scenario_help": "Ajuste os sliders para estimar o upside de receita por categoria.",
        "sim_uplift": "Upside Simulado",
        "sim_nrr": "NRR Simulado",
        "sim_baseline_nrr": "NRR Base",
        "sim_table": "Breakdown por Categoria",
        "anomaly_title": "Alertas de Anomalia (Discount Spikes)",
        "anomaly_empty": "Nenhuma anomalia detectada para o recorte selecionado.",
    },
    "en": {
        "language_label": "Language",
        "language_options": ["International", "PT-BR"],
        "decision_controls": "### Decision Controls",
        "period": "Period",
        "region": "Region",
        "category": "Category",
        "payment": "Payment",
        "all": "All",
        "range": "Range",
        "header_sub": "Business-focused data portfolio: reproducible pipeline, quality, and business impact.",
        "dataset_missing": "Processed dataset not found. Run: python -m amazon_sales_analysis.cli.pipeline",
        "kpi_revenue": "Total Revenue",
        "kpi_orders": "Orders",
        "kpi_units": "Units",
        "kpi_ticket": "Avg Ticket",
        "kpi_rating": "Avg Rating",
        "kpi_nrr": "North Star NRR",
        "of_total": "of total",
        "no_data_cut": "No data available for the selected slice.",
        "revenue_by_region": "Revenue by Region",
        "revenue_by_payment": "Revenue by Payment Method",
        "monthly_trend": "Monthly Revenue Trend",
        "recruiter_signals": "Technical Seniority Signals",
        "recruiter_md": """
- Domain-oriented architecture (`src/amazon_sales_analysis`) with clear separation of responsibilities.
- Packaged pipeline with dedicated CLIs (`amazon-sales-pipeline`, `amazon-sales-alerts`, `amazon-sales-scenario`).
- Quality standards enforced with automated tests, type checking, and repository governance.
- Decision-oriented dashboard with KPIs, segmentation, trends, and executive context.
        """,
        "top_10_categories": "Top 10 Categories by Revenue",
        "action_layer": "Actionable Decision Layer",
        "dq_indicator": "Indicator",
        "dq_value": "Value",
        "dq_rows": "Total rows",
        "dq_nulls": "Total nulls",
        "dq_dup": "Duplicated orders",
        "dq_discount": "Discount outside 0-100",
        "dq_rating": "Rating outside 0-5",
        "tab_exec": "Executive Dashboard",
        "tab_recruiter": "Recruiter Profile",
        "tab_dq": "Data Quality",
        "tab_tables": "Executive Tables",
        "tab_scenario": "Scenario Simulator",
        "kpi_summary": "KPI Summary",
        "category_perf": "Category Performance",
        "regional_perf": "Regional Performance",
        "payment_perf": "Payment Performance",
        "trend_table": "Monthly Trend",
        "dq_audit": "Data Quality Audit",
        "no_records": "No records found for the selected filters.",
        "scenario_title": "Scenario Simulator: Leakage Recovery by Category",
        "scenario_help": "Adjust the sliders to estimate revenue upside by category.",
        "sim_uplift": "Simulated Upside",
        "sim_nrr": "Simulated NRR",
        "sim_baseline_nrr": "Baseline NRR",
        "sim_table": "Category Breakdown",
        "anomaly_title": "Anomaly Alerts (Discount Spikes)",
        "anomaly_empty": "No anomaly detected for this slice.",
    },
}


def t(lang: str, key: str) -> str | list[str]:
    return cast(str | list[str], I18N[lang][key])


@st.cache_data(ttl=3600)
def load_processed_data(lang: str) -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(cast(str, t(lang, "dataset_missing")))
    frame = pd.read_csv(DATASET_PATH, parse_dates=["order_date"])
    return cast(pd.DataFrame, add_derived_metrics(frame))


def render_logo() -> None:
    if LOGO_LOCAL_PATH.exists():
        st.image(str(LOGO_LOCAL_PATH), width=190)
        return
    st.image(LOGO_FALLBACK_URL, width=190)


def render_header(lang: str) -> None:
    st.markdown('<h1 class="main-header">Amazon Sales Analytics</h1>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="sub-header">{cast(str, t(lang, "header_sub"))}</p>',
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    with st.sidebar:
        render_logo()
        st.markdown(cast(str, t(lang, "decision_controls")))

        start_default = df["order_date"].min().date()
        end_default = df["order_date"].max().date()
        date_range = st.date_input(
            cast(str, t(lang, "period")),
            value=(start_default, end_default),
            min_value=start_default,
            max_value=end_default,
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = start_default

        all_label = cast(str, t(lang, "all"))
        regions = [all_label] + sorted(df["customer_region"].dropna().unique().tolist())
        categories = [all_label] + sorted(df["product_category"].dropna().unique().tolist())
        payment_methods = [all_label] + sorted(df["payment_method"].dropna().unique().tolist())

        selected_region = st.selectbox(cast(str, t(lang, "region")), regions)
        selected_category = st.selectbox(cast(str, t(lang, "category")), categories)
        selected_payment = st.selectbox(cast(str, t(lang, "payment")), payment_methods)

        st.markdown("---")
        st.caption(f"{cast(str, t(lang, 'range'))}: {start_date} - {end_date}")

    filtered = df[(df["order_date"].dt.date >= start_date) & (df["order_date"].dt.date <= end_date)]
    if selected_region != all_label:
        filtered = filtered[filtered["customer_region"] == selected_region]
    if selected_category != all_label:
        filtered = filtered[filtered["product_category"] == selected_category]
    if selected_payment != all_label:
        filtered = filtered[filtered["payment_method"] == selected_payment]

    return cast(pd.DataFrame, filtered.copy())


def render_kpis(df_filtered: pd.DataFrame, df_all: pd.DataFrame, lang: str) -> None:
    kpis = summarize_kpis(df_filtered)
    baseline = summarize_kpis(df_all)

    coverage = (
        (kpis["total_revenue"] / baseline["total_revenue"] * 100)
        if baseline["total_revenue"]
        else 0
    )
    order_share = (
        (kpis["total_orders"] / baseline["total_orders"] * 100) if baseline["total_orders"] else 0
    )

    def fmt_currency_compact(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"${value / 1_000:.1f}K"
        return f"${value:,.0f}"

    def fmt_number_compact(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:,.0f}"

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    row1_col1.metric(
        cast(str, t(lang, "kpi_revenue")),
        fmt_currency_compact(kpis["total_revenue"]),
        f"{coverage:.1f}% {cast(str, t(lang, 'of_total'))}",
    )
    row1_col2.metric(
        cast(str, t(lang, "kpi_orders")),
        fmt_number_compact(kpis["total_orders"]),
        f"{order_share:.1f}% {cast(str, t(lang, 'of_total'))}",
    )
    row1_col3.metric(cast(str, t(lang, "kpi_units")), fmt_number_compact(kpis["total_units"]))
    row2_col1.metric(cast(str, t(lang, "kpi_ticket")), f"${kpis['avg_ticket']:,.2f}")
    row2_col2.metric(cast(str, t(lang, "kpi_rating")), f"{kpis['avg_rating']:.2f}")
    row2_col3.metric(cast(str, t(lang, "kpi_nrr")), f"{kpis['net_revenue_retained'] * 100:.2f}%")


def render_exec_dashboard(df: pd.DataFrame, lang: str) -> None:
    if df.empty:
        st.warning(cast(str, t(lang, "no_data_cut")))
        return

    col1, col2 = st.columns(2)
    region_revenue = df.groupby("customer_region", as_index=False)["total_revenue"].sum()
    payment_revenue = df.groupby("payment_method", as_index=False)["total_revenue"].sum()

    with col1:
        fig = px.pie(
            region_revenue,
            values="total_revenue",
            names="customer_region",
            title=cast(str, t(lang, "revenue_by_region")),
            hole=0.48,
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            payment_revenue,
            x="payment_method",
            y="total_revenue",
            title=cast(str, t(lang, "revenue_by_payment")),
            color="total_revenue",
            color_continuous_scale="blues",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    monthly = (
        df.set_index("order_date")["total_revenue"]
        .resample("ME")
        .sum()
        .reset_index()
        .sort_values("order_date")
    )
    trend = px.line(
        monthly,
        x="order_date",
        y="total_revenue",
        markers=True,
        title=cast(str, t(lang, "monthly_trend")),
    )
    trend.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(trend, use_container_width=True)


def render_recruiter_section(df: pd.DataFrame, lang: str) -> None:
    st.subheader(cast(str, t(lang, "recruiter_signals")))
    st.markdown(cast(str, t(lang, "recruiter_md")))

    top_categories = (
        df.groupby("product_category", as_index=False)
        .agg(total_revenue=("total_revenue", "sum"))
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )
    fig = px.bar(
        top_categories,
        x="total_revenue",
        y="product_category",
        orientation="h",
        title=cast(str, t(lang, "top_10_categories")),
        color="total_revenue",
        color_continuous_scale="oranges",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(cast(str, t(lang, "action_layer")))
    recommendations = build_actionable_recommendations(df)
    st.dataframe(recommendations, use_container_width=True, hide_index=True)

    st.subheader(cast(str, t(lang, "anomaly_title")))
    anomalies = detect_discount_spikes(df)
    if anomalies.empty:
        st.info(cast(str, t(lang, "anomaly_empty")))
    else:
        st.dataframe(anomalies, use_container_width=True, hide_index=True)


def render_scenario_simulator(df: pd.DataFrame, lang: str) -> None:
    st.subheader(cast(str, t(lang, "scenario_title")))
    st.caption(cast(str, t(lang, "scenario_help")))

    categories = sorted(df["product_category"].dropna().unique().tolist())
    recovery_rates: dict[str, float] = {}

    for category in categories:
        slider_value = st.slider(
            f"{category}",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            key=f"recovery_{category}",
        )
        recovery_rates[category] = slider_value / 100.0

    simulation = cast(dict[str, Any], simulate_leakage_recovery(df, recovery_rates))
    col1, col2, col3 = st.columns(3)
    col1.metric(
        cast(str, t(lang, "sim_uplift")), f"${cast(float, simulation['total_uplift']):,.0f}"
    )
    col2.metric(
        cast(str, t(lang, "sim_baseline_nrr")),
        f"{cast(float, simulation['baseline_nrr']) * 100:.2f}%",
    )
    col3.metric(
        cast(str, t(lang, "sim_nrr")), f"{cast(float, simulation['simulated_nrr']) * 100:.2f}%"
    )

    breakdown = cast(pd.DataFrame, simulation["category_breakdown"]).copy()
    breakdown["recovery_rate"] = breakdown["recovery_rate"] * 100
    st.subheader(cast(str, t(lang, "sim_table")))
    st.dataframe(
        breakdown[
            [
                "product_category",
                "discount_leakage",
                "recovery_rate",
                "expected_uplift",
                "simulated_revenue",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_data_quality(df: pd.DataFrame, lang: str) -> None:
    summary = pd.DataFrame(
        {
            cast(str, t(lang, "dq_indicator")): [
                cast(str, t(lang, "dq_rows")),
                cast(str, t(lang, "dq_nulls")),
                cast(str, t(lang, "dq_dup")),
                cast(str, t(lang, "dq_discount")),
                cast(str, t(lang, "dq_rating")),
            ],
            cast(str, t(lang, "dq_value")): [
                len(df),
                int(df.isna().sum().sum()),
                int(df["order_id"].duplicated().sum()),
                int(((df["discount_percent"] < 0) | (df["discount_percent"] > 100)).sum()),
                int(((df["rating"] < 0) | (df["rating"] > 5)).sum()),
            ],
        }
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


def render_executive_tables(df: pd.DataFrame, lang: str) -> None:
    tables = build_executive_tables(df)

    st.subheader(cast(str, t(lang, "kpi_summary")))
    st.dataframe(tables["kpi_summary"], use_container_width=True, hide_index=True)

    st.subheader(cast(str, t(lang, "category_perf")))
    st.dataframe(tables["category_performance"], use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(cast(str, t(lang, "regional_perf")))
        st.dataframe(tables["regional_performance"], use_container_width=True, hide_index=True)
    with col2:
        st.subheader(cast(str, t(lang, "payment_perf")))
        st.dataframe(tables["payment_performance"], use_container_width=True, hide_index=True)

    st.subheader(cast(str, t(lang, "trend_table")))
    st.dataframe(tables["monthly_trend"], use_container_width=True, hide_index=True)

    st.subheader(cast(str, t(lang, "dq_audit")))
    st.dataframe(tables["data_quality_audit"], use_container_width=True, hide_index=True)


def main() -> None:
    language_option = st.sidebar.selectbox("Language / Idioma", ["International", "PT-BR"])
    lang = "pt-BR" if language_option == "PT-BR" else "en"

    render_header(lang)

    try:
        df_all = load_processed_data(lang)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    filtered_df = render_sidebar(df_all, lang)
    if filtered_df.empty:
        st.warning(cast(str, t(lang, "no_records")))
        return

    render_kpis(filtered_df, df_all, lang)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            cast(str, t(lang, "tab_exec")),
            cast(str, t(lang, "tab_recruiter")),
            cast(str, t(lang, "tab_dq")),
            cast(str, t(lang, "tab_tables")),
            cast(str, t(lang, "tab_scenario")),
        ]
    )
    with tab1:
        render_exec_dashboard(filtered_df, lang)
    with tab2:
        render_recruiter_section(filtered_df, lang)
    with tab3:
        render_data_quality(filtered_df, lang)
    with tab4:
        render_executive_tables(filtered_df, lang)
    with tab5:
        render_scenario_simulator(filtered_df, lang)


if __name__ == "__main__":
    main()
