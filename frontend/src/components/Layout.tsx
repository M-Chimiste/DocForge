import type { ReactNode } from "react";
import { AppBar, Box, Toolbar, Typography } from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <DescriptionIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div">
            DocForge
          </Typography>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flex: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
}
