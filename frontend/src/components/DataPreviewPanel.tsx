import { useEffect, useState } from "react";
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Skeleton,
} from "@mui/material";
import type { DataPreview } from "../types";
import { previewDataSource } from "../api/client";

interface Props {
  projectId: number;
  filename: string;
}

export default function DataPreviewPanel({ projectId, filename }: Props) {
  const [preview, setPreview] = useState<DataPreview | null>(null);
  const [selectedSheet, setSelectedSheet] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    previewDataSource(projectId, filename)
      .then((p) => {
        if (!cancelled) {
          setPreview(p);
          if (p.sheets.length > 0) setSelectedSheet(p.sheets[0]);
        }
      })
      .catch(() => {
        if (!cancelled) setPreview(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, filename]);

  if (loading) {
    return <Skeleton variant="rectangular" height={200} />;
  }

  if (!preview) {
    return (
      <Typography variant="body2" color="text.secondary">
        Could not load preview.
      </Typography>
    );
  }

  const sheetData = preview.preview[selectedSheet];

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <Typography variant="subtitle2">{filename}</Typography>
        {preview.sheets.length > 1 && (
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sheet</InputLabel>
            <Select
              value={selectedSheet}
              label="Sheet"
              onChange={(e) => setSelectedSheet(e.target.value)}
            >
              {preview.sheets.map((s) => (
                <MenuItem key={s} value={s}>
                  {s}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </Box>

      {preview.textSnippet && (
        <Paper
          variant="outlined"
          sx={{ p: 1, mb: 1, maxHeight: 120, overflow: "auto" }}
        >
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {preview.textSnippet}
          </Typography>
        </Paper>
      )}

      {sheetData && sheetData.columns.length > 0 && (
        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                {sheetData.columns.map((col) => (
                  <TableCell key={col} sx={{ fontWeight: "bold" }}>
                    {col}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sheetData.rows.map((row, i) => (
                <TableRow key={i}>
                  {(row as string[]).map((cell, j) => (
                    <TableCell key={j}>{String(cell)}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Typography variant="caption" color="text.secondary" sx={{ p: 1 }}>
            Showing {sheetData.rows.length} of {sheetData.totalRows} rows
          </Typography>
        </TableContainer>
      )}
    </Box>
  );
}
