# Student financial model

A Streamlit app that compares a base case against an alternative option for a
student-focused financial model.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## Model

The app calculates these outputs for the base case subscription type and the
alternative option:

- Order volume
- Monthly active users (MAU)
- Variable profit

Inputs:

- Variable profit per subscription type
- Number of students at start of Year 1
- Number of students that churn after Year 1
- Number of new students in Year 2
- Average order frequency per subscription type

The model treats each student count as monthly active users for the year and
uses the subscription type assumptions to calculate annual order volume and
variable profit:

```text
Year 1 MAU = students at start of Year 1
Year 2 MAU = Year 1 students - churn after Year 1 + new students in Year 2
Order volume = MAU x average monthly order frequency x 12
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
