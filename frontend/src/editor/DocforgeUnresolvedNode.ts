import { Node, mergeAttributes } from "@tiptap/core";

export const DocforgeUnresolved = Node.create({
  name: "docforgeUnresolved",
  group: "inline",
  inline: true,
  atom: true,

  addAttributes() {
    return {
      markerId: { default: null },
      originalText: { default: "" },
    };
  },

  parseHTML() {
    return [{ tag: "span[data-docforge-unresolved]" }];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      "span",
      mergeAttributes(HTMLAttributes, {
        "data-docforge-unresolved": "",
        class: "docforge-unresolved",
      }),
      HTMLAttributes.originalText || "???",
    ];
  },
});
