# docforge-markdown-renderer

A DocForge renderer plugin that converts basic Markdown formatting into Word
document runs with bold, italic, and heading styles.

## How it works

This plugin registers itself under the `docforge.renderers` entry-point group.
When DocForge encounters an `LLM_PROMPT` marker whose text starts with
`[markdown]`, this renderer takes over.  It:

1. Resolves the content from the mapped data source.
2. Parses basic Markdown: `**bold**`, `*italic*`, `***bold italic***`, and
   headings (`#`, `##`, `###`).
3. Writes the result into the document paragraph with appropriate run-level
   formatting.

## Installation

```bash
pip install -e .
```

After installation, DocForge discovers the plugin automatically -- no
configuration needed.

## Supported Markdown

| Syntax | Result |
|--------|--------|
| `**text**` | Bold |
| `*text*` | Italic |
| `***text***` | Bold + Italic |
| `# Heading` | Bold, 16pt |
| `## Heading` | Bold, 14pt |
| `### Heading` | Bold, 12pt |

## Running tests

```bash
pytest tests/
```
