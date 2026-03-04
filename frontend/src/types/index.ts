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

export interface MappingEntry {
  markerId: string;
  dataSource: string;
  field?: string | null;
  sheet?: string | null;
  path?: string | null;
}

export interface DataSource {
  filename: string;
  path: string;
  size: number;
}
