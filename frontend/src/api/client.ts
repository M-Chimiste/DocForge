import axios from "axios";
import type {
  Project,
  TemplateAnalysis,
  DataSource,
  MappingEntry,
  ConditionalConfig,
  GenerateResult,
  AutoResolutionReport,
  ValidationIssue,
  GenerationRun,
  DataPreview,
} from "../types";

const api = axios.create({
  baseURL: "/api/v1",
});

// Projects
export async function createProject(
  name: string,
  description = ""
): Promise<Project> {
  const { data } = await api.post<Project>("/projects", { name, description });
  return data;
}

export async function listProjects(): Promise<Project[]> {
  const { data } = await api.get<Project[]>("/projects");
  return data;
}

export async function getProject(id: number): Promise<Project> {
  const { data } = await api.get<Project>(`/projects/${id}`);
  return data;
}

export async function updateProject(
  id: number,
  updates: { name?: string; description?: string; mappingConfig?: unknown }
): Promise<Project> {
  const { data } = await api.put<Project>(`/projects/${id}`, updates);
  return data;
}

export async function deleteProject(id: number): Promise<void> {
  await api.delete(`/projects/${id}`);
}

// Templates
export async function analyzeTemplate(
  file: File
): Promise<TemplateAnalysis> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<TemplateAnalysis>("/templates/analyze", form);
  return data;
}

// Data Sources
export async function uploadDataSource(
  projectId: number,
  file: File
): Promise<DataSource> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<DataSource>(
    `/projects/${projectId}/data-sources`,
    form
  );
  return data;
}

export async function listDataSources(
  projectId: number
): Promise<DataSource[]> {
  const { data } = await api.get<DataSource[]>(
    `/projects/${projectId}/data-sources`
  );
  return data;
}

export async function previewDataSource(
  projectId: number,
  filename: string,
  rows = 10
): Promise<DataPreview> {
  const { data } = await api.get<DataPreview>(
    `/projects/${projectId}/data-sources/${encodeURIComponent(filename)}/preview`,
    { params: { rows } }
  );
  return data;
}

// Generation
export async function generateDocument(
  projectId: number,
  mappings: MappingEntry[],
  conditionals?: ConditionalConfig[]
): Promise<GenerateResult> {
  const { data } = await api.post<GenerateResult>(
    `/projects/${projectId}/generate`,
    { mappings, conditionals: conditionals ?? [] }
  );
  return data;
}

export async function downloadGeneration(
  projectId: number,
  runId: number
): Promise<Blob> {
  const { data } = await api.get(
    `/projects/${projectId}/generations/${runId}/download`,
    { responseType: "blob" }
  );
  return data;
}

export async function listGenerations(
  projectId: number
): Promise<GenerationRun[]> {
  const { data } = await api.get<GenerationRun[]>(
    `/projects/${projectId}/generations`
  );
  return data;
}

// Auto-Resolution
export async function autoResolve(
  projectId: number
): Promise<AutoResolutionReport> {
  const { data } = await api.post<AutoResolutionReport>(
    `/projects/${projectId}/auto-resolve`
  );
  return data;
}

// Validation
export async function validateMappings(
  projectId: number,
  mappings: MappingEntry[],
  conditionals?: ConditionalConfig[]
): Promise<ValidationIssue[]> {
  const { data } = await api.post<ValidationIssue[]>(
    `/projects/${projectId}/validate`,
    { mappings, conditionals: conditionals ?? [] }
  );
  return data;
}

// Project Export/Import
export async function exportProject(projectId: number): Promise<Blob> {
  const { data } = await api.get(`/projects/${projectId}/export`, {
    responseType: "blob",
  });
  return data;
}

export async function importProject(file: File): Promise<Project> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<Project>("/projects/import", form);
  return data;
}
