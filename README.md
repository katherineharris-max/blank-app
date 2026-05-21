# Student financial model

A Streamlit app that compares a base case against an alternative option for a
student-focused financial model.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## Model

The primary input is the number of students. The app calculates these outputs
for both scenarios:

- Order volume
- Monthly active users (MAU)
- Variable profit

The model uses scenario assumptions for MAU rate, orders per MAU, and variable
profit per order:

```text
MAU = students x MAU rate
Order volume = MAU x orders per MAU
Variable profit = order volume x variable profit per order
```

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
