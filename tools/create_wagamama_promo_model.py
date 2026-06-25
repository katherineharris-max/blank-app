"""Create a Google Sheets-compatible Wagamama challenger promo model.

The generated workbook is intended to be uploaded/imported into Google Sheets.
All modelling logic is in sheet formulas so commercial users can adjust the
inputs without running this script.
"""

from __future__ import annotations

from copy import copy
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter


OUTPUT_PATH = Path("models/wagamama_challenger_promo_model.xlsx")

BLUE = "D9EAF7"
GREEN = "DDEED5"
GREY = "F3F4F6"
DARK = "1F2937"
HEADER = "5B7DB1"
SECTION = "E8EEF9"
WARNING = "FCE4D6"
GOOD = "E2F0D9"
WHITE = "FFFFFF"
BORDER = Side(style="thin", color="D9D9D9")


def style_title(cell, size: int = 16) -> None:
    cell.font = Font(bold=True, size=size, color=DARK)


def style_header_row(ws, row: int, start_col: int, end_col: int) -> None:
    for col in range(start_col, end_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = Font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=HEADER)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)


def style_section_row(ws, row: int, start_col: int, end_col: int) -> None:
    for col in range(start_col, end_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = Font(bold=True, color=DARK)
        cell.fill = PatternFill("solid", fgColor=SECTION)
        cell.border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)


def shade_inputs(cells) -> None:
    for cell in cells:
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)


def shade_formula(cells) -> None:
    for cell in cells:
        cell.fill = PatternFill("solid", fgColor=GREY)
        cell.border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)


def set_widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def add_note(ws, row: int, text: str) -> None:
    ws.cell(row=row, column=1, value=text)
    ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")


def create_readme(ws) -> None:
    ws.title = "README"
    ws["A1"] = "Wagamama challenger promo sizing template"
    style_title(ws["A1"], 18)
    ws["A3"] = "Purpose"
    style_title(ws["A3"], 13)
    add_note(
        ws,
        4,
        "Forecast the gross and net cost of a lapsed-customer challenger promo "
        "for Wagamama customers after multi-aggregator launch. The template is "
        "pre-loaded with the cumulative target groups provided in the brief and "
        "uses editable assumptions for reach, redemption, funding, AOV, "
        "commission, and incrementality.",
    )
    ws["A6"] = "How to use"
    style_title(ws["A6"], 13)
    instructions = [
        "1. Update blue cells in Inputs with the latest promo assumptions.",
        "2. Update Target Groups if CRM sizing changes.",
        "3. Use Scenario Builder to compare group size, voucher value, and low/base/high redemption cases.",
        "4. Use Monthly Phasing to check whether each scenario fits the assumed monthly budget.",
        "5. Use Sensitivity to stress-test one chosen audience and scenario across voucher values and redemption rates.",
    ]
    for index, text in enumerate(instructions, start=7):
        ws.cell(row=index, column=1, value=text)
        ws.cell(row=index, column=1).alignment = Alignment(wrap_text=True)

    ws["A14"] = "Colour key"
    style_title(ws["A14"], 13)
    keys = [("Blue", "Editable input"), ("Grey", "Formula output"), ("Green", "Scenario or model guidance")]
    for row, (label, meaning) in enumerate(keys, start=15):
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=meaning)
    ws["A15"].fill = PatternFill("solid", fgColor=BLUE)
    ws["A16"].fill = PatternFill("solid", fgColor=GREY)
    ws["A17"].fill = PatternFill("solid", fgColor=GREEN)

    ws["A20"] = "Google Sheets setup"
    style_title(ws["A20"], 13)
    setup = [
        "Option A: Upload this .xlsx to Google Drive, open with Google Sheets, then File > Save as Google Sheets.",
        "Option B: If you want an agent to create/update the native GSheet directly, enable a Google Sheets/Drive integration or provide a service-account/OAuth setup with spreadsheet and drive.file scopes, plus a destination folder or existing Sheet URL shared with that account.",
    ]
    for row, text in enumerate(setup, start=21):
        ws.cell(row=row, column=1, value=text)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True)

    ws["A25"] = "Important caveats"
    style_title(ws["A25"], 13)
    caveats = [
        "Default redemption and incrementality values are placeholders for planning only.",
        "Costs are modelled as promotional discount funding plus comms and fixed costs. Update Inputs if restaurant funding or other cost sharing applies.",
        "Net cost after commission uses incremental orders only; if finance wants a different profitability lens, replace the contribution formula in Scenario Builder.",
    ]
    for row, text in enumerate(caveats, start=26):
        ws.cell(row=row, column=1, value=text)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True)

    ws.merge_cells("A1:H1")
    ws.merge_cells("A4:H4")
    for row in [7, 8, 9, 10, 11, 21, 22, 26, 27, 28]:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    set_widths(ws, {"A": 18, "B": 28, "C": 18, "D": 18, "E": 18, "F": 18, "G": 18, "H": 18})


