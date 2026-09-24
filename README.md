"""
Cohort LTV dashboard

Large fake panel of NC Sub / EC Sub / PAYG NC / PAYG EC over acquisition months
and tenure (M1..M24), with LTV calculated from the contribution curve and shown
in a Streamlit dashboard.

### LTV method

For each tenure month t:

    contribution(t) = retention(t) × order_rate(t) × VP_per_order(t)

LTV = sum of contribution(t) from M1 to a chosen horizon (optional monthly discount).

### How to run

```bash
pip install -r requirements.txt
python scripts/generate_data.py
streamlit run streamlit_app.py
```

### Data files (regenerate daily on app load)

| File | What it is |
|------|------------|
| `data/cohort_panel.csv` | Large time-series panel (vintage × cohort × tenure) |
| `data/cohort_ltv_summary.csv` | Calculated LTV per cohort |

On Windows, after unzipping the project, open Command Prompt in that folder, then run the commands above.
