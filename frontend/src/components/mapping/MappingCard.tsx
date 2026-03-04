import {
  Box,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import type {
  AutoResolutionMatch,
  DataSource,
  MappingEntry,
  TemplateMarker,
  TransformConfig,
} from "../../types";
import ConfidenceIndicator from "./ConfidenceIndicator";
import ContextScopeIndicator from "./ContextScopeIndicator";
import TransformPanel from "./TransformPanel";

interface Props {
  marker: TemplateMarker;
  mapping: MappingEntry | undefined;
  dataSources: DataSource[];
  autoMatch?: AutoResolutionMatch;
  onUpdate: (updates: Partial<MappingEntry>) => void;
  onRemove: () => void;
}

export default function MappingCard({
  marker,
  mapping,
  dataSources,
  autoMatch,
  onUpdate,
  onRemove,
}: Props) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 1,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {autoMatch && (
            <ConfidenceIndicator
              confidence={autoMatch.confidence}
              reasoning={autoMatch.reasoning}
            />
          )}
          <Typography variant="body2" fontWeight="bold">
            {marker.text}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            ({marker.marker_type.replace("_", " ")})
          </Typography>
          {marker.marker_type === "llm_prompt" && (
            <ContextScopeIndicator markerText={marker.text} />
          )}
        </Box>
        {mapping && (
          <IconButton size="small" onClick={onRemove}>
            <DeleteIcon fontSize="small" />
          </IconButton>
        )}
      </Box>

      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 1 }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Data Source</InputLabel>
          <Select
            value={mapping?.dataSource || ""}
            label="Data Source"
            onChange={(e) => onUpdate({ dataSource: e.target.value })}
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
              onChange={(e) => onUpdate({ field: e.target.value })}
            />
            <TextField
              size="small"
              label="Path (JSON)"
              value={mapping?.path || ""}
              onChange={(e) => onUpdate({ path: e.target.value })}
            />
          </>
        )}

        {marker.marker_type === "sample_data" && (
          <TextField
            size="small"
            label="Sheet"
            value={mapping?.sheet || ""}
            onChange={(e) => onUpdate({ sheet: e.target.value })}
          />
        )}
      </Box>

      <TransformPanel
        transforms={mapping?.transforms ?? []}
        onChange={(transforms: TransformConfig[]) => onUpdate({ transforms })}
      />
    </Paper>
  );
}
