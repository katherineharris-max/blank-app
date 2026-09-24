"""Generate and load daily-refreshing fake cohort LTV metrics."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "cohort_metrics.csv"

COHORTS = (
    "new_subscriber",
    "existing_subscriber",
    "new_payg",
    "existing_payg",
)

# Baseline economics by cohort (plausible placeholders for demos).
BASELINES = {
    "new_subscriber": {
        "customers": 12_500,
        "ltv": 185.0,
        "vp": 42.0,
        "avg_order_frequency": 2.8,
        "avg_tenure_months": 9.5,
        "monthly_acquisition": 4_200,
    },
    "existing_subscriber": {
        "customers": 48_000,
        "ltv": 310.0,
        "vp": 68.0,
        "avg_order_frequency": 3.6,
        "avg_tenure_months": 22.0,
        "monthly_acquisition": 0,
    },
    "new_payg": {
        "customers": 28_000,
        "ltv": 72.0,
        "vp": 18.0,
        "avg_order_frequency": 1.4,
        "avg_tenure_months": 4.0,
        "monthly_acquisition": 9_500,
    },
    "existing_payg": {
        "customers": 65_000,
        "ltv": 145.0,
        "vp": 31.0,
        "avg_order_frequency": 2.1,
        "avg_tenure_months": 11.0,
        "monthly_acquisition": 0,
    },
}

DISPLAY_NAMES = {
    "new_subscriber": "New subscriber",
    "existing_subscriber": "Existing subscriber",
    "new_payg": "New PAYG",
    "existing_payg": "Existing PAYG",
}


def _day_seed(as_of: date) -> int:
    return int(as_of.strftime("%Y%m%d"))


def generate_cohort_frame(as_of: date | None = None) -> pd.DataFrame:
    """Build one row per cohort; values nudge slightly each calendar day."""
    as_of = as_of or datetime.now(timezone.utc).date()
    rng = np.random.default_rng(_day_seed(as_of))

    rows = []
    for cohort in COHORTS:
        base = BASELINES[cohort]
        # Small daily noise so the linked file "refreshes" each day.
        noise = lambda center, pct: float(center * (1 + rng.uniform(-pct, pct)))
        customers = int(round(noise(base["customers"], 0.03)))
        monthly_acq = int(round(noise(base["monthly_acquisition"], 0.05)))
        rows.append(
            {
                "as_of_date": as_of.isoformat(),
                "cohort": cohort,
                "cohort_label": DISPLAY_NAMES[cohort],
                "customers": customers,
                "ltv": round(noise(base["ltv"], 0.04), 2),
                "vp": round(noise(base["vp"], 0.04), 2),
                "avg_order_frequency": round(noise(base["avg_order_frequency"], 0.03), 2),
                "avg_tenure_months": round(noise(base["avg_tenure_months"], 0.03), 2),
                "monthly_acquisition": monthly_acq,
            }
        )
    return pd.DataFrame(rows)


def refresh_dataset(as_of: date | None = None, force: bool = False) -> pd.DataFrame:
    """
    Write/load cohort_metrics.csv.

    Regenerates when the file is missing, stale (not today's date), or force=True.
    """
    as_of = as_of or datetime.now(timezone.utc).date()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATA_PATH.exists() and not force:
        existing = pd.read_csv(DATA_PATH)
        if not existing.empty and str(existing["as_of_date"].iloc[0]) == as_of.isoformat():
            return existing

    frame = generate_cohort_frame(as_of)
    frame.to_csv(DATA_PATH, index=False)
    return frame


def load_cohort_data() -> pd.DataFrame:
    return refresh_dataset()
