import { useState } from "react";
import {
  Box,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  CircularProgress,
} from "@mui/material";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import AddIcon from "@mui/icons-material/Add";
import type { DataSource } from "../types";
import { uploadDataSource } from "../api/client";

interface Props {
  projectId: number;
  dataSources: DataSource[];
  onUploaded: (ds: DataSource) => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DataSourceUpload({
  projectId,
  dataSources,
  onUploaded,
}: Props) {
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const ds = await uploadDataSource(projectId, file);
      onUploaded(ds);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Failed to upload data source");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <Typography variant="subtitle1">Data Sources</Typography>
        <Button
          size="small"
          startIcon={loading ? <CircularProgress size={16} /> : <AddIcon />}
          component="label"
          disabled={loading}
        >
          Add
          <input
            type="file"
            hidden
            accept=".xlsx,.xls,.csv,.tsv,.json"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
            }}
          />
        </Button>
      </Box>

      {dataSources.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No data sources uploaded yet.
        </Typography>
      ) : (
        <List dense>
          {dataSources.map((ds) => (
            <ListItem key={ds.filename}>
              <ListItemIcon>
                <InsertDriveFileIcon />
              </ListItemIcon>
              <ListItemText
                primary={ds.filename}
                secondary={formatSize(ds.size)}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