def create_inputs(ws) -> None:
    ws.title = "Inputs"
    ws["A1"] = "Editable assumptions"
    style_title(ws["A1"], 18)
    ws["A2"] = "Only edit blue cells. Scenario Builder and other output tabs update from these assumptions."
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:F2")

    rows = [
        (4, "Promo setup", "", "", ""),
        (5, "Promo length (months)", 2, "months", "Current thinking is a longer two-month challenger."),
        (6, "Monthly budget available", 250000, "GBP", "Brief indicated an indicative 250k/month budget."),
        (7, "Month 1 redemption weight", 0.55, "% of total", "Used by Monthly Phasing."),
        (8, "Month 2 redemption weight", 0.45, "% of total", "Used by Monthly Phasing."),
        (9, "Selected voucher value", 7, "GBP", "Primary mechanic for quick checks; scenario table also tests 5/7/10."),
        (10, "Max claims per redeemer", 1, "orders", "Set >1 if the challenger allows multiple discounted orders."),
        (11, "Deliveroo funding share", 1.0, "%", "Share of discount cost paid by Deliveroo/Rx marketing."),
        (12, "Restaurant/partner funding share", 0.0, "%", "Information only unless finance wants to net this separately."),
        (13, "Comms cost per targeted customer", 0.03, "GBP", "CRM, push, email or paid audience activation cost."),
        (14, "Other fixed campaign costs", 0, "GBP", "Creative, tooling or agency costs."),
        (16, "Commercial assumptions", "", "", ""),
        (17, "Average order value", 25, "GBP", "Use Wagamama AOV for the relevant lapsed cohort if available."),
        (18, "Commission rate", 0.30, "% of AOV", "Use the new Wagamama commission rate."),
        (19, "Variable cost to serve per order", 0, "GBP", "Optional fulfilment/support variable cost per incremental order."),
        (20, "Baseline orders per reached customer", 0.10, "orders over promo period", "Used as a context metric, not in cost calculation."),
    ]
    for row, label, value, unit, notes in rows:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=value)
        ws.cell(row=row, column=3, value=unit)
        ws.cell(row=row, column=4, value=notes)
        ws.cell(row=row, column=4).alignment = Alignment(wrap_text=True)
        if value == "":
            style_section_row(ws, row, 1, 4)
        else:
            shade_inputs([ws.cell(row=row, column=2)])
            for col in [1, 3, 4]:
                ws.cell(row=row, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)

    ws["A23"] = "Scenario assumptions"
    style_title(ws["A23"], 14)
    headers = ["Assumption", "Low", "Base", "High", "Notes"]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=24, column=col, value=header)
    style_header_row(ws, 24, 1, 5)

    scenario_rows = [
        ("Reachable rate", 0.75, 0.85, 0.90, "Share of targetable customers who can be reached during the campaign."),
        ("Redemption / completion rate", 0.08, 0.15, 0.25, "Share of reached customers who redeem or complete the challenger."),
        ("Avg claims per redeemer", 1.00, 1.00, 1.10, "Average discounted orders per redeemer."),
        ("Incrementality", 0.35, 0.50, 0.65, "Share of promo orders assumed incremental vs baseline/pulled-forward orders."),
    ]
    for row_offset, values in enumerate(scenario_rows, start=25):
        for col, value in enumerate(values, start=1):
            ws.cell(row=row_offset, column=col, value=value)
            ws.cell(row=row_offset, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)
            if col in [2, 3, 4]:
                ws.cell(row=row_offset, column=col).fill = PatternFill("solid", fgColor=BLUE)
        ws.cell(row=row_offset, column=5).alignment = Alignment(wrap_text=True)

    ws["A31"] = "Selected scenario controls"
    style_title(ws["A31"], 14)
    selected_rows = [
        ("Selected group for Sensitivity", "Medium"),
        ("Selected scenario for Sensitivity", "Base"),
    ]
    for idx, (label, value) in enumerate(selected_rows, start=32):
        ws.cell(row=idx, column=1, value=label)
        ws.cell(row=idx, column=2, value=value)
        shade_inputs([ws.cell(row=idx, column=2)])

    group_validation = DataValidation(type="list", formula1='"Tightest,Tight,Medium,Broad,Widest"', allow_blank=False)
    scenario_validation = DataValidation(type="list", formula1='"Low,Base,High"', allow_blank=False)
    voucher_validation = DataValidation(type="list", formula1='"5,7,10"', allow_blank=False)
    ws.add_data_validation(group_validation)
    ws.add_data_validation(scenario_validation)
    ws.add_data_validation(voucher_validation)
    group_validation.add(ws["B32"])
    scenario_validation.add(ws["B33"])
    voucher_validation.add(ws["B9"])

    for row in [7, 8, 11, 12, 18, 25, 26, 28]:
        for col in [2, 3, 4]:
            ws.cell(row=row, column=col).number_format = "0.0%"
    for row in [6, 9, 13, 14, 17, 19]:
        ws.cell(row=row, column=2).number_format = '"GBP" #,##0.00'
    for row in [5, 10, 20]:
        ws.cell(row=row, column=2).number_format = "0.00"
    for row in [25, 26, 27, 28]:
        for col in [2, 3, 4]:
            if row == 27:
                ws.cell(row=row, column=col).number_format = "0.00"
            else:
                ws.cell(row=row, column=col).number_format = "0.0%"

    set_widths(ws, {"A": 34, "B": 18, "C": 24, "D": 60, "E": 56})
    ws.freeze_panes = "A24"


