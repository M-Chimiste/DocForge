# Troubleshooting

This page covers common errors you may encounter when using DocForge, organized by error code. Each entry includes the error message, likely cause, and resolution steps.

## Template Errors

### `template_parse_failed`

**Message:** "Failed to parse the .docx template."

**Cause:** The uploaded file is not a valid `.docx` document, or it is corrupted.

**Resolution:**

1. Ensure the file is a valid `.docx` document created in Microsoft Word or a compatible editor (Google Docs export, LibreOffice).
2. Open the file in Word to verify it loads correctly.
3. Re-save the file in `.docx` format and try uploading again.
4. Files in `.doc` (legacy Word) format are not supported -- save as `.docx`.

### `template_not_found`

**Message:** "Template file does not exist on disk."

**Cause:** The template file was deleted or moved after it was uploaded to the project.

**Resolution:**

1. Re-upload the template to the project.
2. Check the server's upload directory to ensure files are persisted correctly.

### `template_missing`

**Message:** "No template has been uploaded for this project."

**Cause:** You attempted to generate a document or auto-resolve mappings without first uploading a template.

**Resolution:**

1. Upload a `.docx` template on the project workspace before attempting generation.

### Red text not detected

**Cause:** The text is not formatted with exact RGB `#FF0000` at the Word run level.

**Resolution:**

1. In Microsoft Word, select the text and set the font color to exact red (`#FF0000`).
2. Avoid using theme colors or approximate reds -- DocForge requires an exact match.
3. Check that the entire run is red, not just part of it. Split formatting within a Word run may not be detected.
4. Re-upload the template and verify the analysis shows the expected markers.

## Data / Extractor Errors

### `extractor_not_found`

**Message:** "No extractor available for file type '{extension}'."

**Cause:** The uploaded data file has an extension that no extractor supports.

**Resolution:**

1. Supported data file types are `.xlsx`, `.csv`, `.json`, `.txt`, `.docx`, `.pptx`, `.pdf`, `.yaml`, and `.yml`.
2. Convert your data into one of these formats and re-upload.
3. If you need support for a custom format, consider building an [extractor plugin](plugins/developing-extractors.md).

### `data_source_not_found`

**Message:** "Referenced data source could not be found."

**Cause:** A mapping references a data source that is not uploaded to the project.

**Resolution:**

1. Upload the referenced data source to the project.
2. Or update the mapping to reference an existing data source.
3. Check for typos in the data source filename.

### `field_not_found`

**Message:** "Field '{field}' was not found in data source '{source}'."

**Cause:** The mapping references a column or key that does not exist in the data source.

**Resolution:**

1. Check that the field name matches a column header (for Excel/CSV) or JSON key exactly. Field names are **case-sensitive**.
2. Use the data preview endpoint to verify available column names:
   ```bash
   curl "http://localhost:8000/api/v1/projects/{id}/data-sources/{filename}/preview"
   ```
3. Update the mapping with the correct field name.

## Mapping / Rendering Errors

### `no_mapping`

**Message:** "No mapping provided for marker '{marker_id}'."

**Cause:** A template marker has no mapping assigned, and it cannot be rendered.

**Resolution:**

1. Open the Mapping Panel and assign a data source and field to the highlighted marker.
2. Run auto-resolution to attempt automatic mapping:
   ```bash
   curl -X POST http://localhost:8000/api/v1/projects/{id}/auto-resolve
   ```
3. LLM prompt markers without a mapping are skipped during generation (not treated as errors).

### `no_renderer`

**Message:** "No renderer available for marker type '{marker_type}'."

**Cause:** The marker type is not supported by any registered renderer.

**Resolution:**

1. Check that you are using the latest version of DocForge.
2. If this is a custom marker type, ensure the appropriate renderer plugin is installed.
3. Check installed plugins:
   ```bash
   curl http://localhost:8000/api/v1/plugins
   ```

### `render_failed`

**Message:** "Renderer failed for marker '{marker_id}'."

**Cause:** The renderer encountered an error while processing the marker. Common causes include data type mismatches, missing data, or corrupt template structure.

**Resolution:**

1. Review the marker's mapping and data source.
2. Verify the data source contains the expected values.
3. Try simplifying the template section (remove complex formatting) and regenerate.
4. Check the generation report for the specific error details.

## LLM Errors

### `llm_not_configured`

**Message:** "LLM features are required but no LLM provider is configured."

**Cause:** The template contains LLM prompt markers, but no LLM provider is set up.

**Resolution:**

