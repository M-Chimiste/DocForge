# Quickstart

This guide walks you through generating your first document with DocForge in about 5 minutes.

## Step 1: Start DocForge

If you have not already installed DocForge, see the [Installation](installation.md) guide. The quickest way is Docker:

```bash
git clone https://github.com/m-chimiste/docforge.git
cd docforge
docker compose up
```

Open `http://localhost:5173` in your browser.

## Step 2: Create a Project

1. Click **New Project** on the projects page.
2. Enter a name (e.g., "Quarterly Report") and an optional description.
3. Click **Create**. You will be taken to the project workspace.

Using the API:

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Quarterly Report", "description": "Q1 2026 report"}'
```

## Step 3: Author a Template

Create a Word document (`.docx`) with your report structure. Use **red-formatted text** (exact RGB `#FF0000`) for instructions:

- **Short placeholders** (1-3 words like `Company Name` or `Revenue`) are treated as variable placeholders that get substituted from data.
- **Longer instructions** (like "Summarize the quarterly performance based on the attached data") are treated as LLM prompts.
- **Red text inside table rows** is treated as sample data that indicates the table should be populated from a data source.

Example template structure:

```
Quarterly Report for [Company Name]    <-- red text, variable placeholder

Executive Summary
[Provide a brief executive summary      <-- red text, LLM prompt
of the quarterly results]

Financial Results
| Metric    | Q1      | Q2      |
| Revenue   | $1.2M   | $1.5M   |       <-- red text in table, sample data
| Expenses  | $0.8M   | $0.9M   |
```

## Step 4: Upload Template and Data

1. In the project workspace, click **Upload Template** and select your `.docx` file.
2. DocForge parses the template and displays the analysis: sections, markers, and tables found.
3. Click **Upload Data** and select your data files (`.xlsx`, `.csv`, or `.json`).

Using the API:

```bash
# Upload template
curl -X POST http://localhost:8000/api/v1/templates/analyze \
  -F "file=@quarterly_report_template.docx"

# Upload data source (replace 1 with your project ID)
curl -X POST http://localhost:8000/api/v1/projects/1/data-sources \
  -F "file=@financial_data.xlsx"
```

## Step 5: Review Mappings

DocForge automatically resolves data mappings using fuzzy matching:

1. Click **Auto-Resolve** to run automatic mapping.
2. Review the suggested mappings in the Mapping Panel.
3. High-confidence matches (>= 0.8) are auto-accepted.
4. Medium-confidence matches (0.4-0.79) are flagged for review.
5. Unresolved markers (< 0.4) need manual assignment.
6. Adjust any mappings as needed.

## Step 6: Generate the Document

1. Click **Generate** to start document generation.
2. A progress indicator shows each stage: parsing, data loading, rendering, validation.
3. When complete, the generated document opens in the built-in editor.

Using the API:

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": [
      {
        "markerId": "marker_0",
        "dataSource": "financial_data.xlsx",
        "field": "company_name",
        "sheet": "Sheet1"
      }
    ]
  }'
```

## Step 7: Review and Export

1. In the editor, review the generated content.
2. LLM-generated sections are highlighted for review.
3. Low-confidence items are flagged with warning indicators.
4. Edit text directly in the editor as needed.
5. Click **Export** to download the final `.docx` file.

## Next Steps

- [Templates Guide](user-guide/templates.md) -- Learn the full template authoring system
- [Data Sources](user-guide/data-sources.md) -- Supported file formats and extraction options
- [LLM Configuration](user-guide/llm-config.md) -- Set up LLM providers for content generation
- [API Reference](api/overview.md) -- Integrate DocForge into your workflow via the REST API