def create_target_groups(ws) -> None:
    ws.title = "Target Groups"
    ws["A1"] = "Cumulative target groups"
    style_title(ws["A1"], 18)
    ws["A2"] = "Customer counts are cumulative based on the Wagamama frequency-decline groups in the brief."
    ws.merge_cells("A2:F2")

    headers = ["Group option", "Definition", "Cumulative customers", "Incremental customers", "Recommended?", "Notes"]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=4, column=col, value=header)
    style_header_row(ws, 4, 1, len(headers))

    groups = [
        ("Tightest", "Habitual (3+ Wagamama orders) who fully lapsed", 16209, "No", "Smallest high-intent pool."),
        ("Tight", "Tightest + habitual (3+) with >50% frequency decline", 36746, "No", "Adds heavy decliners."),
        ("Medium", "Tight + 2-order customers who lapsed", 70821, "Minimum", "Brief indicated target up to Medium as a minimum."),
        ("Broad", "Medium + habitual (3+) with 10-50% frequency decline", 80431, "Size", "Marginal expansion from Medium."),
        ("Widest", "Broad + lighter / one-time decliners", 266280, "Size", "Largest pool; likely lower intent and lower redemption quality."),
    ]
    for row, (name, definition, customers, recommended, notes) in enumerate(groups, start=5):
        ws.cell(row=row, column=1, value=name)
        ws.cell(row=row, column=2, value=definition)
        ws.cell(row=row, column=3, value=customers)
        if row == 5:
            ws.cell(row=row, column=4, value="=C5")
        else:
            ws.cell(row=row, column=4, value=f"=C{row}-C{row-1}")
        ws.cell(row=row, column=5, value=recommended)
        ws.cell(row=row, column=6, value=notes)
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)
            ws.cell(row=row, column=col).alignment = Alignment(wrap_text=True, vertical="top")
        shade_inputs([ws.cell(row=row, column=3)])
        shade_formula([ws.cell(row=row, column=4)])
        if recommended in ["Minimum", "Size"]:
            ws.cell(row=row, column=5).fill = PatternFill("solid", fgColor=GREEN)

    for row in range(5, 10):
        for col in [3, 4]:
            ws.cell(row=row, column=col).number_format = "#,##0"

    set_widths(ws, {"A": 16, "B": 56, "C": 22, "D": 22, "E": 18, "F": 42})
    ws.freeze_panes = "A5"