1. Set your LLM API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
2. Or configure LLM settings in the project:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/projects/{id}/llm-config \
     -H "Content-Type: application/json" \
     -d '{"provider": "openai", "model": "gpt-4o"}'
   ```
3. DocForge supports OpenAI, Anthropic, and other providers via LiteLLM.
4. If you do not need LLM features, the generation will still produce output with LLM markers left as original red text.

### `llm_auth_failed`

**Message:** "LLM API authentication failed for provider '{provider}'."

**Cause:** The API key is invalid, expired, or not set.

**Resolution:**

1. Verify your API key is correct and has not expired.
2. Check the environment variable is set:
   ```bash
   echo $OPENAI_API_KEY  # or ANTHROPIC_API_KEY
   ```
3. Test the connection:
   ```bash
   curl -X POST http://localhost:8000/api/v1/projects/{id}/llm-test
   ```
4. Update the key in project settings or server configuration.

### `llm_timeout`

**Message:** "LLM request timed out after {seconds} seconds."

**Cause:** The LLM provider is slow or experiencing high load.

**Resolution:**

1. Wait a moment and retry the generation.
2. Increase the timeout in project settings.
3. Consider using a faster model or a local model.
4. If using a local model (Ollama, LM Studio), ensure it is running and responsive.

### `llm_rate_limit`

**Message:** "LLM rate limit exceeded for provider '{provider}'."

**Cause:** Too many API requests in a short period.

**Resolution:**

1. Wait a few minutes before retrying.
2. Reduce the number of LLM prompt markers in the template.
3. Upgrade your plan with the LLM provider for higher rate limits.

## Upload / File Errors

### `upload_too_large`

**Message:** "Uploaded file exceeds the maximum size of {max_size_mb} MB."

**Cause:** The file is larger than the server's upload limit.

**Resolution:**

1. Reduce the file size or split it into smaller parts.
2. The upload limit can be configured in the server settings.

### `invalid_file_type`

**Message:** "File type '{extension}' is not supported."

**Cause:** The uploaded file has an unsupported extension.

**Resolution:**

1. Supported template types: `.docx`.
2. Supported data types: `.xlsx`, `.csv`, `.json`, `.txt`, `.docx`, `.pptx`, `.pdf`, `.yaml`, `.yml`.
3. Convert your file to a supported format and try again.

## Resource Errors

### `project_not_found`

**Message:** "Project {project_id} does not exist."

**Cause:** The project ID in the URL does not correspond to any existing project.

**Resolution:**

1. The project may have been deleted.
2. Return to the projects list and select an existing project.
3. List all projects:
   ```bash
   curl http://localhost:8000/api/v1/projects
   ```

### `generation_not_found`

**Message:** "Generation run {run_id} does not exist."

**Cause:** The generation run ID is invalid or the run was deleted.

**Resolution:**

1. Check the generation history for the project:
   ```bash
   curl http://localhost:8000/api/v1/projects/{id}/generations
   ```
2. Use a valid run ID from the list.

## Configuration / Transform Errors

### `invalid_mapping_config`

**Message:** "Mapping configuration is malformed."

**Cause:** The mapping JSON sent in the request body has syntax errors or missing required fields.

**Resolution:**

1. Review the mapping JSON for syntax errors.
2. Each entry must include `markerId` and `dataSource`.
3. Validate your JSON before sending:
   ```bash
   echo '{"mappings": [...]}' | python -m json.tool
   ```

### `transform_failed`

**Message:** "Transform '{transform}' failed for marker '{marker_id}'."

**Cause:** A data transform in the mapping pipeline failed, typically due to a missing column, invalid parameter, or data type mismatch.

**Resolution:**

1. Check the transform parameters and ensure the input data matches the expected format.
2. Remove the transform to use raw values and verify the data is correct.
3. Use the data preview to check column names and data types.

### `export_failed`

**Message:** "Document export failed."

**Cause:** The editor-to-docx conversion or file writing failed.

**Resolution:**

1. Try exporting again.
2. If the issue persists, save your edits and re-generate the document from the original template.
3. Check that the server has write permissions to the output directory.

## General Debugging Tips

1. **Check the server logs** -- The backend logs detailed information about errors, including stack traces for unexpected failures.

2. **Use the validation endpoint** -- Before generating, validate your mappings to catch configuration issues early:
   ```bash
   curl -X POST http://localhost:8000/api/v1/projects/{id}/validate \
     -H "Content-Type: application/json" \
     -d '{"mappings": [...]}'
   ```

3. **Check the generation report** -- After generation, the report contains detailed information about which markers succeeded, failed, or were skipped.

4. **Preview your data** -- Use the data preview endpoint to verify that data sources were extracted correctly before mapping.

5. **Test LLM connectivity** -- Use the LLM test endpoint to verify your provider configuration before generation:
   ```bash
   curl -X POST http://localhost:8000/api/v1/projects/{id}/llm-test
   ```
