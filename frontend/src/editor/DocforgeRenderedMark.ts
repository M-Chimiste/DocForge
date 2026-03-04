import { Mark, mergeAttributes } from "@tiptap/core";

export interface DocforgeRenderedAttrs {
  markerId: string;
  renderType: "llm" | "placeholder" | "text" | "table";
  confidence: number | null;
}

export const DocforgeRendered = Mark.create({
  name: "docforgeRendered",

  addAttributes() {
    return {
      markerId: { default: null },
      renderType: { default: "llm" },
      confidence: { default: null },
    };
  },

  parseHTML() {
    return [{ tag: "span[data-docforge-rendered]" }];
  },

  renderHTML({ HTMLAttributes }) {
    const confidence = HTMLAttributes.confidence;
    const isLowConfidence =
      confidence !== null && confidence !== undefined && confidence < 0.8;
    const classes = [
      "docforge-rendered",
      `docforge-rendered--${HTMLAttributes.renderType}`,
    ];
    if (isLowConfidence) {
      classes.push("docforge-rendered--low-confidence");
    }

    return [
      "span",
      mergeAttributes(HTMLAttributes, {
        "data-docforge-rendered": "",
        class: classes.join(" "),
        "data-marker-id": HTMLAttributes.markerId,
      }),
      0,
    ];
  },
});
