import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional, List
import json
from pathlib import Path

from config import Config
from models import (
    RedactRequest, RedactResponse, ErrorResponse, HealthResponse,
    FileRedactRequest, FileRedactResponse, FileInfo
)
from ollama_client import OllamaClient
from pii_service import PIIService
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
ollama_client = None
pii_service = None
pdf_processor = None

# Create necessary directories before app initialization
def create_directories():
    """Create upload and output directories if they don't exist"""
    upload_dir = Path(Config.UPLOAD_DIR)
    output_dir = Path(Config.OUTPUT_DIR)
    
    upload_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Created/verified directories: {upload_dir}, {output_dir}")

# Create directories
create_directories()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ollama_client, pii_service, pdf_processor
    
    # Startup
    logger.info("Starting PII Redaction API...")
    
    # Validate configuration
    config_issues = Config.validate()
    if config_issues:
        logger.error(f"Configuration issues: {config_issues}")
        raise RuntimeError(f"Invalid configuration: {config_issues}")
    
    # Initialize services
    ollama_client = OllamaClient(
        base_url=Config.OLLAMA_BASE_URL,
        model_name=Config.MODEL_NAME
    )
    pii_service = PIIService(ollama_client)
    pdf_processor = PDFProcessor(
        upload_dir=Config.UPLOAD_DIR,
        output_dir=Config.OUTPUT_DIR
    )
    
    logger.info(f"Initialized with model: {Config.MODEL_NAME}")
    logger.info(f"Ollama URL: {Config.OLLAMA_BASE_URL}")
    logger.info(f"Hybrid mode: {'enabled' if Config.HYBRID_MODE_ENABLED else 'disabled'}")
    logger.info(f"Upload directory: {Config.UPLOAD_DIR}")
    logger.info(f"Output directory: {Config.OUTPUT_DIR}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PII Redaction API...")


