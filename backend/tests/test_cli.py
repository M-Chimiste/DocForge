"""Tests for CLI commands using Click's CliRunner."""

import json

from click.testing import CliRunner

from cli import main


def test_analyze_outputs_json(templates_dir):
    runner = CliRunner()
    result = runner.invoke(
        main, ["analyze", "--template", str(templates_dir / "simple_placeholder.docx")]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "sections" in data
    assert "markers" in data
    assert "tables" in data


def test_analyze_mixed_markers(templates_dir):
    runner = CliRunner()
    result = runner.invoke(
        main, ["analyze", "--template", str(templates_dir / "mixed_markers.docx")]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data["sections"]) >= 3
    assert len(data["markers"]) >= 3


def test_generate_produces_output(templates_dir, data_dir, tmp_path):
    # Create a mapping file
    mapping_file = tmp_path / "mapping.json"
    mapping_data = [
        {
            "marker_id": "marker-0",
            "data_source": "config.json",
            "field": "name",
            "path": "project",
        }
    ]
    mapping_file.write_text(json.dumps(mapping_data))

    output = tmp_path / "output.docx"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "generate",
            "--template",
            str(templates_dir / "simple_placeholder.docx"),
            "--data",
            str(data_dir / "config.json"),
            "--mapping",
            str(mapping_file),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert output.exists()
    assert "Generation complete" in result.output


def test_generate_reports_failures(templates_dir, data_dir, tmp_path):
    # Empty mapping — all markers will fail
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text("[]")

    output = tmp_path / "output.docx"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "generate",
            "--template",
            str(templates_dir / "simple_placeholder.docx"),
            "--data",
            str(data_dir / "config.json"),
            "--mapping",
            str(mapping_file),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert "FAIL" in result.output


def test_analyze_missing_template():
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--template", "/nonexistent/file.docx"])
    assert result.exit_code != 0
