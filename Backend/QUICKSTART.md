# Quick Start Guide

Get your PII Redaction API running in 5 minutes! 🚀

## Prerequisites

- Python 3.8+
- Ollama installed and running

## 1. Install Ollama (if not already installed)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Start Ollama and Pull a Model

```bash
# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull mistral
```

## 3. Setup the API

```bash
# Navigate to Backend directory
cd Backend

# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Start the API

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the API
python run.py
```

The API will be available at `http://localhost:8000`

## 5. Test the API

```bash
# Run the test suite
python test_api.py

# Run file functionality tests
python test_file_api.py

# Or try the examples
python example_usage.py
```

## 6. View API Documentation

Open your browser and go to:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Quick Test with cURL

### Text Redaction
```bash
curl -X POST "http://localhost:8000/redact" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, my name is John Doe and my email is john@example.com",
    "redact_types": ["name", "email"]
  }'
```

### File Upload and Redaction
```bash
# Create a test file
echo "My name is Alice and my email is alice@test.com" > test.txt

# Upload and redact
curl -X POST "http://localhost:8000/redact-file" \
  -F "file=@test.txt" \
  -F "redact_types=[\"name\", \"email\"]" \
  -F "export_format=both"
```

### Download Generated Files
```bash
# Download the generated files (replace with actual filename)
curl -O "http://localhost:8000/download/test_redacted_20231201_143022.txt"
curl -O "http://localhost:8000/download/test_redacted_20231201_143022.pdf"
```

## File Upload Features

### Supported Formats
- **Upload**: PDF (.pdf), Text (.txt)
- **Export**: PDF, TXT, or both
- **Max Size**: 10MB per file

### File Processing Flow
1. Upload PDF or text file
2. Extract text (PDF) or read text (TXT)
3. Detect and redact PII using hybrid approach
4. Generate output files in requested format
5. Download the redacted files

### Example with Custom Tags
```bash
curl -X POST "http://localhost:8000/redact-file" \
  -F "file=@document.pdf" \
  -F "redact_types=[\"name\", \"email\", \"phone\"]" \
  -F "custom_tags={\"name\": \"[ANONYMOUS]\", \"email\": \"[EMAIL]\", \"phone\": \"[PHONE]\"}" \
  -F "export_format=both"
```

## Troubleshooting

### Ollama not running
```bash
ollama serve
```

### Model not found
```bash
ollama pull mistral
```

### Port already in use
Edit `config.env` and change `API_PORT=8001`

### Permission denied
```bash
chmod +x setup.sh run.py test_api.py test_file_api.py example_usage.py
```

### File upload issues
- Check file size (max 10MB)
- Ensure file is PDF or TXT format
- Verify file is not corrupted

### PDF extraction issues
- Ensure PDF contains extractable text (not scanned images)
- Check PDF is not password protected

## Next Steps

- Check the full [README.md](README.md) for detailed documentation
- Explore the [example_usage.py](example_usage.py) for more examples
- Test file functionality with [test_file_api.py](test_file_api.py)
- Integrate with your frontend application
- Customize the configuration in `config.env`

Happy redacting! 🛡️ 