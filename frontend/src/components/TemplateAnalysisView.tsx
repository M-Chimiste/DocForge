import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  Chip,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
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
    <ListItemButton dense onClick={onClick}>
      <ListItemIcon sx={{ minWidth: 32 }}>
        {markerIcon(marker.marker_type)}
      </ListItemIcon>
      <ListItemText
        primary={marker.text}
        primaryTypographyProps={{ variant: "body2", noWrap: true }}
      />
      <Chip
        label={markerLabel(marker.marker_type)}
        size="small"
        variant="outlined"
      />
    </ListItemButton>
  );
}

export default function TemplateAnalysisView({
  analysis,
  onSelectMarker,
}: Props) {
  return (
    <Box>
      {analysis.sections.map((section) => (
        <Accordion key={section.id} disableGutters defaultExpanded={false}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle2">
              H{section.level}: {section.title}
            </Typography>
            <Chip
              label={`${section.markers.length} markers`}
              size="small"
              variant="outlined"
              sx={{ ml: 1 }}
            />
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <List disablePadding>
              {section.markers.map((m) => (
                <MarkerItem
                  key={m.id}
                  marker={m}
                  onClick={() => onSelectMarker?.(m.id)}
                />
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}

      {analysis.tables.length > 0 && (
        <Accordion disableGutters defaultExpanded={false}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle2">
              Tables ({analysis.tables.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <List disablePadding>
              {analysis.tables.map((table) => (
                <ListItemButton key={table.id} dense>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <TableChartIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={table.headers.join(" | ")}
                    primaryTypographyProps={{ variant: "body2" }}
                  />
                  <Chip
                    label={`${table.row_count} rows`}
                    size="small"
                    variant="outlined"
                  />
                </ListItemButton>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
}
