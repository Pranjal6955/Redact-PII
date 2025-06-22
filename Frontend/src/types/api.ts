export interface RedactionRequest {
  text: string;
  redact_types: string[];
  custom_tags?: Record<string, string>;
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