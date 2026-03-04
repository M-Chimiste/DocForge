export interface Project {
  id: number;
  name: string;
  description: string;
  templatePath: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface TemplateMarker {
  id: string;
  text: string;
  marker_type: "variable_placeholder" | "sample_data" | "llm_prompt";
  section_id: string | null;
  paragraph_index: number;
  run_indices: number[];
  table_id: string | null;
  row_index: number | null;
}

export interface Section {
  id: string;
  title: string;
  level: number;
  paragraph_index: number;
  markers: TemplateMarker[];
}

export interface SkeletonTable {
  id: string;
  section_id: string | null;
  paragraph_index: number;
  headers: string[];
  row_count: number;
  sample_data_markers: TemplateMarker[];
}

export interface TemplateAnalysis {
  sections: Section[];
  markers: TemplateMarker[];
  tables: SkeletonTable[];
}

export interface TransformConfig {
  type: string;
  params: Record<string, unknown>;
}

export interface MappingEntry {
  markerId: string;
  dataSource: string;
  field?: string | null;
  sheet?: string | null;
  path?: string | null;
  transforms?: TransformConfig[];
}

export interface ConditionalConfig {
  sectionId: string;
  conditionType: "data_presence" | "explicit";
  dataSource?: string | null;
  field?: string | null;
  operator?: string | null;
  value?: string | null;
  include?: boolean;
}

export interface DataSource {
  filename: string;
  path: string;
  size: number;
}

export interface AutoResolutionMatch {
  markerId: string;
  dataSource: string;
  field?: string | null;
  sheet?: string | null;
  path?: string | null;
  confidence: number;
  matchType: string;
  reasoning: string;
}

export interface AutoResolutionReport {
  matches: AutoResolutionMatch[];
  unresolved: string[];
}

export interface ValidationIssue {
  level: "error" | "warning" | "info";
  markerId?: string | null;
  message: string;
}

export interface GenerationReport {
  totalMarkers: number;
  rendered: number;
  skipped: number;
  warnings: ValidationIssue[];
  errors: ValidationIssue[];
}

export interface GenerateResult {
  runId: number;
  downloadUrl: string;
  report: GenerationReport;
}

export interface GenerationRun {
  id: number;
  projectId: number;
  status: string;
  report: Record<string, unknown> | null;
  createdAt: string;
}

// LLM Configuration
export interface LLMConfig {
  provider: string;
  model: string;
  endpoint?: string | null;
  apiKeyConfigured: boolean;
  temperature: number;
  maxTokens: number;
}

export interface LLMConfigUpdate {
  provider?: string;
  model?: string;
  endpoint?: string | null;
  apiKeyEnv?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface LLMTestResult {
  success: boolean;
  message: string;
}

// Generation Progress (SSE)
export interface GenerationProgress {
  stage: "parsing" | "ingestion" | "rendering" | "validation" | "complete";
  status: string;
  markerIndex?: number;
  totalMarkers?: number;
  markerId?: string;
  markerText?: string;
  tokens?: number;
  sources?: number;
  markers?: number;
  error?: string;
}

export interface DataPreview {
  source: string;
  sheets: string[];
  preview: Record<
    string,
    {
      columns: string[];
      rows: unknown[][];
      totalRows: number;
    }
  >;
  textSnippet?: string | null;
}

// Editor types (Phase 4)
export interface EditorMark {
  type: string;
  attrs?: Record<string, unknown> | null;
}

export interface EditorNode {
  type: string;
  attrs?: Record<string, unknown> | null;
  marks?: EditorMark[] | null;
  content?: EditorNode[] | null;
  text?: string | null;
}

export interface MarkerEditorMeta {
  marker_id: string;
  marker_type: string;
  original_text: string;
  rendered_by: string;
  confidence: number | null;
  llm_model: string | null;
  section_id: string | null;
  mapping_snapshot: Record<string, unknown> | null;
}

export interface EditorDocumentMeta {
  generation_run_id: number;
  project_id: number;
  template_analysis: Record<string, unknown> | null;
  marker_metadata: Record<string, MarkerEditorMeta>;
}

export interface EditorDocumentResponse {
  content: EditorNode;
  meta: EditorDocumentMeta;
}

export interface RegenerateSectionResponse {
  content: string;
  llmUsage: Record<string, unknown> | null;
}
