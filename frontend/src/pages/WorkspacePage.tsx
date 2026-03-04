import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Container, Divider, Paper, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import type {
  DataSource,
  MappingEntry,
  TemplateAnalysis,
} from "../types";
import { getProject, listDataSources } from "../api/client";
import TemplateUpload from "../components/TemplateUpload";
import TemplateAnalysisView from "../components/TemplateAnalysisView";
import DataSourceUpload from "../components/DataSourceUpload";
import MappingPanel from "../components/MappingPanel";
import GenerateButton from "../components/GenerateButton";

export default function WorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId);

  const [projectName, setProjectName] = useState("");
  const [analysis, setAnalysis] = useState<TemplateAnalysis | null>(null);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [mappings, setMappings] = useState<MappingEntry[]>([]);

  useEffect(() => {
    getProject(id).then((p) => setProjectName(p.name));
    listDataSources(id).then(setDataSources).catch(() => {});
  }, [id]);

  // Build table-level mappings from analysis tables
  const tableMappings: MappingEntry[] = analysis
    ? analysis.tables
        .filter((t) => mappings.some((m) => m.markerId === t.id))
        .map((t) => mappings.find((m) => m.markerId === t.id)!)
    : [];

  const allMappings = [...mappings, ...tableMappings.filter(
    (tm) => !mappings.some((m) => m.markerId === tm.markerId)
  )];

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
              <TemplateUpload
                onAnalyzed={(a) => setAnalysis(a)}
              />
            )}
          </Paper>
        </Grid>

        {/* Center column: Data Sources */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <DataSourceUpload
              projectId={id}
              dataSources={dataSources}
              onUploaded={(ds) =>
                setDataSources((prev) => [...prev, ds])
              }
            />
          </Paper>
        </Grid>

        {/* Right column: Mappings */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            {analysis ? (
              <MappingPanel
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

      <Divider sx={{ my: 3 }} />

      <GenerateButton
        projectId={id}
        mappings={allMappings}
        disabled={!analysis || mappings.length === 0}
      />
    </Container>
  );
}
