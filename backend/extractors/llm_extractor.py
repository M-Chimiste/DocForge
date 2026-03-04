"""LLM-based schema-driven extraction from unstructured sources."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel

from core.llm_client import LLMClient
from extractors.base import ExtractedData


class FieldSchema(BaseModel):
    name: str
    type: str = "string"  # "string", "number", "date", "boolean"
    description: str = ""


class LLMExtractionSchema(BaseModel):
    fields: list[FieldSchema]


class LLMExtractor:
    """Schema-driven extraction using an LLM.

    Not registered in ExtractorRegistry — invoked explicitly via API to
    prevent accidental LLM calls during normal data loading.
    """

    def __init__(self, llm_client: LLMClient):
        self._client = llm_client

    def extract(
        self,
        source_text: str,
        schema: LLMExtractionSchema,
        source_name: str = "extracted",
    ) -> ExtractedData:
        """Extract structured data from text using the LLM."""
        prompt = self._build_extraction_prompt(source_text, schema)
        response = self._client.complete(
            prompt,
            system=(
                "Extract structured data from the provided text. "
                "Return valid JSON only — no markdown fences, no explanation."
            ),
        )

        parsed = self._parse_json_response(response.content)

        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)
        elif isinstance(parsed, dict):
            df = pd.DataFrame([parsed])
        else:
            raise ValueError(f"LLM returned unexpected format: {type(parsed)}")

        validation_errors = self._validate_against_schema(df, schema)

        return ExtractedData(
            source_path=Path(source_name),
            dataframes={"extracted": df},
            metadata={
                "extraction_method": "llm",
                "schema": schema.model_dump(),
                "validation_errors": validation_errors,
                "llm_model": response.model,
                "tokens_used": response.total_tokens,
            },
        )

    def _build_extraction_prompt(self, text: str, schema: LLMExtractionSchema) -> str:
        field_lines = "\n".join(
            f"  - {f.name} ({f.type}): {f.description}"
            if f.description
            else f"  - {f.name} ({f.type})"
            for f in schema.fields
        )
        return (
            f"Extract the following fields from the text below:\n{field_lines}\n\n"
            f"Return a JSON array of objects. Each object should have the fields listed above.\n\n"
            f"TEXT:\n{text[:8000]}"
        )

    def _parse_json_response(self, content: str) -> Any:
        """Parse JSON from LLM response, handling markdown fences."""
        content = content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines (fences)
            lines = [line for line in lines if not line.strip().startswith("```")]
            content = "\n".join(lines).strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON array or object in the response
            match = re.search(r"(\[.*\]|\{.*\})", content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse JSON from LLM response: {content[:200]}") from None

    def _validate_against_schema(self, df: pd.DataFrame, schema: LLMExtractionSchema) -> list[str]:
        errors: list[str] = []
        for field in schema.fields:
            if field.name not in df.columns:
                errors.append(f"Missing field: {field.name}")
        return errors
