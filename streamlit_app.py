from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class SubscriptionInputs:
    name: str
    variable_profit_per_order: float
    average_monthly_order_frequency: float


@dataclass(frozen=True)
class YearOutputs:
    label: str
    order_volume: float
    mau: float
    variable_profit: float


@dataclass(frozen=True)
class ModelOutputs:
    subscription_type: str
    year_1: YearOutputs
    year_2: YearOutputs


def calculate_year_outputs(
    label: str,
    mau: int,
    subscription_inputs: SubscriptionInputs,
) -> YearOutputs:
    """Calculate annual output metrics from monthly active students."""
    order_volume = mau * subscription_inputs.average_monthly_order_frequency * 12
    variable_profit = order_volume * subscription_inputs.variable_profit_per_order

    return YearOutputs(
        label=label,
        order_volume=order_volume,
        mau=mau,
        variable_profit=variable_profit,
    )


def calculate_model_outputs(
    subscription_inputs: SubscriptionInputs,
    students_start_year_1: int,
    students_churn_after_year_1: int,
    new_students_year_2: int,
) -> ModelOutputs:
    year_1_mau = students_start_year_1
    year_2_mau = students_start_year_1 - students_churn_after_year_1 + new_students_year_2

    return ModelOutputs(
        subscription_type=subscription_inputs.name,
        year_1=calculate_year_outputs("Year 1", year_1_mau, subscription_inputs),
        year_2=calculate_year_outputs("Year 2", year_2_mau, subscription_inputs),
    )


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_currency(value: float) -> str:
    if value < 0:
        return f"-${abs(value):,.0f}"

    return f"${value:,.0f}"


def format_currency_precise(value: float) -> str:
    if value < 0:
        return f"-${abs(value):,.2f}"

    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    return f"{value:.0%}"


def delta_percentage(base_value: float, alternative_value: float) -> str:
    if base_value == 0:
        return "n/a"

    return format_percentage((alternative_value - base_value) / base_value)


def build_output_rows(
    base_outputs: ModelOutputs,
    alternative_outputs: ModelOutputs,
) -> list[dict[str, str]]:
    metrics = [
        (
            "Order volume",
            "order_volume",
            format_number,
        ),
        ("MAU", "mau", format_number),
        (
            "Variable profit",
            "variable_profit",
            format_currency,
        ),
    ]

    rows = []
    for base_year, alternative_year in [
        (base_outputs.year_1, alternative_outputs.year_1),
        (base_outputs.year_2, alternative_outputs.year_2),
    ]:
        for metric_name, attribute_name, formatter in metrics:
            base_value = getattr(base_year, attribute_name)
            alternative_value = getattr(alternative_year, attribute_name)
            rows.append(
                {
                    "Year": base_year.label,
                    "Metric": metric_name,
                    base_outputs.subscription_type: formatter(base_value),
                    alternative_outputs.subscription_type: formatter(alternative_value),
                    "Delta": formatter(alternative_value - base_value),
                    "Delta %": delta_percentage(base_value, alternative_value),
                }
            )

    return rows


def build_subscription_input(
    label: str,
    default_variable_profit: float,
    default_order_frequency: float,
) -> SubscriptionInputs:
    st.markdown(f"**{label}**")
    variable_profit_per_order = st.number_input(
        "Variable profit per order",
        min_value=0.0,
        value=default_variable_profit,
        step=0.25,
        format="%.2f",
        key=f"{label}-variable-profit",
    )
    average_monthly_order_frequency = st.number_input(
        "Average monthly order frequency",
        min_value=0.0,
        value=default_order_frequency,
        step=0.10,
        format="%.2f",
        key=f"{label}-order-frequency",
        help="Average orders per monthly active student.",
    )

    return SubscriptionInputs(
        name=label,
        variable_profit_per_order=variable_profit_per_order,
        average_monthly_order_frequency=average_monthly_order_frequency,
    )


st.set_page_config(page_title="Student financial model", page_icon=":moneybag:")

st.title("Student financial model")
st.write(
    "Compare order volume, monthly active users, and variable profit between a "
    "base case subscription type and an alternative option."
)

st.sidebar.header("Student inputs")
students_start_year_1 = st.sidebar.number_input(
    "Number of students at start of Year 1",
    min_value=0,
    value=10_000,
    step=100,
)
students_churn_after_year_1 = st.sidebar.number_input(
    "Number of students that churn after Year 1",
    min_value=0,
    max_value=students_start_year_1,
    value=min(1_500, students_start_year_1),
    step=100,
)
new_students_year_2 = st.sidebar.number_input(
    "Number of new students in Year 2",
    min_value=0,
    value=3_000,
    step=100,
)

st.sidebar.header("Subscription type inputs")
base_column, alternative_column = st.sidebar.columns(2)

