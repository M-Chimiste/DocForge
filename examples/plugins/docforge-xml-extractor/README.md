# docforge-xml-extractor

A DocForge extractor plugin that reads `.xml` files and converts them into
pandas DataFrames for use in document generation.

## How it works

This plugin registers itself under the `docforge.extractors` entry-point
group.  When DocForge encounters a data source with a `.xml` extension, this
extractor takes over.  It:

1. Parses the XML using `xml.etree.ElementTree`.
2. Flattens the first level of repeated child elements into rows.
3. Promotes element attributes and sub-element text to columns.
4. Returns an `ExtractedData` object with the resulting DataFrame.

## Example

Given this XML:

```xml
<employees>
  <employee id="1" department="eng">
    <name>Alice</name>
    <title>Developer</title>
  </employee>
  <employee id="2" department="sales">
    <name>Bob</name>
    <title>Manager</title>
  </employee>
</employees>
```

The extractor produces a DataFrame with columns `id`, `department`, `name`,
`title` and two rows.

## Installation

```bash
pip install -e .
```

After installation, DocForge discovers the plugin automatically -- no
configuration needed.

## Running tests

```bash
pytest tests/
```
