# Financial Report Template

An annual financial report template for DocForge demonstrating variable placeholders, skeleton tables, and LLM prompt markers.

## Template Markers

| Marker | Type | Description |
|--------|------|-------------|
| Company Name | Variable Placeholder | Company name from config |
| Fiscal Year | Variable Placeholder | Fiscal year from config |
| Report Date | Variable Placeholder | Report date from config |
| Revenue Summary table | Skeleton Table | Quarterly revenue data from Excel |
| Expense Analysis table | Skeleton Table | Expense breakdown from CSV |
| Financial Outlook prompt | LLM Prompt | AI-generated financial outlook |

## Data Files

- `data/revenue.xlsx` — Quarterly revenue data (4 quarters)
- `data/expenses.csv` — Expense categories (6 rows)
- `data/config.json` — Company name, fiscal year, report date

## Usage

### Generate the template (if template.docx is missing)

```bash
conda run -n docforge python examples/templates/financial_report/create_template.py
```

### Analyze the template

```bash
conda run -n docforge python -m cli analyze --template examples/templates/financial_report/template.docx
```

### Generate the document

```bash
conda run -n docforge python -m cli generate \
  --template examples/templates/financial_report/template.docx \
  --data examples/templates/financial_report/data/ \
  --mapping examples/templates/financial_report/mapping.json \
  --output output/financial_report.docx
```