with base_column:
    base_inputs = build_subscription_input("Base case", 4.25, 1.40)

with alternative_column:
    alternative_inputs = build_subscription_input("Alternative option", 4.75, 1.60)

base_outputs = calculate_model_outputs(
    base_inputs,
    students_start_year_1,
    students_churn_after_year_1,
    new_students_year_2,
)
alternative_outputs = calculate_model_outputs(
    alternative_inputs,
    students_start_year_1,
    students_churn_after_year_1,
    new_students_year_2,
)

retained_students_year_2 = students_start_year_1 - students_churn_after_year_1
year_2_students = retained_students_year_2 + new_students_year_2

st.subheader("Student cohort")
student_col_1, student_col_2, student_col_3 = st.columns(3)
student_col_1.metric("Year 1 MAU", format_number(students_start_year_1))
student_col_2.metric("Retained students", format_number(retained_students_year_2))
student_col_3.metric("Year 2 MAU", format_number(year_2_students))

st.subheader("Outputs")

year_1_tab, year_2_tab = st.tabs(["Year 1", "Year 2"])

with year_1_tab:
    base_col, alternative_col = st.columns(2)
    with base_col:
        st.markdown(f"**{base_outputs.subscription_type}**")
        st.metric("Order volume", format_number(base_outputs.year_1.order_volume))
        st.metric("MAU", format_number(base_outputs.year_1.mau))
        st.metric("Variable profit", format_currency(base_outputs.year_1.variable_profit))
    with alternative_col:
        st.markdown(f"**{alternative_outputs.subscription_type}**")
        st.metric(
            "Order volume",
            format_number(alternative_outputs.year_1.order_volume),
            delta=format_number(
                alternative_outputs.year_1.order_volume - base_outputs.year_1.order_volume
            ),
        )
        st.metric(
            "MAU",
            format_number(alternative_outputs.year_1.mau),
            delta=format_number(alternative_outputs.year_1.mau - base_outputs.year_1.mau),
        )
        st.metric(
            "Variable profit",
            format_currency(alternative_outputs.year_1.variable_profit),
            delta=format_currency(
                alternative_outputs.year_1.variable_profit
                - base_outputs.year_1.variable_profit
            ),
        )

with year_2_tab:
    base_col, alternative_col = st.columns(2)
    with base_col:
        st.markdown(f"**{base_outputs.subscription_type}**")
        st.metric("Order volume", format_number(base_outputs.year_2.order_volume))
        st.metric("MAU", format_number(base_outputs.year_2.mau))
        st.metric("Variable profit", format_currency(base_outputs.year_2.variable_profit))
    with alternative_col:
        st.markdown(f"**{alternative_outputs.subscription_type}**")
        st.metric(
            "Order volume",
            format_number(alternative_outputs.year_2.order_volume),
            delta=format_number(
                alternative_outputs.year_2.order_volume - base_outputs.year_2.order_volume
            ),
        )
        st.metric(
            "MAU",
            format_number(alternative_outputs.year_2.mau),
            delta=format_number(alternative_outputs.year_2.mau - base_outputs.year_2.mau),
        )
        st.metric(
            "Variable profit",
            format_currency(alternative_outputs.year_2.variable_profit),
            delta=format_currency(
                alternative_outputs.year_2.variable_profit
                - base_outputs.year_2.variable_profit
            ),
        )

st.subheader("Base case vs. alternative option")
st.table(build_output_rows(base_outputs, alternative_outputs))

with st.expander("Model assumptions"):
    st.table(
        [
            {
                "Input": "Students at start of Year 1",
                "Value": format_number(students_start_year_1),
            },
            {
                "Input": "Students that churn after Year 1",
                "Value": format_number(students_churn_after_year_1),
            },
            {
                "Input": "New students in Year 2",
                "Value": format_number(new_students_year_2),
            },
            {
                "Input": "Base case variable profit per order",
                "Value": format_currency_precise(base_inputs.variable_profit_per_order),
            },
            {
                "Input": "Base case average monthly order frequency",
                "Value": f"{base_inputs.average_monthly_order_frequency:.2f}",
            },
            {
                "Input": "Alternative option variable profit per order",
                "Value": format_currency_precise(
                    alternative_inputs.variable_profit_per_order
                ),
            },
            {
                "Input": "Alternative option average monthly order frequency",
                "Value": f"{alternative_inputs.average_monthly_order_frequency:.2f}",
            },
        ]
    )

st.caption(
    "Formula: Year 1 MAU = students at start of Year 1; Year 2 MAU = Year 1 "
    "students - churn + new students; order volume = MAU x average monthly "
    "order frequency x 12; variable profit = order volume x variable profit "
    "per order."
)
