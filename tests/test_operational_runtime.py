import builtins
import json
import logging
import sys
import types

import pandas as pd
import pytest

from amazon_sales_analysis.cli import alerts as alerts_cli
from amazon_sales_analysis.cli import pipeline as pipeline_cli
from amazon_sales_analysis.cli import scenario as scenario_cli
from amazon_sales_analysis.data_ingestion import download_amazon_sales_dataset
from amazon_sales_analysis.logging_config import configure_logging


def test_download_dataset_copies_files_from_kagglehub(tmp_path, monkeypatch) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "amazon_sales_dataset.csv"
    source_file.write_text("order_id\n1\n", encoding="utf-8")

    fake_module = types.SimpleNamespace(dataset_download=lambda _: str(source_dir))
    monkeypatch.setitem(sys.modules, "kagglehub", fake_module)
    monkeypatch.setattr("amazon_sales_analysis.data_ingestion.RAW_DATA_DIR", tmp_path / "raw")

    target_dir = download_amazon_sales_dataset()

    copied_file = target_dir / "amazon_sales_dataset.csv"
    assert copied_file.exists()
    assert copied_file.read_text(encoding="utf-8") == source_file.read_text(encoding="utf-8")


def test_download_dataset_uses_existing_local_copy_when_kagglehub_is_missing(
    tmp_path, monkeypatch
) -> None:
    raw_dir = tmp_path / "raw"
    target_dir = raw_dir / "amazon_sales"
    target_dir.mkdir(parents=True)
    existing_file = target_dir / "amazon_sales_dataset.csv"
    existing_file.write_text("order_id\n1\n", encoding="utf-8")

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "kagglehub":
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "kagglehub", raising=False)
    monkeypatch.setattr("amazon_sales_analysis.data_ingestion.RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    target = download_amazon_sales_dataset()

    assert target == target_dir


def test_configure_logging_delegates_to_basic_config(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_basic_config(**kwargs) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)

    configure_logging(logging.DEBUG)

    assert captured["level"] == logging.DEBUG
    assert "%(levelname)s" in str(captured["format"])


def test_scenario_cli_helpers_parse_and_merge_category_rates() -> None:
    overrides = scenario_cli.parse_category_rates("Beauty=0.1,Fashion=0.2")
    recovery_rates = scenario_cli.build_recovery_rates(["Beauty", "Books"], 0.05, overrides)

    assert overrides == {"Beauty": 0.1, "Fashion": 0.2}
    assert recovery_rates == {"Beauty": 0.1, "Books": 0.05, "Fashion": 0.2}


def test_scenario_cli_rejects_invalid_override_format() -> None:
    with pytest.raises(ValueError):
        scenario_cli.parse_category_rates("Beauty:0.1")


def test_scenario_cli_run_generates_artifacts(tmp_path) -> None:
    input_path = tmp_path / "clean.csv"
    output_dir = tmp_path / "reports"
    frame = pd.DataFrame(
        {
            "order_id": [1, 2],
            "order_date": ["2024-01-01", "2024-01-02"],
            "product_id": [10, 11],
            "product_category": ["Beauty", "Books"],
            "price": [100.0, 200.0],
            "discount_percent": [10.0, 20.0],
            "quantity_sold": [1, 1],
            "customer_region": ["North", "South"],
            "payment_method": ["Card", "Pix"],
            "rating": [4.8, 4.7],
            "review_count": [10, 20],
            "discounted_price": [90.0, 160.0],
            "total_revenue": [90.0, 160.0],
        }
    )
    frame.to_csv(input_path, index=False)

    scenario_cli.run(
        input_path=input_path,
        output_dir=output_dir,
        recovery_rate=0.05,
        category_rates="Beauty=0.1",
    )

    assert (output_dir / "scenario_simulation_breakdown.csv").exists()
    assert (output_dir / "scenario_simulation_summary.json").exists()


def test_alerts_cli_run_rejects_invalid_parameters(tmp_path) -> None:
    with pytest.raises(SystemExit):
        alerts_cli.run(
            input_path=tmp_path / "missing.csv",
            z_threshold=2.5,
            min_observations=5,
            summary_output=tmp_path / "summary.json",
        )


def test_alerts_cli_run_generates_csv_and_summary(tmp_path, monkeypatch) -> None:
    input_path = tmp_path / "clean.csv"
    summary_output = tmp_path / "metrics" / "alerts_summary.json"
    exported_csv = tmp_path / "tables" / "discount_spike_alerts.csv"
    frame = pd.DataFrame(
        {
            "order_date": ["2024-01-05"],
            "product_category": ["Beauty"],
            "discount_percent": [30.0],
            "price": [100.0],
            "quantity_sold": [1],
        }
    )
    alerts = pd.DataFrame(
        {
            "order_date": ["2024-01-05"],
            "product_category": ["Beauty"],
            "avg_discount_percent": [30.0],
            "baseline_mean": [10.0],
            "baseline_std": [5.0],
            "z_score": [4.0],
            "gross_revenue": [100.0],
            "estimated_leakage_usd": [20.0],
            "severity": ["high"],
        }
    )
    frame.to_csv(input_path, index=False)

    def fake_export_discount_spike_alerts(detected: pd.DataFrame):
        exported_csv.parent.mkdir(parents=True, exist_ok=True)
        detected.to_csv(exported_csv, index=False)
        return exported_csv

    monkeypatch.setattr(alerts_cli, "detect_discount_spikes", lambda *args, **kwargs: alerts)
    monkeypatch.setattr(alerts_cli, "export_discount_spike_alerts", fake_export_discount_spike_alerts)

    alerts_cli.run(
        input_path=input_path,
        z_threshold=2.5,
        min_observations=5,
        summary_output=summary_output,
    )

    payload = json.loads(summary_output.read_text(encoding="utf-8"))
    assert exported_csv.exists()
    assert payload["status"] == "attention"
    assert payload["alerts_count"] == 1
    assert payload["severity_counts"] == {"high": 1}


def test_pipeline_cli_main_orchestrates_pipeline_outputs(tmp_path, monkeypatch) -> None:
    raw_df = pd.DataFrame({"order_id": [1], "price": [100.0]})
    clean_df = pd.DataFrame({"order_id": [1], "price": [100.0]})
    featured_df = pd.DataFrame({"order_id": [1], "total_revenue": [90.0]})
    alerts_df = pd.DataFrame({"product_category": ["Beauty"], "severity": ["high"]})
    recommendations = pd.DataFrame({"owner": ["Revenue Ops"], "action": ["Cap discounts"]})
    organized_tables = {
        "category_performance": pd.DataFrame({"product_category": ["Beauty"], "revenue": [90.0]}),
        "product_contribution": pd.DataFrame({"product_id": [1], "revenue": [90.0]}),
    }
    insights = pd.DataFrame({"headline": ["Revenue baseline"], "insight": ["..."]})

    contract_path = tmp_path / "contracts" / "snapshot.json"
    metrics_path = tmp_path / "metrics" / "product_metrics.json"
    processed_path = tmp_path / "processed" / "amazon_sales_clean.csv"
    alerts_path = tmp_path / "tables" / "discount_spike_alerts.csv"
    tables_dir = tmp_path / "tables"
    logged_messages: list[str] = []

    class FakeLogger:
        def info(self, message: str, *args) -> None:
            logged_messages.append(message % args if args else message)

    monkeypatch.setattr(pipeline_cli, "configure_logging", lambda: None)
    monkeypatch.setattr(
        pipeline_cli, "logging", types.SimpleNamespace(getLogger=lambda name=None: FakeLogger())
    )
    monkeypatch.setattr(pipeline_cli, "download_amazon_sales_dataset", lambda: tmp_path / "raw")
    monkeypatch.setattr(pipeline_cli, "load_raw_sales_data", lambda: raw_df)
    monkeypatch.setattr(pipeline_cli, "enforce_raw_contract", lambda frame: None)
    monkeypatch.setattr(pipeline_cli, "validate_raw_sales_data", lambda frame: frame)
    monkeypatch.setattr(pipeline_cli, "export_contract_snapshot", lambda contract_version: contract_path)
    monkeypatch.setattr(pipeline_cli, "clean_sales_data", lambda frame: clean_df)
    monkeypatch.setattr(pipeline_cli, "enforce_clean_quality_gates", lambda frame: None)
    monkeypatch.setattr(pipeline_cli, "save_processed_data", lambda frame: processed_path)
    monkeypatch.setattr(pipeline_cli, "prepare_sales_frame", lambda frame: featured_df)
    monkeypatch.setattr(pipeline_cli, "generate_executive_insights", lambda frame: insights)
    monkeypatch.setattr(
        pipeline_cli,
        "build_executive_report",
        lambda frame, report_insights: types.SimpleNamespace(insights=report_insights),
    )
    monkeypatch.setattr(pipeline_cli, "build_storytelling_visuals", lambda frame: None)
    monkeypatch.setattr(pipeline_cli, "build_actionable_recommendations", lambda frame: recommendations)
    monkeypatch.setattr(pipeline_cli, "build_executive_tables", lambda frame: organized_tables)
    monkeypatch.setattr(
        pipeline_cli,
        "collect_product_metrics",
        lambda raw_df, clean_df, featured_df, contract_version, pipeline_version: {
            "contract_version": contract_version,
            "pipeline_version": pipeline_version,
        },
    )
    monkeypatch.setattr(pipeline_cli, "save_product_metrics", lambda payload: metrics_path)
    monkeypatch.setattr(pipeline_cli, "detect_discount_spikes", lambda frame: alerts_df)
    monkeypatch.setattr(pipeline_cli, "export_discount_spike_alerts", lambda frame: alerts_path)
    monkeypatch.setattr(pipeline_cli, "TABLES_DIR", tables_dir)

    pipeline_cli.main()

    assert (tables_dir / "actionable_recommendations.csv").exists()
    assert (tables_dir / "executive_insights.csv").exists()
    assert (tables_dir / "category_performance.csv").exists()
    assert (tables_dir / "product_contribution.csv").exists()
    assert any("Pipeline completed successfully" in message for message in logged_messages)
