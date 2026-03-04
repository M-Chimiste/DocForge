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
  LLMConfig,
  LLMConfigUpdate,
  LLMTestResult,
  EditorDocumentResponse,
  RegenerateSectionResponse,
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
  page = 1,
  pageSize = 50
): Promise<DataPreview> {
  const { data } = await api.get<DataPreview>(
    `/projects/${projectId}/data-sources/${encodeURIComponent(filename)}/preview`,
    { params: { page, page_size: pageSize } }
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

// LLM Configuration
export async function getGlobalLLMConfig(): Promise<LLMConfig> {
  const { data } = await api.get<LLMConfig>("/llm/config");
  return data;
}

export async function getProjectLLMConfig(
  projectId: number
): Promise<LLMConfig> {
  const { data } = await api.get<LLMConfig>(
    `/projects/${projectId}/llm-config`
  );
  return data;
}

export async function updateProjectLLMConfig(
  projectId: number,
  config: LLMConfigUpdate
): Promise<LLMConfig> {
  const { data } = await api.put<LLMConfig>(
    `/projects/${projectId}/llm-config`,
    config
  );
  return data;
}

export async function testLLMConnection(
  projectId?: number
): Promise<LLMTestResult> {
  const url = projectId
    ? `/projects/${projectId}/llm-test`
    : "/llm/test";
  const { data } = await api.post<LLMTestResult>(url);
  return data;
}

// Streaming generation URL helper
export function getGenerateStreamUrl(projectId: number): string {
  return `/api/v1/projects/${projectId}/generate-stream`;
}

// Editor (Phase 4)
export async function getEditorDocument(
  runId: number
): Promise<EditorDocumentResponse> {
  const { data } = await api.get<EditorDocumentResponse>(
    `/generations/${runId}/document`
  );
  return data;
}

export async function saveEditorDocument(
  runId: number,
  state: unknown
): Promise<void> {
  await api.put(`/generations/${runId}/document`, state);
}

export async function regenerateSection(
  runId: number,
  markerId: string,
  modifiedPrompt?: string
): Promise<RegenerateSectionResponse> {
  const { data } = await api.post<RegenerateSectionResponse>(
    `/generations/${runId}/regenerate-section`,
    { markerId, modifiedPrompt }
  );
  return data;
}

export async function exportDocument(runId: number): Promise<Blob> {
  const { data } = await api.get(`/generations/${runId}/export`, {
    responseType: "blob",
  });
  return data;
}
