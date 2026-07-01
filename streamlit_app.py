from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Marketing Performance Dashboard",
    page_icon="📈",
    layout="wide",
)


REQUIRED_COLUMNS = {
    "campaign",
    "vertical",
    "channel",
    "spend",
    "impressions",
    "clicks",
    "leads",
    "conversions",
    "revenue",
}

COLUMN_ALIASES = {
    "campaign_name": "campaign",
    "campaign_title": "campaign",
    "business_vertical": "vertical",
    "category": "vertical",
    "marketing_channel": "channel",
    "media_channel": "channel",
    "media_spend": "spend",
    "amount_spent": "spend",
    "cost": "spend",
    "views": "impressions",
    "link_clicks": "clicks",
    "signups": "leads",
    "orders": "conversions",
    "purchases": "conversions",
    "attributed_revenue": "revenue",
    "sales": "revenue",
    "flight_start": "start_date",
    "launch_date": "start_date",
    "flight_end": "end_date",
    "end": "end_date",
    "campaign_status": "status",
    "owner_name": "owner",
    "campaign_owner": "owner",
    "goal": "objective",
}

OPTIONAL_COLUMNS = {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
    "status": "Unknown",
    "owner": "Unassigned",
    "objective": "Not specified",
}

TRACKER_ROWS = [
    {
        "campaign": "Summer Hydration Push",
        "vertical": "Grocery",
        "channel": "Paid Social",
        "objective": "Acquire high-frequency grocery shoppers",
        "owner": "Maya",
        "status": "Live",
        "start_date": "2026-05-20",
        "end_date": "2026-07-05",
        "spend": 148000,
        "impressions": 8200000,
        "clicks": 188600,
        "leads": 18750,
        "conversions": 5680,
        "revenue": 624800,
    },
    {
        "campaign": "Back-to-School Essentials",
        "vertical": "Retail",
        "channel": "Search",
        "objective": "Capture seasonal intent",
        "owner": "Noah",
        "status": "Planned",
        "start_date": "2026-07-15",
        "end_date": "2026-08-30",
        "spend": 126500,
        "impressions": 4850000,
        "clicks": 164900,
        "leads": 15520,
        "conversions": 4210,
        "revenue": 461700,
    },
    {
        "campaign": "Game Day Bundles",
        "vertical": "Restaurant",
        "channel": "Email",
        "objective": "Increase basket size from loyal customers",
        "owner": "Ari",
        "status": "Live",
        "start_date": "2026-06-01",
        "end_date": "2026-07-20",
        "spend": 52000,
        "impressions": 1350000,
        "clicks": 129400,
        "leads": 21280,
        "conversions": 7460,
        "revenue": 373000,
    },
    {
        "campaign": "Late Night Cravings",
        "vertical": "Restaurant",
        "channel": "Paid Social",
        "objective": "Grow late-night order frequency",
        "owner": "Maya",
        "status": "Live",
        "start_date": "2026-04-18",
        "end_date": "2026-07-31",
        "spend": 98000,
        "impressions": 6200000,
        "clicks": 142600,
        "leads": 17510,
        "conversions": 6210,
        "revenue": 341550,
    },
    {
        "campaign": "Family Pantry Restock",
        "vertical": "Grocery",
        "channel": "CRM",
        "objective": "Reactivate lapsed grocery buyers",
        "owner": "Leah",
        "status": "Complete",
        "start_date": "2026-03-01",
        "end_date": "2026-04-15",
        "spend": 61000,
        "impressions": 1850000,
        "clicks": 98700,
        "leads": 16880,
        "conversions": 4820,
        "revenue": 279560,
    },
    {
        "campaign": "Convenience Refill Reminders",
        "vertical": "Convenience",
        "channel": "Push",
        "objective": "Increase repeat purchase cadence",
        "owner": "Sam",
        "status": "Live",
        "start_date": "2026-05-05",
        "end_date": "2026-07-10",
        "spend": 43000,
        "impressions": 2100000,
        "clicks": 119300,
        "leads": 13640,
        "conversions": 3980,
        "revenue": 202980,
    },
    {
        "campaign": "Beauty Discovery Week",
        "vertical": "Retail",
        "channel": "Influencer",
        "objective": "Introduce premium retail partners",
        "owner": "Noah",
        "status": "Complete",
        "start_date": "2026-02-12",
        "end_date": "2026-03-05",
        "spend": 87000,
        "impressions": 3950000,
        "clicks": 77400,
        "leads": 9310,
        "conversions": 2470,
        "revenue": 212420,
    },
    {
        "campaign": "Pharmacy First Order",
        "vertical": "Pharmacy",
        "channel": "Search",
        "objective": "Convert high-intent first orders",
        "owner": "Ivy",
        "status": "Live",
        "start_date": "2026-04-01",
        "end_date": "2026-07-01",
        "spend": 112000,
        "impressions": 3600000,
        "clicks": 122400,
        "leads": 10430,
        "conversions": 3150,
        "revenue": 264600,
    },
    {
        "campaign": "Pet Care Auto-Replenish",
        "vertical": "Retail",
        "channel": "Affiliate",
        "objective": "Build recurring pet supply orders",
        "owner": "Leah",
        "status": "Planned",
        "start_date": "2026-07-01",
        "end_date": "2026-08-12",
        "spend": 69500,
        "impressions": 2750000,
        "clicks": 60500,
        "leads": 7850,
        "conversions": 2160,
        "revenue": 177120,
    },
    {
        "campaign": "Office Lunch Reset",
        "vertical": "Restaurant",
        "channel": "Search",
        "objective": "Win weekday group orders",
        "owner": "Ari",
        "status": "Complete",
        "start_date": "2026-01-08",
        "end_date": "2026-02-28",
        "spend": 75500,
        "impressions": 2920000,
        "clicks": 104900,
        "leads": 12770,
        "conversions": 3980,
        "revenue": 230840,
    },
    {
        "campaign": "Fresh Produce Guarantee",
        "vertical": "Grocery",
        "channel": "Display",
        "objective": "Improve perception of fresh selection",
        "owner": "Sam",
        "status": "Paused",
        "start_date": "2026-03-18",
        "end_date": "2026-05-10",
        "spend": 93000,
        "impressions": 7100000,
        "clicks": 92300,
        "leads": 9040,
        "conversions": 2280,
        "revenue": 143640,
    },
    {
        "campaign": "Wellness Routine Builder",
        "vertical": "Pharmacy",
        "channel": "CRM",
        "objective": "Drive supplement subscription trials",
        "owner": "Ivy",
        "status": "Complete",
        "start_date": "2026-02-01",
        "end_date": "2026-03-31",
        "spend": 48500,
        "impressions": 1420000,
        "clicks": 71100,
        "leads": 8620,
        "conversions": 2140,
        "revenue": 128400,
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(94, 92, 230, 0.18), transparent 32rem),
                radial-gradient(circle at top right, rgba(18, 184, 134, 0.14), transparent 30rem),
                linear-gradient(180deg, #f8fbff 0%, #eef3f9 100%);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #172554 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        .hero {
            padding: 2rem;
            border-radius: 28px;
            color: #ffffff;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 64, 175, 0.88)),
                url("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1400&q=80");
            background-size: cover;
            background-position: center;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
            margin-bottom: 1.25rem;
        }

        .hero h1 {
            color: #ffffff;
            font-size: clamp(2.2rem, 5vw, 4.5rem);
            letter-spacing: -0.08em;
            line-height: 0.92;
            margin: 0 0 0.75rem;
        }

        .hero p {
            color: #dbeafe;
            font-size: 1.05rem;
            max-width: 62rem;
            margin: 0;
        }

        .metric-card, .insight-card {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 22px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            padding: 1.15rem 1.2rem;
            height: 100%;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .metric-caption {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }

        .section-title {
            color: #0f172a;
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 1.5rem 0 0.75rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            color: #1e3a8a;
            background: #dbeafe;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.35rem 0.7rem;
            margin: 0 0.35rem 0.35rem 0;
        }

        .stDataFrame {
            border-radius: 18px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = (
        normalized.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    normalized = normalized.rename(columns=COLUMN_ALIASES)
    return normalized


def prepare_tracker(frame: pd.DataFrame) -> pd.DataFrame:
    tracker = normalize_columns(frame)

    for column, default in OPTIONAL_COLUMNS.items():
        if column not in tracker.columns:
            tracker[column] = default

    for column in REQUIRED_COLUMNS:
        if column not in tracker.columns:
            tracker[column] = 0 if column not in {"campaign", "vertical", "channel"} else "Unknown"

    numeric_columns = [
        "spend",
        "impressions",
        "clicks",
        "leads",
        "conversions",
        "revenue",
    ]
    for column in numeric_columns:
        tracker[column] = pd.to_numeric(tracker[column], errors="coerce").fillna(0)

    for column in ["start_date", "end_date"]:
        tracker[column] = pd.to_datetime(tracker[column], errors="coerce")

    fallback_start = tracker["start_date"].min()
    if pd.isna(fallback_start):
        fallback_start = pd.Timestamp("2026-01-01")

    tracker["start_date"] = tracker["start_date"].fillna(fallback_start)
    tracker["end_date"] = tracker["end_date"].fillna(tracker["start_date"])

    text_columns = ["campaign", "vertical", "channel", "status", "owner", "objective"]
    for column in text_columns:
        tracker[column] = tracker[column].fillna("Unknown").astype(str).str.strip()

    tracker["roas"] = tracker.apply(
        lambda row: safe_divide(row["revenue"], row["spend"]), axis=1
    )
    tracker["cpa"] = tracker.apply(
        lambda row: safe_divide(row["spend"], row["conversions"]), axis=1
    )
    tracker["ctr"] = tracker.apply(
        lambda row: safe_divide(row["clicks"], row["impressions"]), axis=1
    )
    tracker["lead_rate"] = tracker.apply(
        lambda row: safe_divide(row["leads"], row["clicks"]), axis=1
    )
    tracker["conversion_rate"] = tracker.apply(
        lambda row: safe_divide(row["conversions"], row["leads"]), axis=1
    )
    return tracker


@st.cache_data
def load_default_tracker() -> pd.DataFrame:
    return prepare_tracker(pd.DataFrame(TRACKER_ROWS))


def aggregate_performance(frame: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    summary = (
        frame.groupby(dimensions, dropna=False)[
            ["spend", "impressions", "clicks", "leads", "conversions", "revenue"]
        ]
        .sum()
        .reset_index()
    )
    summary["roas"] = summary.apply(
        lambda row: safe_divide(row["revenue"], row["spend"]), axis=1
    )
    summary["cpa"] = summary.apply(
        lambda row: safe_divide(row["spend"], row["conversions"]), axis=1
    )
    summary["ctr"] = summary.apply(
        lambda row: safe_divide(row["clicks"], row["impressions"]), axis=1
    )
    summary["lead_rate"] = summary.apply(
        lambda row: safe_divide(row["leads"], row["clicks"]), axis=1
    )
    summary["conversion_rate"] = summary.apply(
        lambda row: safe_divide(row["conversions"], row["leads"]), axis=1
    )
    return summary


def render_metric_card(label: str, value: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_sidebar(tracker: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("Dashboard controls")
    st.sidebar.caption("Upload a CSV tracker or use the built-in sample data.")

    uploaded_file = st.sidebar.file_uploader(
        "Marketing tracker CSV",
        type=["csv"],
        help=(
            "Expected columns include campaign, vertical, channel, spend, impressions, "
            "clicks, leads, conversions, and revenue."
        ),
    )

    if uploaded_file is not None:
        uploaded_tracker = normalize_columns(pd.read_csv(uploaded_file))
        missing_columns = REQUIRED_COLUMNS.difference(uploaded_tracker.columns)
        if missing_columns:
            st.sidebar.error(
                "Missing required columns: " + ", ".join(sorted(missing_columns))
            )
        else:
            tracker = prepare_tracker(uploaded_tracker)
            st.sidebar.success("Using uploaded tracker data")

    date_min = tracker["start_date"].min().date()
    date_max = tracker["end_date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Campaign flight window",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    if len(selected_dates) == 2:
        start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(
            selected_dates[1]
        )
    else:
        start_date, end_date = pd.to_datetime(date_min), pd.to_datetime(date_max)

    def multiselect_filter(label: str, column: str) -> list[str]:
        options = sorted(tracker[column].dropna().unique())
        return st.sidebar.multiselect(label, options, default=options)

    verticals = multiselect_filter("Vertical", "vertical")
    campaigns = multiselect_filter("Campaign", "campaign")
    channels = multiselect_filter("Channel", "channel")
    statuses = multiselect_filter("Status", "status")
    owners = multiselect_filter("Owner", "owner")

    filtered = tracker[
        tracker["vertical"].isin(verticals)
        & tracker["campaign"].isin(campaigns)
        & tracker["channel"].isin(channels)
        & tracker["status"].isin(statuses)
        & tracker["owner"].isin(owners)
        & (tracker["start_date"] <= end_date)
        & (tracker["end_date"] >= start_date)
    ].copy()
    return filtered


def render_hero(filtered: pd.DataFrame) -> None:
    vertical_count = filtered["vertical"].nunique()
    campaign_count = filtered["campaign"].nunique()
    st.markdown(
        f"""
        <div class="hero">
            <span class="pill">Marketing tracker dashboard</span>
            <span class="pill">{campaign_count} campaigns</span>
            <span class="pill">{vertical_count} verticals</span>
            <h1>Performance by campaign and vertical.</h1>
            <p>
                A polished readout of spend, revenue, conversion efficiency, and funnel
                health across the tracker. Use the sidebar to focus the story by flight,
                owner, channel, status, campaign, or vertical.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(filtered: pd.DataFrame) -> None:
    totals = filtered[
        ["spend", "impressions", "clicks", "leads", "conversions", "revenue"]
    ].sum()
    roas = safe_divide(totals["revenue"], totals["spend"])
    cpa = safe_divide(totals["spend"], totals["conversions"])
    ctr = safe_divide(totals["clicks"], totals["impressions"])
    conversion_rate = safe_divide(totals["conversions"], totals["leads"])

    cols = st.columns(6)
    with cols[0]:
        render_metric_card("Revenue", format_currency(totals["revenue"]), "Attributed")
    with cols[1]:
        render_metric_card("Spend", format_currency(totals["spend"]), "Media budget")
    with cols[2]:
        render_metric_card("ROAS", f"{roas:.2f}x", "Revenue / spend")
    with cols[3]:
        render_metric_card("Conversions", format_number(totals["conversions"]), "Orders")
    with cols[4]:
        render_metric_card("CPA", format_currency(cpa), "Spend / conversion")
    with cols[5]:
        render_metric_card("CTR", format_percent(ctr), "Clicks / impressions")

    st.caption(
        f"Lead conversion rate: {format_percent(conversion_rate)} · "
        f"Total leads: {format_number(totals['leads'])} · "
        f"Impressions: {format_number(totals['impressions'])}"
    )


def render_vertical_section(filtered: pd.DataFrame) -> pd.DataFrame:
    st.markdown('<div class="section-title">Vertical performance</div>', unsafe_allow_html=True)
    vertical_summary = aggregate_performance(filtered, ["vertical"]).sort_values(
        "revenue", ascending=False
    )

    vertical_value = vertical_summary.melt(
        id_vars=["vertical"],
        value_vars=["spend", "revenue"],
        var_name="metric",
        value_name="amount",
    )

    revenue_spend_chart = (
        alt.Chart(vertical_value)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("vertical:N", title=None, sort="-y"),
            y=alt.Y("amount:Q", title="Amount", axis=alt.Axis(format="$,.0f")),
            color=alt.Color(
                "metric:N",
                title=None,
                scale=alt.Scale(range=["#2563eb", "#14b8a6"]),
            ),
            xOffset="metric:N",
            tooltip=[
                alt.Tooltip("vertical:N", title="Vertical"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("amount:Q", title="Amount", format="$,.0f"),
            ],
        )
        .properties(height=330)
    )

    roas_chart = (
        alt.Chart(vertical_summary)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("vertical:N", title=None, sort="-y"),
            y=alt.Y("roas:Q", title="ROAS"),
            color=alt.Color(
                "roas:Q",
                title="ROAS",
                scale=alt.Scale(scheme="tealblues"),
            ),
            tooltip=[
                alt.Tooltip("vertical:N", title="Vertical"),
                alt.Tooltip("roas:Q", title="ROAS", format=".2f"),
                alt.Tooltip("cpa:Q", title="CPA", format="$,.0f"),
                alt.Tooltip("conversions:Q", title="Conversions", format=",.0f"),
            ],
        )
        .properties(height=330)
    )

    col_a, col_b = st.columns([1.15, 1])
    with col_a:
        st.altair_chart(revenue_spend_chart, use_container_width=True)
    with col_b:
        st.altair_chart(roas_chart, use_container_width=True)

    return vertical_summary


def render_campaign_section(filtered: pd.DataFrame) -> pd.DataFrame:
    st.markdown('<div class="section-title">Campaign performance</div>', unsafe_allow_html=True)
    campaign_summary = aggregate_performance(
        filtered, ["campaign", "vertical", "channel", "objective", "status", "owner"]
    ).sort_values("revenue", ascending=False)

    scatter = (
        alt.Chart(campaign_summary)
        .mark_circle(opacity=0.86, stroke="#ffffff", strokeWidth=1.4)
        .encode(
            x=alt.X("spend:Q", title="Spend", axis=alt.Axis(format="$,.0f")),
            y=alt.Y("revenue:Q", title="Revenue", axis=alt.Axis(format="$,.0f")),
            size=alt.Size(
                "conversions:Q",
                title="Conversions",
                scale=alt.Scale(range=[120, 1200]),
            ),
            color=alt.Color("vertical:N", title="Vertical"),
            tooltip=[
                alt.Tooltip("campaign:N", title="Campaign"),
                alt.Tooltip("vertical:N", title="Vertical"),
                alt.Tooltip("channel:N", title="Channel"),
                alt.Tooltip("status:N", title="Status"),
                alt.Tooltip("owner:N", title="Owner"),
                alt.Tooltip("spend:Q", title="Spend", format="$,.0f"),
                alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
                alt.Tooltip("roas:Q", title="ROAS", format=".2f"),
                alt.Tooltip("cpa:Q", title="CPA", format="$,.0f"),
            ],
        )
        .properties(height=430)
        .interactive()
    )

    ranking = (
        alt.Chart(campaign_summary.head(10))
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("roas:Q", title="ROAS"),
            y=alt.Y("campaign:N", title=None, sort="-x"),
            color=alt.Color("vertical:N", title="Vertical"),
            tooltip=[
                alt.Tooltip("campaign:N", title="Campaign"),
                alt.Tooltip("roas:Q", title="ROAS", format=".2f"),
                alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
                alt.Tooltip("spend:Q", title="Spend", format="$,.0f"),
            ],
        )
        .properties(height=430)
    )

    col_a, col_b = st.columns([1.1, 1])
    with col_a:
        st.altair_chart(scatter, use_container_width=True)
    with col_b:
        st.altair_chart(ranking, use_container_width=True)

    return campaign_summary


def render_funnel(filtered: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Funnel health</div>', unsafe_allow_html=True)
    totals = filtered[["impressions", "clicks", "leads", "conversions"]].sum()
    funnel = pd.DataFrame(
        {
            "stage": ["Impressions", "Clicks", "Leads", "Conversions"],
            "volume": [
                totals["impressions"],
                totals["clicks"],
                totals["leads"],
                totals["conversions"],
            ],
        }
    )
    funnel["stage"] = pd.Categorical(
        funnel["stage"],
        categories=["Impressions", "Clicks", "Leads", "Conversions"],
        ordered=True,
    )

    chart = (
        alt.Chart(funnel)
        .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
        .encode(
            x=alt.X("volume:Q", title="Volume"),
            y=alt.Y("stage:N", title=None, sort=["Impressions", "Clicks", "Leads", "Conversions"]),
            color=alt.Color(
                "stage:N",
                title=None,
                scale=alt.Scale(range=["#1d4ed8", "#2563eb", "#0d9488", "#14b8a6"]),
            ),
            tooltip=[
                alt.Tooltip("stage:N", title="Stage"),
                alt.Tooltip("volume:Q", title="Volume", format=",.0f"),
            ],
        )
        .properties(height=250)
    )
    st.altair_chart(chart, use_container_width=True)


def render_insights(
    vertical_summary: pd.DataFrame, campaign_summary: pd.DataFrame
) -> None:
    st.markdown('<div class="section-title">Executive readout</div>', unsafe_allow_html=True)

    top_vertical = vertical_summary.sort_values("roas", ascending=False).iloc[0]
    top_campaign = campaign_summary.sort_values("roas", ascending=False).iloc[0]
    biggest_campaign = campaign_summary.sort_values("revenue", ascending=False).iloc[0]
    attention_campaign = campaign_summary[
        campaign_summary["spend"] >= campaign_summary["spend"].median()
    ].sort_values("roas", ascending=True).iloc[0]

    cols = st.columns(4)
    with cols[0]:
        render_insight_card(
            "Best vertical efficiency",
            str(top_vertical["vertical"]),
            f"{top_vertical['roas']:.2f}x ROAS on {format_currency(top_vertical['spend'])} spend",
        )
    with cols[1]:
        render_insight_card(
            "Top campaign ROAS",
            str(top_campaign["campaign"]),
            f"{top_campaign['roas']:.2f}x ROAS in {top_campaign['vertical']}",
        )
    with cols[2]:
        render_insight_card(
            "Largest revenue driver",
            str(biggest_campaign["campaign"]),
            f"{format_currency(biggest_campaign['revenue'])} attributed revenue",
        )
    with cols[3]:
        render_insight_card(
            "Watchlist",
            str(attention_campaign["campaign"]),
            f"{attention_campaign['roas']:.2f}x ROAS with {format_currency(attention_campaign['spend'])} spend",
        )


def render_tracker_table(campaign_summary: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Detailed tracker summary</div>', unsafe_allow_html=True)
    table = campaign_summary[
        [
            "campaign",
            "vertical",
            "channel",
            "objective",
            "status",
            "owner",
            "spend",
            "revenue",
            "roas",
            "conversions",
            "cpa",
            "ctr",
            "lead_rate",
            "conversion_rate",
        ]
    ].copy()
    table["ctr_percent"] = table["ctr"] * 100
    table["lead_rate_percent"] = table["lead_rate"] * 100
    table["conversion_rate_percent"] = table["conversion_rate"] * 100
    table = table.drop(columns=["ctr", "lead_rate", "conversion_rate"])
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "campaign": "Campaign",
            "vertical": "Vertical",
            "channel": "Channel",
            "objective": "Objective",
            "status": "Status",
            "owner": "Owner",
            "spend": st.column_config.NumberColumn("Spend", format="$%d"),
            "revenue": st.column_config.NumberColumn("Revenue", format="$%d"),
            "roas": st.column_config.NumberColumn("ROAS", format="%.2fx"),
            "conversions": st.column_config.NumberColumn("Conversions", format="%d"),
            "cpa": st.column_config.NumberColumn("CPA", format="$%d"),
            "ctr_percent": st.column_config.ProgressColumn(
                "CTR", format="%.1f%%", min_value=0, max_value=10
            ),
            "lead_rate_percent": st.column_config.ProgressColumn(
                "Lead Rate", format="%.1f%%", min_value=0, max_value=25
            ),
            "conversion_rate_percent": st.column_config.ProgressColumn(
                "Lead-to-Conversion", format="%.1f%%", min_value=0, max_value=45
            ),
        },
    )


def main() -> None:
    inject_styles()
    tracker = load_default_tracker()
    filtered = build_sidebar(tracker)

    if filtered.empty:
        st.warning("No campaigns match the selected filters.")
        return

    render_hero(filtered)
    render_kpis(filtered)
    vertical_summary = render_vertical_section(filtered)
    campaign_summary = render_campaign_section(filtered)
    render_funnel(filtered)
    render_insights(vertical_summary, campaign_summary)
    render_tracker_table(campaign_summary)


if __name__ == "__main__":
    main()
