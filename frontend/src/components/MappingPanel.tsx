import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Paper,
  IconButton,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import type { TemplateMarker, DataSource, MappingEntry } from "../types";

interface Props {
  markers: TemplateMarker[];
  dataSources: DataSource[];
  mappings: MappingEntry[];
  onMappingsChange: (mappings: MappingEntry[]) => void;
}

export default function MappingPanel({
  markers,
  dataSources,
  mappings,
  onMappingsChange,
}: Props) {
  const mappableMarkers = markers.filter(
    (m) => m.marker_type !== "llm_prompt"
  );

  const getMapping = (markerId: string) =>
    mappings.find((m) => m.markerId === markerId);

  const updateMapping = (markerId: string, updates: Partial<MappingEntry>) => {
    const existing = mappings.findIndex((m) => m.markerId === markerId);
    const newMappings = [...mappings];
    if (existing >= 0) {
      newMappings[existing] = { ...newMappings[existing], ...updates };
    } else {
      newMappings.push({
        markerId,
        dataSource: "",
        ...updates,
      });
    }
    onMappingsChange(newMappings);
  };

  const removeMapping = (markerId: string) => {
    onMappingsChange(mappings.filter((m) => m.markerId !== markerId));
  };

  if (mappableMarkers.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No mappable markers found. Upload a template first.
      </Typography>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="subtitle1">Marker Mappings</Typography>
      {mappableMarkers.map((marker) => {
        const mapping = getMapping(marker.id);
        return (
          <Paper key={marker.id} variant="outlined" sx={{ p: 2 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="body2" fontWeight="bold">
                {marker.text}
              </Typography>
              {mapping && (
                <IconButton
                  size="small"
                  onClick={() => removeMapping(marker.id)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              )}
            </Box>

            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Data Source</InputLabel>
                <Select
                  value={mapping?.dataSource || ""}
                  label="Data Source"
                  onChange={(e) =>
                    updateMapping(marker.id, {
                      dataSource: e.target.value,
                    })
                  }
                >
                  {dataSources.map((ds) => (
                    <MenuItem key={ds.filename} value={ds.filename}>
                      {ds.filename}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {marker.marker_type === "variable_placeholder" && (
                <>
                  <TextField
                    size="small"
                    label="Field"
                    value={mapping?.field || ""}
                    onChange={(e) =>
                      updateMapping(marker.id, { field: e.target.value })
                    }
                  />
                  <TextField
                    size="small"
                    label="Path (JSON)"
                    value={mapping?.path || ""}
                    onChange={(e) =>
                      updateMapping(marker.id, { path: e.target.value })
                    }
                  />
                </>
              )}

              {marker.marker_type === "sample_data" && (
                <TextField
                  size="small"
                  label="Sheet"
                  value={mapping?.sheet || ""}
                  onChange={(e) =>
                    updateMapping(marker.id, { sheet: e.target.value })
                  }
                />
              )}
            </Box>
          </Paper>
        );
      })}
    </Box>
  );
}
