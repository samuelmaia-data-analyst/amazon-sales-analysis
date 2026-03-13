from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    src_dir = Path(__file__).resolve().parent / "src"
    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)


_ensure_src_on_path()

from amazon_sales_analysis.cli.pipeline import main

if __name__ == "__main__":
    main()
