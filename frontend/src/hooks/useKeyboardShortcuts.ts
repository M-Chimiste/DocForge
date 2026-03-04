import { useEffect } from "react";

export interface ShortcutActions {
  onSave?: () => void;
  onExport?: () => void;
  onAccept?: () => void;
  onReject?: () => void;
  onRegenerate?: () => void;
  onShowHelp?: () => void;
}

interface ShortcutDef {
  key: string;
  shift: boolean;
  action: keyof ShortcutActions;
}

const SHORTCUTS: ShortcutDef[] = [
  { key: "s", shift: false, action: "onSave" },
  { key: "e", shift: true, action: "onExport" },
  { key: "a", shift: true, action: "onAccept" },
  { key: "r", shift: true, action: "onReject" },
  { key: "g", shift: true, action: "onRegenerate" },
  { key: "/", shift: false, action: "onShowHelp" },
];

export default function useKeyboardShortcuts(actions: ShortcutActions) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Require Ctrl (Win/Linux) or Cmd (Mac)
      if (!e.metaKey && !e.ctrlKey) return;

      for (const shortcut of SHORTCUTS) {
        if (
          e.key.toLowerCase() === shortcut.key &&
          e.shiftKey === shortcut.shift
        ) {
          const callback = actions[shortcut.action];
          if (callback) {
            e.preventDefault();
            callback();
          }
          return;
        }
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [actions]);
}
