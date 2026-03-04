"""Script to programmatically create .docx test fixtures.

Run: conda run -n docforge python tests/fixtures/create_fixtures.py
"""

from pathlib import Path

from docx import Document
from docx.shared import RGBColor

FIXTURES_DIR = Path(__file__).parent
TEMPLATES_DIR = FIXTURES_DIR / "templates"
DATA_DIR = FIXTURES_DIR / "data"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _add_red_text(paragraph, text):
    """Add a red-colored run to a paragraph."""
    run = paragraph.add_run(text)
    run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
    return run


def create_simple_placeholder():
    """Create a doc with one heading and one red text placeholder."""
    doc = Document()
    doc.add_heading("Introduction", level=1)
    para = doc.add_paragraph("The project name is ")
    _add_red_text(para, "Project Name")
    para.add_run(".")
    doc.save(str(TEMPLATES_DIR / "simple_placeholder.docx"))
    print("Created simple_placeholder.docx")


def create_simple_table():
    """Create a doc with one heading and one skeleton table."""
    doc = Document()
    doc.add_heading("Metrics", level=1)
    doc.add_paragraph("The following table shows key metrics:")
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    headers = table.rows[0].cells
    headers[0].text = "Metric"
    headers[1].text = "Value"
    headers[2].text = "Target"
    doc.save(str(TEMPLATES_DIR / "simple_table.docx"))
    print("Created simple_table.docx")


def create_mixed_markers():
    """Create a doc with placeholders, a table, and an LLM prompt marker."""
    doc = Document()

    # Section 1 with placeholders
    doc.add_heading("Project Overview", level=1)
    p1 = doc.add_paragraph("Report prepared by ")
    _add_red_text(p1, "Author")
    p1.add_run(" on ")
    _add_red_text(p1, "Report Date")
    p1.add_run(".")

    # Section 2 with a skeleton table
    doc.add_heading("Key Metrics", level=1)
    doc.add_paragraph("Below are the quarterly metrics:")
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    headers = table.rows[0].cells
    headers[0].text = "Quarter"
    headers[1].text = "Revenue"
    headers[2].text = "Growth"

    # Section 3 with an LLM prompt
    doc.add_heading("Executive Summary", level=1)
    p2 = doc.add_paragraph()
    _add_red_text(
        p2,
        "Provide an executive summary covering the key findings from the quarterly data",
    )

    doc.save(str(TEMPLATES_DIR / "mixed_markers.docx"))
    print("Created mixed_markers.docx")


def create_table_with_sample_data():
    """Create a doc with a skeleton table containing red sample data rows."""
    doc = Document()
    doc.add_heading("Project Status", level=1)
    table = doc.add_table(rows=3, cols=3)
    table.style = "Table Grid"
    # Header row
    headers = table.rows[0].cells
    headers[0].text = "Project"
    headers[1].text = "Status"
    headers[2].text = "Progress"
    # Sample data rows in red
    for row_idx in range(1, 3):
        for col_idx in range(3):
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = ""  # Clear default
            para = cell.paragraphs[0]
            sample_texts = [
                ["Alpha", "Active", "75%"],
                ["Beta", "Planning", "20%"],
            ]
            _add_red_text(para, sample_texts[row_idx - 1][col_idx])

    doc.save(str(TEMPLATES_DIR / "table_with_sample_data.docx"))
    print("Created table_with_sample_data.docx")


def create_data_fixtures():
    """Create test data files."""
    import json

    import pandas as pd

    # Excel with two sheets
    with pd.ExcelWriter(str(DATA_DIR / "metrics.xlsx"), engine="openpyxl") as writer:
        df1 = pd.DataFrame(
            {
                "Quarter": ["Q1", "Q2", "Q3", "Q4"],
                "Revenue": [100000, 120000, 115000, 140000],
                "Growth": [0.05, 0.20, -0.04, 0.22],
            }
        )
        df1.to_excel(writer, sheet_name="Revenue", index=False)
        df2 = pd.DataFrame(
            {
                "Metric": ["Users", "Sessions", "Conversions"],
                "Value": [5000, 25000, 500],
                "Target": [4500, 20000, 450],
            }
        )
        df2.to_excel(writer, sheet_name="KPIs", index=False)
    print("Created metrics.xlsx")

    # CSV
    df_csv = pd.DataFrame(
        {
            "Project": ["Alpha", "Beta", "Gamma", "Delta"],
            "Status": ["Active", "Planning", "Complete", "Active"],
            "Progress": [75, 20, 100, 45],
            "Lead": ["Alice", "Bob", "Carol", "Dave"],
        }
    )
    df_csv.to_csv(str(DATA_DIR / "project_status.csv"), index=False)
    print("Created project_status.csv")

    # JSON
    config = {
        "project": {
            "name": "DocForge Demo",
            "date": "2026-03-03",
            "version": "1.0",
        },
        "settings": {"author": "Test Author", "department": "Engineering"},
    }
    with open(DATA_DIR / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Created config.json")


if __name__ == "__main__":
    create_simple_placeholder()
    create_simple_table()
    create_mixed_markers()
    create_table_with_sample_data()
    create_data_fixtures()
    print("\nAll fixtures created successfully!")