def scenario_formula(row: int, assumption_row: int) -> str:
    return f"=INDEX(Inputs!$B${assumption_row}:$D${assumption_row},1,MATCH($D{row},Inputs!$B$24:$D$24,0))"


def create_scenario_builder(ws) -> None:
    ws.title = "Scenario Builder"
    ws["A1"] = "Scenario Builder"
    style_title(ws["A1"], 18)
    ws["A2"] = "Compare cumulative audience groups, challenger voucher values, and low/base/high redemption assumptions."
    ws.merge_cells("A2:W2")

    headers = [
        "Group",
        "Target customers",
        "Voucher value",
        "Scenario",
        "Reachable rate",
        "Reached customers",
        "Redemption rate",
        "Redeemers",
        "Avg claims / redeemer",
        "Promo orders / claims",
        "Gross discount cost",
        "Deliveroo funded discount",
        "Comms cost",
        "Total investment",
        "Monthly investment",
        "Monthly budget gap/(headroom)",
        "Baseline orders",
        "Incrementality",
        "Incremental orders",
        "Estimated commission contribution",
        "Variable cost",
        "Net cost after contribution",
        "Cost per incremental order",
    ]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=4, column=col, value=header)
    style_header_row(ws, 4, 1, len(headers))

    row = 5
    for group in ["Tightest", "Tight", "Medium", "Broad", "Widest"]:
        for voucher in [5, 7, 10]:
            for scenario in ["Low", "Base", "High"]:
                ws.cell(row=row, column=1, value=group)
                ws.cell(row=row, column=2, value=f'=VLOOKUP(A{row},\'Target Groups\'!$A$5:$C$9,3,FALSE)')
                ws.cell(row=row, column=3, value=voucher)
                ws.cell(row=row, column=4, value=scenario)
                ws.cell(row=row, column=5, value=scenario_formula(row, 25))
                ws.cell(row=row, column=6, value=f"=B{row}*E{row}")
                ws.cell(row=row, column=7, value=scenario_formula(row, 26))
                ws.cell(row=row, column=8, value=f"=F{row}*G{row}")
                ws.cell(row=row, column=9, value=scenario_formula(row, 27))
                ws.cell(row=row, column=10, value=f"=H{row}*I{row}")
                ws.cell(row=row, column=11, value=f"=J{row}*C{row}")
                ws.cell(row=row, column=12, value=f"=K{row}*Inputs!$B$11")
                ws.cell(row=row, column=13, value=f"=B{row}*Inputs!$B$13")
                ws.cell(row=row, column=14, value=f"=L{row}+M{row}+Inputs!$B$14")
                ws.cell(row=row, column=15, value=f"=N{row}/Inputs!$B$5")
                ws.cell(row=row, column=16, value=f"=Inputs!$B$6-O{row}")
                ws.cell(row=row, column=17, value=f"=F{row}*Inputs!$B$20")
                ws.cell(row=row, column=18, value=scenario_formula(row, 28))
                ws.cell(row=row, column=19, value=f"=J{row}*R{row}")
                ws.cell(row=row, column=20, value=f"=S{row}*Inputs!$B$17*Inputs!$B$18")
                ws.cell(row=row, column=21, value=f"=S{row}*Inputs!$B$19")
                ws.cell(row=row, column=22, value=f"=N{row}-T{row}+U{row}")
                ws.cell(row=row, column=23, value=f'=IFERROR(V{row}/S{row},"")')
                for col in range(1, 24):
                    ws.cell(row=row, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)
                    ws.cell(row=row, column=col).alignment = Alignment(vertical="top")
                for col in [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                    ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=GREY)
                row += 1

    last_row = row - 1
    for current_row in range(5, last_row + 1):
        for col in [5, 7, 18]:
            ws.cell(row=current_row, column=col).number_format = "0.0%"
        for col in [2, 6, 8, 10, 17, 19]:
            ws.cell(row=current_row, column=col).number_format = "#,##0"
        for col in [3, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23]:
            ws.cell(row=current_row, column=col).number_format = '"GBP" #,##0'
        ws.cell(row=current_row, column=9).number_format = "0.00"

    ws.conditional_formatting.add(
        f"P5:P{last_row}",
        CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=WARNING)),
    )
    ws.conditional_formatting.add(
        f"P5:P{last_row}",
        CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=PatternFill("solid", fgColor=GOOD)),
    )

    set_widths(
        ws,
        {
            "A": 13,
            "B": 17,
            "C": 15,
            "D": 11,
            "E": 14,
            "F": 17,
            "G": 16,
            "H": 13,
            "I": 18,
            "J": 18,
            "K": 19,
            "L": 22,
            "M": 13,
            "N": 17,
            "O": 18,
            "P": 24,
            "Q": 16,
            "R": 14,
            "S": 17,
            "T": 28,
            "U": 14,
            "V": 24,
            "W": 24,
        },
    )
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:W{last_row}"


