import { Box, Tooltip } from "@mui/material";

interface Props {
  confidence: number;
  reasoning: string;
}

function getColor(confidence: number): string {
  if (confidence >= 0.8) return "#4caf50"; // green
  if (confidence >= 0.4) return "#ff9800"; // yellow/orange
  return "#f44336"; // red
}

export default function ConfidenceIndicator({ confidence, reasoning }: Props) {
  const pct = Math.round(confidence * 100);
  return (
    <Tooltip title={`${pct}% confidence — ${reasoning}`} arrow>
      <Box
        sx={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: getColor(confidence),
          display: "inline-block",
          cursor: "help",
          flexShrink: 0,
        }}
      />
    </Tooltip>
  );
}
