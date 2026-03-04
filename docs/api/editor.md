# Editor API

The editor API provides document retrieval, persistence, section regeneration, and export for the built-in WYSIWYG editor.

## Get Editor Document

```
GET /api/v1/generations/{run_id}/document
```

Retrieve the generated document in TipTap-compatible JSON format for the editor.

If the user has previously saved edits, the saved editor state is returned. Otherwise, the output `.docx` is converted on-the-fly to editor format and cached for future requests.

**Response:** `200 OK`

Returns the `EditorDocument` JSON structure containing document content, metadata, marker annotations, and confidence scores.

**curl Example:**

```bash
curl http://localhost:8000/api/v1/generations/1/document
```

## Save Editor State

```
PUT /api/v1/generations/{run_id}/document
```

Persist the current editor state to the database. This saves all user edits and can be retrieved later.

**Request Body:** The full editor state as TipTap-compatible JSON.

**Response:** `200 OK`

```json
{
  "status": "saved"
}
```

**curl Example:**

```bash
curl -X PUT http://localhost:8000/api/v1/generations/1/document \
  -H "Content-Type: application/json" \
  -d '{ ... editor state JSON ... }'
```

## Regenerate a Section

```
POST /api/v1/generations/{run_id}/regenerate-section
```

Re-run the LLM for a specific marker, optionally with a modified prompt. Returns new text content that the frontend patches into the editor state. This does not create a new generation run.

**Request Body:**

```json
{
  "markerId": "marker_2",
  "modifiedPrompt": "Provide a more concise summary focusing on revenue growth"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `markerId` | string | Yes | ID of the marker to regenerate |
| `modifiedPrompt` | string | No | Alternative prompt text (uses original if omitted) |

**Response:** `200 OK`

```json
{
  "content": "Revenue grew by 15% year-over-year, driven primarily by expansion in the enterprise segment...",
  "llmUsage": {
    "model": "gpt-4o",
    "prompt_tokens": 450,
    "completion_tokens": 120
  }
}
```

!!! note "LLM Required"
    This endpoint requires an LLM to be configured. Returns a `400` error with code `llm_not_configured` if no LLM is available.

**Process:**

1. Loads the template analysis and mapping snapshot from the generation run.
2. Loads the project's data sources for context assembly.
3. Assembles the LLM context using the section-scoped strategy.
4. Calls the LLM with the original or modified prompt.
5. Returns the generated text.

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/generations/1/regenerate-section \
  -H "Content-Type: application/json" \
  -d '{"markerId": "marker_2", "modifiedPrompt": "Write a brief summary of key findings"}'
```

## Export Document

```
POST /api/v1/generations/{run_id}/export
```

Convert the current editor state back to a `.docx` file and download it.

- If no editor state exists (no user edits), returns the original generated `.docx`.
- If edits exist, converts the editor state back to `.docx` using the original template as a formatting reference.

**Response:** File download with `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`

The response includes a `Content-Disposition` header with the filename `docforge_export_{run_id}.docx`.

**curl Example:**

```bash
curl -O -J http://localhost:8000/api/v1/generations/1/export
```

## Response Schemas

### RegenerateSectionResponse

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Generated text content |
| `llmUsage` | object or null | LLM usage statistics |
| `llmUsage.model` | string | Model used for generation |
| `llmUsage.prompt_tokens` | integer | Tokens in the prompt |
| `llmUsage.completion_tokens` | integer | Tokens in the response |

## Error Responses

| Error Code | Status | Description |
|-----------|--------|-------------|
| `generation_not_found` | 404 | Generation run does not exist |
| `output_missing` | 404 | Generated document file not found on disk |
| `llm_not_configured` | 400 | LLM features required but not configured |
| `marker_not_found` | 404 | Specified marker not found in template analysis |
| `no_analysis` | 400 | No template analysis available for the run |
| `template_not_found` | 400 | Template file not found (needed for export formatting) |
