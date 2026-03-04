# Templates

DocForge templates are standard Microsoft Word `.docx` files that use red-formatted text as instructions to the document generation engine. This guide covers how to author effective templates.

## Red Text Convention

The core convention is simple: any text formatted with **exact RGB `#FF0000`** (pure red) at the Word run level is treated as an instruction to DocForge. Everything else in the template is preserved as-is in the generated output.

!!! warning "Exact Color Match Required"
    DocForge detects red text by exact RGB match at the run level. Colors like `#FF0001` or `#EE0000` will **not** be detected. Always use the exact red `#FF0000` in your Word editor.

## Marker Types

DocForge classifies red text into three marker types using a rule chain:

### 1. Sample Data

Red text found **inside a table data row** is classified as sample data. This tells DocForge that the table should be populated from an external data source.

| Name    | Department | Salary  |
|---------|-----------|---------|
| *Jane Doe* | *Engineering* | *$95,000* |

In this example, the italic red text in the data row signals that this table should be filled from a data source containing employee records.

### 2. Variable Placeholder

Red text consisting of **1-3 words with a noun or label structure** (outside of a table) is classified as a variable placeholder. These are simple value substitutions.

Examples:

- `Company Name`
- `Report Date`
- `Revenue`
- `Author`

### 3. LLM Prompt

All other red text defaults to an **LLM prompt**. This is the intended behavior -- template authors write natural language instructions in red, and the system treats them as prompts for content generation.

Examples:

- "Provide a brief executive summary of the quarterly results"
- "Analyze the revenue trends and provide recommendations"
- "Summarize the methods used in this study"

!!! note "Classification Priority"
    The rule chain evaluates in this order: sample data (in table) -> variable placeholder (1-3 words, noun/label) -> LLM prompt (default). Users can override any classification in the mapping panel.

## Template Structure

DocForge recognizes document structure through Word heading styles:

- **Heading 1, Heading 2, Heading 3** define sections
- Sections scope LLM context (each prompt only sees data from its own section by default)
- Tables with red sample data are detected and mapped to data sources

### Sections

Use standard Word heading styles to organize your template into sections. DocForge uses these to:

- Display a structured tree view of the template in the UI
- Scope LLM context to the containing section
- Enable conditional section inclusion/exclusion

### Tables

Tables in your template can be populated automatically from data sources. To indicate a table should be auto-populated:

1. Create the table with header rows in normal (black) formatting
2. Add one or more data rows with red-formatted sample values
3. DocForge detects the red sample data and maps the table to a matching data source

The table headers are used to match columns from the data source. DocForge preserves the table formatting from the template when populating rows.

## Best Practices

1. **Use clear heading structure** -- Organize templates with Heading 1/2/3 styles. This improves auto-mapping and LLM context scoping.

2. **Keep placeholders concise** -- Variable placeholders should be 1-3 descriptive words (e.g., "Company Name", not "Enter the company name here").

3. **Write specific LLM prompts** -- Instead of "Write something about the results", write "Analyze the quarterly revenue trends and highlight the top 3 growth areas".

4. **Reference data files explicitly** -- LLM prompts can reference specific data files: "Summarize the findings from quarterly_metrics.xlsx". DocForge uses these references for auto-resolution.

5. **Use sample data that matches your source** -- Red sample data in tables should resemble the actual data format (column count, data types) to improve auto-mapping confidence.

6. **Test incrementally** -- Upload and analyze your template before adding data. Check that all markers are detected and classified correctly in the analysis view.

## Broadening LLM Scope

By default, each LLM prompt only sees data from its containing section. To broaden the scope, use explicit signals in your prompt text:

- "Provide an executive summary covering all sections"
- "Summarize the entire document"
- "Analyze data from the Financial Results section"

DocForge detects these broadening signals heuristically and presents them for user confirmation in the mapping panel.
