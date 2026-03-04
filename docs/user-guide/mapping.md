# Mapping

Mapping connects template markers to data sources. DocForge provides automatic resolution with confidence scoring, along with a visual mapping panel for manual adjustments.

## Auto-Resolution

DocForge can automatically map template markers to data sources using fuzzy matching. The system applies multiple matching strategies in order:

### Matching Strategies

| Strategy | Confidence | Description |
|----------|-----------|-------------|
| Exact file reference | 1.0 | LLM prompt text contains a filename matching an uploaded file |
| Field name match | 0.9 | Placeholder text exactly matches a column header or JSON key |
| Fuzzy field name match | 0.5-0.8 | Placeholder is a close match via edit distance or token overlap |
| Sample data structural match | 0.6-0.8 | Red sample data matches column count and data types |
| No match | 0.0 | Marker left unresolved |

### Confidence Thresholds

- **>= 0.8** -- Auto-resolved, no flag. Proceeds silently through generation.
- **0.4 - 0.79** -- Auto-resolved, but flagged post-generation in the editor for user review.
- **< 0.4** -- Left unresolved. Highlighted in the mapping panel for manual resolution before generation.

### Running Auto-Resolution

In the web UI, click **Auto-Resolve** after uploading both a template and data sources.

Via the API:

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/auto-resolve
```

Response:

```json
{
  "matches": [
    {
      "markerId": "marker_0",
      "dataSource": "financial_data.xlsx",
      "field": "company_name",
      "sheet": "Sheet1",
      "confidence": 0.92,
      "matchType": "exact",
      "reasoning": "Exact field name match: 'Company Name' -> 'company_name'"
    }
  ],
  "unresolved": ["marker_3"]
}
```

## Manual Mapping

For markers that were not auto-resolved, or to adjust auto-resolved mappings:

1. Open the **Mapping Panel** in the project workspace.
2. Each marker is listed with its detected type and current mapping status.
3. Click a marker to assign or change its data source and field.
4. For table markers, select the data source and sheet that should populate the table.
5. For variable placeholders, select the data source, sheet, and specific field (column).

## Mapping Entry Structure

Each mapping entry connects a marker to its data source:

```json
{
  "markerId": "marker_0",
  "dataSource": "financial_data.xlsx",
  "field": "company_name",
  "sheet": "Sheet1",
  "path": null,
  "transforms": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `markerId` | string | ID of the template marker |
| `dataSource` | string | Filename of the data source |
| `field` | string | Column name or JSON key to extract |
| `sheet` | string | Sheet name for Excel files |
| `path` | string | JSON path for nested JSON data |
| `transforms` | array | Optional transform pipeline (see below) |

## Transforms

Mappings can include a transform pipeline that processes the data before insertion. Each transform has a type and parameters:

```json
{
  "markerId": "marker_1",
  "dataSource": "data.xlsx",
  "field": "price",
  "sheet": "Sheet1",
  "transforms": [
    {
      "type": "format_number",
      "params": {"decimals": 2, "prefix": "$"}
    },
    {
      "type": "sort",
      "params": {"column": "price", "ascending": false}
    }
  ]
}
```

### Built-in Transform Types

| Type | Description | Parameters |
|------|-------------|------------|
| `rename` | Rename columns | `{"from": "old_name", "to": "new_name"}` |
| `filter` | Filter rows | `{"column": "status", "operator": "equals", "value": "active"}` |
| `sort` | Sort rows | `{"column": "name", "ascending": true}` |
| `format_date` | Format date values | `{"column": "date", "format": "%Y-%m-%d"}` |
| `format_number` | Format numeric values | `{"column": "price", "decimals": 2, "prefix": "$"}` |
| `computed` | Add computed columns | `{"expression": "col_a + col_b", "output": "total"}` |

Custom transforms can be added via the [plugin system](../plugins/developing-transforms.md).

## Conditional Sections

Mappings also support conditional section inclusion or exclusion based on data:

```json
{
  "conditionals": [
    {
      "sectionId": "section_3",
      "conditionType": "data_presence",
      "dataSource": "optional_data.xlsx",
      "include": true
    },
    {
      "sectionId": "section_5",
      "conditionType": "explicit",
      "dataSource": "config.json",
      "field": "include_appendix",
      "operator": "equals",
      "value": "true",
      "include": true
    }
  ]
}
```

### Condition Types

- **data_presence** -- Include or exclude a section based on whether a data source exists
- **explicit** -- Include or exclude based on a specific field value

### Operators for Explicit Conditions

`equals`, `not_equals`, `contains`, `gt` (greater than), `lt` (less than)

## Validation

Before generating, you can validate your mappings to catch issues early:

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/validate \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": [
      {"markerId": "marker_0", "dataSource": "data.xlsx", "field": "name"}
    ]
  }'
```

The validation endpoint returns a list of issues at `error`, `warning`, and `info` levels:

```json
[
  {
    "level": "error",
    "markerId": "marker_2",
    "message": "Field 'revenue_total' not found in data source 'data.xlsx'"
  },
  {
    "level": "warning",
    "markerId": null,
    "message": "Data source 'notes.txt' is uploaded but not mapped to any marker"
  }
]
```
