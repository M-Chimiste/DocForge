import { Box, Chip, Divider, Typography } from "@mui/material";

export interface MarkerMeta {
  markerId: string;
  markerType: string;
  originalText: string;
  renderedBy: string | null;
  confidence: number | null;
  llmModel: string | null;
  sectionId: string | null;
  mappingSnapshot: Record<string, unknown> | null;
}

interface Props {
  marker: MarkerMeta | null;
}

function confidenceColor(confidence: number): "success" | "warning" | "error" {
  if (confidence >= 0.8) return "success";
  if (confidence >= 0.4) return "warning";
  return "error";
}

function rendererLabel(renderedBy: string | null): string {
  switch (renderedBy) {
    case "llm":
      return "LLM Generated";
    case "placeholder":
      return "Placeholder";
    case "text":
      return "Static Text";
    case "table":
      return "Table Renderer";
    default:
      return "Unknown";
  }
}

export default function MarkerDetailsPanel({ marker }: Props) {
  if (!marker) {
    return (
      <Box sx={{ p: 2, color: "text.secondary" }}>
        <Typography variant="body2">
          Select a rendered section to view its details.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="overline" gutterBottom display="block">
        Marker Details
      </Typography>

      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Marker ID
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
            {marker.markerId}
          </Typography>
        </Box>

        <Box>
          <Typography variant="caption" color="text.secondary">
            Type
          </Typography>
          <Box>
            <Chip
              label={marker.markerType.replace("_", " ")}
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>

        <Box>
          <Typography variant="caption" color="text.secondary">
            Rendered By
          </Typography>
          <Typography variant="body2">
            {rendererLabel(marker.renderedBy)}
          </Typography>
        </Box>

        {marker.confidence !== null && (
          <Box>
            <Typography variant="caption" color="text.secondary">
              Confidence
            </Typography>
            <Box>
              <Chip
                label={`${(marker.confidence * 100).toFixed(0)}%`}
                size="small"
                color={confidenceColor(marker.confidence)}
              />
            </Box>
          </Box>
        )}

        {marker.llmModel && (
          <Box>
            <Typography variant="caption" color="text.secondary">
              LLM Model
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
              {marker.llmModel}
            </Typography>
          </Box>
        )}

        <Divider />

        <Box>
          <Typography variant="caption" color="text.secondary">
            Original Text
          </Typography>
          <Typography
            variant="body2"
            sx={{
              mt: 0.5,
              p: 1,
              bgcolor: "grey.50",
              borderRadius: 1,
              fontStyle: "italic",
              whiteSpace: "pre-wrap",
              maxHeight: 200,
              overflow: "auto",
            }}
          >
            {marker.originalText}
          </Typography>
        </Box>

        {marker.mappingSnapshot && (
          <Box>
            <Typography variant="caption" color="text.secondary">
              Mapping
            </Typography>
            <Typography
              variant="body2"
              sx={{
                mt: 0.5,
                p: 1,
                bgcolor: "grey.50",
                borderRadius: 1,
                fontFamily: "monospace",
                fontSize: "0.75rem",
                whiteSpace: "pre-wrap",
                maxHeight: 200,
                overflow: "auto",
              }}
            >
              {JSON.stringify(marker.mappingSnapshot, null, 2)}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
