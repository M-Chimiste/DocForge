import { Chip, Tooltip } from "@mui/material";
import SectionIcon from "@mui/icons-material/Article";
import DocumentIcon from "@mui/icons-material/Description";

interface Props {
  markerText: string;
}

const BROADENING_PATTERNS = [
  /\ball\s+sections?\b/i,
  /\bentire\s+document\b/i,
  /\bcovering\s+all\b/i,
  /\boverall\b/i,
  /\bexecutive\s+summary\b/i,
  /\bcross[\s-]section\b/i,
  /\bdocument[\s-]wide\b/i,
  /\bfull\s+report\b/i,
];

function detectScope(text: string): "section" | "document" {
  for (const pattern of BROADENING_PATTERNS) {
    if (pattern.test(text)) return "document";
  }
  return "section";
}

export default function ContextScopeIndicator({ markerText }: Props) {
  const scope = detectScope(markerText);
  const isDocument = scope === "document";

  return (
    <Tooltip
      title={
        isDocument
          ? "This prompt references the entire document — all data sources will be included as context"
          : "Context is scoped to the containing section only"
      }
    >
      <Chip
        icon={isDocument ? <DocumentIcon /> : <SectionIcon />}
        label={isDocument ? "Document" : "Section"}
        size="small"
        color={isDocument ? "warning" : "info"}
        variant="outlined"
        sx={{ ml: 0.5 }}
      />
    </Tooltip>
  );
}
