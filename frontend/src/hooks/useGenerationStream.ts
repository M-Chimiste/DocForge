import { useState, useRef, useCallback } from "react";
import type {
  MappingEntry,
  ConditionalConfig,
  GenerateResult,
  GenerationProgress,
} from "../types";
import { getGenerateStreamUrl } from "../api/client";

interface StreamState {
  isGenerating: boolean;
  progress: GenerationProgress | null;
  progressPercent: number;
  result: GenerateResult | null;
  error: string | null;
}

export default function useGenerationStream(projectId: number) {
  const [state, setState] = useState<StreamState>({
    isGenerating: false,
    progress: null,
    progressPercent: 0,
    result: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(
    async (mappings: MappingEntry[], conditionals?: ConditionalConfig[]) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setState({
        isGenerating: true,
        progress: null,
        progressPercent: 0,
        result: null,
        error: null,
      });

      const handleEvent = (eventType: string, data: string) => {
        try {
          const parsed = JSON.parse(data);

          if (eventType === "complete" || parsed.stage === "complete") {
            setState((s) => ({
              ...s,
              isGenerating: false,
              progress: null,
              progressPercent: 100,
              result: parsed.result ?? parsed,
            }));
          } else if (eventType === "error") {
            setState((s) => ({
              ...s,
              isGenerating: false,
              error: parsed.message || parsed.error || "Generation failed",
            }));
          } else {
            const progress = parsed as GenerationProgress;
            const percent = computePercent(progress);
            setState((s) => ({
              ...s,
              progress,
              progressPercent: percent,
            }));
          }
        } catch {
          // Ignore unparseable events
        }
      };

      try {
        const url = getGenerateStreamUrl(projectId);
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            mappings,
            conditionals: conditionals ?? [],
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          const text = await response.text();
          let message = `Generation failed (${response.status})`;
          try {
            const err = JSON.parse(text);
            message = err.message || err.error || message;
          } catch {
            // use default message
          }
          setState((s) => ({ ...s, isGenerating: false, error: message }));
          return;
        }

        const reader = response.body?.getReader();
        if (!reader) {
          setState((s) => ({
            ...s,
            isGenerating: false,
            error: "No response stream",
          }));
          return;
        }

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          let eventType = "";
          let eventData = "";

          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventType = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              eventData = line.slice(5).trim();
            } else if (line.trim() === "" && eventData) {
              handleEvent(eventType, eventData);
              eventType = "";
              eventData = "";
            }
          }
        }

        // Process any remaining buffered event
        if (buffer.trim()) {
          const remainLines = buffer.split("\n");
          let eventType = "";
          let eventData = "";
          for (const line of remainLines) {
            if (line.startsWith("event:")) {
              eventType = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              eventData = line.slice(5).trim();
            }
          }
          if (eventData) {
            handleEvent(eventType, eventData);
          }
        }

        // If we didn't get a complete event with a result, mark as done
        setState((s) => {
          if (s.isGenerating) {
            return { ...s, isGenerating: false };
          }
          return s;
        });
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        const message =
          err instanceof Error ? err.message : "Stream connection failed";
        setState((s) => ({ ...s, isGenerating: false, error: message }));
      }
    },
    [projectId]
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setState((s) => ({ ...s, isGenerating: false }));
  }, []);

  return {
    ...state,
    generate,
    cancel,
  };
}

function computePercent(p: GenerationProgress): number {
  switch (p.stage) {
    case "parsing":
      return p.status === "completed" ? 15 : 5;
    case "ingestion":
      return p.status === "completed" ? 30 : 20;
    case "rendering": {
      if (p.totalMarkers && p.markerIndex !== undefined) {
        const base = 30;
        const range = 55; // 30% to 85%
        return base + Math.round((p.markerIndex / p.totalMarkers) * range);
      }
      return 50;
    }
    case "validation":
      return 90;
    case "complete":
      return 100;
    default:
      return 0;
  }
}
