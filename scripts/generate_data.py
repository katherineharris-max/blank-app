"""Create / refresh the large cohort panel and LTV summary CSVs."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cohort_panel import refresh_panel, PANEL_PATH
from ltv import calculate_cohort_ltv, write_summary

if __name__ == "__main__":
    panel = refresh_panel(force=True)
    summary = calculate_cohort_ltv(panel)
    path = write_summary(summary)
    print(f"Panel rows: {len(panel):,} → {PANEL_PATH}")
    print(f"LTV summary → {path}")
    print(summary.to_string(index=False))
