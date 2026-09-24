"""Customer cohort LTV dashboard — editable assumptions + forward Cx forecast."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from cohort_data import load_cohort_data, refresh_dataset  # noqa: E402

st.set_page_config(
    page_title="Cohort LTV Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Cohort LTV & investment dashboard")
st.caption(
    "Model lifetime value (LTV), variable profit (VP), order frequency, and tenure "
    "by customer cohort. Edit assumptions to forecast future customers and compare "
    "investment scenarios. Fake data regenerates once per calendar day."
)


@st.cache_data(ttl=60 * 60)
def get_data(force: bool = False) -> pd.DataFrame:
    return refresh_dataset(force=force) if force else load_cohort_data()


with st.sidebar:
    st.header("Controls")
    if st.button("Refresh today's data", help="Regenerate the fake daily snapshot"):
        st.cache_data.clear()
        get_data(force=True)
        st.rerun()

    horizon = st.slider("Forecast horizon (months)", 1, 24, 12)
    st.divider()
    st.markdown(
        "**How to use**\n\n"
        "1. Review baseline metrics from today's fake dataset.\n"
        "2. Tweak LTV, VP, frequency, tenure, or acquisition in the table.\n"
        "3. Read the forecast and scenario totals below."
    )

df = get_data().copy()
as_of = df["as_of_date"].iloc[0]
st.info(f"Dataset as of **{as_of}** · linked file: `data/cohort_metrics.csv`")

# --- Baseline snapshot ---
st.subheader("1. Baseline cohort metrics")
baseline_view = df[
    [
        "cohort_label",
        "customers",
        "ltv",
        "vp",
        "avg_order_frequency",
        "avg_tenure_months",
        "monthly_acquisition",
    ]
].rename(
    columns={
        "cohort_label": "Cohort",
        "customers": "Customers",
        "ltv": "LTV ($)",
        "vp": "VP ($)",
        "avg_order_frequency": "Avg orders / month",
        "avg_tenure_months": "Avg tenure (months)",
        "monthly_acquisition": "New Cx / month",
    }
)
st.dataframe(baseline_view, use_container_width=True, hide_index=True)

# --- Editable assumptions ---
st.subheader("2. Editable assumptions (what-if)")
st.write(
    "Change any value. Forecasts update immediately. "
    "VP = variable profit per customer (contribution after variable costs)."
)

edit_seed = df[
    [
        "cohort",
        "cohort_label",
        "customers",
        "ltv",
        "vp",
        "avg_order_frequency",
        "avg_tenure_months",
        "monthly_acquisition",
    ]
].copy()

edited = st.data_editor(
    edit_seed,
    hide_index=True,
    use_container_width=True,
    disabled=["cohort", "cohort_label"],
    column_config={
        "cohort": None,
        "cohort_label": st.column_config.TextColumn("Cohort", width="medium"),
        "customers": st.column_config.NumberColumn("Customers", min_value=0, step=100),
        "ltv": st.column_config.NumberColumn("LTV ($)", min_value=0.0, format="%.2f"),
        "vp": st.column_config.NumberColumn("VP ($)", min_value=0.0, format="%.2f"),
        "avg_order_frequency": st.column_config.NumberColumn(
            "Avg orders / month", min_value=0.0, format="%.2f"
        ),
        "avg_tenure_months": st.column_config.NumberColumn(
            "Avg tenure (months)", min_value=0.0, format="%.2f"
        ),
        "monthly_acquisition": st.column_config.NumberColumn(
            "New Cx / month", min_value=0, step=50
        ),
    },
    key="assumption_editor",
)

assumptions = edited.copy()
assumptions["portfolio_ltv"] = assumptions["customers"] * assumptions["ltv"]
assumptions["portfolio_vp"] = assumptions["customers"] * assumptions["vp"]
assumptions["implied_orders_per_cx"] = (
    assumptions["avg_order_frequency"] * assumptions["avg_tenure_months"]
)

# --- KPI row ---
st.subheader("3. Portfolio snapshot (from your assumptions)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total customers", f"{int(assumptions['customers'].sum()):,}")
c2.metric("Portfolio LTV", f"${assumptions['portfolio_ltv'].sum():,.0f}")
c3.metric("Portfolio VP", f"${assumptions['portfolio_vp'].sum():,.0f}")
weighted_ltv = (
    assumptions["portfolio_ltv"].sum() / assumptions["customers"].sum()
    if assumptions["customers"].sum()
    else 0
)
c4.metric("Blended LTV / Cx", f"${weighted_ltv:,.2f}")

# --- Forecast ---
st.subheader(f"4. Forward customer forecast ({horizon} months)")
st.write(
    "Simple model: each month adds *New Cx / month* for new cohorts; "
    "existing cohorts hold base size (no churn in this demo). "
    "New customers contribute LTV and VP at your edited rates."
)

months = list(range(1, horizon + 1))
forecast_rows = []
for _, row in assumptions.iterrows():
    base_cx = float(row["customers"])
    acq = float(row["monthly_acquisition"])
    for m in months:
        # New cohorts grow with acquisition; existing stay flat + optional residual acq.
        cx = base_cx + acq * m
        forecast_rows.append(
            {
                "month": m,
                "cohort": row["cohort_label"],
                "customers": cx,
                "cumulative_ltv": cx * float(row["ltv"]),
                "cumulative_vp": cx * float(row["vp"]),
                "monthly_orders": cx * float(row["avg_order_frequency"]),
            }
        )

forecast = pd.DataFrame(forecast_rows)

chart_cx = forecast.pivot(index="month", columns="cohort", values="customers")
chart_vp = forecast.pivot(index="month", columns="cohort", values="cumulative_vp")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Customers by cohort**")
    st.line_chart(chart_cx)
with col_b:
    st.markdown("**Cumulative VP by cohort**")
    st.line_chart(chart_vp)

end_month = forecast[forecast["month"] == horizon]
st.markdown(f"**Month {horizon} totals**")
t1, t2, t3 = st.columns(3)
t1.metric("Projected customers", f"{int(end_month['customers'].sum()):,}")
t2.metric("Projected portfolio LTV", f"${end_month['cumulative_ltv'].sum():,.0f}")
t3.metric("Projected portfolio VP", f"${end_month['cumulative_vp'].sum():,.0f}")

# --- Investment helper ---
st.subheader("5. Investment decision helper")
st.write(
    "Rank cohorts by VP per customer and LTV per order-month to see where "
    "incremental spend is most efficient under your assumptions."
)

helper = assumptions.copy()
helper["vp_per_cx"] = helper["vp"]
helper["ltv_per_order_month"] = helper.apply(
    lambda r: (r["ltv"] / r["implied_orders_per_cx"])
    if r["implied_orders_per_cx"]
    else 0.0,
    axis=1,
)
helper["acq_efficiency_vp"] = helper.apply(
    lambda r: (r["vp"] / max(r["monthly_acquisition"], 1))
    if r["monthly_acquisition"]
    else None,
    axis=1,
)

rank = helper[
    [
        "cohort_label",
        "vp_per_cx",
        "ltv",
        "ltv_per_order_month",
        "monthly_acquisition",
        "acq_efficiency_vp",
    ]
].rename(
    columns={
        "cohort_label": "Cohort",
        "vp_per_cx": "VP / Cx ($)",
        "ltv": "LTV ($)",
        "ltv_per_order_month": "LTV / order-month ($)",
        "monthly_acquisition": "New Cx / month",
        "acq_efficiency_vp": "VP per acquired Cx / monthly acq rate",
    }
).sort_values("VP / Cx ($)", ascending=False)

st.dataframe(
    rank,
    use_container_width=True,
    hide_index=True,
    column_config={
        "VP / Cx ($)": st.column_config.NumberColumn(format="%.2f"),
        "LTV ($)": st.column_config.NumberColumn(format="%.2f"),
        "LTV / order-month ($)": st.column_config.NumberColumn(format="%.2f"),
        "VP per acquired Cx / monthly acq rate": st.column_config.NumberColumn(
            format="%.4f"
        ),
    },
)

best = rank.iloc[0]["Cohort"]
st.success(
    f"Under current assumptions, **{best}** has the highest VP per customer — "
    f"a natural place to test incremental investment first."
)

with st.expander("How the daily fake data refresh works"):
    st.markdown(
        """
1. On load, the app calls `src/cohort_data.py`.
2. If `data/cohort_metrics.csv` is missing or dated before today, it regenerates
   four cohort rows with light random noise around fixed baselines.
3. The seed is the calendar date, so everyone sees the same numbers on a given day.
4. Use **Refresh today's data** in the sidebar to force a rewrite.
5. Later, swap `load_cohort_data()` for a real warehouse / API pull — keep the same columns.
        """
    )
