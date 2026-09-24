"""
LTV from cohort tenure curves.

Recommended method (implemented here)
-------------------------------------
For each acquisition vintage and cohort, build a monthly contribution curve:

    vp_per_acquired_customer(t) = retention(t) × order_rate(t) × vp_per_order(t)

Then:

    observed_LTV  = sum of vp_per_acquired_customer from M1..last observed month
    projected_LTV = observed_LTV + sum of forecasted months to a horizon

Forecast for unobserved / incomplete tenure months uses the *average* maturity
curve across vintages that have reached that tenure (with optional monthly
discount for time value of money).

Why this method
---------------
- Matches how marketplace / subscription teams usually think: follow a cohort
  month by month and add up contribution.
- Separates behaviour (retention, order rate) from monetisation (VP / order).
- Easy to stress-test: edit decay, discount, or horizon in the dashboard.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from cohort_panel import SUMMARY_PATH

DEFAULT_HORIZON = 24
DEFAULT_MONTHLY_DISCOUNT = 0.0  # e.g. 0.01 ≈ 1% per month


def average_tenure_curve(panel: pd.DataFrame) -> pd.DataFrame:
    """Mean contribution / order rate / VP by cohort × tenure across vintages."""
    grouped = (
        panel.groupby(["cohort", "cohort_label", "tenure_month", "tenure_label"], as_index=False)
        .agg(
            vp_per_acquired_customer=("vp_per_acquired_customer", "mean"),
            order_rate=("order_rate", "mean"),
            vp_per_order=("vp_per_order", "mean"),
            retention_rate=("retention_rate", "mean"),
            n_vintages=("acquisition_month", "nunique"),
            avg_starting_customers=("starting_customers", "mean"),
        )
        .sort_values(["cohort", "tenure_month"])
    )
    return grouped


def _discount_factors(n: int, monthly_discount: float) -> np.ndarray:
    if monthly_discount <= 0:
        return np.ones(n)
    t = np.arange(1, n + 1)
    return 1.0 / np.power(1.0 + monthly_discount, t)


def calculate_cohort_ltv(
    panel: pd.DataFrame,
    horizon_months: int = DEFAULT_HORIZON,
    monthly_discount: float = DEFAULT_MONTHLY_DISCOUNT,
) -> pd.DataFrame:
    """
    Return one row per cohort with observed + projected LTV and curve diagnostics.
    """
    curve = average_tenure_curve(panel)
    rows = []

    for cohort, g in curve.groupby("cohort", sort=False):
        g = g.sort_values("tenure_month")
        label = g["cohort_label"].iloc[0]
        max_obs = int(g["tenure_month"].max())
        horizon = max(horizon_months, max_obs)

        # Build contribution series to horizon; fill missing tenures by
        # decaying the last observed point (simple, transparent projection).
        contrib = {
            int(r.tenure_month): float(r.vp_per_acquired_customer) for r in g.itertuples()
        }
        last = contrib[max_obs]
        series = []
        for t in range(1, horizon + 1):
            if t in contrib:
                series.append(contrib[t])
                last = contrib[t]
            else:
                # Mild decay projection beyond observed curve
                last *= 0.95
                series.append(last)

        series_arr = np.array(series, dtype=float)
        discounts = _discount_factors(len(series_arr), monthly_discount)
        discounted = series_arr * discounts

        observed = float(discounted[:max_obs].sum())
        projected = float(discounted.sum())

        rows.append(
            {
                "cohort": cohort,
                "cohort_label": label,
                "ltv_observed": round(observed, 2),
                "ltv_projected": round(projected, 2),
                "horizon_months": horizon,
                "monthly_discount": monthly_discount,
                "months_observed": max_obs,
                "avg_m1_order_rate": round(float(g.loc[g["tenure_month"] == 1, "order_rate"].iloc[0]), 3),
                "avg_m1_vp_per_order": round(
                    float(g.loc[g["tenure_month"] == 1, "vp_per_order"].iloc[0]), 3
                ),
                "avg_starting_customers": int(round(g["avg_starting_customers"].mean())),
            }
        )

    summary = pd.DataFrame(rows).sort_values("ltv_projected", ascending=False)
    return summary


def vintage_ltv_to_date(panel: pd.DataFrame) -> pd.DataFrame:
    """Cumulative LTV realised so far for each acquisition vintage × cohort."""
    p = panel.sort_values(["cohort", "acquisition_month", "tenure_month"]).copy()
    p["cumulative_ltv"] = p.groupby(["cohort", "acquisition_month"])[
        "vp_per_acquired_customer"
    ].cumsum()
    latest = p.groupby(["cohort", "cohort_label", "acquisition_month"], as_index=False).agg(
        months_observed=("tenure_month", "max"),
        ltv_to_date=("cumulative_ltv", "max"),
        starting_customers=("starting_customers", "first"),
    )
    return latest


def write_summary(summary: pd.DataFrame) -> Path:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_PATH, index=False)
    return SUMMARY_PATH
