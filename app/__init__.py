"""Application entry points for API and Streamlit surfaces."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    src_dir = Path(__file__).resolve().parent.parent / "src"
    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)


_ensure_src_on_path()
