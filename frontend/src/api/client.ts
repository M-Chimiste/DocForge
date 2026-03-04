import axios from "axios";
import type {
  Project,
  TemplateAnalysis,
  DataSource,
  MappingEntry,
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

// Generation
export async function generateDocument(
  projectId: number,
  mappings: MappingEntry[]
): Promise<Blob> {
  const { data } = await api.post(
    `/projects/${projectId}/generate`,
    { mappings },
    { responseType: "blob" }
  );
  return data;
}
