import { SimpleTreeView } from "@mui/x-tree-view/SimpleTreeView";
import { TreeItem } from "@mui/x-tree-view/TreeItem";
import { Box, Chip, Typography } from "@mui/material";
import TextFieldsIcon from "@mui/icons-material/TextFields";
import TableChartIcon from "@mui/icons-material/TableChart";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import type { TemplateAnalysis, TemplateMarker } from "../types";

interface Props {
  analysis: TemplateAnalysis;
  onSelectMarker?: (markerId: string) => void;
}

function markerIcon(type: string) {
  switch (type) {
    case "variable_placeholder":
      return <TextFieldsIcon fontSize="small" color="primary" />;
    case "sample_data":
      return <TableChartIcon fontSize="small" color="secondary" />;
    case "llm_prompt":
      return <AutoAwesomeIcon fontSize="small" color="warning" />;
    default:
      return null;
  }
}

function markerLabel(type: string) {
  switch (type) {
    case "variable_placeholder":
      return "Placeholder";
    case "sample_data":
      return "Sample Data";
    case "llm_prompt":
      return "LLM Prompt";
    default:
      return type;
  }
}

function MarkerItem({
  marker,
  onClick,
}: {
  marker: TemplateMarker;
  onClick?: () => void;
}) {
  return (
    <TreeItem
      itemId={marker.id}
      label={
        <Box
          sx={{ display: "flex", alignItems: "center", gap: 1, py: 0.5 }}
          onClick={onClick}
        >
          {markerIcon(marker.marker_type)}
          <Typography variant="body2" noWrap sx={{ flex: 1 }}>
            {marker.text}
          </Typography>
          <Chip
            label={markerLabel(marker.marker_type)}
            size="small"
            variant="outlined"
          />
        </Box>
      }
    />
  );
}

export default function TemplateAnalysisView({
  analysis,
  onSelectMarker,
}: Props) {
  return (
    <SimpleTreeView>
      {analysis.sections.map((section) => (
        <TreeItem
          key={section.id}
          itemId={section.id}
          label={
            <Typography variant="subtitle2">
              H{section.level}: {section.title}
            </Typography>
          }
        >
          {section.markers.map((m) => (
            <MarkerItem
              key={m.id}
              marker={m}
              onClick={() => onSelectMarker?.(m.id)}
            />
          ))}
        </TreeItem>
      ))}

      {analysis.tables.length > 0 && (
        <TreeItem
          itemId="tables-group"
          label={
            <Typography variant="subtitle2">
              Tables ({analysis.tables.length})
            </Typography>
          }
        >
          {analysis.tables.map((table) => (
            <TreeItem
              key={table.id}
              itemId={table.id}
              label={
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TableChartIcon fontSize="small" />
                  <Typography variant="body2">
                    {table.headers.join(" | ")}
                  </Typography>
                  <Chip
                    label={`${table.row_count} rows`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              }
            />
          ))}
        </TreeItem>
      )}
    </SimpleTreeView>
  );
}
