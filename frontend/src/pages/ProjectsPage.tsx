import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import type { Project } from "../types";
import { createProject, deleteProject, listProjects } from "../api/client";
import DeleteConfirmDialog from "../components/DeleteConfirmDialog";
import {
  ExportButton,
  ImportButton,
} from "../components/ProjectExportImport";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ProjectsPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  useEffect(() => {
    listProjects().then(setProjects).catch(console.error);
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setCreating(true);
    try {
      const project = await createProject(name.trim());
      setProjects((prev) => [project, ...prev]);
      setName("");
    } catch (err) {
      console.error("Failed to create project:", err);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteProject(deleteTarget.id);
      setProjects((prev) => prev.filter((p) => p.id !== deleteTarget.id));
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
    setDeleteTarget(null);
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Projects
      </Typography>

      <Box sx={{ display: "flex", gap: 1, mb: 3, alignItems: "center" }}>
        <TextField
          size="small"
          label="New project name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
          disabled={creating || !name.trim()}
        >
          Create
        </Button>
        <Box sx={{ flexGrow: 1 }} />
        <ImportButton
          onImported={(p) => setProjects((prev) => [p, ...prev])}
        />
      </Box>

      {projects.length === 0 ? (
        <Typography color="text.secondary">
          No projects yet. Create one to get started.
        </Typography>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {projects.map((project) => (
            <Card key={project.id} variant="outlined">
              <CardContent
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 2,
                  "&:last-child": { pb: 2 },
                }}
              >
                <Box
                  sx={{ flexGrow: 1, cursor: "pointer" }}
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <Typography variant="h6">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {project.description || "No description"}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Created: {formatDate(project.createdAt)} | Updated:{" "}
                    {formatDate(project.updatedAt)}
                  </Typography>
                </Box>

                <ExportButton projectId={project.id} />

                <Tooltip title="Delete project">
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteTarget(project);
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <DeleteConfirmDialog
        open={deleteTarget !== null}
        title="Delete Project"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </Container>
  );
}
