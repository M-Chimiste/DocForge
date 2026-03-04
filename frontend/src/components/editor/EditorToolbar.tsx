import {
  Box,
  Divider,
  IconButton,
  Select,
  MenuItem,
  Tooltip,
} from "@mui/material";
import {
  FormatBold,
  FormatItalic,
  FormatUnderlined,
  FormatAlignLeft,
  FormatAlignCenter,
  FormatAlignRight,
  TableChart,
  AddBox,
  IndeterminateCheckBox,
} from "@mui/icons-material";
import type { Editor } from "@tiptap/react";

interface Props {
  editor: Editor | null;
}

export default function EditorToolbar({ editor }: Props) {
  if (!editor) return null;

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.5,
        px: 2,
        py: 0.5,
        borderBottom: 1,
        borderColor: "divider",
        flexWrap: "wrap",
        bgcolor: "background.paper",
      }}
    >
      {/* Heading level */}
      <Select
        size="small"
        value={
          editor.isActive("heading", { level: 1 })
            ? "1"
            : editor.isActive("heading", { level: 2 })
              ? "2"
              : editor.isActive("heading", { level: 3 })
                ? "3"
                : "p"
        }
        onChange={(e) => {
          const val = e.target.value;
          if (val === "p") {
            editor.chain().focus().setParagraph().run();
          } else {
            editor
              .chain()
              .focus()
              .toggleHeading({ level: Number(val) as 1 | 2 | 3 })
              .run();
          }
        }}
        sx={{ minWidth: 120, mr: 1 }}
      >
        <MenuItem value="p">Paragraph</MenuItem>
        <MenuItem value="1">Heading 1</MenuItem>
        <MenuItem value="2">Heading 2</MenuItem>
        <MenuItem value="3">Heading 3</MenuItem>
      </Select>

      <Divider orientation="vertical" flexItem />

      {/* Text formatting */}
      <Tooltip title="Bold">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().toggleBold().run()}
          color={editor.isActive("bold") ? "primary" : "default"}
        >
          <FormatBold />
        </IconButton>
      </Tooltip>
      <Tooltip title="Italic">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          color={editor.isActive("italic") ? "primary" : "default"}
        >
          <FormatItalic />
        </IconButton>
      </Tooltip>
      <Tooltip title="Underline">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          color={editor.isActive("underline") ? "primary" : "default"}
        >
          <FormatUnderlined />
        </IconButton>
      </Tooltip>

      <Divider orientation="vertical" flexItem />

      {/* Alignment */}
      <Tooltip title="Align Left">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().setTextAlign("left").run()}
          color={editor.isActive({ textAlign: "left" }) ? "primary" : "default"}
        >
          <FormatAlignLeft />
        </IconButton>
      </Tooltip>
      <Tooltip title="Align Center">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().setTextAlign("center").run()}
          color={
            editor.isActive({ textAlign: "center" }) ? "primary" : "default"
          }
        >
          <FormatAlignCenter />
        </IconButton>
      </Tooltip>
      <Tooltip title="Align Right">
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().setTextAlign("right").run()}
          color={
            editor.isActive({ textAlign: "right" }) ? "primary" : "default"
          }
        >
          <FormatAlignRight />
        </IconButton>
      </Tooltip>

      <Divider orientation="vertical" flexItem />

      {/* Table operations */}
      <Tooltip title="Insert Table">
        <IconButton
          size="small"
          onClick={() =>
            editor
              .chain()
              .focus()
              .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
              .run()
          }
        >
          <TableChart />
        </IconButton>
      </Tooltip>
      {editor.isActive("table") && (
        <>
          <Tooltip title="Add Row">
            <IconButton
              size="small"
              onClick={() => editor.chain().focus().addRowAfter().run()}
            >
              <AddBox fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Row">
            <IconButton
              size="small"
              onClick={() => editor.chain().focus().deleteRow().run()}
            >
              <IndeterminateCheckBox fontSize="small" />
            </IconButton>
          </Tooltip>
        </>
      )}
    </Box>
  );
}
