# Compliance Assessment Report Template

A regulatory compliance assessment template for DocForge demonstrating variable placeholders, skeleton tables for controls and findings, and an LLM-generated remediation plan.

## Template Markers

| Marker | Type | Description |
|--------|------|-------------|
| Organization Name | Variable Placeholder | Organization name from config |
| Assessment Date | Variable Placeholder | Assessment date from config |
| Assessor | Variable Placeholder | Lead assessor name from config |
| Control Checklist table | Skeleton Table | Controls and status from Excel |
| Findings table | Skeleton Table | Assessment findings from CSV |
| Remediation Plan prompt | LLM Prompt | AI-generated remediation plan |

## Data Files

- `data/controls.xlsx` — Control checklist with 10 controls and statuses
- `data/findings.csv` — Assessment findings (5 findings, various severities)
- `data/assessment.json` — Organization name, assessment date, assessor

## Usage

### Generate the template (if template.docx is missing)

```bash
conda run -n docforge python examples/templates/compliance_document/create_template.py
```

### Analyze the template

```bash
conda run -n docforge python -m cli analyze --template examples/templates/compliance_document/template.docx
```

### Generate the document

```bash
conda run -n docforge python -m cli generate \
  --template examples/templates/compliance_document/template.docx \
  --data examples/templates/compliance_document/data/ \
  --mapping examples/templates/compliance_document/mapping.json \
  --output output/compliance_document.docx
```
