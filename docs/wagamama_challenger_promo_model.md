# Wagamama challenger promo model

This repository includes a Google Sheets-compatible workbook for sizing a
Wagamama lapsed-customer challenger promo:

- `models/wagamama_challenger_promo_model.xlsx`
- Generator: `tools/create_wagamama_promo_model.py`

## What the model covers

The workbook is pre-loaded with the cumulative customer groups from the brief:

| Group | Cumulative customers |
| --- | ---: |
| Tightest | 16,209 |
| Tight | 36,746 |
| Medium | 70,821 |
| Broad | 80,431 |
| Widest | 266,280 |

It compares:

- Cumulative audience groups
- Challenger values of GBP 5, GBP 7, and GBP 10
- Low/base/high reach, redemption, and incrementality cases
- Two-month spend phasing against a default GBP 250k monthly budget
- Total investment, monthly investment, budget headroom/gap, estimated
  incremental orders, commission contribution, net cost after contribution, and
  cost per incremental order

## Workbook tabs

1. `README` - model instructions, caveats, and Google Sheets setup notes.
2. `Inputs` - editable promo, funding, commercial, and scenario assumptions.
3. `Target Groups` - cumulative Wagamama audience sizes from the brief.
4. `Scenario Builder` - full scenario table across audience, voucher, and demand cases.
5. `Monthly Phasing` - month 1/month 2 cost and budget checks for Medium/Broad/Widest.
6. `Sensitivity` - stress test for selected group and scenario.

Blue cells are intended for user inputs. Grey cells are formula outputs.

## How to use in Google Sheets

1. Upload `models/wagamama_challenger_promo_model.xlsx` to Google Drive.
2. Open it with Google Sheets.
3. Use **File > Save as Google Sheets** so it becomes a native GSheet.
4. Replace the placeholder assumptions in blue cells on `Inputs`.
5. Share the native GSheet with stakeholders.

## Setup needed for direct agent-created GSheets

This agent did not have a live Google Sheets/Drive integration available. To let
an agent create or update the native GSheet directly, set up one of:

- A Google Sheets/Drive MCP or Cursor integration with permission to create and
  edit spreadsheets.
- A Google service account or OAuth client with access to the target Drive
  folder and scopes equivalent to:
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive.file`

Then provide either:

- The destination Google Drive folder ID or URL, or
- An existing Google Sheet URL to update.

The Sheet or folder must be shared with the authenticated account used by the
integration.

## Regenerating the workbook

Install the workbook-generation dependency and run:

```bash
python3 -m pip install --user openpyxl
python3 tools/create_wagamama_promo_model.py
```

The generated file is written to:

```text
models/wagamama_challenger_promo_model.xlsx
```
