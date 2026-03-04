import { BubbleMenu } from "@tiptap/react/menus";
import { Button, Paper, ButtonGroup } from "@mui/material";
import {
  Check,
  Close,
  Refresh,
  EditNote,
} from "@mui/icons-material";
import type { Editor } from "@tiptap/react";

interface Props {
  editor: Editor;
  onAccept: (markerId: string) => void;
  onReject: (markerId: string) => void;
  onRegenerate: (markerId: string) => void;
  onEditMapping: (markerId: string) => void;
}

function getActiveMarkerId(editor: Editor): string | null {
  const { $from } = editor.state.selection;
  const marks = $from.marks();
  for (const mark of marks) {
    if (mark.type.name === "docforgeRendered" && mark.attrs.markerId) {
      return mark.attrs.markerId;
    }
  }
  return null;
}

export default function ReviewToolbar({
  editor,
  onAccept,
  onReject,
  onRegenerate,
  onEditMapping,
}: Props) {
  return (
    <BubbleMenu
      editor={editor}
      options={{ placement: "top" }}
      shouldShow={({ editor: ed }: { editor: Editor }) => {
        return ed.isActive("docforgeRendered");
      }}
    >
      <Paper elevation={4} sx={{ p: 0.5 }}>
        <ButtonGroup size="small" variant="outlined">
          <Button
            startIcon={<Check />}
            color="success"
            aria-label="Accept rendered content"
            onClick={() => {
              const id = getActiveMarkerId(editor);
              if (id) onAccept(id);
            }}
          >
            Accept
          </Button>
          <Button
            startIcon={<Close />}
            color="error"
            aria-label="Reject rendered content"
            onClick={() => {
              const id = getActiveMarkerId(editor);
              if (id) onReject(id);
            }}
          >
            Reject
          </Button>
          <Button
            startIcon={<Refresh />}
            aria-label="Regenerate content"
            onClick={() => {
              const id = getActiveMarkerId(editor);
              if (id) onRegenerate(id);
            }}
          >
            Regenerate
          </Button>
          <Button
            startIcon={<EditNote />}
            aria-label="Edit marker mapping"
            onClick={() => {
              const id = getActiveMarkerId(editor);
              if (id) onEditMapping(id);
            }}
          >
            Edit Mapping
          </Button>
        </ButtonGroup>
      </Paper>
    </BubbleMenu>
  );
}
