# Project Status Report Template

A sprint-based project status report template for DocForge demonstrating variable placeholders, skeleton tables with sprint and risk data, and an LLM-generated executive summary.

## Template Markers

| Marker | Type | Description |
|--------|------|-------------|
| Project Name | Variable Placeholder | Project name from config |
| Sprint Number | Variable Placeholder | Current sprint from config |
| Report Date | Variable Placeholder | Report date from config |
| Sprint Metrics table | Skeleton Table | Sprint performance data from CSV |
| Risk Register table | Skeleton Table | Risk entries from YAML |
| Executive Summary prompt | LLM Prompt | AI-generated executive summary |

## Data Files

- `data/sprints.csv` — Sprint performance data (5 sprints)
- `data/risks.yaml` — Risk register entries (5 risks)
- `data/project.json` — Project name, sprint number, report date

## Usage

### Generate the template (if template.docx is missing)

```bash
conda run -n docforge python examples/templates/project_status/create_template.py
```

### Analyze the template

```bash
conda run -n docforge python -m cli analyze --template examples/templates/project_status/template.docx
```

### Generate the document

```bash
conda run -n docforge python -m cli generate \
  --template examples/templates/project_status/template.docx \
  --data examples/templates/project_status/data/ \
  --mapping examples/templates/project_status/mapping.json \
  --output output/project_status.docx
```
