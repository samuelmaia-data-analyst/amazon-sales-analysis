import pandas as pd

from .sales_analysis import analyze_category_performance, analyze_growth_trends, prepare_sales_frame


def build_actionable_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_sales_frame(df)
    categories = analyze_category_performance(prepared)
    growth = analyze_growth_trends(prepared)

    recommendations: list[dict[str, str | float]] = []

    if not categories.empty:
        lead = categories.iloc[0]
        pressure = categories.sort_values("discount_pressure", ascending=False).iloc[0]
        recommendations.append(
            {
                "priority": "high",
                "decision_rule": f"{lead['product_category']} concentra revenue",
                "recommended_action": (
                    "Definir monitoramento semanal com meta de revenue share e politica de desconto "
                    "dedicada para a categoria lider."
                ),
                "expected_impact_usd": float(lead["discount_value"]) * 0.05,
                "owner_area": "Category Management",
            }
        )
        recommendations.append(
            {
                "priority": "high",
                "decision_rule": f"{pressure['product_category']} sofre maior pressao promocional",
                "recommended_action": (
                    "Revisar profundidade promocional e separar campanhas de volume das campanhas "
                    "de margem para reduzir leakage."
                ),
                "expected_impact_usd": float(pressure["discount_value"]) * 0.05,
                "owner_area": "Revenue Operations",
            }
        )

    if not growth.empty and str(growth.iloc[-1]["momentum"]) == "Declining":
        recommendations.append(
            {
                "priority": "medium",
                "decision_rule": "Revenue mensal em queda no ultimo periodo",
                "recommended_action": (
                    "Investigar segmentos e categorias com queda recente antes de ampliar novos descontos."
                ),
                "expected_impact_usd": float(growth.iloc[-1]["revenue"]) * 0.02,
                "owner_area": "Commercial Strategy",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "priority": "low",
                "decision_rule": "Sem desvio relevante detectado",
                "recommended_action": "Manter rotina de monitoramento e revisar KPIs por categoria.",
                "expected_impact_usd": 0.0,
                "owner_area": "Analytics",
            }
        )

    return pd.DataFrame(recommendations).sort_values(
        by=["priority", "expected_impact_usd"], ascending=[True, False]
    )
