from __future__ import annotations

import pandas as pd

from .data_preprocessing import audit_data_quality


def enforce_clean_quality_gates(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("Quality gate falhou: dataset limpo nao pode ser vazio.")

    if df["discount_percent"].lt(0).any() or df["discount_percent"].gt(100).any():
        raise ValueError("Quality gate falhou: discount_percent fora da faixa [0, 100].")

    if df["rating"].lt(0).any() or df["rating"].gt(5).any():
        raise ValueError("Quality gate falhou: rating fora da faixa [0, 5].")

    if df["quantity_sold"].le(0).any():
        raise ValueError("Quality gate falhou: quantity_sold deve ser maior que zero.")

    if df["price"].lt(0).any():
        raise ValueError("Quality gate falhou: price nao pode ser negativo.")


def summarize_quality_gates(df: pd.DataFrame) -> pd.DataFrame:
    summary = audit_data_quality(df).copy()
    summary["status"] = summary["value"].apply(lambda value: "pass" if int(value) == 0 else "alert")
    summary.loc[summary["check"] == "row_count", "status"] = "pass" if len(df) > 0 else "alert"
    return summary
