"""Error catalog: maps error codes to user-facing messages and remediation hints.

Every entry uses `.format()` style placeholders for dynamic values.
"""

from __future__ import annotations

ERROR_CATALOG: dict[str, dict[str, str]] = {
    # ── Template errors ──────────────────────────────────────────────
    "template_parse_failed": {
        "message": "Failed to parse the .docx template{detail}.",
        "remediation": (
            "Ensure the file is a valid .docx document created in Microsoft Word "
            "or a compatible editor. Re-save the file and try uploading again."
        ),
    },
    "template_not_found": {
        "message": "Template file '{path}' does not exist on disk.",
        "remediation": (
            "The template may have been deleted or moved. "
            "Re-upload the template to the project and try again."
        ),
    },
    "template_missing": {
        "message": "No template has been uploaded for this project.",
        "remediation": (
            "Upload a .docx template on the project workspace before "
            "attempting to generate a document."
        ),
    },
    # ── Data / extractor errors ──────────────────────────────────────
    "extractor_not_found": {
        "message": "No extractor available for file type '{extension}'.",
        "remediation": (
            "Supported data file types are .xlsx, .csv, and .json. "
            "Convert your data into one of these formats and re-upload."
        ),
    },
    "data_source_not_found": {
        "message": "Referenced data source '{name}' could not be found.",
        "remediation": (
            "Upload the data source to the project, or update the mapping "
            "to reference an existing data source."
        ),
    },
    "field_not_found": {
        "message": "Field '{field}' was not found in data source '{source}'.",
        "remediation": (
            "Check that the field name matches a column or key in the data source. "
            "Field names are case-sensitive."
        ),
    },
    # ── Mapping / rendering errors ───────────────────────────────────
    "no_mapping": {
        "message": "No mapping provided for marker '{marker_id}'.",
        "remediation": (
            "Open the Mapping panel and assign a data source field or LLM prompt "
            "to the highlighted marker before generating."
        ),
    },
    "no_renderer": {
        "message": "No renderer available for marker type '{marker_type}'.",
        "remediation": (
            "This marker type is not yet supported. "
            "Check that you are using the latest version of DocForge."
        ),
    },
    "render_failed": {
        "message": "Renderer failed for marker '{marker_id}': {reason}.",
        "remediation": (
            "Review the marker's mapping and data source. "
            "If the problem persists, try simplifying the template section "
            "and regenerating."
        ),
    },
    # ── LLM errors ───────────────────────────────────────────────────
    "llm_not_configured": {
        "message": "LLM features are required but no LLM provider is configured.",
        "remediation": (
            "Set your LLM API key in the project settings or server environment "
            "variables (e.g. OPENAI_API_KEY). DocForge supports OpenAI, Anthropic, "
            "and other providers via LLMFactory."
        ),
    },
    "llm_auth_failed": {
        "message": "LLM API authentication failed for provider '{provider}'.",
        "remediation": (
            "Verify that your API key is correct and has not expired. "
            "You can update the key in project settings or server configuration."
        ),
    },
    "llm_timeout": {
        "message": "LLM request timed out after {seconds} seconds.",
        "remediation": (
            "The LLM provider may be experiencing high load. "
            "Wait a moment and retry, or increase the timeout in project settings."
        ),
    },
    "llm_rate_limit": {
        "message": "LLM rate limit exceeded for provider '{provider}'.",
        "remediation": (
            "You have exceeded the API rate limit. Wait a few minutes before "
            "retrying, or upgrade your plan with the LLM provider."
        ),
    },
    # ── Upload / file errors ─────────────────────────────────────────
    "upload_too_large": {
        "message": "Uploaded file exceeds the maximum size of {max_size_mb} MB.",
        "remediation": (
            "Reduce the file size or split it into smaller parts. "
            "The upload limit can be configured in the server settings."
        ),
    },
    "invalid_file_type": {
        "message": "File type '{extension}' is not supported.",
        "remediation": (
            "Supported template types: .docx. "
            "Supported data types: .xlsx, .csv, .json. "
            "Convert your file to a supported format and try again."
        ),
    },
    # ── Resource not-found errors ────────────────────────────────────
    "project_not_found": {
        "message": "Project {project_id} does not exist.",
        "remediation": (
            "The project may have been deleted. "
            "Return to the projects list and select an existing project."
        ),
    },
    "generation_not_found": {
        "message": "Generation run {run_id} does not exist.",
        "remediation": (
            "The generation run may have been deleted or the ID is invalid. "
            "Check the generation history for available runs."
        ),
    },
    # ── Config / transform / export errors ───────────────────────────
    "invalid_mapping_config": {
        "message": "Mapping configuration is malformed: {reason}.",
        "remediation": (
            "Review the mapping JSON for syntax errors. Each entry must include "
            "'marker_id' and either a 'data_source'/'field' pair or an LLM prompt."
        ),
    },
    "transform_failed": {
        "message": "Transform '{transform}' failed for marker '{marker_id}': {reason}.",
        "remediation": (
            "Check the transform parameters and ensure the input data matches "
            "the expected format. Remove the transform to use raw values."
        ),
    },
    "export_failed": {
        "message": "Document export failed: {reason}.",
        "remediation": (
            "Try exporting again. If the issue persists, save your edits "
            "and re-generate the document from the original template."
        ),
    },
}


def get_error(code: str, **kwargs: object) -> dict[str, str]:
    """Return error dict with message and remediation, formatting with kwargs.

    Unknown placeholders are left as-is so callers can omit optional fields.
    If *code* is not in the catalog, a generic entry is returned.
    """
    entry = ERROR_CATALOG.get(code)
    if entry is None:
        return {
            "message": f"An error occurred (code: {code}).",
            "remediation": "Please try again or contact support if the issue persists.",
        }

    # Provide safe defaults for any missing kwargs so .format() doesn't blow up.
    # We first discover which keys the templates expect, then fill in blanks.
    import string

    def _safe_format(template: str) -> str:
        # Collect field names referenced in the template
        field_names = [
            fname for _, fname, _, _ in string.Formatter().parse(template) if fname is not None
        ]
        # Build a defaults dict: use kwargs if present, else leave placeholder
        merged = {name: kwargs.get(name, f"<{name}>") for name in field_names}
        return template.format(**merged)

    return {
        "message": _safe_format(entry["message"]),
        "remediation": _safe_format(entry["remediation"]),
    }
