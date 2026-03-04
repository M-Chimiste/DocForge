import { IconButton, Tooltip } from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";

interface HelpTooltipProps {
  title: string;
}

export default function HelpTooltip({ title }: HelpTooltipProps) {
  return (
    <Tooltip title={title} placement="right">
      <IconButton
        size="small"
        aria-label={title}
        sx={{ color: "grey.500", p: 0.5 }}
      >
        <HelpOutlineIcon sx={{ fontSize: 18 }} />
      </IconButton>
    </Tooltip>
  );
}
