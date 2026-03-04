import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  CircularProgress,
} from "@mui/material";

interface Props {
  open: boolean;
  markerId: string;
  originalPrompt: string;
  onClose: () => void;
  onRegenerate: (markerId: string, modifiedPrompt: string) => Promise<void>;
}

export default function RegenerateDialog({
  open,
  markerId,
  originalPrompt,
  onClose,
  onRegenerate,
}: Props) {
  const [prompt, setPrompt] = useState(originalPrompt);
  const [loading, setLoading] = useState(false);

  const handleRegenerate = async () => {
    setLoading(true);
    try {
      await onRegenerate(markerId, prompt);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Regenerate Section</DialogTitle>
      <DialogContent>
        <TextField
          label="Prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          multiline
          minRows={4}
          maxRows={12}
          fullWidth
          sx={{ mt: 1 }}
          helperText="Modify the prompt and click Regenerate to re-run the LLM"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleRegenerate}
          variant="contained"
          disabled={loading || !prompt.trim()}
          startIcon={loading ? <CircularProgress size={16} /> : undefined}
        >
          Regenerate
        </Button>
      </DialogActions>
    </Dialog>
  );
}
