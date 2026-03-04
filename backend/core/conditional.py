"""Conditional section evaluation for include/exclude logic."""

from __future__ import annotations

from docx import Document

from core.data_loader import DataStore
from core.models import ConditionalConfig, TemplateAnalysis


def evaluate_condition(config: ConditionalConfig, data_store: DataStore) -> bool:
    """Evaluate a conditional configuration against the data store.

    Returns True if the section should be included.
    """
    if config.condition_type == "data_presence":
        result = _check_data_presence(config, data_store)
    elif config.condition_type == "explicit":
        result = _check_explicit_condition(config, data_store)
    else:
        result = True

    return result if config.include else not result


def _check_data_presence(config: ConditionalConfig, data_store: DataStore) -> bool:
    """Include if the specified data source/field exists and has data."""
    if not config.data_source:
        return False

    source = data_store.get(config.data_source)
    if source is None:
        return False

    if config.field:
        for df in source.dataframes.values():
            if config.field in df.columns and not df[config.field].dropna().empty:
                return True
        return False

    return bool(source.dataframes or source.text_content)


def _check_explicit_condition(config: ConditionalConfig, data_store: DataStore) -> bool:
    """Evaluate explicit GUI-configured condition."""
    if not config.data_source or not config.field or not config.operator:
        return True

    df = data_store.get_dataframe(config.data_source)
    if df is None or config.field not in df.columns:
        return False

    value = df.iloc[0][config.field]
    compare_value = config.value

    ops = {
        "equals": lambda a, b: str(a).lower() == str(b).lower(),
        "not_equals": lambda a, b: str(a).lower() != str(b).lower(),
        "contains": lambda a, b: str(b).lower() in str(a).lower(),
        "gt": lambda a, b: float(a) > float(b),
        "lt": lambda a, b: float(a) < float(b),
    }

    op_func = ops.get(config.operator)
    if op_func is None:
        return True

    try:
        return op_func(value, compare_value)
    except (ValueError, TypeError):
        return False


def remove_section_content(
    document: Document, section_id: str, analysis: TemplateAnalysis
) -> list[str]:
    """Remove all content belonging to a section from the document.

    Returns list of marker IDs that were in the removed section.
    """
    section = next((s for s in analysis.sections if s.id == section_id), None)
    if not section:
        return []

    removed_markers = [m.id for m in section.markers]

    # Find paragraph range
    section_idx = next(i for i, s in enumerate(analysis.sections) if s.id == section_id)
    start_idx = section.paragraph_index

    if section_idx + 1 < len(analysis.sections):
        end_idx = analysis.sections[section_idx + 1].paragraph_index
    else:
        end_idx = len(document.paragraphs)

    # Remove paragraphs in reverse order to preserve indices
    body = document.element.body
    paragraphs_to_remove = list(document.paragraphs[start_idx:end_idx])
    for para in reversed(paragraphs_to_remove):
        body.remove(para._element)

    return removed_markers
