import { useCallback, useState } from "react";
import { Box, Button, Typography, CircularProgress } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import type { TemplateAnalysis } from "../types";
import { analyzeTemplate } from "../api/client";

interface TemplateUploadProps {
  onAnalyzed: (analysis: TemplateAnalysis, file: File) => void;
}

export default function TemplateUpload({ onAnalyzed }: TemplateUploadProps) {
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".docx")) {
        alert("Please upload a .docx file");
        return;
      }
      setLoading(true);
      try {
        const analysis = await analyzeTemplate(file);
        onAnalyzed(analysis, file);
      } catch (err) {
        console.error("Template analysis failed:", err);
        alert("Failed to analyze template");
      } finally {
        setLoading(false);
      }
    },
    [onAnalyzed]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <Box
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      sx={{
        border: "2px dashed",
        borderColor: dragOver ? "primary.main" : "grey.400",
        borderRadius: 2,
        p: 4,
        textAlign: "center",
        bgcolor: dragOver ? "action.hover" : "background.paper",
        transition: "all 0.2s",
      }}
    >
      {loading ? (
        <CircularProgress />
      ) : (
        <>
          <CloudUploadIcon sx={{ fontSize: 48, color: "grey.500", mb: 1 }} />
          <Typography variant="body1" gutterBottom>
            Drag & drop a .docx template here
          </Typography>
          <Button variant="contained" component="label">
            Browse Files
            <input
              type="file"
              hidden
              accept=".docx"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />
          </Button>
        </>
      )}
    </Box>
  );
}
