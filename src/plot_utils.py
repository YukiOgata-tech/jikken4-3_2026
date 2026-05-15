"""Plotting helpers for report-quality figures."""

from __future__ import annotations

import os
from pathlib import Path


def setup_matplotlib() -> None:
    """Configure matplotlib for headless execution in this workspace."""
    cache_dir = Path("outputs/logs/matplotlib")
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir.resolve()))
    import matplotlib

    matplotlib.use("Agg", force=True)


def ensure_output_dirs() -> None:
    for path in ("outputs/figures", "outputs/tables", "outputs/logs", "reports"):
        Path(path).mkdir(parents=True, exist_ok=True)
