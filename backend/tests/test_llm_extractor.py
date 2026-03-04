"""Tests for extractors.llm_extractor — LLM-based schema-driven extraction."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from core.llm_client import LLMClient, LLMConfig, LLMResponse
from extractors.llm_extractor import FieldSchema, LLMExtractionSchema, LLMExtractor


def _make_mock_client(response_content: str) -> LLMClient:
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    client.complete = MagicMock(
        return_value=LLMResponse(
            content=response_content,
            model="gpt-4o-mini",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
    )
    return client


def _make_schema(*fields: tuple[str, str]) -> LLMExtractionSchema:
    return LLMExtractionSchema(fields=[FieldSchema(name=n, type=t) for n, t in fields])


class TestBasicExtraction:
    def test_extract_json_array(self):
        data = json.dumps(
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        )
        client = _make_mock_client(data)
        schema = _make_schema(("name", "string"), ("age", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("Some text about Alice and Bob", schema)

        df = result.dataframes["extracted"]
        assert len(df) == 2
        assert list(df.columns) == ["name", "age"]
        assert df.iloc[0]["name"] == "Alice"
        assert result.metadata["extraction_method"] == "llm"
        assert result.metadata["tokens_used"] == 150

    def test_extract_json_object(self):
        data = json.dumps({"title": "Report", "year": 2024})
        client = _make_mock_client(data)
        schema = _make_schema(("title", "string"), ("year", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("A report from 2024", schema)

        df = result.dataframes["extracted"]
        assert len(df) == 1
        assert df.iloc[0]["title"] == "Report"


class TestJsonParsing:
    def test_markdown_fenced_json(self):
        content = '```json\n[{"name": "Alice"}]\n```'
        client = _make_mock_client(content)
        schema = _make_schema(("name", "string"))
        extractor = LLMExtractor(client)

        result = extractor.extract("text", schema)

        df = result.dataframes["extracted"]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "Alice"

    def test_json_with_surrounding_text(self):
        content = 'Here is the data:\n[{"x": 1}]\nEnd.'
        client = _make_mock_client(content)
        schema = _make_schema(("x", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("text", schema)

        df = result.dataframes["extracted"]
        assert len(df) == 1

    def test_invalid_json_raises(self):
        client = _make_mock_client("This is not JSON at all")
        schema = _make_schema(("name", "string"))
        extractor = LLMExtractor(client)

        with pytest.raises(ValueError, match="Could not parse JSON"):
            extractor.extract("text", schema)


class TestSchemaValidation:
    def test_all_fields_present(self):
        data = json.dumps([{"name": "Alice", "age": 30}])
        client = _make_mock_client(data)
        schema = _make_schema(("name", "string"), ("age", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("text", schema)

        assert result.metadata["validation_errors"] == []

    def test_missing_field_reported(self):
        data = json.dumps([{"name": "Alice"}])
        client = _make_mock_client(data)
        schema = _make_schema(("name", "string"), ("age", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("text", schema)

        assert len(result.metadata["validation_errors"]) == 1
        assert "age" in result.metadata["validation_errors"][0]

    def test_extra_fields_not_errors(self):
        data = json.dumps([{"name": "Alice", "age": 30, "city": "NYC"}])
        client = _make_mock_client(data)
        schema = _make_schema(("name", "string"), ("age", "number"))
        extractor = LLMExtractor(client)

        result = extractor.extract("text", schema)

        assert result.metadata["validation_errors"] == []


class TestPromptConstruction:
    def test_prompt_includes_field_names(self):
        data = json.dumps([{"name": "X"}])
        client = _make_mock_client(data)
        schema = LLMExtractionSchema(
            fields=[
                FieldSchema(name="project_name", type="string", description="Name of the project"),
                FieldSchema(name="budget", type="number"),
            ]
        )
        extractor = LLMExtractor(client)

        extractor.extract("Some project text here", schema)

        prompt = client.complete.call_args[0][0]
        assert "project_name" in prompt
        assert "budget" in prompt
        assert "Name of the project" in prompt
        assert "Some project text" in prompt

    def test_long_text_truncated(self):
        long_text = "x" * 20000
        data = json.dumps([{"a": 1}])
        client = _make_mock_client(data)
        schema = _make_schema(("a", "number"))
        extractor = LLMExtractor(client)

        extractor.extract(long_text, schema)

        prompt = client.complete.call_args[0][0]
        assert len(prompt) < 10000
