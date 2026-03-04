import { useState, useEffect, useRef } from "react";
import {
  Box,
  Button,
  LinearProgress,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  Stack,
} from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import DownloadIcon from "@mui/icons-material/Download";
import StopIcon from "@mui/icons-material/Stop";
import EditNoteIcon from "@mui/icons-material/EditNote";
import type { MappingEntry, GenerateResult, ConditionalConfig } from "../types";
import { generateDocument, downloadGeneration } from "../api/client";
import useGenerationStream from "../hooks/useGenerationStream";
import { useNavigate } from "react-router-dom";

interface Props {
  projectId: number;
  mappings: MappingEntry[];
  conditionals?: ConditionalConfig[];
  disabled?: boolean;
  hasLLMMarkers?: boolean;
}

function stageLabel(
  stage: string | undefined,
  status: string | undefined,
  markerText?: string
): string {
  if (!stage) return "Generating...";
  switch (stage) {
    case "parsing":
      return status === "completed"
        ? "Template parsed"
        : "Parsing template...";
    case "ingestion":
      return status === "completed"
        ? "Data loaded"
        : "Loading data sources...";
    case "rendering":
      if (status === "llm_call_started" && markerText)
        return `Calling LLM: "${markerText.slice(0, 40)}${markerText.length > 40 ? "..." : ""}"`;
      if (status === "llm_call_completed") return "LLM response received";
      return "Rendering markers...";
    case "validation":
      return "Validating output...";
    default:
      return "Generating...";
  }
}

export default function GenerateButton({
  projectId,
  mappings,
  conditionals,
  disabled,
  hasLLMMarkers,
}: Props) {
  const navigate = useNavigate();
  // Sync generation state
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncResult, setSyncResult] = useState<GenerateResult | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  // Streaming generation
  const stream = useGenerationStream(projectId);

  const [reportOpen, setReportOpen] = useState(false);

  const useStream = hasLLMMarkers ?? false;
  const loading = useStream ? stream.isGenerating : syncLoading;
  const result = useStream ? stream.result : syncResult;
  const error = useStream ? stream.error : syncError;

  const handleGenerate = async () => {
    if (useStream) {
      stream.generate(mappings, conditionals);
    } else {
      setSyncLoading(true);
      setSyncError(null);
      setSyncResult(null);
      try {
        const res = await generateDocument(projectId, mappings, conditionals);
        setSyncResult(res);
        setReportOpen(true);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Generation failed";
        setSyncError(message);
      } finally {
        setSyncLoading(false);
      }
    }
  };

  // Open report dialog when streaming completes with result
  const prevStreamResult = useRef(stream.result);
  useEffect(() => {
    if (stream.result && stream.result !== prevStreamResult.current) {
      prevStreamResult.current = stream.result;
      setReportOpen(true);
    }
  }, [stream.result]);

  const handleDownload = async () => {
    if (!result) return;
    const blob = await downloadGeneration(projectId, result.runId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "output.docx";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      {loading && (
        <Box>
          {useStream && stream.progress ? (
            <>
              <LinearProgress
                variant="determinate"
                value={stream.progressPercent}
              />
              <Typography variant="caption" color="text.secondary">
                {stageLabel(
                  stream.progress.stage,
                  stream.progress.status,
                  stream.progress.markerText
                )}
              </Typography>
            </>
          ) : (
            <LinearProgress />
          )}
        </Box>
      )}

      <Box sx={{ display: "flex", gap: 1 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PlayArrowIcon />}
          onClick={handleGenerate}
          disabled={disabled || loading}
        >
          Generate Document
        </Button>

        {useStream && loading && (
          <Button
            variant="outlined"
            color="warning"
            startIcon={<StopIcon />}
            onClick={stream.cancel}
          >
            Cancel
          </Button>
        )}

        {result && (
          <>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
            >
              Download .docx
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<EditNoteIcon />}
              onClick={() =>
                navigate(`/projects/${projectId}/editor/${result.runId}`)
              }
            >
              Open in Editor
            </Button>
          </>
        )}
      </Box>

      {error && (
        <Typography variant="body2" color="error">
          {error}
        </Typography>
      )}

      {/* Generation Report Dialog */}
      <Dialog
        open={reportOpen}
        onClose={() => setReportOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Generation Report</DialogTitle>
        <DialogContent>
          {result && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Chip
                  label={`${result.report.rendered} rendered`}
                  color="success"
                  size="small"
                />
                <Chip
                  label={`${result.report.skipped} skipped`}
                  color={result.report.skipped > 0 ? "warning" : "default"}
                  size="small"
                />
                <Chip
                  label={`${result.report.totalMarkers} total`}
                  size="small"
                />
              </Box>

              {result.report.errors.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Errors
                  </Typography>
                  {result.report.errors.map((e, i) => (
                    <Alert key={i} severity="error" sx={{ mb: 0.5 }}>
                      {e.markerId && <strong>[{e.markerId}]</strong>}{" "}
                      {e.message}
                    </Alert>
                  ))}
                </Box>
              )}

              {result.report.warnings.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Warnings
                  </Typography>
                  {result.report.warnings.map((w, i) => (
                    <Alert key={i} severity="warning" sx={{ mb: 0.5 }}>
                      {w.markerId && <strong>[{w.markerId}]</strong>}{" "}
                      {w.message}
                    </Alert>
                  ))}
                </Box>
              )}

              {result.report.errors.length === 0 &&
                result.report.warnings.length === 0 && (
                  <Alert severity="success">
                    All markers rendered successfully.
                  </Alert>
                )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportOpen(false)}>Close</Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            Download
          </Button>
          {result && (
            <Button
              variant="contained"
              color="secondary"
              startIcon={<EditNoteIcon />}
              onClick={() => {
                setReportOpen(false);
                navigate(`/projects/${projectId}/editor/${result.runId}`);
              }}
            >
              Open in Editor
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
