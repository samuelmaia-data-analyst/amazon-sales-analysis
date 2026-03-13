from __future__ import annotations

import logging

from amazon_sales_analysis import __version__
from amazon_sales_analysis.anomaly_detection import (
    detect_discount_spikes,
    export_discount_spike_alerts,
)
from amazon_sales_analysis.config import TABLES_DIR
from amazon_sales_analysis.contracts import enforce_raw_contract, export_contract_snapshot
from amazon_sales_analysis.data_ingestion import download_amazon_sales_dataset
from amazon_sales_analysis.data_preprocessing import (
    clean_sales_data,
    load_raw_sales_data,
    save_processed_data,
    validate_raw_sales_data,
)
from amazon_sales_analysis.decision_engine import build_actionable_recommendations
from amazon_sales_analysis.insights import generate_executive_insights
from amazon_sales_analysis.logging_config import configure_logging
from amazon_sales_analysis.metrics import collect_product_metrics, save_product_metrics
from amazon_sales_analysis.quality import enforce_clean_quality_gates
from amazon_sales_analysis.sales_analysis import build_executive_report, prepare_sales_frame
from amazon_sales_analysis.table_organization import build_executive_tables
from amazon_sales_analysis.visualization import build_storytelling_visuals

CONTRACT_VERSION = "2.0.0"
PIPELINE_VERSION = __version__


def main() -> None:
    configure_logging()
    logger = logging.getLogger("pipeline")

    try:
        logger.info("[1/7] Ensuring source dataset availability")
        download_amazon_sales_dataset()

        logger.info("[2/7] Loading and validating raw data")
        raw_df = load_raw_sales_data()
        enforce_raw_contract(raw_df)
        validate_raw_sales_data(raw_df)
        contract_path = export_contract_snapshot(contract_version=CONTRACT_VERSION)
        logger.info("Data contract snapshot saved to: %s", contract_path)

        logger.info("[3/7] Cleaning and quality-checking the dataset")
        clean_df = clean_sales_data(raw_df)
        enforce_clean_quality_gates(clean_df)
        output_path = save_processed_data(clean_df)
        logger.info("Processed dataset saved to: %s", output_path)

        logger.info("[4/7] Building the commercial performance model")
        featured_df = prepare_sales_frame(clean_df)
        insights = generate_executive_insights(featured_df)
        report = build_executive_report(featured_df, insights)

        logger.info("[5/7] Exporting executive storytelling outputs")
        build_storytelling_visuals(featured_df)
        tables = build_executive_tables(featured_df)
        recommendations = build_actionable_recommendations(featured_df)
        anomalies = detect_discount_spikes(featured_df)

        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        for table_name, table_df in tables.items():
            table_df.to_csv(TABLES_DIR / f"{table_name}.csv", index=False)
        recommendations.to_csv(TABLES_DIR / "actionable_recommendations.csv", index=False)
        report.insights.to_csv(TABLES_DIR / "executive_insights.csv", index=False)
        alerts_path = export_discount_spike_alerts(anomalies)
        logger.info("Executive tables saved to: %s", TABLES_DIR)
        logger.info("Discount spike alerts saved to: %s", alerts_path)

        logger.info("[6/7] Persisting KPI package")
        metrics_payload = collect_product_metrics(
            raw_df,
            clean_df,
            featured_df,
            contract_version=CONTRACT_VERSION,
            pipeline_version=PIPELINE_VERSION,
        )
        metrics_path = save_product_metrics(metrics_payload)
        logger.info("Product metrics saved to: %s", metrics_path)

        logger.info("[7/7] Pipeline completed successfully")
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        raise
