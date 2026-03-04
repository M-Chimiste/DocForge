import { SimpleTreeView } from "@mui/x-tree-view/SimpleTreeView";
import { TreeItem } from "@mui/x-tree-view/TreeItem";
import { Box, Chip, Typography } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PendingIcon from "@mui/icons-material/Pending";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

export interface SectionNode {
  id: string;
  title: string;
  level: number;
  markerCount: number;
  acceptedCount: number;
  hasUnresolved: boolean;
}

interface Props {
  sections: SectionNode[];
  onScrollToSection: (sectionId: string) => void;
}

function statusIcon(section: SectionNode) {
  if (section.hasUnresolved) {
    return <WarningAmberIcon fontSize="small" color="error" />;
  }
  if (section.markerCount > 0 && section.acceptedCount === section.markerCount) {
    return <CheckCircleIcon fontSize="small" color="success" />;
  }
  if (section.markerCount > 0) {
    return <PendingIcon fontSize="small" color="warning" />;
  }
  return null;
}

function statusLabel(section: SectionNode): string | null {
  if (section.markerCount === 0) return null;
  if (section.hasUnresolved) return "Unresolved";
  return `${section.acceptedCount}/${section.markerCount}`;
}

export default function EditorSectionTree({
  sections,
  onScrollToSection,
}: Props) {
  return (
    <Box sx={{ overflow: "auto", py: 1 }}>
      <Typography variant="overline" sx={{ px: 2, mb: 1, display: "block" }}>
        Document Sections
      </Typography>
      <SimpleTreeView>
        {sections.map((section) => {
          const label = statusLabel(section);
          return (
            <TreeItem
              key={section.id}
              itemId={section.id}
              label={
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    py: 0.5,
                    cursor: "pointer",
                  }}
                  onClick={() => onScrollToSection(section.id)}
                >
                  {statusIcon(section)}
                  <Typography
                    variant="body2"
                    noWrap
                    sx={{
                      flex: 1,
                      fontWeight: section.level <= 2 ? 600 : 400,
                      pl: (section.level - 1) * 1,
                    }}
                  >
                    {section.title}
                  </Typography>
                  {label && (
                    <Chip
                      label={label}
                      size="small"
                      variant="outlined"
                      color={section.hasUnresolved ? "error" : "default"}
                    />
                  )}
                </Box>
              }
            />
          );
        })}
      </SimpleTreeView>
    </Box>
  );
}
