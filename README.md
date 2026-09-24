# Cohort LTV dashboard

Streamlit dashboard that models customer **LTV**, **VP** (variable profit), average order frequency, and average tenure for four cohorts:

- New subscriber
- Existing subscriber
- New PAYG
- Existing PAYG

Fake metrics live in `data/cohort_metrics.csv` and regenerate once per calendar day (seeded by date). Edit assumptions in the UI to forecast customers and compare investment scenarios.

### How to run

```bash
pip install -r requirements.txt
python scripts/generate_data.py   # optional; app also refreshes on load
streamlit run streamlit_app.py
```

### Daily refresh

- Automatic: opening the app rewrites the CSV when `as_of_date` is not today.
- Manual: sidebar **Refresh today's data**, or `python scripts/generate_data.py`.
- Production: replace `src/cohort_data.py` load path with your warehouse query; keep the same column names.
