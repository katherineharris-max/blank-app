from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class ScenarioAssumptions:
    name: str
    mau_rate: float
    orders_per_mau: float
    variable_profit_per_order: float


@dataclass(frozen=True)
class ScenarioOutputs:
    order_volume: float
    mau: float
    variable_profit: float


BASE_CASE = ScenarioAssumptions(
    name="Base case",
    mau_rate=0.35,
    orders_per_mau=1.40,
    variable_profit_per_order=4.25,
)

ALTERNATIVE_OPTION = ScenarioAssumptions(
    name="Alternative option",
    mau_rate=0.42,
    orders_per_mau=1.60,
    variable_profit_per_order=4.75,
)


def calculate_outputs(students: int, assumptions: ScenarioAssumptions) -> ScenarioOutputs:
    """Calculate volume, MAU, and variable profit for one scenario."""
    mau = students * assumptions.mau_rate
    order_volume = mau * assumptions.orders_per_mau
    variable_profit = order_volume * assumptions.variable_profit_per_order

    return ScenarioOutputs(
        order_volume=order_volume,
        mau=mau,
        variable_profit=variable_profit,
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
    base_outputs: ScenarioOutputs,
    alternative_outputs: ScenarioOutputs,
) -> list[dict[str, str]]:
    metrics = [
        (
            "Order volume",
            base_outputs.order_volume,
            alternative_outputs.order_volume,
            format_number,
        ),
        ("MAU", base_outputs.mau, alternative_outputs.mau, format_number),
        (
            "Variable profit",
            base_outputs.variable_profit,
            alternative_outputs.variable_profit,
            format_currency,
        ),
    ]

    rows = []
    for metric_name, base_value, alternative_value, formatter in metrics:
        rows.append(
            {
                "Metric": metric_name,
                "Base case": formatter(base_value),
                "Alternative option": formatter(alternative_value),
                "Delta": formatter(alternative_value - base_value),
                "Delta %": delta_percentage(base_value, alternative_value),
            }
        )

    return rows


st.set_page_config(page_title="Student financial model", page_icon="💸")

st.title("Student financial model")
st.write(
    "Compare order volume, monthly active users, and variable profit between a "
    "base case and an alternative option."
)

students = st.number_input(
    "# of students",
    min_value=0,
    value=10_000,
    step=100,
    help="Total addressable student population for the model.",
)

base_outputs = calculate_outputs(students, BASE_CASE)
alternative_outputs = calculate_outputs(students, ALTERNATIVE_OPTION)

st.subheader("Outputs")

base_tab, alternative_tab = st.tabs([BASE_CASE.name, ALTERNATIVE_OPTION.name])

with base_tab:
    st.metric("Order volume", format_number(base_outputs.order_volume))
    st.metric("MAU", format_number(base_outputs.mau))
    st.metric("Variable profit", format_currency(base_outputs.variable_profit))

with alternative_tab:
    st.metric(
        "Order volume",
        format_number(alternative_outputs.order_volume),
        delta=format_number(
            alternative_outputs.order_volume - base_outputs.order_volume
        ),
    )
    st.metric(
        "MAU",
        format_number(alternative_outputs.mau),
        delta=format_number(alternative_outputs.mau - base_outputs.mau),
    )
    st.metric(
        "Variable profit",
        format_currency(alternative_outputs.variable_profit),
        delta=format_currency(
            alternative_outputs.variable_profit - base_outputs.variable_profit
        ),
    )

st.subheader("Base case vs. alternative option")
st.table(build_output_rows(base_outputs, alternative_outputs))

with st.expander("Model assumptions"):
    st.table(
        [
            {
                "Scenario": BASE_CASE.name,
                "MAU rate": format_percentage(BASE_CASE.mau_rate),
                "Orders / MAU": f"{BASE_CASE.orders_per_mau:.2f}",
                "Variable profit / order": format_currency_precise(
                    BASE_CASE.variable_profit_per_order
                ),
            },
            {
                "Scenario": ALTERNATIVE_OPTION.name,
                "MAU rate": format_percentage(ALTERNATIVE_OPTION.mau_rate),
                "Orders / MAU": f"{ALTERNATIVE_OPTION.orders_per_mau:.2f}",
                "Variable profit / order": format_currency_precise(
                    ALTERNATIVE_OPTION.variable_profit_per_order
                ),
            },
        ]
    )

st.caption(
    "Formula: MAU = students x MAU rate; order volume = MAU x orders per MAU; "
    "variable profit = order volume x variable profit per order."
)