def create_monthly_phasing(ws) -> None:
    ws.title = "Monthly Phasing"
    ws["A1"] = "Monthly Phasing"
    style_title(ws["A1"], 18)
    ws["A2"] = "Two-month spend phasing from Inputs. Negative monthly headroom indicates a budget gap."
    ws.merge_cells("A2:J2")

    headers = [
        "Group",
        "Voucher value",
        "Scenario",
        "Total investment",
        "Month 1 weight",
        "Month 1 cost",
        "Month 1 headroom",
        "Month 2 weight",
        "Month 2 cost",
        "Month 2 headroom",
    ]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=4, column=col, value=header)
    style_header_row(ws, 4, 1, len(headers))

    row = 5
    for group in ["Medium", "Broad", "Widest"]:
        for voucher in [5, 7, 10]:
            for scenario in ["Low", "Base", "High"]:
                ws.cell(row=row, column=1, value=group)
                ws.cell(row=row, column=2, value=voucher)
                ws.cell(row=row, column=3, value=scenario)
                lookup = (
                    f"=SUMIFS('Scenario Builder'!$N$5:$N$49,"
                    f"'Scenario Builder'!$A$5:$A$49,A{row},"
                    f"'Scenario Builder'!$C$5:$C$49,B{row},"
                    f"'Scenario Builder'!$D$5:$D$49,C{row})"
                )
                ws.cell(row=row, column=4, value=lookup)
                ws.cell(row=row, column=5, value="=Inputs!$B$7")
                ws.cell(row=row, column=6, value=f"=D{row}*E{row}")
                ws.cell(row=row, column=7, value=f"=Inputs!$B$6-F{row}")
                ws.cell(row=row, column=8, value="=Inputs!$B$8")
                ws.cell(row=row, column=9, value=f"=D{row}*H{row}")
                ws.cell(row=row, column=10, value=f"=Inputs!$B$6-I{row}")
                for col in range(1, 11):
                    ws.cell(row=row, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)
                for col in [4, 5, 6, 7, 8, 9, 10]:
                    ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=GREY)
                row += 1

    last_row = row - 1
    for current_row in range(5, last_row + 1):
        for col in [5, 8]:
            ws.cell(row=current_row, column=col).number_format = "0.0%"
        for col in [2, 4, 6, 7, 9, 10]:
            ws.cell(row=current_row, column=col).number_format = '"GBP" #,##0'

    ws.conditional_formatting.add(
        f"G5:G{last_row}",
        CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=WARNING)),
    )
    ws.conditional_formatting.add(
        f"J5:J{last_row}",
        CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=WARNING)),
    )
    ws.auto_filter.ref = f"A4:J{last_row}"
    ws.freeze_panes = "A5"
    set_widths(ws, {"A": 13, "B": 14, "C": 11, "D": 18, "E": 16, "F": 16, "G": 18, "H": 16, "I": 16, "J": 18})


