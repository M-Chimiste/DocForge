import { useState } from "react";
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
import type { MappingEntry, GenerateResult, ConditionalConfig } from "../types";
import { generateDocument, downloadGeneration } from "../api/client";

interface Props {
  projectId: number;
  mappings: MappingEntry[];
  conditionals?: ConditionalConfig[];
  disabled?: boolean;
}

export default function GenerateButton({
  projectId,
  mappings,
  conditionals,
  disabled,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reportOpen, setReportOpen] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await generateDocument(projectId, mappings, conditionals);
      setResult(res);
      setReportOpen(true);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Generation failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

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
      {loading && <LinearProgress />}

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

        {result && (
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            Download .docx
          </Button>
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
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
