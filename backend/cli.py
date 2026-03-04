"""DocForge CLI — template-driven document generation."""

from __future__ import annotations

import json
from pathlib import Path

import click

from core.engine import GenerationEngine
from core.models import MappingEntry


@click.group()
def main():
    """DocForge — template-driven document generation."""
    pass


@main.command()
@click.option(
    "--template", required=True, type=click.Path(exists=True), help="Path to .docx template"
)
def analyze(template: str):
    """Parse a template and output analysis JSON."""
    engine = GenerationEngine()
    analysis = engine.analyze(Path(template))
    click.echo(json.dumps(analysis.model_dump(mode="json"), indent=2))


@main.command()
@click.option(
    "--template", required=True, type=click.Path(exists=True), help="Path to .docx template"
)
@click.option(
    "--data", required=True, multiple=True, type=click.Path(exists=True), help="Data source files"
)
@click.option(
    "--mapping", required=True, type=click.Path(exists=True), help="JSON file with mappings"
)
@click.option("--output", required=True, type=click.Path(), help="Output .docx path")
def generate(template: str, data: tuple, mapping: str, output: str):
    """Generate a document from template + data."""
    engine = GenerationEngine()

    with open(mapping) as f:
        mapping_data = json.load(f)
    mappings = [MappingEntry(**m) for m in mapping_data]

    results = engine.generate(
        Path(template),
        [Path(d) for d in data],
        mappings,
        Path(output),
    )

    click.echo(
        f"Generation complete. "
        f"{sum(1 for r in results if r.success)}/{len(results)} markers rendered."
    )
    for r in results:
        status = "OK" if r.success else f"FAIL: {r.error}"
        click.echo(f"  {r.marker_id}: {status}")


if __name__ == "__main__":
    main()
