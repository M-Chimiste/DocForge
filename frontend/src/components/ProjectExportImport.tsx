import { useRef, useState } from "react";
import { Button, CircularProgress } from "@mui/material";
import FileUploadIcon from "@mui/icons-material/FileUpload";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import type { Project } from "../types";
import { exportProject, importProject } from "../api/client";

interface ExportProps {
  projectId: number;
}

export function ExportButton({ projectId }: ExportProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const blob = await exportProject(projectId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `project_${projectId}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      size="small"
      startIcon={
        loading ? <CircularProgress size={16} /> : <FileDownloadIcon />
      }
      onClick={handleExport}
      disabled={loading}
    >
      Export
    </Button>
  );
}

interface ImportProps {
  onImported: (project: Project) => void;
}

export function ImportButton({ onImported }: ImportProps) {
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleImport = async (file: File) => {
    setLoading(true);
    try {
      const project = await importProject(file);
      onImported(project);
    } catch (err) {
      console.error("Import failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        size="small"
        startIcon={
          loading ? <CircularProgress size={16} /> : <FileUploadIcon />
        }
        onClick={() => inputRef.current?.click()}
        disabled={loading}
      >
        Import
      </Button>
      <input
        ref={inputRef}
        type="file"
        hidden
        accept=".zip"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleImport(file);
        }}
      />
    </>
  );
}
