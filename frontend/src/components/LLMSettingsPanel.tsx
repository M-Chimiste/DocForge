import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Button,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Stack,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import type { LLMConfig, LLMConfigUpdate } from "../types";
import {
  getProjectLLMConfig,
  updateProjectLLMConfig,
  testLLMConnection,
} from "../api/client";

interface Props {
  projectId: number;
  hasLLMMarkers: boolean;
}

const PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "ollama", label: "Ollama" },
  { value: "lm_studio", label: "LM Studio" },
  { value: "other", label: "Other" },
];

const NEEDS_ENDPOINT = ["ollama", "lm_studio", "other"];

export default function LLMSettingsPanel({ projectId, hasLLMMarkers }: Props) {
  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [endpoint, setEndpoint] = useState("");
  const [apiKeyEnv, setApiKeyEnv] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadConfig = useCallback(async () => {
    try {
      const cfg = await getProjectLLMConfig(projectId);
      setConfig(cfg);
      setProvider(cfg.provider);
      setModel(cfg.model);
      setEndpoint(cfg.endpoint ?? "");
      setTemperature(cfg.temperature);
      setMaxTokens(cfg.maxTokens);
    } catch {
      // ignore
    }
  }, [projectId]);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const update: LLMConfigUpdate = {
        provider: provider || undefined,
        model: model || undefined,
        endpoint: endpoint || undefined,
        apiKeyEnv: apiKeyEnv || undefined,
        temperature,
        maxTokens,
      };
      const updated = await updateProjectLLMConfig(projectId, update);
      setConfig(updated);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testLLMConnection(projectId);
      setTestResult(result);
    } catch {
      setTestResult({ success: false, message: "Connection test failed" });
    } finally {
      setTesting(false);
    }
  };

  if (!hasLLMMarkers) return null;

  const isConfigured = config?.provider && config?.model;

  return (
    <Accordion defaultExpanded={false}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Stack direction="row" spacing={1} alignItems="center">
          <SmartToyIcon fontSize="small" />
          <Typography variant="subtitle2">LLM Settings</Typography>
          {isConfigured ? (
            <Chip
              label={`${config.provider}/${config.model}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          ) : (
            <Chip label="Not configured" size="small" color="default" />
          )}
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={2}>
          <FormControl size="small" fullWidth>
            <InputLabel>Provider</InputLabel>
            <Select
              value={provider}
              label="Provider"
              onChange={(e) => setProvider(e.target.value)}
            >
              {PROVIDERS.map((p) => (
                <MenuItem key={p.value} value={p.value}>
                  {p.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            size="small"
            label="Model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g., gpt-4o-mini, claude-sonnet-4-20250514"
            fullWidth
          />

          {NEEDS_ENDPOINT.includes(provider) && (
            <TextField
              size="small"
              label="Endpoint URL"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              placeholder="e.g., http://localhost:11434"
              fullWidth
            />
          )}

          <TextField
            size="small"
            label="API Key Environment Variable"
            value={apiKeyEnv}
            onChange={(e) => setApiKeyEnv(e.target.value)}
            placeholder="e.g., OPENAI_API_KEY"
            helperText={
              config?.apiKeyConfigured
                ? "API key is configured"
                : "Name of the env var containing the API key"
            }
            fullWidth
          />

          <Box>
            <Typography variant="caption" gutterBottom>
              Temperature: {temperature}
            </Typography>
            <Slider
              value={temperature}
              onChange={(_, v) => setTemperature(v as number)}
              min={0}
              max={2}
              step={0.1}
              size="small"
            />
          </Box>

          <TextField
            size="small"
            label="Max Tokens"
            type="number"
            value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))}
            fullWidth
          />

          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              size="small"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save"}
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={handleTest}
              disabled={testing || !provider || !model}
            >
              {testing ? "Testing..." : "Test Connection"}
            </Button>
          </Stack>

          {testResult && (
            <Alert
              severity={testResult.success ? "success" : "error"}
              icon={
                testResult.success ? (
                  <CheckCircleIcon fontSize="small" />
                ) : (
                  <ErrorIcon fontSize="small" />
                )
              }
            >
              {testResult.message}
            </Alert>
          )}
        </Stack>
      </AccordionDetails>
    </Accordion>
  );
}
