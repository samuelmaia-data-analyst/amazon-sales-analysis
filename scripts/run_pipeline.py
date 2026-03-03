from pathlib import Path
import logging
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from amazon_sales_analysis.data_ingestion import download_amazon_sales_dataset
from amazon_sales_analysis.data_preprocessing import clean_sales_data, load_raw_sales_data, save_processed_data
from amazon_sales_analysis.eda import basic_eda
from amazon_sales_analysis.evaluation import build_executive_summary
from amazon_sales_analysis.feature_engineering import build_features
from amazon_sales_analysis.logging_config import configure_logging
from amazon_sales_analysis.modeling import rank_discount_opportunities
from amazon_sales_analysis.visualization import sales_trend_over_time, top_categories_by_sales
from amazon_sales_analysis.config import TABLES_DIR


def main() -> None:
    configure_logging()
    logger = logging.getLogger("pipeline")

    logger.info("[1/7] Downloading raw dataset")
    download_amazon_sales_dataset()

    logger.info("[2/7] Loading raw data")
    raw_df = load_raw_sales_data()

    logger.info("[3/7] Cleaning dataset")
    clean_df = clean_sales_data(raw_df)
    output_path = save_processed_data(clean_df)
    logger.info("Processed dataset saved to: %s", output_path)

    logger.info("[4/7] Building business features")
    featured_df = build_features(clean_df)

    logger.info("[5/7] Running exploratory analysis and visual exports")
    basic_eda(featured_df)
    sales_trend_over_time(featured_df)
    top_categories_by_sales(featured_df)

    logger.info("[6/7] Evaluating business impact and opportunities")
    executive_summary = build_executive_summary(featured_df)
    opportunities = rank_discount_opportunities(featured_df)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    executive_path = TABLES_DIR / "executive_summary.csv"
    opportunities_path = TABLES_DIR / "discount_opportunities.csv"
    executive_summary.to_csv(executive_path, index=False)
    opportunities.to_csv(opportunities_path, index=False)

    logger.info("Executive summary saved to: %s", executive_path)
    logger.info("Opportunities table saved to: %s", opportunities_path)
    logger.info("[7/7] Pipeline completed successfully")


if __name__ == "__main__":
    main()
