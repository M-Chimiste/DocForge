import { useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Table } from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import Underline from "@tiptap/extension-underline";
import { TextStyle } from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import FontFamily from "@tiptap/extension-font-family";
import TextAlign from "@tiptap/extension-text-align";
import { DocforgeRendered } from "./DocforgeRenderedMark";
import { DocforgeUnresolved } from "./DocforgeUnresolvedNode";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useDocforgeEditor(initialContent: Record<string, any> | null) {
  return useEditor(
    {
      extensions: [
        StarterKit.configure({
          heading: { levels: [1, 2, 3, 4, 5, 6] },
        }),
        Table.configure({ resizable: true }),
        TableRow,
        TableCell,
        TableHeader,
        Underline,
        TextStyle,
        Color,
        FontFamily,
        TextAlign.configure({ types: ["heading", "paragraph"] }),
        DocforgeRendered,
        DocforgeUnresolved,
      ],
      content: initialContent,
      editorProps: {
        attributes: {
          class: "docforge-editor-content",
        },
      },
    },
    [initialContent]
  );
}
