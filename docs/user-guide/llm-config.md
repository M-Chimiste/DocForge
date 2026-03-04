# LLM Configuration

DocForge integrates with LLM providers via [LiteLLM](https://docs.litellm.ai/), supporting a wide range of providers including OpenAI, Anthropic, local models, and more. LLM features are entirely optional -- DocForge is fully functional without any LLM API keys.

## Configuration Hierarchy

LLM configuration is resolved in a layered hierarchy:

1. **Project-level overrides** -- Set per-project via the API or UI
2. **Server-level defaults** -- Set via environment variables
3. **Built-in defaults** -- Used when nothing else is configured

Project-level settings override server-level settings, allowing different projects to use different providers or models.

## Server-Level Configuration

Set LLM defaults via environment variables:

```bash
# Provider and model
export DOCFORGE_LLM_PROVIDER="openai"
export DOCFORGE_LLM_MODEL="gpt-4o"

# API key (provider-specific)
export OPENAI_API_KEY="sk-..."

# Optional: custom endpoint (for local models)
export DOCFORGE_LLM_ENDPOINT="http://localhost:11434"

# Optional: generation parameters
export DOCFORGE_LLM_TEMPERATURE="0.7"
export DOCFORGE_LLM_MAX_TOKENS="2048"
```

## Project-Level Configuration

### Via the Web UI

1. Open your project workspace.
2. Navigate to project settings.
3. Configure the LLM provider, model, and parameters.
4. Click **Test Connection** to verify.

### Via the API

**Get current configuration:**

```bash
curl http://localhost:8000/api/v1/projects/{project_id}/llm-config
```

Response:

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "endpoint": null,
  "apiKeyConfigured": true,
  "temperature": 0.7,
  "maxTokens": 2048
}
```

**Update configuration:**

```bash
curl -X PUT http://localhost:8000/api/v1/projects/{project_id}/llm-config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.5,
    "maxTokens": 4096
  }'
```

**Test connection:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/llm-test
```

Response:

```json
{
  "success": true,
  "message": "Connection successful"
}
```

## Global Configuration

You can also check and test the global (server-level) LLM configuration:

```bash
# Get global config
curl http://localhost:8000/api/v1/llm/config

# Test global config
curl -X POST http://localhost:8000/api/v1/llm/test
```

## Supported Providers

DocForge supports any provider that LiteLLM supports. Common configurations:

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

```json
{
  "provider": "openai",
  "model": "gpt-4o"
}
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514"
}
```

### Ollama (Local)

No API key needed. Ensure Ollama is running locally:

```json
{
  "provider": "ollama",
  "model": "llama3.1",
  "endpoint": "http://localhost:11434"
}
```

### LM Studio (Local)

No API key needed. Ensure LM Studio server is running:

```json
{
  "provider": "openai",
  "model": "local-model",
  "endpoint": "http://localhost:1234/v1"
}
```

### AWS Bedrock

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION_NAME="us-east-1"
```

```json
{
  "provider": "bedrock",
  "model": "anthropic.claude-sonnet-4-20250514-v1:0"
}
```

## LLM Context Assembly

When an LLM prompt is rendered, DocForge assembles context using a section-scoped strategy:

- **Default scope**: Each prompt only sees data from its containing section.
- **Broadened scope**: If the prompt text contains signals like "all sections", "entire document", or explicit cross-section references, the scope is widened.
- **File references**: If the prompt references a specific data file by name, that file's data is always included in the context.

The context is assembled by the `ContextAssembler` and includes relevant data from the `DataStore` along with any section-specific content.

## Generation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `temperature` | Controls randomness (0.0 = deterministic, 1.0 = creative) | 0.7 |
| `maxTokens` | Maximum tokens in LLM response | 2048 |

Lower temperature values produce more consistent, factual output. Higher values produce more varied, creative content. For document generation, values between 0.3 and 0.7 are typically recommended.

## Running Without LLM

When no LLM is configured:

- Variable placeholder markers are still rendered from data sources.
- Table markers are still populated from data sources.
- LLM prompt markers are left with their original red text in the output.
- The generation report notes skipped LLM markers.
- No errors are thrown -- the system degrades gracefully.

This makes DocForge useful as a pure data-driven template engine even without any LLM integration.
