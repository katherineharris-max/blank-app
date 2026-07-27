#!/usr/bin/env python3
"""Build H2 2026 forecast template for 6 markets with Spend and Traffic tables."""

from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

MARKETS = ["UKI", "France", "Belgium", "UAE", "KW", "Italy"]
OUTPUT = "/workspace/H2_2026_Forecast_Template.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
SECTION_FONT = Font(bold=True, color="1F4E79")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def week_commencing_mondays(start: date, end: date) -> list[date]:
    """Return Mondays from start through end inclusive."""
    # Move to first Monday on/after start
    d = start
    while d.weekday() != 0:
        d += timedelta(days=1)
    weeks = []
    while d <= end:
        weeks.append(d)
        d += timedelta(days=7)
    return weeks


def style_range(ws, cell_range, fill=None, font=None, border=True, align_center=False):
    for row in ws[cell_range]:
        for cell in row:
            if fill:
                cell.fill = fill
            if font:
                cell.font = font
            if border:
                cell.border = BORDER
            if align_center:
                cell.alignment = Alignment(horizontal="center", vertical="center")


def write_table(ws, start_row: int, title: str, period_label: str, periods: list[str]) -> int:
    """Write one forecast table. Returns next free row."""
    last_col = 2 + len(MARKETS)  # A=period, B-G=markets, H=total
    total_col = get_column_letter(last_col)
    first_market_col = "B"
    last_market_col = get_column_letter(1 + len(MARKETS))

    ws.cell(start_row, 1, title).font = SECTION_FONT
    ws.cell(start_row, 1).fill = SECTION_FILL
    ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=last_col)
    style_range(ws, f"A{start_row}:{total_col}{start_row}", fill=SECTION_FILL, font=SECTION_FONT)

    header_row = start_row + 1
    headers = [period_label, *MARKETS, "Total"]
    for col, value in enumerate(headers, start=1):
        ws.cell(header_row, col, value)
    style_range(
        ws,
        f"A{header_row}:{total_col}{header_row}",
        fill=HEADER_FILL,
        font=HEADER_FONT,
        align_center=True,
    )
    ws.column_dimensions["A"].width = 18
    for idx in range(2, last_col + 1):
        ws.column_dimensions[get_column_letter(idx)].width = 14

    data_start = header_row + 1
    for i, period in enumerate(periods):
        row = data_start + i
        ws.cell(row, 1, period)
        for col in range(2, last_col):
            ws.cell(row, col, "")
        ws.cell(row, last_col, f"=SUM({first_market_col}{row}:{last_market_col}{row})")
        style_range(ws, f"A{row}:{total_col}{row}")

    total_row = data_start + len(periods)
    ws.cell(total_row, 1, "Total")
    ws.cell(total_row, 1).font = Font(bold=True)
    for col in range(2, last_col + 1):
        col_letter = get_column_letter(col)
        ws.cell(
            total_row,
            col,
            f"=SUM({col_letter}{data_start}:{col_letter}{total_row - 1})",
        )
        ws.cell(total_row, col).font = Font(bold=True)
    style_range(ws, f"A{total_row}:{total_col}{total_row}")

    return total_row + 2


def build_weekly_sheet(wb: Workbook):
    ws = wb.active
    ws.title = "Weekly"
    weeks = week_commencing_mondays(date(2026, 7, 1), date(2026, 12, 31))
    period_labels = [f"W/C {d.strftime('%d-%b-%Y')}" for d in weeks]

    ws["A1"] = "H2 2026 Forecast — Weekly View"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:H1")

    row = 3
    row = write_table(ws, row, "SPEND", "Week", period_labels)
    write_table(ws, row, "TRAFFIC", "Week", period_labels)


def build_monthly_sheet(wb: Workbook):
    ws = wb.create_sheet("Monthly")
    periods = ["Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026", "Nov-2026", "Dec-2026"]

    ws["A1"] = "H2 2026 Forecast — Monthly View"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:H1")

    row = 3
    row = write_table(ws, row, "SPEND", "Month", periods)
    write_table(ws, row, "TRAFFIC", "Month", periods)


def build_quarterly_sheet(wb: Workbook):
    ws = wb.create_sheet("Quarterly")
    periods = ["Q3 2026 (Jul-Sep)", "Q4 2026 (Oct-Dec)", "H2 2026 Total"]

    ws["A1"] = "H2 2026 Forecast — Quarterly View"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:H1")

    row = 3
    row = write_table(ws, row, "SPEND", "Quarter", periods)
    write_table(ws, row, "TRAFFIC", "Quarter", periods)


def build_readme_sheet(wb: Workbook):
    ws = wb.create_sheet("README")
    lines = [
        "H2 2026 Forecast Template",
        "",
        "Markets: UKI, France, Belgium, UAE, KW, Italy",
        "Tabs: Weekly, Monthly, Quarterly",
        "Each tab contains two tables: SPEND and TRAFFIC",
        "",
        "Import into Google Sheets:",
        "1. File > Import > Upload > select this file",
        "2. Choose 'Replace spreadsheet' or 'Insert new sheet(s)'",
        "",
        "Sheet URL target:",
        "https://docs.google.com/spreadsheets/d/1z-sr3zo15-ehHzbOqTejCZGTKHRaNaxJ_g7G2eVuoUI/edit",
    ]
    for i, line in enumerate(lines, start=1):
        ws.cell(i, 1, line)
        if i == 1:
            ws.cell(i, 1).font = Font(bold=True, size=14)
    ws.column_dimensions["A"].width = 80


def main():
    wb = Workbook()
    build_weekly_sheet(wb)
    build_monthly_sheet(wb)
    build_quarterly_sheet(wb)
    build_readme_sheet(wb)
    wb.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
