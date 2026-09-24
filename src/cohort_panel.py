"""Generate a large fake cohort panel over time (tenure curves by vintage)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PANEL_PATH = DATA_DIR / "cohort_panel.csv"
SUMMARY_PATH = DATA_DIR / "cohort_ltv_summary.csv"

# User-facing cohort names
COHORTS = {
    "nc_sub": {
        "label": "NC Sub",
        "description": "New customer subscriber",
        "start_customers": 4_200,
        "m1_order_rate": 2.8,
        "m1_vp_per_order": 9.5,
        "retention_decay": 0.92,  # share of prior-month actives retained
        "order_decay": 0.97,
        "vp_decay": 0.995,
    },
    "ec_sub": {
        "label": "EC Sub",
        "description": "Existing customer subscriber",
        "start_customers": 3_800,
        "m1_order_rate": 3.5,
        "m1_vp_per_order": 11.0,
        "retention_decay": 0.96,
        "order_decay": 0.99,
        "vp_decay": 0.998,
    },
    "payg_nc": {
        "label": "PAYG NC",
        "description": "New customer pay-as-you-go",
        "start_customers": 9_500,
        "m1_order_rate": 1.6,
        "m1_vp_per_order": 7.0,
        "retention_decay": 0.82,
        "order_decay": 0.94,
        "vp_decay": 0.99,
    },
    "payg_ec": {
        "label": "PAYG EC",
        "description": "Existing customer pay-as-you-go",
        "start_customers": 6_200,
        "m1_order_rate": 2.2,
        "m1_vp_per_order": 8.2,
        "retention_decay": 0.90,
        "order_decay": 0.96,
        "vp_decay": 0.993,
    },
}

N_VINTAGES = 24  # acquisition months of history
MAX_TENURE = 24  # M1..M24


def _day_seed(as_of: date) -> int:
    return int(as_of.strftime("%Y%m%d"))


def generate_panel(as_of: date | None = None) -> pd.DataFrame:
    """
    One row per (acquisition_month, cohort, tenure_month).

    Metrics evolve by tenure so you can chart order rate / VP over time
    and sum contribution to get LTV.
    """
    as_of = as_of or datetime.now(timezone.utc).date()
    rng = np.random.default_rng(_day_seed(as_of))
    as_of_month = pd.Timestamp(as_of).to_period("M").to_timestamp()

    rows: list[dict] = []
    for v in range(N_VINTAGES):
        acquisition_month = (as_of_month - pd.DateOffset(months=v)).strftime("%Y-%m")
        # How many tenure months this vintage has lived through (at least 1).
        max_t = min(MAX_TENURE, v + 1)

        for cohort_key, cfg in COHORTS.items():
            start = int(
                round(cfg["start_customers"] * (1 + rng.uniform(-0.08, 0.08)))
            )
            active = float(start)
            order_rate = cfg["m1_order_rate"] * (1 + rng.uniform(-0.05, 0.05))
            vp_per_order = cfg["m1_vp_per_order"] * (1 + rng.uniform(-0.05, 0.05))

            for tenure in range(1, max_t + 1):
                if tenure > 1:
                    active *= cfg["retention_decay"] * (1 + rng.uniform(-0.02, 0.02))
                    order_rate *= cfg["order_decay"] * (1 + rng.uniform(-0.015, 0.015))
                    vp_per_order *= cfg["vp_decay"] * (1 + rng.uniform(-0.01, 0.01))

                active_i = max(0, int(round(active)))
                retention = active_i / start if start else 0.0
                # Contribution per *acquired* customer this tenure month
                vp_per_acquired = retention * order_rate * vp_per_order
                orders = active_i * order_rate
                total_vp = orders * vp_per_order

                rows.append(
                    {
                        "as_of_date": as_of.isoformat(),
                        "acquisition_month": acquisition_month,
                        "cohort": cohort_key,
                        "cohort_label": cfg["label"],
                        "cohort_description": cfg["description"],
                        "tenure_month": tenure,
                        "tenure_label": f"M{tenure}",
                        "cohort_tenure_label": f"M{tenure} {cfg['label']}",
                        "starting_customers": start,
                        "active_customers": active_i,
                        "retention_rate": round(retention, 4),
                        "order_rate": round(float(order_rate), 3),
                        "vp_per_order": round(float(vp_per_order), 3),
                        "vp_per_acquired_customer": round(float(vp_per_acquired), 4),
                        "orders": round(float(orders), 1),
                        "total_vp": round(float(total_vp), 2),
                    }
                )

    return pd.DataFrame(rows)


def refresh_panel(as_of: date | None = None, force: bool = False) -> pd.DataFrame:
    as_of = as_of or datetime.now(timezone.utc).date()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if PANEL_PATH.exists() and not force:
        existing = pd.read_csv(PANEL_PATH)
        if not existing.empty and str(existing["as_of_date"].iloc[0]) == as_of.isoformat():
            return existing

    panel = generate_panel(as_of)
    panel.to_csv(PANEL_PATH, index=False)
    return panel


def load_panel() -> pd.DataFrame:
    return refresh_panel()
