import { useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import DownloadIcon from "@mui/icons-material/Download";
import type { MappingEntry } from "../types";
import { generateDocument } from "../api/client";

interface Props {
  projectId: number;
  mappings: MappingEntry[];
  disabled?: boolean;
}

export default function GenerateButton({
  projectId,
  mappings,
  disabled,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [blob, setBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setBlob(null);
    try {
      const result = await generateDocument(projectId, mappings);
      setBlob(result);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Generation failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!blob) return;
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

        {blob && (
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
    </Box>
  );
}
