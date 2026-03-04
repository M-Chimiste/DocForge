# Plugin Development Overview

DocForge supports three types of plugins that extend the core pipeline:

- **Renderers** -- Handle new marker types or custom rendering logic
- **Extractors** -- Support new data file formats
- **Transforms** -- Add custom data transformation operations

Plugins are discovered automatically at startup via Python entry points. Install a plugin package into the same environment as DocForge, and it is picked up without any configuration changes.

## Plugin Architecture

DocForge uses a **Strategy + Registry** pattern for all three plugin types. Each plugin type has:

1. An **abstract base class** defining the interface (`BaseRenderer`, `BaseExtractor`, `BaseTransform`)
2. A **registry** that holds all available implementations
3. A **discovery mechanism** via Python entry points

At startup, each registry calls `load_plugins()`, which uses `importlib.metadata.entry_points()` to discover and instantiate third-party plugins.

## Entry Point Groups

| Plugin Type | Entry Point Group |
|------------|-------------------|
| Renderers | `docforge.renderers` |
| Extractors | `docforge.extractors` |
| Transforms | `docforge.transforms` |

## How Discovery Works

The plugin loader (`core/plugin_loader.py`) performs the following:

1. Queries Python's `importlib.metadata` for all entry points in the target group.
2. For each entry point, loads the class and instantiates it.
3. Registers the instance with the appropriate registry.
4. Failed loads are logged as warnings but never crash the application (fail-forward pattern).

```python
# Simplified discovery logic
import importlib.metadata

def discover_plugins(group: str) -> list:
    instances = []
    for ep in importlib.metadata.entry_points(group=group):
        cls = ep.load()
        instances.append(cls())
    return instances
```

## Listing Installed Plugins

You can query the API to see all installed plugins:

```bash
curl http://localhost:8000/api/v1/plugins
```

Response:

```json
[
  {
    "name": "markdown",
    "group": "renderers",
    "package": "docforge-markdown-renderer",
    "version": "0.1.0"
  },
  {
    "name": "xml",
    "group": "extractors",
    "package": "docforge-xml-extractor",
    "version": "0.1.0"
  }
]
```

## Example Plugins

DocForge ships with three example plugins in the `examples/plugins/` directory:

| Plugin | Type | Description |
|--------|------|-------------|
| `docforge-markdown-renderer` | Renderer | Renders `[markdown]`-prefixed LLM prompts with bold/italic formatting |
| `docforge-xml-extractor` | Extractor | Extracts tabular data from XML files |
| `docforge-currency-transform` | Transform | Multiplies numeric columns by an exchange rate |

These examples serve as starting points for building your own plugins. See the type-specific guides for detailed walkthroughs:

- [Custom Renderers](developing-renderers.md)
- [Custom Extractors](developing-extractors.md)
- [Custom Transforms](developing-transforms.md)
- [Distribution](distributing.md)

## Quick Start: Creating a Plugin

Every DocForge plugin follows the same structure:

```
docforge-my-plugin/
  pyproject.toml           # Package metadata + entry point declaration
  docforge_my_plugin/
    __init__.py
    plugin.py              # Your plugin class
  tests/
    test_plugin.py
```

The `pyproject.toml` declares the entry point:

```toml
[project.entry-points."docforge.renderers"]
my_renderer = "docforge_my_plugin.plugin:MyRenderer"
```

Install the plugin:

```bash
pip install -e ./docforge-my-plugin
```

Restart DocForge, and the plugin is automatically discovered and registered.
