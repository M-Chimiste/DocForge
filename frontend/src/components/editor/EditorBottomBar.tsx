import { Box, Button, Chip, CircularProgress } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import FileDownloadIcon from "@mui/icons-material/FileDownload";

interface Props {
  hasUnsavedChanges: boolean;
  saving: boolean;
  exporting: boolean;
  onSave: () => void;
  onExport: () => void;
}

export default function EditorBottomBar({
  hasUnsavedChanges,
  saving,
  exporting,
  onSave,
  onExport,
}: Props) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        px: 2,
        py: 1,
        borderTop: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }} aria-live="polite">
        {hasUnsavedChanges && (
          <Chip label="Unsaved changes" size="small" color="warning" />
        )}
        {saving && <span className="sr-only">Saving document...</span>}
      </Box>
      <Box sx={{ display: "flex", gap: 1 }}>
        <Button
          variant="outlined"
          startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
          onClick={onSave}
          disabled={saving || !hasUnsavedChanges}
        >
          Save
        </Button>
        <Button
          variant="contained"
          startIcon={
            exporting ? <CircularProgress size={16} /> : <FileDownloadIcon />
          }
          onClick={onExport}
          disabled={exporting}
        >
          Export .docx
        </Button>
      </Box>
    </Box>
  );
}
