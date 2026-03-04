import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  Container,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import type {
  DataSource,
  MappingEntry,
  TemplateAnalysis,
  ValidationIssue,
} from "../types";
import {
  getProject,
  listDataSources,
  validateMappings,
} from "../api/client";
import TemplateUpload from "../components/TemplateUpload";
import TemplateAnalysisView from "../components/TemplateAnalysisView";
import DataSourceUpload from "../components/DataSourceUpload";
import MappingPanel from "../components/MappingPanel";
import GenerateButton from "../components/GenerateButton";
import DataPreviewPanel from "../components/DataPreviewPanel";
import ValidationDisplay from "../components/ValidationDisplay";
import LLMSettingsPanel from "../components/LLMSettingsPanel";

export default function WorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId);

  const [projectName, setProjectName] = useState("");
  const [analysis, setAnalysis] = useState<TemplateAnalysis | null>(null);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [mappings, setMappings] = useState<MappingEntry[]>([]);
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>(
    []
  );
  const [previewSource, setPreviewSource] = useState("");

  useEffect(() => {
    getProject(id).then((p) => setProjectName(p.name));
    listDataSources(id)
      .then(setDataSources)
      .catch(() => {});
  }, [id]);

  // Run validation when mappings change (debounced)
  useEffect(() => {
    if (!analysis || mappings.length === 0) {
      return;
    }
    const timer = setTimeout(() => {
      validateMappings(id, mappings)
        .then(setValidationIssues)
        .catch(() => {});
    }, 500);
    return () => clearTimeout(timer);
  }, [id, analysis, mappings]);

  // Build table-level mappings from analysis tables
  const tableMappings: MappingEntry[] = analysis
    ? analysis.tables
        .filter((t) => mappings.some((m) => m.markerId === t.id))
        .map((t) => mappings.find((m) => m.markerId === t.id)!)
    : [];

  const allMappings = [
    ...mappings,
    ...tableMappings.filter(
      (tm) => !mappings.some((m) => m.markerId === tm.markerId)
    ),
  ];

  const hasLLMMarkers =
    analysis?.markers.some((m) => m.marker_type === "llm_prompt") ?? false;

  return (
    <Container maxWidth="xl">
      <Typography variant="h5" gutterBottom>
        {projectName || "Loading..."}
      </Typography>

      <Grid container spacing={2}>
        {/* Left column: Template */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Template
            </Typography>
            {analysis ? (
              <TemplateAnalysisView analysis={analysis} />
            ) : (
              <TemplateUpload onAnalyzed={(a) => setAnalysis(a)} />
            )}
          </Paper>
        </Grid>

        {/* Center column: Data Sources + Preview */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <DataSourceUpload
              projectId={id}
              dataSources={dataSources}
              onUploaded={(ds) => setDataSources((prev) => [...prev, ds])}
            />
          </Paper>

          {dataSources.length > 0 && (
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ mb: 1 }}>
                <FormControl size="small" fullWidth>
                  <InputLabel>Preview Data Source</InputLabel>
                  <Select
                    value={previewSource}
                    label="Preview Data Source"
                    onChange={(e) => setPreviewSource(e.target.value)}
                  >
                    {dataSources.map((ds) => (
                      <MenuItem key={ds.filename} value={ds.filename}>
                        {ds.filename}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              {previewSource && (
                <DataPreviewPanel projectId={id} filename={previewSource} />
              )}
            </Paper>
          )}
        </Grid>

        {/* Right column: Mappings */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            {analysis ? (
              <MappingPanel
                projectId={id}
                markers={analysis.markers}
                dataSources={dataSources}
                mappings={mappings}
                onMappingsChange={setMappings}
              />
            ) : (
              <Typography variant="body2" color="text.secondary">
                Upload a template to configure mappings.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Validation */}
      {validationIssues.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <ValidationDisplay issues={validationIssues} />
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      <LLMSettingsPanel projectId={id} hasLLMMarkers={hasLLMMarkers} />

      <GenerateButton
        projectId={id}
        mappings={allMappings}
        disabled={!analysis || mappings.length === 0}
        hasLLMMarkers={hasLLMMarkers}
      />
    </Container>
  );
}
