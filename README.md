# RedactPII

[![Frontend Live](https://img.shields.io/badge/Frontend-Live-green)](https://frontend-one-rho-99.vercel.app/)  
[![Backend Live](https://img.shields.io/badge/Backend-Live-blue)](https://backend-cd5r.onrender.com)

---

> **Live Demo:**
> - Frontend: [https://frontend-one-rho-99.vercel.app/](https://frontend-one-rho-99.vercel.app/)
> - Backend: [https://backend-cd5r.onrender.com](https://backend-cd5r.onrender.com)

---

## 🖼️ Screenshots

> **Tip:** Place your screenshot images in a `screenshots/` or `public/` directory and update the image paths below as needed.

### Frontend Dashboard
![Frontend Dashboard](screenshots/frontend_dashboard.png)

### Backend Dashboard
![Backend Dashboard](screenshots/backend_dashboard.png)

### Dark Mode
![Dark Mode](screenshots/darkmode.png)

## 🚀 Features

- **Text Redaction**: AI-powered PII detection and redaction from plain text
- **File Processing**: Upload and process PDF and text files
- **PDF Format Preservation**: Maintain original PDF layout, images, and structure
- **Multiple Export Formats**: Export as PDF, text, or both formats
- **OCR Support**: Optional OCR for scanned PDFs
- **Hybrid Detection**: Combine AI detection with regex patterns for better accuracy
- **Custom Redaction Tags**: Define custom replacement tags for different PII types
- **Real-time Processing**: Fast and efficient redaction with visual feedback
- **Dark Mode Support**: Modern UI with light/dark theme switching

## 🏗️ Architecture

```
RedactPII/
├── Backend/          # FastAPI backend with Ollama integration
├── Frontend/         # React + TypeScript frontend with Vite
└── README.md         # This file
```

### Backend Stack
- **FastAPI** - High-performance Python web framework
- **Ollama** - Local LLM for PII detection
- **PyMuPDF** - PDF processing and format preservation
- **Tesseract** - OCR capabilities for scanned documents

### Frontend Stack
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast development and build tool
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Modern icon library

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Ollama** ([Installation guide](https://ollama.ai))

### 1. Start the Backend

```bash
cd Backend
bash setup.sh install  # Install dependencies and setup
source venv/bin/activate
python run.py
```

**Note**: If you want to generate test files for testing the redaction system, make sure reportlab is installed:
```bash
pip install reportlab>=4.0.0
python3 generate_test_files.py
```

The backend will be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd Frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📖 Usage

### Text Redaction
1. Navigate to the **Text** tab
2. Enter or paste text containing PII
3. Select PII types to redact (names, emails, phones, etc.)
4. Add custom replacement tags if needed
5. Click **Redact Text**
6. Copy or download the redacted results

### File Processing
1. Navigate to the **File** tab
2. Upload a PDF or text file
3. Configure redaction settings:
   - Select PII types to redact
   - Choose export format (PDF, TXT, or both)
   - Enable OCR for scanned documents
   - Toggle PDF format preservation
4. Process the file and download results

## 🔧 Configuration

### Backend Configuration

Create a `Backend/config.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama2

# File Processing
MAX_FILE_SIZE=10485760  # 10MB
HYBRID_MODE_ENABLED=true

# Supported PII Types
DEFAULT_REDACT_TYPES=["name", "email", "phone", "address", "ssn", "credit_card"]
```

### Frontend Configuration

The frontend automatically connects to the backend API. For custom configurations, modify [`Frontend/vite.config.ts`](Frontend/vite.config.ts).

## 🔍 Supported PII Types

- **Names** - Personal names and identities
- **Email Addresses** - Email contacts
- **Phone Numbers** - Phone and fax numbers
- **Addresses** - Physical addresses
- **SSN** - Social Security Numbers
- **Credit Cards** - Credit card numbers
- **Custom** - User-defined patterns

## 📡 API Endpoints

### Text Redaction
```http
POST /redact
Content-Type: application/json

{
  "text": "Contact John Doe at john@example.com",
  "redact_types": ["name", "email"],
  "custom_tags": {}
}
```

### File Processing
```http
POST /redact-file
Content-Type: multipart/form-data

- file: PDF or text file
- redact_types: JSON array of PII types
- export_format: "pdf", "txt", or "both"
- preserve_pdf_format: boolean
```

### Other Endpoints
- `GET /health` - Health check
- `GET /supported-types` - Get supported PII types
- `GET /download/{filename}` - Download processed files

## 🖼️ PDF Format Preservation

The application offers two PDF processing modes:

### Preserve Original Format (Recommended)
- Maintains original PDF layout and structure
- Preserves images, graphics, and formatting
- Best for documents with complex layouts
- Uses original text positioning for redacted content

### Create New Document
- Generates a new PDF from plain text
- Simpler formatting, easier to read
- Faster processing for text-heavy documents
- Useful when layout preservation isn't critical

## 🔨 What We Built and Why

### Our Approach
We built a **two-part system** - a React website and a Python server that work together:

- **React Frontend**: Easy-to-use website where users upload files and see results
- **Python Backend**: Does the heavy work of finding and hiding personal information
- **Local AI (Ollama)**: Keeps your data private by processing everything on your computer

### Why We Chose This Way
- **Keep Data Safe**: Everything stays on your computer, nothing goes to the internet
- **Easy to Use**: Simple web interface that anyone can understand
- **Fast and Smart**: Combines computer patterns with AI for better results
- **Flexible**: Can handle both text typing and file uploads

## ⚠️ What to Know (Limitations)

### What We Assume
- You can install and run software on your computer
- Your computer has enough memory (at least 8GB recommended)
- You mainly work with English text
- Your files are PDFs or text documents

### Current Limits
- **Speed**: AI checking takes time, so large files process slowly
- **File Size**: We limit files to 10MB to prevent crashes (you can change this)
- **PDF Quality**: Very fancy layouts might not look perfect after redaction
- **One at a Time**: Can only process one file at a time right now

### Trade-offs We Made
- **Privacy over Speed**: We chose local processing to keep your data safe, even though it's slower
- **Accuracy over Quick**: We use AI + patterns together for better results, even though it takes longer
- **Flexibility over Simple**: We give you options to configure, which makes it a bit more complex

## 🚀 What We'd Improve Next

### Make It Faster
- **Background Processing**: Let you upload files while others are still processing
- **Multiple Files**: Process several files at once
- **Better Memory Use**: Make it work on computers with less memory

### Better Features
- **More Languages**: Support Spanish, French, and other languages
- **Smarter Detection**: Better at understanding context to avoid mistakes
- **Mobile Friendly**: Make it work better on phones and tablets

### Easier to Use
- **Drag and Drop**: Just drag files onto the website
- **Preview**: Show you what will be redacted before doing it
- **Undo**: Let you reverse changes if you don't like them
- **Save Settings**: Remember your preferences for next time

### For Businesses
- **User Accounts**: Different people can have their own settings
- **Process History**: Keep track of what files were processed when
- **Team Features**: Multiple people working together
- **Better Security**: Extra protection for sensitive documents

## 🛠️ Development

### Backend Development

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run.py
```

### Frontend Development

```bash
cd Frontend
npm install
npm run dev     # Development server
npm run build   # Production build
npm run preview # Preview production build
```

### Project Structure

```
Backend/
├── main.py                # FastAPI application
├── pii_service.py         # PII detection service
├── pdf_processor.py       # PDF processing utilities
├── ollama_client.py       # Ollama integration
├── models.py              # Data models
├── config.py              # Configuration management
├── improved_pii_service.py# Enhanced PII service
├── regex_redactor.py      # Regex-based redaction
├── prompt_generator.py    # Prompt generation for LLM
├── pii_validator.py       # PII validation utilities
├── evaluate_pii_model.py  # Model evaluation scripts
├── fine_tune_ollama.py    # Ollama fine-tuning
├── pii_dataset_generator.py # Synthetic PII data generator
├── debug_logger.py        # Debug logging utilities
├── run.py                 # Entry point script
├── setup.sh               # Setup and install script
├── requirements.txt       # Python dependencies
├── config.env             # Environment configuration
├── uploads/               # Uploaded files
├── outputs/               # Redacted output files
├── logs/                  # Log files
└── venv/                  # Python virtual environment

Frontend/
├── src/
│   ├── components/        # React components
│   ├── services/          # API services
│   ├── types/             # TypeScript types
│   └── App.tsx            # Main application
├── node_modules/          # Node.js dependencies
├── public/                # Static assets (add screenshots here)
├── package.json           # NPM dependencies
├── package-lock.json      # NPM lockfile
├── tailwind.config.js     # Tailwind CSS config
├── postcss.config.js      # PostCSS config
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript config
├── tsconfig.app.json      # TypeScript app config
├── tsconfig.node.json     # TypeScript node config
├── index.html             # HTML entry point
├── eslint.config.js       # ESLint config
└── .gitignore             # Git ignore rules
```

## 🧪 Testing

### Generate Test Files

To create demo files with PII data for testing the redaction system:

```bash
cd Backend
# Make sure reportlab is installed
pip install reportlab>=4.0.0
python3 generate_test_files.py
```

This will create 4 test files in the `test_files/` directory:
- **medical_records_demo.pdf** - 3 pages of medical records with patient PII
- **employee_records_demo.pdf** - 3 pages of employee data with HR information  
- **customer_records_demo.txt** - 3 pages of customer database with e-commerce PII
- **legal_documents_demo.txt** - 3 pages of legal documents with attorney-client information

Each file contains realistic demo data including:
- Names, emails, phone numbers
- Social Security Numbers
- Credit card numbers
- Addresses and dates of birth
- Medical, legal, and financial information

⚠️ **Note**: All data is fictional and generated for testing purposes only!

### Test the Redaction System

1. **Generate test files**:
   ```bash
   cd Backend
   pip install reportlab>=4.0.0  # If not already installed
   python3 generate_test_files.py
   ```

2. **Start the application**:
   ```bash
   # Terminal 1: Backend
   cd Backend
   source venv/bin/activate
   python run.py
   
   # Terminal 2: Frontend  
   cd Frontend
   npm install
   npm run dev
   ```

3. **Test via web interface**:
   - Open `http://localhost:5173`
   - Go to File tab
   - Upload files from `Backend/test_files/`
   - Test different redaction settings

4. **Test via API**:
   ```bash
   curl -X POST "http://localhost:8000/redact-file" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@Backend/test_files/medical_records_demo.pdf" \
     -F "redact_types=[\"name\",\"email\",\"phone\",\"ssn\",\"credit_card\",\"date\"]" \
     -F "export_format=both" \
     -F "preserve_pdf_format=true"
   ```

### Backend Testing
```bash
cd Backend
pip install reportlab>=4.0.0  # For test file generation
python3 generate_test_files.py  # Generate test files
python -m pytest  # Run unit tests
python test_pdf_redaction.py  # PDF-specific tests
```

### Frontend Testing
```bash
cd Frontend
npm run test
```

## 🐛 Troubleshooting

### Common Issues

**Test file generation fails:**
- Install reportlab: `pip install reportlab>=4.0.0`
- Ensure you're in the Backend directory
- Check write permissions for test_files directory

**Backend not starting:**
- Ensure Ollama is installed and running
- Check Python version (3.8+ required)
- Verify virtual environment activation

**PDF format not preserved:**
- Ensure `preserve_pdf_format=true` is set
- Check that PDF has extractable text
- Verify PyMuPDF installation

**Large file processing:**
- Increase `MAX_FILE_SIZE` in configuration
- Monitor memory usage for large PDFs
- Consider processing during off-peak hours

**Frontend connection issues:**
- Verify backend is running on port 8000
- Check CORS settings in backend configuration
- Ensure frontend is connecting to correct API endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local LLM capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the robust backend framework
- [React](https://reactjs.org/) and [Vite](https://vitejs.dev/) for the modern frontend stack
- [Tailwind CSS](https://tailwindcss.com/) for beautiful, responsive design

## 📞 Support

If you encounter any issues or have questions, please [open an issue](../../issues) on GitHub.

---

**Built with ❤️ for privacy and data protection**