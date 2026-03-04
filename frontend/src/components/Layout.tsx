import type { ReactNode } from "react";
import { AppBar, Box, Toolbar, Typography } from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box
        component="a"
        href="#main-content"
        sx={{
          position: "absolute",
          left: "-9999px",
          top: "auto",
          width: "1px",
          height: "1px",
          overflow: "hidden",
          "&:focus": {
            position: "fixed",
            top: 8,
            left: 8,
            width: "auto",
            height: "auto",
            overflow: "visible",
            zIndex: 1301,
            bgcolor: "background.paper",
            p: 1,
            borderRadius: 1,
            boxShadow: 3,
            color: "primary.main",
            textDecoration: "underline",
          },
        }}
      >
        Skip to main content
      </Box>
      <AppBar position="static" component="nav" aria-label="Main navigation">
        <Toolbar>
          <DescriptionIcon sx={{ mr: 1 }} aria-hidden="true" />
          <Typography variant="h6" component="div">
            DocForge
          </Typography>
        </Toolbar>
      </AppBar>
      <Box component="main" id="main-content" role="main" aria-label="Main content" sx={{ flex: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
}
