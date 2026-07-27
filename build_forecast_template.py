#!/usr/bin/env python3
"""Build H2 2026 forecast template for 6 markets with Spend and Traffic tables."""

from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

MARKETS = ["UKI", "France", "Belgium", "UAE", "KW", "Italy"]
CHANNELS = ["Digital", "TV / BVOD", "Radio", "OOH"]
OUTPUT = "/workspace/H2_2026_Forecast_Template.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
SECTION_FONT = Font(bold=True, color="1F4E79")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def week_commencing_mondays(start: date, end: date) -> list[date]:
    """Return Mondays from start through end inclusive."""
    d = start
    while d.weekday() != 0:
        d += timedelta(days=1)
    weeks = []
    while d <= end:
        weeks.append(d)
        d += timedelta(days=7)
    return weeks


def last_col_index(period_count: int) -> int:
    """Country + Channel + periods + Total."""
    return 2 + period_count + 1


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


def write_table(ws, start_row: int, title: str, periods: list[str]) -> int:
    """Write one forecast table with country/channel rows and period columns."""
    first_period_col = 3
    last_period_col = first_period_col + len(periods) - 1
    total_col = last_period_col + 1
    last_col_letter = get_column_letter(total_col)
    first_period_letter = get_column_letter(first_period_col)
    last_period_letter = get_column_letter(last_period_col)

    ws.cell(start_row, 1, title).font = SECTION_FONT
    ws.cell(start_row, 1).fill = SECTION_FILL
    ws.merge_cells(
        start_row=start_row,
        start_column=1,
        end_row=start_row,
        end_column=total_col,
    )
    style_range(
        ws,
        f"A{start_row}:{last_col_letter}{start_row}",
        fill=SECTION_FILL,
        font=SECTION_FONT,
    )

    header_row = start_row + 1
    headers = ["Country", "Channel", *periods, "Total"]
    for col, value in enumerate(headers, start=1):
        ws.cell(header_row, col, value)
    style_range(
        ws,
        f"A{header_row}:{last_col_letter}{header_row}",
        fill=HEADER_FILL,
        font=HEADER_FONT,
        align_center=True,
    )

    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 14
    for col in range(first_period_col, total_col + 1):
        ws.column_dimensions[get_column_letter(col)].width = 12

    data_start = header_row + 1
    row = data_start
    for market in MARKETS:
        block_start = row
        for channel in CHANNELS:
            ws.cell(row, 2, channel)
            for col in range(first_period_col, total_col):
                ws.cell(row, col, "")
            ws.cell(
                row,
                total_col,
                f"=SUM({first_period_letter}{row}:{last_period_letter}{row})",
            )
            style_range(ws, f"A{row}:{last_col_letter}{row}")
            row += 1

        block_end = row - 1
        ws.cell(block_start, 1, market)
        ws.cell(block_start, 1).alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        if block_end > block_start:
            ws.merge_cells(
                start_row=block_start,
                start_column=1,
                end_row=block_end,
                end_column=1,
            )

    return row + 1


def build_sheet_title(ws, title: str, period_count: int):
    last_col = get_column_letter(last_col_index(period_count))
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells(f"A1:{last_col}1")


def build_weekly_sheet(wb: Workbook):
    ws = wb.active
    ws.title = "Weekly"
    weeks = week_commencing_mondays(date(2026, 7, 1), date(2026, 12, 31))
    period_labels = [f"W/C {d.strftime('%d-%b')}" for d in weeks]
    build_sheet_title(ws, "H2 2026 Forecast — Weekly View", len(period_labels))

    row = 3
    row = write_table(ws, row, "SPEND", period_labels)
    write_table(ws, row, "TRAFFIC", period_labels)


def build_monthly_sheet(wb: Workbook):
    ws = wb.create_sheet("Monthly")
    periods = ["Jul-26", "Aug-26", "Sep-26", "Oct-26", "Nov-26", "Dec-26"]
    build_sheet_title(ws, "H2 2026 Forecast — Monthly View", len(periods))

    row = 3
    row = write_table(ws, row, "SPEND", periods)
    write_table(ws, row, "TRAFFIC", periods)


def build_quarterly_sheet(wb: Workbook):
    ws = wb.create_sheet("Quarterly")
    periods = ["Q3 2026", "Q4 2026"]
    build_sheet_title(ws, "H2 2026 Forecast — Quarterly View", len(periods))

    row = 3
    row = write_table(ws, row, "SPEND", periods)
    write_table(ws, row, "TRAFFIC", periods)


def build_readme_sheet(wb: Workbook):
    ws = wb.create_sheet("README")
    lines = [
        "H2 2026 Forecast Template",
        "",
        "Layout: countries as rows with channel breakdowns, periods as columns",
        "Markets: UKI, France, Belgium, UAE, KW, Italy",
        "Channels per country: Digital, TV / BVOD, Radio, OOH",
        "Tabs: Weekly, Monthly, Quarterly",
        "Each tab contains two tables: SPEND and TRAFFIC",
        "Each channel row includes a Total column summing values across periods",
        "",
        "Import into Google Sheets:",
        "1. File > Import > Upload > select this file",
        "2. Choose 'Replace spreadsheet' or 'Insert new sheet(s)'",
    ]
    for i, line in enumerate(lines, start=1):
        ws.cell(i, 1, line)
        if i == 1:
            ws.cell(i, 1).font = Font(bold=True, size=14)
    ws.column_dimensions["A"].width = 72


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
