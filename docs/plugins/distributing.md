# Distributing Plugins

This guide covers how to package, publish, and install DocForge plugins.

## Package Structure

A DocForge plugin is a standard Python package with an entry point declaration. The minimal structure:

```
docforge-my-plugin/
  pyproject.toml
  docforge_my_plugin/
    __init__.py
    plugin.py
  tests/
    test_plugin.py
  README.md
  LICENSE
```

## pyproject.toml

The `pyproject.toml` file defines your package metadata and the critical entry point that DocForge uses for discovery:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "docforge-my-plugin"
version = "0.1.0"
description = "DocForge plugin: description of what it does."
requires-python = ">=3.12"
license = "MIT"
authors = [
    {name = "Your Name", email = "you@example.com"},
]
dependencies = [
    "docforge",
]

[project.urls]
Homepage = "https://github.com/yourname/docforge-my-plugin"

# Entry point -- choose the appropriate group:
# docforge.renderers, docforge.extractors, or docforge.transforms

[project.entry-points."docforge.renderers"]
my_renderer = "docforge_my_plugin.plugin:MyRenderer"
```

### Entry Point Groups

| Plugin Type | Group | Example |
|------------|-------|---------|
| Renderer | `docforge.renderers` | `markdown = "pkg.module:MarkdownRenderer"` |
| Extractor | `docforge.extractors` | `xml = "pkg.module:XmlExtractor"` |
| Transform | `docforge.transforms` | `currency_convert = "pkg.module:CurrencyConvertTransform"` |

The entry point key (left side of `=`) becomes the plugin name shown in the plugins API. The value (right side) is the dotted import path to your class.

## Naming Conventions

- **Package name**: `docforge-<description>` (e.g., `docforge-xml-extractor`, `docforge-markdown-renderer`)
- **Module name**: `docforge_<description>` with underscores (e.g., `docforge_xml_extractor`)
- **Entry point key**: A short, descriptive name matching your `can_handle()` check

## Local Development

During development, install your plugin in editable mode:

```bash
cd docforge-my-plugin
pip install -e .
```

This registers the entry point immediately. Restart the DocForge server to pick up the new plugin.

Verify your plugin is discovered:

```bash
curl http://localhost:8000/api/v1/plugins
```

## Publishing to PyPI

### 1. Prepare the Package

Ensure your `pyproject.toml` has complete metadata:

- `name`, `version`, `description`
- `license`
- `authors`
- `requires-python`
- `dependencies` (include `docforge` as a dependency)
- `project.urls` (homepage, repository)

### 2. Build the Distribution

```bash
pip install build
python -m build
```

This creates `dist/docforge-my-plugin-0.1.0.tar.gz` and `dist/docforge_my_plugin-0.1.0-py3-none-any.whl`.

### 3. Upload to PyPI

```bash
pip install twine
twine upload dist/*
```

### 4. Install from PyPI

Users can then install your plugin with:

```bash
pip install docforge-my-plugin
```

## Docker Deployment

When deploying DocForge with Docker, add your plugin to the Docker image. Create a custom `Dockerfile`:

```dockerfile
FROM docforge/docforge:latest

RUN pip install docforge-my-plugin
```

Or add it to a `requirements.txt` and install during the build:

```dockerfile
FROM docforge/docforge:latest

COPY requirements-plugins.txt .
RUN pip install -r requirements-plugins.txt
```

## Versioning

Follow semantic versioning for your plugins:

- **Patch** (0.1.1): Bug fixes
- **Minor** (0.2.0): New features, backward compatible
- **Major** (1.0.0): Breaking changes

Pin your `docforge` dependency to a compatible range:

```toml
dependencies = [
    "docforge>=0.1.0,<1.0.0",
]
```

## Testing Your Plugin

### Unit Tests

Test your plugin class in isolation:

```bash
cd docforge-my-plugin
pip install -e ".[dev]"
pytest
```

### Integration Tests

Test that your plugin is properly discovered by DocForge:

```python
from core.plugin_loader import discover_plugins

def test_plugin_discovered():
    plugins = discover_plugins("docforge.renderers")
    names = [type(p).__name__ for p in plugins]
    assert "MyRenderer" in names
```

### Manual Testing

1. Install the plugin into the DocForge environment.
2. Start the server.
3. Verify the plugin appears in `GET /api/v1/plugins`.
4. Create a project with data that exercises your plugin.
5. Run generation and verify the output.

## Fail-Forward Behavior

DocForge uses a fail-forward pattern for plugin loading. If your plugin fails to load (import error, initialization error, etc.):

- A warning is logged with the error details.
- The application continues to start normally.
- Other plugins are unaffected.
- Your plugin simply will not be available.

This means a broken plugin never prevents DocForge from running. Check the server logs if your plugin is not appearing in the plugins list.
