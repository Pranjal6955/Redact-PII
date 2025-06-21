const API_BASE_URL = 'http://localhost:8000';

class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    throw new APIError(`API Error: ${errorText}`, response.status);
  }
  return response.json();
}

export const apiService = {
  async getHealth(): Promise<import('../types/api').HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },

  async getAPIInfo(): Promise<import('../types/api').APIInfo> {
    const response = await fetch(`${API_BASE_URL}/`);
    return handleResponse(response);
  },

  async getSupportedTypes(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/supported-types`);
    return handleResponse(response);
  },

  async getSupportedFormats(): Promise<import('../types/api').FileFormat[]> {
    const response = await fetch(`${API_BASE_URL}/supported-formats`);
    return handleResponse(response);
  },

  async redactText(request: import('../types/api').RedactionRequest): Promise<import('../types/api').RedactionResponse> {
    const response = await fetch(`${API_BASE_URL}/redact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async analyzeText(text: string, redactTypes: string[]): Promise<import('../types/api').AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        redact_types: redactTypes,
      }),
    });
    return handleResponse(response);
  },

  async uploadFile(
    file: File,
    redactTypes: string[],
    customTags?: Record<string, string>,
    exportFormat: string = 'both',
    useOCR: boolean = false,
    preservePdfFormat: boolean = true
  ): Promise<import('../types/api').FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('redact_types', JSON.stringify(redactTypes));
    if (customTags) {
      formData.append('custom_tags', JSON.stringify(customTags));
    }
    formData.append('export_format', exportFormat);
    formData.append('use_ocr', useOCR.toString());
    formData.append('preserve_pdf_format', preservePdfFormat.toString());

    const response = await fetch(`${API_BASE_URL}/redact-file`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response);
  },

  async downloadFile(filename: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/download/${filename}`);
    if (!response.ok) {
      throw new APIError(`Failed to download file: ${filename}`, response.status);
    }
    return response.blob();
  },
};