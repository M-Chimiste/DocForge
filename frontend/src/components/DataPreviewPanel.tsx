import { useEffect, useRef, useState } from "react";
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
  TablePagination,
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
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);
  const fetchIdRef = useRef(0);

  useEffect(() => {
    const id = ++fetchIdRef.current;
    previewDataSource(projectId, filename, page + 1, rowsPerPage)
      .then((p) => {
        if (id !== fetchIdRef.current) return;
        setPreview(p);
        if (p.sheets.length > 0 && !selectedSheet) {
          setSelectedSheet(p.sheets[0]);
        }
      })
      .catch(() => {
        if (id === fetchIdRef.current) setPreview(null);
      })
      .finally(() => {
        if (id === fetchIdRef.current) setLoading(false);
      });
    return () => {
      /* fetchIdRef check handles staleness */
    };
  }, [projectId, filename, page, rowsPerPage]); // eslint-disable-line react-hooks/exhaustive-deps

  const handlePageChange = (_event: unknown, newPage: number) => {
    setLoading(true);
    setPage(newPage);
  };

  const handleRowsPerPageChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setLoading(true);
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

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
        </TableContainer>
      )}
      {sheetData && (
        <TablePagination
          component="div"
          count={sheetData.totalRows}
          page={page}
          onPageChange={handlePageChange}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleRowsPerPageChange}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      )}
    </Box>
  );
}
