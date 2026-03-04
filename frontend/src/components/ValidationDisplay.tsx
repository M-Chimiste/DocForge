import { Alert, Box, Typography } from "@mui/material";
import type { ValidationIssue } from "../types";

interface Props {
  issues: ValidationIssue[];
}

export default function ValidationDisplay({ issues }: Props) {
  if (issues.length === 0) return null;

  const errors = issues.filter((i) => i.level === "error");
  const warnings = issues.filter((i) => i.level === "warning");

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <Typography variant="subtitle2">Validation Issues</Typography>

      {errors.map((e, i) => (
        <Alert key={`e-${i}`} severity="error" sx={{ py: 0 }}>
          {e.markerId && <strong>[{e.markerId}] </strong>}
          {e.message}
        </Alert>
      ))}

      {warnings.map((w, i) => (
        <Alert key={`w-${i}`} severity="warning" sx={{ py: 0 }}>
          {w.markerId && <strong>[{w.markerId}] </strong>}
          {w.message}
        </Alert>
      ))}
    </Box>
  );
}
