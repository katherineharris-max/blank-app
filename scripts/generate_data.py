"""Create or refresh data/cohort_metrics.csv for today."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cohort_data import refresh_dataset

if __name__ == "__main__":
    frame = refresh_dataset(force=True)
    print(f"Wrote {len(frame)} rows to data/cohort_metrics.csv")
    print(frame.to_string(index=False))
