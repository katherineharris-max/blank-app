# 📈 Marketing Performance Dashboard

A polished Streamlit dashboard for summarizing marketing tracker performance by
campaign and vertical.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## What it shows

- Executive KPI cards for revenue, spend, ROAS, conversions, CPA, and CTR
- Vertical-level spend, revenue, and efficiency comparisons
- Campaign-level revenue/spend bubble chart and ROAS ranking
- Funnel summary from impressions through conversions
- Insight cards that highlight strongest verticals, top campaigns, and watchlist items
- A detailed campaign table with channel, owner, status, and conversion metrics

The app ships with sample tracker data so it works immediately. Use the sidebar
CSV uploader to replace it with the real marketing tracker.

## Tracker CSV columns

Required columns:

- `campaign`
- `vertical`
- `channel`
- `spend`
- `impressions`
- `clicks`
- `leads`
- `conversions`
- `revenue`

Optional columns:

- `start_date`
- `end_date`
- `status`
- `owner`
- `objective`

Column names are normalized when uploaded, so names such as `Campaign Name` or
`Start Date` are converted to dashboard-friendly snake case.

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
