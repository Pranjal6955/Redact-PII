# PII Redaction API

A FastAPI backend for redacting Personally Identifiable Information (PII) using Ollama LLM with advanced file upload support and PDF formatting preservation.

## Features

- **Text Redaction**: Redact PII from plain text using AI-powered detection
- **File Upload Support**: Process PDF and text files with PII redaction
- **PDF Format Preservation**: Maintain original PDF layout, images, and structure when creating redacted PDFs
- **Multiple Export Formats**: Export as PDF, text, or both formats
- **OCR Support**: Optional OCR for scanned PDFs
- **Hybrid Mode**: Combine AI detection with regex patterns for better accuracy
- **Custom Redaction Tags**: Define custom replacement tags for different PII types

## New PDF Format Preservation Feature

The latest update includes a significant improvement to PDF processing:

### Before (Old Method)
- Extracted text from PDF
- Redacted PII from text
- Created a **new** PDF document from plain text
- **Result**: Lost original formatting, layout, images, and structure

### After (New Method)
- Extracts text from PDF for redaction
- Preserves original PDF structure and formatting
- Applies redacted text while maintaining:
  - Original page layout
  - Images and graphics
  - Font styles and sizes
  - Text positioning
  - Document structure

### How It Works

1. **Original PDF Analysis**: Analyzes the original PDF to understand text positioning and layout
2. **Text Redaction**: Redacts PII from extracted text using AI
3. **Format Preservation**: Creates a new PDF that:
   - Copies the original page content (images, graphics, etc.)
   - Covers original text with white rectangles
   - Inserts redacted text at the original text positions
   - Maintains font styles and sizes from the original

### Usage Options

Users can choose between two PDF export methods:

1. **Preserve Original Format** (Default: `true`)
   - Maintains original PDF layout and structure
   - Best for documents with complex formatting, images, or specific layouts
   - Recommended for most use cases

2. **Create New Document** (Default: `false`)
   - Creates a new PDF from plain text
   - Simpler formatting, easier to read
   - Useful for text-heavy documents where layout isn't critical

## Installation

### Prerequisites

- Python 3.8+
- Ollama (for LLM processing)
- Virtual environment (recommended)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RedactPII/Backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Ollama**:
   ```bash
   # Follow instructions at https://ollama.ai
   ollama pull llama2  # or your preferred model
   ```

5. **Configure environment**:
   ```bash
   cp config.env.example config.env
   # Edit config.env with your settings
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

## API Endpoints

### File Redaction with Format Preservation

**POST** `/redact-file`

Upload and redact PII from PDF or text files with format preservation options.

**Parameters**:
- `file`: PDF or text file to process
- `redact_types`: JSON string of PII types to redact (default: `["name", "email", "phone", "address", "ssn", "credit_card"]`)
- `custom_tags`: JSON string of custom replacement tags (optional)
- `export_format`: Output format - `"pdf"`, `"txt"`, or `"both"` (default: `"both"`)
- `use_ocr`: Use OCR for PDF text extraction (default: `false`)
- `preserve_pdf_format`: Preserve original PDF formatting (default: `true`)

**Example Request**:
```bash
curl -X POST "http://localhost:8000/redact-file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "redact_types=[\"name\",\"email\",\"phone\"]" \
  -F "export_format=pdf" \
  -F "preserve_pdf_format=true"
```

**Response**:
```json
{
  "original_text": "Original document text...",
  "redacted_text": "Redacted document text...",
  "summary": {
    "names": 3,
    "emails": 2,
    "phones": 1
  },
  "redact_types_used": ["name", "email", "phone"],
  "files_generated": ["document_redacted_20241201_143022.pdf"],
  "file_sizes": {
    "document_redacted_20241201_143022.pdf": 245760
  }
}
```

### Other Endpoints

- **POST** `/redact` - Redact PII from text
- **GET** `/download/{filename}` - Download generated files
- **GET** `/health` - Health check
- **GET** `/supported-types` - Get supported PII types
- **GET** `/supported-formats` - Get supported file formats

## Configuration

### Environment Variables

Create a `config.env` file with the following settings:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama2

# File Processing
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES_PER_REQUEST=1

# Redaction Settings
HYBRID_MODE_ENABLED=true
DEFAULT_REDACT_TYPES=["name", "email", "phone", "address", "ssn", "credit_card"]

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Frontend Integration

The frontend includes a new option to control PDF format preservation:

```typescript
// Example frontend usage
const response = await apiService.uploadFile(
  file,
  redactTypes,
  customTags,
  'pdf',  // export format
  false,  // use OCR
  true    // preserve PDF format
);
```

## Testing

Run the test script to verify PDF redaction functionality:

```bash
python3 test_pdf_redaction.py
```

## Troubleshooting

### Common Issues

1. **PDF Format Not Preserved**
   - Ensure `preserve_pdf_format=true` is set
   - Check that the original PDF has extractable text
   - Verify PyMuPDF is properly installed

2. **Text Positioning Issues**
   - The system uses the original text positions for redacted text
   - Complex layouts may require manual adjustment
   - Consider using the "Create New Document" option for text-heavy files

3. **Large File Processing**
   - Increase `MAX_FILE_SIZE` in configuration
   - Monitor memory usage for very large PDFs
   - Consider processing in smaller chunks

### Performance Tips

- Use `preserve_pdf_format=false` for faster processing of text-heavy documents
- Enable OCR only when necessary (scanned PDFs)
- Process large files during off-peak hours

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 