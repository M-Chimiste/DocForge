import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
  styled,
} from "@mui/material";
import { Close } from "@mui/icons-material";

interface Props {
  open: boolean;
  onClose: () => void;
}

const isMac =
  typeof navigator !== "undefined" &&
  /Mac|iPod|iPhone|iPad/.test(navigator.platform);

const modKey = isMac ? "\u2318" : "Ctrl";

const SHORTCUT_LIST = [
  { description: "Save", keys: [modKey, "S"] },
  { description: "Export document", keys: [modKey, "Shift", "E"] },
  { description: "Accept marker", keys: [modKey, "Shift", "A"] },
  { description: "Reject marker", keys: [modKey, "Shift", "R"] },
  { description: "Regenerate marker", keys: [modKey, "Shift", "G"] },
  { description: "Show keyboard shortcuts", keys: [modKey, "/"] },
];

const Kbd = styled("kbd")(({ theme }) => ({
  display: "inline-block",
  padding: "2px 6px",
  fontSize: "0.8rem",
  fontFamily: "monospace",
  lineHeight: 1.4,
  color: theme.palette.text.primary,
  backgroundColor: theme.palette.grey[100],
  border: `1px solid ${theme.palette.grey[300]}`,
  borderRadius: 4,
  boxShadow: `0 1px 0 ${theme.palette.grey[300]}`,
}));

export default function KeyboardShortcutsDialog({ open, onClose }: Props) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Typography variant="h6" component="span">
          Keyboard Shortcuts
        </Typography>
        <IconButton size="small" onClick={onClose} aria-label="Close">
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Table size="small">
          <TableBody>
            {SHORTCUT_LIST.map((s) => (
              <TableRow key={s.description}>
                <TableCell sx={{ border: 0, py: 1.2 }}>
                  {s.description}
                </TableCell>
                <TableCell sx={{ border: 0, py: 1.2, textAlign: "right" }}>
                  {s.keys.map((k, i) => (
                    <span key={i}>
                      {i > 0 && " + "}
                      <Kbd>{k}</Kbd>
                    </span>
                  ))}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DialogContent>
    </Dialog>
  );
}
