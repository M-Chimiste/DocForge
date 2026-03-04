import { useState, useCallback } from "react";

const STORAGE_KEY = "docforge_onboarding_complete";

export default function useOnboarding() {
  const [showOnboarding, setShowOnboarding] = useState<boolean>(
    () => localStorage.getItem(STORAGE_KEY) !== "true"
  );

  const dismissOnboarding = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, "true");
    setShowOnboarding(false);
  }, []);

  const restartOnboarding = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setShowOnboarding(true);
  }, []);

  return { showOnboarding, dismissOnboarding, restartOnboarding };
}
