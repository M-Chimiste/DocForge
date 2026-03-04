import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, CircularProgress, Paper, Typography } from "@mui/material";
import { EditorContent } from "@tiptap/react";
import { useDocforgeEditor } from "../editor/useDocforgeEditor";
import "../editor/editor.css";
import EditorToolbar from "../components/editor/EditorToolbar";
import ReviewToolbar from "../components/editor/ReviewToolbar";
import RegenerateDialog from "../components/editor/RegenerateDialog";
import EditorSectionTree, {
  type SectionNode,
} from "../components/editor/EditorSectionTree";
import EditorBottomBar from "../components/editor/EditorBottomBar";
import MarkerDetailsPanel, {
  type MarkerMeta,
} from "../components/editor/MarkerDetailsPanel";
import KeyboardShortcutsDialog from "../components/KeyboardShortcutsDialog";
import useKeyboardShortcuts from "../hooks/useKeyboardShortcuts";
import {
  getEditorDocument,
  saveEditorDocument,
  regenerateSection,
  exportDocument,
} from "../api/client";
import type {
  EditorDocumentResponse,
  MarkerEditorMeta,
} from "../types";

export default function EditorPage() {
  const { runId } = useParams<{ runId: string }>();
  const numRunId = Number(runId);

  const [docData, setDocData] = useState<EditorDocumentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Keyboard shortcuts dialog state
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  // Regenerate dialog state
  const [regenOpen, setRegenOpen] = useState(false);
  const [regenMarkerId, setRegenMarkerId] = useState("");
  const [regenPrompt, setRegenPrompt] = useState("");

  // Selected marker for details panel
  const [selectedMarkerMeta, setSelectedMarkerMeta] =
    useState<MarkerMeta | null>(null);

  // Accepted markers set (by markerId)
  const [acceptedMarkers, setAcceptedMarkers] = useState<Set<string>>(
    new Set()
  );

  // Load document
  useEffect(() => {
    setLoading(true);
    getEditorDocument(numRunId)
      .then((data) => {
        setDocData(data);
        setError(null);
      })
      .catch((err) => {
        setError(err?.response?.data?.message || "Failed to load document");
      })
      .finally(() => setLoading(false));
  }, [numRunId]);

  // Initialize TipTap editor with document content
  const editor = useDocforgeEditor(docData?.content ?? null);

  // Track changes
  useEffect(() => {
    if (!editor) return;
    const handler = () => setHasUnsavedChanges(true);
    editor.on("update", handler);
    return () => {
      editor.off("update", handler);
    };
  }, [editor]);

  // Build section tree from document content
  const sections: SectionNode[] = useMemo(() => {
    if (!docData?.content?.content) return [];
    const markerMeta = docData.meta.marker_metadata;
    const result: SectionNode[] = [];

    for (const node of docData.content.content) {
      if (node.type === "heading" && node.attrs?.id) {
        const textContent =
          node.content?.map((c) => c.text || "").join("") || "";
        const sectionId = String(node.attrs.id);
        const level = (node.attrs.level as number) || 1;

        // Count markers in this section from metadata
        const sectionMarkers = Object.values(markerMeta).filter(
          (m) => m.section_id === sectionId
        );
        const acceptedCount = sectionMarkers.filter((m) =>
          acceptedMarkers.has(m.marker_id)
        ).length;
        const hasUnresolved = sectionMarkers.some(
          (m) => m.rendered_by === "unresolved"
        );

        result.push({
          id: sectionId,
          title: textContent || `Section`,
          level,
          markerCount: sectionMarkers.length,
          acceptedCount,
          hasUnresolved,
        });
      }
    }
    return result;
  }, [docData, acceptedMarkers]);

  // Section scroll handler
  const handleScrollToSection = useCallback((sectionId: string) => {
    const el = document.querySelector(`[id="${sectionId}"]`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, []);

  // Build MarkerMeta from backend metadata
  const getMarkerMeta = useCallback(
    (markerId: string): MarkerMeta | null => {
      if (!docData?.meta.marker_metadata) return null;
      const m: MarkerEditorMeta | undefined =
        docData.meta.marker_metadata[markerId];
      if (!m) return null;
      return {
        markerId: m.marker_id,
        markerType: m.marker_type,
        originalText: m.original_text,
        renderedBy: m.rendered_by,
        confidence: m.confidence,
        llmModel: m.llm_model,
        sectionId: m.section_id,
        mappingSnapshot: m.mapping_snapshot,
      };
    },
    [docData]
  );

  // Accept: remove the docforgeRendered mark from the marker's text
  const handleAccept = useCallback(
    (markerId: string) => {
      if (!editor) return;
      // Find and unset the mark for this markerId
      const { doc } = editor.state;
      let from: number | null = null;
      let to: number | null = null;

      doc.descendants((node, pos) => {
        if (node.isText) {
          const renderedMark = node.marks.find(
            (m) =>
              m.type.name === "docforgeRendered" &&
              m.attrs.markerId === markerId
          );
          if (renderedMark) {
            from = pos;
            to = pos + node.nodeSize;
            return false;
          }
        }
      });

      if (from !== null && to !== null) {
        editor
          .chain()
          .focus()
          .setTextSelection({ from, to })
          .unsetMark("docforgeRendered")
          .run();
        setAcceptedMarkers((prev) => new Set([...prev, markerId]));
      }
    },
    [editor]
  );

  // Reject: delete the rendered content
  const handleReject = useCallback(
    (markerId: string) => {
      if (!editor) return;
      const { doc } = editor.state;
      let from: number | null = null;
      let to: number | null = null;

      doc.descendants((node, pos) => {
        if (node.isText) {
          const renderedMark = node.marks.find(
            (m) =>
              m.type.name === "docforgeRendered" &&
              m.attrs.markerId === markerId
          );
          if (renderedMark) {
            from = pos;
            to = pos + node.nodeSize;
            return false;
          }
        }
      });

      if (from !== null && to !== null) {
        editor.chain().focus().deleteRange({ from, to }).run();
      }
    },
    [editor]
  );

  // Regenerate: open dialog with prompt
  const handleRegenerateOpen = useCallback(
    (markerId: string) => {
      const meta = getMarkerMeta(markerId);
      setRegenMarkerId(markerId);
      setRegenPrompt(meta?.originalText || "");
      setRegenOpen(true);
    },
    [getMarkerMeta]
  );

  // Regenerate: call API and patch content
  const handleRegenerate = useCallback(
    async (markerId: string, modifiedPrompt: string) => {
      const response = await regenerateSection(
        numRunId,
        markerId,
        modifiedPrompt
      );
      if (!editor) return;

      // Find the marked range and replace content
      const { doc } = editor.state;
      let from: number | null = null;
      let to: number | null = null;

      doc.descendants((node, pos) => {
        if (node.isText) {
          const renderedMark = node.marks.find(
            (m) =>
              m.type.name === "docforgeRendered" &&
              m.attrs.markerId === markerId
          );
          if (renderedMark) {
            from = pos;
            to = pos + node.nodeSize;
            return false;
          }
        }
      });

      if (from !== null && to !== null) {
        editor
          .chain()
          .focus()
          .deleteRange({ from, to })
          .insertContentAt(from, response.content)
          .run();
      }
    },
    [editor, numRunId]
  );

  // Edit mapping: show marker details
  const handleEditMapping = useCallback(
    (markerId: string) => {
      const meta = getMarkerMeta(markerId);
      setSelectedMarkerMeta(meta);
    },
    [getMarkerMeta]
  );

  // Update selected marker on selection change
  useEffect(() => {
    if (!editor) return;
    const handler = () => {
      const { $from } = editor.state.selection;
      const marks = $from.marks();
      for (const mark of marks) {
        if (
          mark.type.name === "docforgeRendered" &&
          mark.attrs.markerId
        ) {
          const meta = getMarkerMeta(mark.attrs.markerId);
          setSelectedMarkerMeta(meta);
          return;
        }
      }
      setSelectedMarkerMeta(null);
    };
    editor.on("selectionUpdate", handler);
    return () => {
      editor.off("selectionUpdate", handler);
    };
  }, [editor, getMarkerMeta]);

  // Save handler
  const handleSave = useCallback(async () => {
    if (!editor || !docData) return;
    setSaving(true);
    try {
      const editorJson = editor.getJSON();
      await saveEditorDocument(numRunId, {
        content: editorJson,
        meta: docData.meta,
      });
      setHasUnsavedChanges(false);
    } catch {
      // TODO: show error toast
    } finally {
      setSaving(false);
    }
  }, [editor, docData, numRunId]);

  // Auto-save with debounce
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (!hasUnsavedChanges) return;
    saveTimerRef.current = setTimeout(() => {
      handleSave();
    }, 30000); // Auto-save every 30s of inactivity
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, [hasUnsavedChanges, handleSave]);

  // Export handler
  const handleExport = useCallback(async () => {
    setExporting(true);
    try {
      // Save first if there are unsaved changes
      if (hasUnsavedChanges && editor && docData) {
        const editorJson = editor.getJSON();
        await saveEditorDocument(numRunId, {
          content: editorJson,
          meta: docData.meta,
        });
        setHasUnsavedChanges(false);
      }
      const blob = await exportDocument(numRunId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `docforge_export_${numRunId}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // TODO: show error toast
    } finally {
      setExporting(false);
    }
  }, [numRunId, hasUnsavedChanges, editor, docData]);

  // Helper: get currently active marker ID from editor selection
  const getActiveMarkerId = useCallback((): string | null => {
    if (!editor) return null;
    const { $from } = editor.state.selection;
    const marks = $from.marks();
    for (const mark of marks) {
      if (mark.type.name === "docforgeRendered" && mark.attrs.markerId) {
        return mark.attrs.markerId;
      }
    }
    return null;
  }, [editor]);

  // Keyboard shortcuts
  useKeyboardShortcuts(
    useMemo(
      () => ({
        onSave: handleSave,
        onExport: handleExport,
        onAccept: () => {
          const id = getActiveMarkerId();
          if (id) handleAccept(id);
        },
        onReject: () => {
          const id = getActiveMarkerId();
          if (id) handleReject(id);
        },
        onRegenerate: () => {
          const id = getActiveMarkerId();
          if (id) handleRegenerateOpen(id);
        },
        onShowHelp: () => setShortcutsOpen(true),
      }),
      [
        handleSave,
        handleExport,
        handleAccept,
        handleReject,
        handleRegenerateOpen,
        getActiveMarkerId,
      ]
    )
  );

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Main content area */}
      <Box sx={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Left panel: Section tree */}
        <Paper
          variant="outlined"
          component="nav"
          aria-label="Document sections"
          sx={{
            width: 280,
            flexShrink: 0,
            overflow: "auto",
            borderRadius: 0,
          }}
        >
          <EditorSectionTree
            sections={sections}
            onScrollToSection={handleScrollToSection}
          />
        </Paper>

        {/* Center: Editor */}
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <EditorToolbar
            editor={editor}
            onShowShortcuts={() => setShortcutsOpen(true)}
          />
          <Box
            sx={{
              flex: 1,
              overflow: "auto",
              bgcolor: "grey.50",
            }}
          >
            <Paper
              elevation={1}
              sx={{
                maxWidth: 900,
                mx: "auto",
                my: 2,
                minHeight: "calc(100vh - 200px)",
              }}
            >
              {editor && (
                <>
                  <EditorContent editor={editor} />
                  <ReviewToolbar
                    editor={editor}
                    onAccept={handleAccept}
                    onReject={handleReject}
                    onRegenerate={handleRegenerateOpen}
                    onEditMapping={handleEditMapping}
                  />
                </>
              )}
            </Paper>
          </Box>
        </Box>

        {/* Right panel: Marker details */}
        <Paper
          variant="outlined"
          component="aside"
          aria-label="Marker details"
          sx={{
            width: 320,
            flexShrink: 0,
            overflow: "auto",
            borderRadius: 0,
          }}
        >
          <MarkerDetailsPanel marker={selectedMarkerMeta} />
        </Paper>
      </Box>

      {/* Bottom bar */}
      <EditorBottomBar
        hasUnsavedChanges={hasUnsavedChanges}
        saving={saving}
        exporting={exporting}
        onSave={handleSave}
        onExport={handleExport}
      />

      {/* Regenerate dialog */}
      <RegenerateDialog
        open={regenOpen}
        markerId={regenMarkerId}
        originalPrompt={regenPrompt}
        onClose={() => setRegenOpen(false)}
        onRegenerate={handleRegenerate}
      />

      {/* Keyboard shortcuts dialog */}
      <KeyboardShortcutsDialog
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
      />
    </Box>
  );
}