# Create FastAPI app
app = FastAPI(
    title="PII Redaction API",
    description="A FastAPI backend for redacting Personally Identifiable Information using Ollama LLM with file upload support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for downloads
app.mount("/downloads", StaticFiles(directory=Config.OUTPUT_DIR), name="downloads")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PII Redaction API",
        "version": "1.0.0",
        "description": "Redact Personally Identifiable Information using Ollama LLM with file support",
        "endpoints": {
            "redact": "/redact",
            "redact-file": "/redact-file",
            "download": "/download/{filename}",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not pii_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    status_info = await pii_service.get_service_status()
    
    return HealthResponse(
        status=status_info["service_status"],
        ollama_status=status_info["ollama_status"],
        model=status_info["model_name"],
        timestamp=datetime.now().isoformat()
    )


@app.post("/redact", response_model=RedactResponse)
async def redact_pii(request: RedactRequest):
    """
    Redact PII from input text
    
    - **text**: Input text containing PII to redact
    - **redact_types**: Optional list of PII types to redact (defaults to all)
    - **custom_tags**: Optional custom replacement tags for PII types
    """
    if not pii_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"Processing redaction request for {len(request.text)} characters")
        logger.debug(f"Redact types: {request.redact_types}")
        
        success, response, error = await pii_service.redact_text(
            request, 
            use_hybrid=Config.HYBRID_MODE_ENABLED
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=error)
        
        logger.info(f"Redaction completed. Summary: {response.summary}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing redaction request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/redact-file", response_model=FileRedactResponse)
async def redact_file(
    file: UploadFile = File(..., description="PDF or text file to redact"),
    redact_types: Optional[str] = Form(default='["name", "email", "phone", "address", "credit_card", "date"]'),
    custom_tags: Optional[str] = Form(default=None),
    export_format: str = Form(default="both", description="Export format: pdf, txt, or both"),
    use_ocr: bool = Form(default=False, description="Use OCR for PDF text extraction if normal extraction fails"),
    preserve_pdf_format: bool = Form(default=True, description="Preserve original PDF formatting when creating redacted PDF")
):
    """
    Upload and redact PII from a file (PDF or text)
    
    - **file**: PDF or text file to process
    - **redact_types**: JSON string of PII types to redact
    - **custom_tags**: JSON string of custom replacement tags
    - **export_format**: Output format (pdf, txt, or both)
    - **use_ocr**: Use OCR fallback for PDF text extraction
    - **preserve_pdf_format**: Preserve original PDF formatting when creating redacted PDF
    """
    if not pii_service or not pdf_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if file.size and file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Parse form data
        try:
            redact_types_list = json.loads(redact_types)
            custom_tags_dict = json.loads(custom_tags) if custom_tags else None
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in form data: {str(e)}")
        
        # Validate export format
        if export_format not in ["pdf", "txt", "both"]:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file
        saved_path = await pdf_processor.save_uploaded_file(file_content, file.filename)
        
        try:
            # Extract text from file
            if file.filename.lower().endswith('.pdf'):
                # Validate PDF
                is_valid, error_msg = pdf_processor.validate_pdf(saved_path)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=f"Invalid PDF: {error_msg}")
                
                # Get PDF info for logging
                pdf_info = pdf_processor.get_pdf_info(saved_path)
                logger.info(f"Processing PDF: {pdf_info.get('page_count', 'unknown')} pages, {pdf_info.get('file_size', 0)} bytes")
                
                # Extract text from PDF with improved extraction
                if use_ocr:
                    # User explicitly requested OCR, use OCR fallback method
                    success, extracted_text, error = pdf_processor.extract_text_with_ocr_fallback(saved_path)
                else:
                    # Try normal extraction first, then automatically fallback to OCR if it fails
                    success, extracted_text, error = pdf_processor.extract_text_from_pdf(saved_path)
                    
                    # If normal extraction failed, automatically try OCR as fallback
                    if not success:
                        logger.info("Normal text extraction failed, attempting OCR fallback...")
                        success, extracted_text, error = pdf_processor.extract_text_with_ocr_fallback(saved_path)
                        if success:
                            logger.info("OCR fallback successful")
                        else:
                            logger.error(f"OCR fallback also failed: {error}")
                
                if not success:
                    raise HTTPException(status_code=400, detail=f"Failed to extract text: {error}")
                
                logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
                
            else:
                # Assume text file
                extracted_text = file_content.decode('utf-8')
                logger.info(f"Processing text file: {len(extracted_text)} characters")
            
            # Create redaction request
            redact_request = RedactRequest(
                text=extracted_text,
                redact_types=redact_types_list,
                custom_tags=custom_tags_dict
            )
            
            # Perform redaction
            success, response, error = await pii_service.redact_text(
                redact_request,
                use_hybrid=Config.HYBRID_MODE_ENABLED
            )
            
            if not success:
                raise HTTPException(status_code=500, detail=error)
            
            # Generate output files
            files_generated = []
            file_sizes = {}
            base_filename = os.path.splitext(file.filename)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format in ["txt", "both"]:
                txt_filename = f"{base_filename}_redacted_{timestamp}.txt"
                success, txt_path, error = pdf_processor.create_txt_file(
                    response.redacted, txt_filename
                )
                if success:
                    files_generated.append(txt_filename)
                    file_sizes[txt_filename] = pdf_processor.get_file_size(txt_path)
            
            if export_format in ["pdf", "both"]:
                pdf_filename = f"{base_filename}_redacted_{timestamp}.pdf"
                
                # Choose PDF generation method based on user preference and file type
                if file.filename.lower().endswith('.pdf') and preserve_pdf_format:
                    # For PDF input, try to preserve original formatting
                    logger.info("Using format-preserving PDF generation method")
                    success, pdf_path, error = pdf_processor.create_redacted_pdf_alternative(
                        saved_path, response.redacted, pdf_filename
                    )
                    
                    # If format-preserving method fails, fallback to standard method
                    if not success:
                        logger.warning(f"Format-preserving method failed: {error}")
                        logger.info("Falling back to standard PDF generation")
                        success, pdf_path, error = pdf_processor.create_pdf_from_text(
                            response.redacted, pdf_filename
                        )
                else:
                    # For text files or when format preservation is not requested
                    logger.info("Using standard PDF generation method")
                    success, pdf_path, error = pdf_processor.create_pdf_from_text(
                        response.redacted, pdf_filename
                    )
                
                if success:
                    files_generated.append(pdf_filename)
                    file_sizes[pdf_filename] = pdf_processor.get_file_size(pdf_path)
                    logger.info(f"Successfully generated PDF: {pdf_filename}")
                else:
                    logger.error(f"Failed to generate PDF: {error}")
                    # Don't raise exception, just log the error and continue
            
            # Clean up uploaded file
            pdf_processor.cleanup_file(saved_path)
            
            logger.info(f"File processing completed. Generated {len(files_generated)} files")
            
            return FileRedactResponse(
                original_text=response.original,
                redacted_text=response.redacted,
                summary=response.summary,
                redact_types_used=response.redact_types_used,
                files_generated=files_generated,
                file_sizes=file_sizes
            )
            
        except HTTPException:
            # Clean up on error
            pdf_processor.cleanup_file(saved_path)
            raise
        except Exception as e:
            # Clean up on error
            pdf_processor.cleanup_file(saved_path)
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a generated file
    
    - **filename**: Name of the file to download
    """
    if not pdf_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        file_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type
        if filename.lower().endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.lower().endswith('.txt'):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/supported-types")
async def get_supported_types():
    """Get information about supported PII types"""
    if not pii_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return pii_service.get_supported_types()


@app.get("/supported-formats")
async def get_supported_formats():
    """Get information about supported file formats"""
    if not pdf_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Get OCR status
    ocr_status = pdf_processor.get_ocr_status()
    
    return {
        "upload_formats": ["pdf", "txt"],
        "export_formats": ["pdf", "txt", "both"],
        "max_file_size": Config.MAX_FILE_SIZE,
        "max_files_per_request": Config.MAX_FILES_PER_REQUEST,
        "pdf_extraction_methods": ["PyMuPDF", "pdfplumber", "PyPDF2"],
        "ocr_support": ocr_status,
        "auto_ocr_fallback": True,
        "recommendations": {
            "scanned_pdfs": "Use OCR for scanned PDFs or images of text",
            "text_pdfs": "Normal extraction works for most text-based PDFs",
            "mixed_content": "Auto-fallback to OCR if normal extraction fails"
        }
    }


@app.post("/analyze")
async def analyze_pii(request: RedactRequest):
    """
    Analyze text for PII without redacting
    
    Returns count of each PII type found in the text
    """
    if not pii_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"Processing analysis request for {len(request.text)} characters")
        
        success, summary, error = await pii_service.analyze_text(
            request.text, 
            request.redact_types
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=error)
        
        logger.info(f"Analysis completed. Summary: {summary}")
        return {
            "text": request.text,
            "summary": summary,
            "redact_types_analyzed": request.redact_types
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/create-pdf")
async def create_pdf_from_text(request: dict):
    """
    Create a PDF file from text content
    
    - **text**: Text content to convert to PDF
    - **filename**: Optional filename for the PDF
    """
    if not pdf_processor:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        text = request.get('text', '')
        filename = request.get('filename', f'document_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content provided")
        
        logger.info(f"Creating PDF from text: {len(text)} characters")
        
        # Create PDF from text
        success, pdf_path, error = pdf_processor.create_pdf_from_text(text, filename)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to create PDF: {error}")
        
        file_size = pdf_processor.get_file_size(pdf_path)
        
        logger.info(f"Successfully created PDF: {filename} ({file_size} bytes)")
        
        return {
            "filename": filename,
            "file_size": file_size,
            "message": "PDF created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PDF from text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    )