def create_sensitivity(ws) -> None:
    ws.title = "Sensitivity"
    ws["A1"] = "Sensitivity"
    style_title(ws["A1"], 18)
    ws["A2"] = "Stress-test total investment and net cost for the selected group/scenario in Inputs."
    ws.merge_cells("A2:H2")

    ws["A4"] = "Selected group"
    ws["B4"] = "=Inputs!$B$32"
    ws["A5"] = "Selected scenario"
    ws["B5"] = "=Inputs!$B$33"
    ws["A6"] = "Target customers"
    ws["B6"] = "=VLOOKUP(B4,'Target Groups'!$A$5:$C$9,3,FALSE)"
    ws["A7"] = "Reachable rate"
    ws["B7"] = "=INDEX(Inputs!$B$25:$D$25,1,MATCH(B5,Inputs!$B$24:$D$24,0))"
    ws["A8"] = "Avg claims / redeemer"
    ws["B8"] = "=INDEX(Inputs!$B$27:$D$27,1,MATCH(B5,Inputs!$B$24:$D$24,0))"
    ws["A9"] = "Incrementality"
    ws["B9"] = "=INDEX(Inputs!$B$28:$D$28,1,MATCH(B5,Inputs!$B$24:$D$24,0))"
    for row in range(4, 10):
        ws.cell(row=row, column=1).font = Font(bold=True)
        ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor=GREY)
        ws.cell(row=row, column=2).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)

    ws["A12"] = "Total investment by voucher value and redemption rate"
    style_title(ws["A12"], 13)
    redemption_rates = [0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]
    ws.cell(row=14, column=1, value="Voucher value")
    for col, rate in enumerate(redemption_rates, start=2):
        ws.cell(row=14, column=col, value=rate)
    style_header_row(ws, 14, 1, len(redemption_rates) + 1)
    for row_offset, voucher in enumerate([5, 7, 10], start=15):
        ws.cell(row=row_offset, column=1, value=voucher)
        for col in range(2, len(redemption_rates) + 2):
            col_letter = get_column_letter(col)
            ws.cell(
                row=row_offset,
                column=col,
                value=(
                    f"=($B$6*$B$7*{col_letter}$14*$B$8*$A{row_offset}*Inputs!$B$11)"
                    f"+($B$6*Inputs!$B$13)+Inputs!$B$14"
                ),
            )

    ws["A20"] = "Net cost after contribution by voucher value and redemption rate"
    style_title(ws["A20"], 13)
    ws.cell(row=22, column=1, value="Voucher value")
    for col, rate in enumerate(redemption_rates, start=2):
        ws.cell(row=22, column=col, value=rate)
    style_header_row(ws, 22, 1, len(redemption_rates) + 1)
    for row_offset, voucher in enumerate([5, 7, 10], start=23):
        ws.cell(row=row_offset, column=1, value=voucher)
        for col in range(2, len(redemption_rates) + 2):
            col_letter = get_column_letter(col)
            total_cost_cell = f"{col_letter}{row_offset - 8}"
            incremental_orders = f"($B$6*$B$7*{col_letter}$22*$B$8*$B$9)"
            contribution = f"({incremental_orders}*Inputs!$B$17*Inputs!$B$18)"
            variable_cost = f"({incremental_orders}*Inputs!$B$19)"
            ws.cell(row=row_offset, column=col, value=f"={total_cost_cell}-{contribution}+{variable_cost}")

    for row in [14, 22]:
        for col in range(2, len(redemption_rates) + 2):
            ws.cell(row=row, column=col).number_format = "0.0%"
    for row in list(range(15, 18)) + list(range(23, 26)):
        ws.cell(row=row, column=1).number_format = '"GBP" #,##0'
        for col in range(2, len(redemption_rates) + 2):
            ws.cell(row=row, column=col).number_format = '"GBP" #,##0'
            ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=GREY)
            ws.cell(row=row, column=col).border = Border(top=BORDER, bottom=BORDER, left=BORDER, right=BORDER)

    for row in [7, 9]:
        ws.cell(row=row, column=2).number_format = "0.0%"
    ws["B6"].number_format = "#,##0"
    ws["B8"].number_format = "0.00"

    set_widths(ws, {"A": 22, "B": 16, "C": 16, "D": 16, "E": 16, "F": 16, "G": 16, "H": 16})


def finalise_workbook(wb: Workbook) -> None:
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
        for row in ws.iter_rows():
            for cell in row:
                alignment = copy(cell.alignment)
                alignment.wrap_text = True
                alignment.vertical = "top"
                cell.alignment = alignment


def main() -> None:
    wb = Workbook()
    create_readme(wb.active)
    create_inputs(wb.create_sheet("Inputs"))
    create_target_groups(wb.create_sheet("Target Groups"))
    create_scenario_builder(wb.create_sheet("Scenario Builder"))
    create_monthly_phasing(wb.create_sheet("Monthly Phasing"))
    create_sensitivity(wb.create_sheet("Sensitivity"))
    finalise_workbook(wb)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_PATH)
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
