export interface RedactionRequest {
  text: string;
  redact_types: string[];
  custom_tags?: Record<string, string>;
  auto_detect_all?: boolean;
}

export interface RedactionResponse {
  original: string;
  redacted: string;
  summary: Record<string, number>;
  redact_types_used: string[];
}

export interface FileUploadResponse {
  original_text: string;
  redacted_text: string;
  summary: Record<string, number>;
  redact_types_used: string[];
  files_generated: string[];
  file_sizes: Record<string, number>;
}

export interface AnalysisResponse {
  summary: Record<string, number>;
  total_entities: number;
}

export interface HealthResponse {
  status: string;
  ollama_status: string;
  model: string;
  timestamp: string;
}

export interface APIInfo {
  name: string;
  version: string;
  description: string;
}

export interface PIIType {
  id: string;
  label: string;
  description: string;
  category?: string;
  critical?: boolean;
}

export interface PIITypeCategory {
  id: string;
  label: string;
  types: PIIType[];
}

export interface SupportedTypesResponse {
  regex_supported: string[];
  all_supported: string[];
  critical_types: string[];
  common_types: string[];
  auto_detect_types: string[];
  total_types: number;
  categories: Record<string, string[]>;
  description: string;
}

export interface FileFormat {
  extension: string;
  mime_type: string;
  description: string;
}

export interface PdfCreationResponse {
  filename: string;
  file_size: number;
  message: string;
}