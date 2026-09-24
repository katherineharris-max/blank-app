"""Customer cohort LTV dashboard — tenure curves, calculated LTV, forecasts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from cohort_panel import load_panel, refresh_panel  # noqa: E402
from ltv import (  # noqa: E402
    average_tenure_curve,
    calculate_cohort_ltv,
    vintage_ltv_to_date,
    write_summary,
)

st.set_page_config(
    page_title="Cohort LTV Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Cohort LTV over time")
st.caption(
    "Fake monthly panel for **NC Sub**, **EC Sub**, **PAYG NC**, and **PAYG EC**. "
    "Order rate and VP evolve by tenure (M1, M2, …). LTV is calculated from those "
    "curves and feeds the forecast below."
)


@st.cache_data(ttl=60 * 60)
def get_panel(force: bool = False) -> pd.DataFrame:
    return refresh_panel(force=force) if force else load_panel()


with st.sidebar:
    st.header("Controls")
    if st.button("Refresh today's data"):
        st.cache_data.clear()
        get_panel(force=True)
        st.rerun()

    horizon = st.slider("LTV / forecast horizon (months)", 6, 36, 24)
    monthly_discount = st.slider(
        "Monthly discount rate",
        min_value=0.0,
        max_value=0.05,
        value=0.0,
        step=0.005,
        help="0 = no discount. 0.01 ≈ 1% per month time value of money.",
    )
    st.divider()
    st.markdown(
        "**LTV formula**\n\n"
        "`contribution(t) = retention × order rate × VP / order`\n\n"
        "`LTV = sum of contribution from M1 → horizon`\n\n"
        "Edit the curve multipliers below to stress-test investment cases."
    )

panel = get_panel().copy()
as_of = panel["as_of_date"].iloc[0]
st.info(
    f"Dataset as of **{as_of}** · **{len(panel):,}** rows · "
    f"`data/cohort_panel.csv` (refreshes once per day)"
)

# --- Calculated LTV ---
summary = calculate_cohort_ltv(
    panel, horizon_months=horizon, monthly_discount=monthly_discount
)
write_summary(summary)

st.subheader("1. Calculated LTV by cohort")
st.write(
    "Observed = sum of the average tenure curve so far. "
    "Projected = same curve extended to your horizon (with optional discount)."
)

ltv_view = summary[
    [
        "cohort_label",
        "ltv_observed",
        "ltv_projected",
        "avg_m1_order_rate",
        "avg_m1_vp_per_order",
        "avg_starting_customers",
        "months_observed",
    ]
].rename(
    columns={
        "cohort_label": "Cohort",
        "ltv_observed": "LTV observed ($)",
        "ltv_projected": "LTV projected ($)",
        "avg_m1_order_rate": "M1 order rate",
        "avg_m1_vp_per_order": "M1 VP / order ($)",
        "avg_starting_customers": "Avg starting Cx / vintage",
        "months_observed": "Months in curve",
    }
)
st.dataframe(ltv_view, use_container_width=True, hide_index=True)

c1, c2, c3, c4 = st.columns(4)
for col, (_, row) in zip((c1, c2, c3, c4), summary.iterrows()):
    col.metric(row["cohort_label"], f"${row['ltv_projected']:,.0f}", help="Projected LTV")

# --- What-if multipliers ---
st.subheader("2. Stress-test the curve (multipliers)")
st.write(
    "Change these to model better/worse economics. "
    "1.0 = baseline from the fake data. 1.1 = +10%."
)

mult_cols = st.columns(4)
multipliers = {}
for col, (_, row) in zip(mult_cols, summary.iterrows()):
    with col:
        multipliers[row["cohort"]] = {
            "label": row["cohort_label"],
            "order": st.number_input(
                f"{row['cohort_label']} order-rate ×",
                min_value=0.5,
                max_value=1.5,
                value=1.0,
                step=0.05,
                key=f"ord_{row['cohort']}",
            ),
            "vp": st.number_input(
                f"{row['cohort_label']} VP/order ×",
                min_value=0.5,
                max_value=1.5,
                value=1.0,
                step=0.05,
                key=f"vp_{row['cohort']}",
            ),
            "retention": st.number_input(
                f"{row['cohort_label']} retention ×",
                min_value=0.5,
                max_value=1.5,
                value=1.0,
                step=0.05,
                key=f"ret_{row['cohort']}",
            ),
        }

stressed = panel.copy()
for cohort, m in multipliers.items():
    mask = stressed["cohort"] == cohort
    stressed.loc[mask, "order_rate"] *= m["order"]
    stressed.loc[mask, "vp_per_order"] *= m["vp"]
    stressed.loc[mask, "retention_rate"] = (
        stressed.loc[mask, "retention_rate"] * m["retention"]
    ).clip(upper=1.0)
    stressed.loc[mask, "vp_per_acquired_customer"] = (
        stressed.loc[mask, "retention_rate"]
        * stressed.loc[mask, "order_rate"]
        * stressed.loc[mask, "vp_per_order"]
    )

stressed_summary = calculate_cohort_ltv(
    stressed, horizon_months=horizon, monthly_discount=monthly_discount
)

compare = summary[["cohort", "cohort_label", "ltv_projected"]].merge(
    stressed_summary[["cohort", "ltv_projected"]],
    on="cohort",
    suffixes=("_base", "_stressed"),
)
compare["delta"] = compare["ltv_projected_stressed"] - compare["ltv_projected_base"]
st.dataframe(
    compare.rename(
        columns={
            "cohort_label": "Cohort",
            "ltv_projected_base": "Base LTV ($)",
            "ltv_projected_stressed": "Stressed LTV ($)",
            "delta": "Change ($)",
        }
    )[["Cohort", "Base LTV ($)", "Stressed LTV ($)", "Change ($)"]],
    use_container_width=True,
    hide_index=True,
)

# --- Curves over tenure ---
st.subheader("3. Behaviour over tenure (average across vintages)")
curve = average_tenure_curve(stressed)

tab1, tab2, tab3 = st.tabs(["Order rate", "VP per acquired Cx", "Retention"])
with tab1:
    st.line_chart(
        curve.pivot(index="tenure_month", columns="cohort_label", values="order_rate")
    )
with tab2:
    st.line_chart(
        curve.pivot(
            index="tenure_month",
            columns="cohort_label",
            values="vp_per_acquired_customer",
        )
    )
with tab3:
    st.line_chart(
        curve.pivot(index="tenure_month", columns="cohort_label", values="retention_rate")
    )

# --- Vintage LTV to date ---
st.subheader("4. LTV to date by acquisition month")
vintages = vintage_ltv_to_date(stressed)
st.line_chart(
    vintages.pivot(index="acquisition_month", columns="cohort_label", values="ltv_to_date")
)

# --- Investment / forecast helper ---
st.subheader("5. Simple acquisition forecast")
st.write(
    "Uses projected (stressed) LTV × assumed new customers per month "
    "to size portfolio value over your horizon."
)

acq = {}
acq_cols = st.columns(4)
defaults = {"nc_sub": 4200, "ec_sub": 500, "payg_nc": 9500, "payg_ec": 800}
for col, (_, row) in zip(acq_cols, stressed_summary.iterrows()):
    with col:
        acq[row["cohort"]] = st.number_input(
            f"New {row['cohort_label']} / month",
            min_value=0,
            value=int(defaults.get(row["cohort"], 1000)),
            step=100,
            key=f"acq_{row['cohort']}",
        )

forecast_rows = []
ltv_map = {
    r.cohort: r.ltv_projected for r in stressed_summary.itertuples()
}
for m in range(1, horizon + 1):
    for cohort, monthly in acq.items():
        forecast_rows.append(
            {
                "month": m,
                "cohort": multipliers[cohort]["label"],
                "customers_acquired_cum": monthly * m,
                "portfolio_ltv": monthly * m * ltv_map[cohort],
            }
        )
forecast = pd.DataFrame(forecast_rows)

f1, f2 = st.columns(2)
with f1:
    st.markdown("**Cumulative customers acquired**")
    st.line_chart(
        forecast.pivot(index="month", columns="cohort", values="customers_acquired_cum")
    )
with f2:
    st.markdown("**Cumulative portfolio LTV**")
    st.line_chart(
        forecast.pivot(index="month", columns="cohort", values="portfolio_ltv")
    )

end = forecast[forecast["month"] == horizon]
t1, t2 = st.columns(2)
t1.metric("Customers acquired by horizon", f"{int(end['customers_acquired_cum'].sum()):,}")
t2.metric("Portfolio LTV by horizon", f"${end['portfolio_ltv'].sum():,.0f}")

best = compare.sort_values("ltv_projected_stressed", ascending=False).iloc[0]
st.success(
    f"Under current assumptions, **{best['cohort_label']}** has the highest stressed LTV "
    f"(${best['ltv_projected_stressed']:,.0f}) — strongest candidate for incremental investment."
)

with st.expander("How the data & LTV calculation work"):
    st.markdown(
        """
**Panel** (`data/cohort_panel.csv`): for each of the last 24 acquisition months,
each cohort (NC Sub, EC Sub, PAYG NC, PAYG EC), and each tenure month M1…M24,
we store retention, order rate, VP per order, and contribution per acquired customer.

**LTV**: average those contribution curves across vintages, then sum from M1 to your
horizon. Optional monthly discount turns this into a present-value LTV.

**Daily refresh**: opening the app (or clicking the sidebar button) regenerates the
fake panel when the calendar date changes.
        """
    )
