import os
import tempfile
import logging
from typing import Tuple, Optional, List
from pathlib import Path
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import aiofiles
import magic
import io
import re

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF upload, text extraction, and PDF generation"""
    
    def __init__(self, upload_dir: str = "uploads", output_dir: str = "outputs"):
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        file_path = self.upload_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        return str(file_path)
    
    def validate_pdf(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if file is a valid PDF
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file type using magic
            file_type = magic.from_file(file_path, mime=True)
            if file_type != 'application/pdf':
                return False, f"File is not a PDF. Detected type: {file_type}"
            
            # Try to open with PyMuPDF to validate
            doc = fitz.open(file_path)
            if doc.page_count == 0:
                doc.close()
                return False, "PDF appears to be empty or corrupted"
            doc.close()
                
            return True, "Valid PDF"
            
        except Exception as e:
            logger.error(f"PDF validation error: {str(e)}")
            return False, f"PDF validation failed: {str(e)}"
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Extract text from PDF file using multiple methods for better extraction
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        extracted_text = ""
        error_messages = []
        
        # Method 1: Try PyMuPDF (fitz) - best for most PDFs
        try:
            logger.info("Attempting text extraction with PyMuPDF...")
            doc = fitz.open(file_path)
            text_parts = []
            
            for page_num in range(doc.page_count):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    else:
                        text_parts.append(f"--- Page {page_num + 1} ---\n[No text found on this page]")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1} with PyMuPDF: {str(e)}")
                    text_parts.append(f"--- Page {page_num + 1} ---\n[Text extraction failed]")
            
            doc.close()
            extracted_text = "\n\n".join(text_parts)
            
            if extracted_text.strip() and not all("[No text found" in part or "[Text extraction failed]" in part for part in text_parts):
                logger.info("Successfully extracted text with PyMuPDF")
                return True, extracted_text, ""
            else:
                error_messages.append("PyMuPDF: No readable text found")
                
        except Exception as e:
            error_messages.append(f"PyMuPDF failed: {str(e)}")
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
        
        # Method 2: Try pdfplumber - good for complex layouts
        try:
            logger.info("Attempting text extraction with pdfplumber...")
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                        else:
                            text_parts.append(f"--- Page {page_num + 1} ---\n[No text found on this page]")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1} with pdfplumber: {str(e)}")
                        text_parts.append(f"--- Page {page_num + 1} ---\n[Text extraction failed]")
                
                extracted_text = "\n\n".join(text_parts)
                
                if extracted_text.strip() and not all("[No text found" in part or "[Text extraction failed]" in part for part in text_parts):
                    logger.info("Successfully extracted text with pdfplumber")
                    return True, extracted_text, ""
                else:
                    error_messages.append("pdfplumber: No readable text found")
                    
        except Exception as e:
            error_messages.append(f"pdfplumber failed: {str(e)}")
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Method 3: Try PyPDF2 - fallback method
        try:
            logger.info("Attempting text extraction with PyPDF2...")
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                text_parts = []
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                        else:
                            text_parts.append(f"--- Page {page_num + 1} ---\n[No text found on this page]")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1} with PyPDF2: {str(e)}")
                        text_parts.append(f"--- Page {page_num + 1} ---\n[Text extraction failed]")
                
                extracted_text = "\n\n".join(text_parts)
                
                if extracted_text.strip() and not all("[No text found" in part or "[Text extraction failed]" in part for part in text_parts):
                    logger.info("Successfully extracted text with PyPDF2")
                    return True, extracted_text, ""
                else:
                    error_messages.append("PyPDF2: No readable text found")
                    
        except Exception as e:
            error_messages.append(f"PyPDF2 failed: {str(e)}")
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # If all methods failed
        combined_error = "; ".join(error_messages)
        logger.error(f"All PDF text extraction methods failed: {combined_error}")
        return False, "", f"Failed to extract text from PDF. Errors: {combined_error}"
    
    def extract_text_with_ocr_fallback(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Extract text from PDF with OCR fallback (if OCR libraries are available)
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        # First try normal text extraction
        success, text, error = self.extract_text_from_pdf(file_path)
        
        if success:
            return success, text, error
        
        # If normal extraction failed, try OCR (if available)
        try:
            import pytesseract
            from PIL import Image
            import fitz
            
            logger.info("Attempting OCR text extraction...")
            
            doc = fitz.open(file_path)
            text_parts = []
            
            for page_num in range(doc.page_count):
                try:
                    page = doc.load_page(page_num)
                    # Convert page to image
                    mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Use PIL to open image
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Extract text using OCR
                    page_text = pytesseract.image_to_string(img)
                    
                    if page_text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    else:
                        text_parts.append(f"--- Page {page_num + 1} ---\n[No text found with OCR]")
                        
                except Exception as e:
                    logger.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
                    text_parts.append(f"--- Page {page_num + 1} ---\n[OCR extraction failed]")
            
            doc.close()
            
            extracted_text = "\n\n".join(text_parts)
            
            if extracted_text.strip() and not all("[No text found" in part or "[OCR extraction failed]" in part for part in text_parts):
                logger.info("Successfully extracted text with OCR")
                return True, extracted_text, ""
            else:
                return False, "", "OCR extraction failed - no readable text found"
                
        except ImportError as e:
            missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
            logger.error(f"OCR libraries not available: {missing_lib}")
            return False, "", f"OCR not available ({missing_lib} not installed). Please install pytesseract and PIL, or try a different PDF file."
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return False, "", f"OCR extraction failed: {str(e)}"
    
    def create_pdf_from_text(self, text: str, filename: str) -> Tuple[bool, str, str]:
        """
        Create a new PDF from text content
        
        Args:
            text: Text content to include in PDF
            filename: Output filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            output_path = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Create custom style for better formatting
            custom_style = ParagraphStyle(
                'CustomStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceAfter=6
            )
            
            # Split text into paragraphs and create story
            story = []
            paragraphs = text.split('\n\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Handle page markers
                    if paragraph.startswith('--- Page'):
                        story.append(Spacer(1, 12))
                        story.append(Paragraph(paragraph, styles['Heading2']))
                        story.append(Spacer(1, 6))
                    else:
                        story.append(Paragraph(paragraph, custom_style))
                        story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Created PDF: {output_path}")
            return True, str(output_path), ""
            
        except Exception as e:
            logger.error(f"PDF creation error: {str(e)}")
            return False, "", f"Failed to create PDF: {str(e)}"
    
    def create_txt_file(self, text: str, filename: str) -> Tuple[bool, str, str]:
        """
        Create a text file from content
        
        Args:
            text: Text content to save
            filename: Output filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            output_path = self.output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Created text file: {output_path}")
            return True, str(output_path), ""
            
        except Exception as e:
            logger.error(f"Text file creation error: {str(e)}")
            return False, "", f"Failed to create text file: {str(e)}"
    
    def cleanup_file(self, file_path: str) -> None:
        """
        Clean up temporary file
        
        Args:
            file_path: Path to file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            List of supported formats
        """
        return ["pdf", "txt"]
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get information about a PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            doc = fitz.open(file_path)
            info = {
                "page_count": doc.page_count,
                "file_size": self.get_file_size(file_path),
                "metadata": doc.metadata
            }
            doc.close()
            return info
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return {"error": str(e)}
    
    def create_redacted_pdf_preserving_format(self, original_pdf_path: str, redacted_text: str, filename: str) -> Tuple[bool, str, str]:
        """
        Create a redacted PDF that preserves the original formatting and structure
        
        Args:
            original_pdf_path: Path to the original PDF file
            redacted_text: Redacted text content
            filename: Output filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            output_path = self.output_dir / filename
            
            # Open the original PDF
            doc = fitz.open(original_pdf_path)
            
            # Create a new PDF document
            new_doc = fitz.open()
            
            # Split redacted text by pages
            page_texts = self._split_text_by_pages(redacted_text)
            
            for page_num in range(doc.page_count):
                try:
                    # Get the original page
                    original_page = doc.load_page(page_num)
                    
                    # Create a new page with the same size
                    new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
                    
                    # Copy the original page content (images, graphics, etc.)
                    new_page.show_pdf_page(new_page.rect, doc, page_num)
                    
                    # Get the redacted text for this page
                    page_text = page_texts.get(page_num, "")
                    
                    if page_text.strip():
                        # Extract text blocks from the original page to understand layout
                        text_blocks = original_page.get_text("dict")
                        
                        # Apply redacted text while preserving layout
                        self._apply_redacted_text_to_page(new_page, page_text, text_blocks)
                    
                except Exception as e:
                    logger.warning(f"Failed to process page {page_num + 1}: {str(e)}")
                    # If processing fails, just copy the original page
                    original_page = doc.load_page(page_num)
                    new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # Save the new PDF
            new_doc.save(str(output_path))
            new_doc.close()
            doc.close()
            
            logger.info(f"Created redacted PDF preserving format: {output_path}")
            return True, str(output_path), ""
            
        except Exception as e:
            logger.error(f"Error creating redacted PDF: {str(e)}")
            return False, "", f"Failed to create redacted PDF: {str(e)}"
    
    def _split_text_by_pages(self, text: str) -> dict:
        """
        Split redacted text by pages based on page markers
        
        Args:
            text: Full redacted text
            
        Returns:
            Dictionary mapping page numbers to page text
        """
        pages = {}
        current_page = 0
        current_text = []
        
        lines = text.split('\n')
        for line in lines:
            # Check for page marker
            page_match = re.match(r'--- Page (\d+) ---', line)
            if page_match:
                # Save previous page
                if current_text:
                    pages[current_page] = '\n'.join(current_text)
                
                # Start new page
                current_page = int(page_match.group(1)) - 1  # Convert to 0-based index
                current_text = []
            else:
                current_text.append(line)
        
        # Save the last page
        if current_text:
            pages[current_page] = '\n'.join(current_text)
        
        return pages
    
    def _apply_redacted_text_to_page(self, page, redacted_text: str, original_blocks: dict):
        """
        Apply redacted text to a page while preserving layout
        
        Args:
            page: PyMuPDF page object
            redacted_text: Redacted text for this page
            original_blocks: Original text blocks from the page
        """
        try:
            # Get text blocks from original page
            blocks = original_blocks.get("blocks", [])
            text_blocks = [b for b in blocks if b.get("type") == 0]  # Text blocks only
            
            if not text_blocks:
                # No text blocks found, create a properly formatted layout
                self._insert_text_with_proper_formatting(page, redacted_text)
                return
            
            # Collect all text spans with their positions
            text_spans = []
            for block in text_blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        bbox = span.get("bbox")
                        if bbox:
                            text_spans.append({
                                "bbox": bbox,
                                "text": span.get("text", ""),
                                "font": span.get("font", "helv"),
                                "size": span.get("size", 12),
                                "flags": span.get("flags", 0),
                                "color": span.get("color", 0)
                            })
            
            # Sort spans by vertical position (top to bottom), then horizontal (left to right)
            text_spans.sort(key=lambda x: (x["bbox"][1], x["bbox"][0]))
            
            # Create white rectangles to cover original text with better coverage
            for span in text_spans:
                rect = fitz.Rect(span["bbox"])
                # Add padding to ensure complete coverage
                rect.x0 -= 4
                rect.y0 -= 4
                rect.x1 += 4
                rect.y1 += 4
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Apply redacted text with improved positioning
            self._insert_redacted_text_with_improved_layout(page, redacted_text, text_spans)
                        
        except Exception as e:
            logger.warning(f"Error applying redacted text to page: {str(e)}")
            # Fallback to simple insertion
            self._insert_text_with_proper_formatting(page, redacted_text)

    def _insert_redacted_text_with_improved_layout(self, page, redacted_text: str, text_spans: list):
        """
        Insert redacted text using improved layout positioning
        
        Args:
            page: PyMuPDF page object
            redacted_text: Redacted text to insert
            text_spans: List of original text spans with position info
        """
        try:
            # Split redacted text into lines
            redacted_lines = [line.strip() for line in redacted_text.strip().split('\n') if line.strip()]
            
            if not redacted_lines or not text_spans:
                self._insert_text_with_proper_formatting(page, redacted_text)
                return
            
            # Get positioning info from first span
            first_span = text_spans[0]
            start_x = first_span["bbox"][0]
            
            # Calculate proper Y position - use the baseline of the text
            baseline_y = first_span["bbox"][3]  # Bottom of the bounding box is closer to baseline
            
            # Use font info from first span
            font_size = max(first_span["size"], 10)
            font_name = first_span["font"] if first_span["font"] else "helv"
            line_height = font_size * 1.3
            
            # Calculate available width
            page_width = page.rect.width
            available_width = page_width - start_x - 50  # Right margin
            
            current_y = baseline_y
            
            # Insert text with proper line wrapping and spacing
            for line in redacted_lines:
                if current_y > page.rect.height - 50:  # Bottom margin
                    break
                    
                if not line:
                    current_y += line_height * 0.5
                    continue
                
                # Wrap text if necessary
                wrapped_lines = self._wrap_text_to_width_advanced(line, available_width, font_size)
                
                for wrapped_line in wrapped_lines:
                    if current_y > page.rect.height - 50:
                        break
                    
                    # Insert text at proper position
                    page.insert_text(
                        fitz.Point(start_x, current_y),
                        wrapped_line,
                        fontsize=font_size,
                        fontname=font_name,
                        color=(0, 0, 0)  # Ensure black text
                    )
                    current_y += line_height
                    
        except Exception as e:
            logger.warning(f"Error in improved layout text insertion: {str(e)}")
            self._insert_text_with_proper_formatting(page, redacted_text)

    def is_ocr_available(self) -> bool:
        """
        Check if OCR libraries are available
        
        Returns:
            True if OCR is available, False otherwise
        """
        try:
            import pytesseract
            from PIL import Image
            return True
        except ImportError:
            return False

    def get_ocr_status(self) -> dict:
        """
        Get detailed OCR status information
        
        Returns:
            Dictionary with OCR status information
        """
        try:
            import pytesseract
            from PIL import Image
            
            # Test if tesseract is properly installed
            try:
                version = pytesseract.get_tesseract_version()
                return {
                    "available": True,
                    "tesseract_version": str(version),
                    "pil_available": True,
                    "message": "OCR is available and ready to use"
                }
            except Exception as e:
                return {
                    "available": False,
                    "tesseract_version": None,
                    "pil_available": True,
                    "message": f"Tesseract not properly installed: {str(e)}"
                }
                
        except ImportError as e:
            missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
            return {
                "available": False,
                "tesseract_version": None,
                "pil_available": False,
                "message": f"OCR libraries not available: {missing_lib} not installed"
            }
    
    def _insert_text_with_proper_formatting(self, page, text: str):
        """
        Insert text with proper formatting and line breaks
        
        Args:
            page: PyMuPDF page object
            text: Text to insert
        """
        try:
            # Page dimensions
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Margins
            left_margin = 50
            right_margin = 50
            top_margin = 50
            bottom_margin = 50
            
            # Text area
            text_width = page_width - left_margin - right_margin
            
            # Font settings
            font_size = 11
            font_name = "helv"
            line_height = font_size * 1.2
            
            # Split text into lines and handle wrapping
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                if not line.strip():
                    formatted_lines.append("")
                    continue
                    
                # Handle long lines by wrapping
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    # Estimate text width (approximate)
                    estimated_width = len(test_line) * font_size * 0.6
                    
                    if estimated_width <= text_width:
                        current_line = test_line
                    else:
                        if current_line:
                            formatted_lines.append(current_line)
                            current_line = word
                        else:
                            # Word is too long, split it
                            formatted_lines.append(word)
                            current_line = ""
                
                if current_line:
                    formatted_lines.append(current_line)
            
            # Insert text line by line
            current_y = top_margin
            for line in formatted_lines:
                if current_y > page_height - bottom_margin:
                    break
                    
                page.insert_text(
                    fitz.Point(left_margin, current_y),
                    line,
                    fontsize=font_size,
                    fontname=font_name
                )
                current_y += line_height
                
        except Exception as e:
            logger.error(f"Error in text formatting: {str(e)}")

    def _wrap_text_to_width_advanced(self, text: str, max_width: float, font_size: float) -> list:
        """
        Advanced text wrapping with better width estimation
        
        Args:
            text: Text to wrap
            max_width: Maximum width in points
            font_size: Font size
            
        Returns:
            List of wrapped lines
        """
        if not text.strip():
            return [""]
        
        # More accurate character width estimation for common fonts
        char_width = font_size * 0.55  # Better approximation for most fonts
        chars_per_line = max(int(max_width / char_width), 20)  # Minimum 20 chars per line
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, try to break it
                    if len(word) > chars_per_line:
                        # Break very long words
                        while len(word) > chars_per_line:
                            lines.append(word[:chars_per_line])
                            word = word[chars_per_line:]
                        current_line = word
                    else:
                        lines.append(word)
                        current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]

    def create_redacted_pdf_alternative(self, original_pdf_path: str, redacted_text: str, filename: str) -> Tuple[bool, str, str]:
        """
        Alternative method to create redacted PDF with better text positioning
        
        Args:
            original_pdf_path: Path to the original PDF file
            redacted_text: Redacted text content
            filename: Output filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            output_path = self.output_dir / filename
            
            # Open the original PDF
            doc = fitz.open(original_pdf_path)
            
            # Create a new PDF document
            new_doc = fitz.open()
            
            # Split redacted text by pages
            page_texts = self._split_text_by_pages(redacted_text)
            
            for page_num in range(doc.page_count):
                try:
                    # Get the original page
                    original_page = doc.load_page(page_num)
                    
                    # Create a new page with the same size
                    new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
                    
                    # Copy the original page content (images, graphics, etc.)
                    new_page.show_pdf_page(new_page.rect, doc, page_num)
                    
                    # Get the redacted text for this page
                    page_text = page_texts.get(page_num, "")
                    
                    if page_text.strip():
                        # Use a more sophisticated approach for text replacement
                        self._apply_redacted_text_advanced(new_page, page_text, original_page)
                    
                except Exception as e:
                    logger.warning(f"Failed to process page {page_num + 1}: {str(e)}")
                    # If processing fails, just copy the original page
                    original_page = doc.load_page(page_num)
                    new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # Save the new PDF
            new_doc.save(str(output_path))
            new_doc.close()
            doc.close()
            
            logger.info(f"Created redacted PDF with alternative method: {output_path}")
            return True, str(output_path), ""
            
        except Exception as e:
            logger.error(f"Error creating redacted PDF with alternative method: {str(e)}")
            return False, "", f"Failed to create redacted PDF: {str(e)}"

    def _apply_redacted_text_advanced(self, page, redacted_text: str, original_page):
        """
        Advanced method to apply redacted text with better positioning
        
        Args:
            page: PyMuPDF page object (new page)
            redacted_text: Redacted text for this page
            original_page: Original page object
        """
        try:
            # Extract text blocks with their positions
            text_dict = original_page.get_text("dict")
            blocks = text_dict.get("blocks", [])
            
            # Collect all text spans with their positions
            text_spans = []
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            bbox = span.get("bbox")
                            if bbox:
                                text_spans.append({
                                    "bbox": bbox,
                                    "text": span.get("text", ""),
                                    "font": span.get("font", "helv"),
                                    "size": span.get("size", 12),
                                    "flags": span.get("flags", 0)
                                })
            
            # Sort by vertical position (top to bottom), then horizontal (left to right)
            text_spans.sort(key=lambda x: (x["bbox"][1], x["bbox"][0]))
            
            # Create white rectangles to cover original text with proper padding
            for span in text_spans:
                rect = fitz.Rect(span["bbox"])
                # Add more padding to ensure complete coverage
                rect.x0 -= 3
                rect.y0 -= 3
                rect.x1 += 3
                rect.y1 += 3
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Split redacted text into lines, preserving structure
            redacted_lines = []
            for line in redacted_text.strip().split('\n'):
                if line.strip():
                    redacted_lines.append(line.strip())
            
            if not redacted_lines or not text_spans:
                self._insert_text_with_proper_formatting(page, redacted_text)
                return
            
            # Calculate better positioning based on original text layout
            self._apply_redacted_text_with_proper_spacing(page, redacted_lines, text_spans)
                        
        except Exception as e:
            logger.warning(f"Error in advanced text application: {str(e)}")
            # Fallback to simple text insertion
            self._insert_text_with_proper_formatting(page, redacted_text)

    def _apply_redacted_text_with_proper_spacing(self, page, redacted_lines: list, text_spans: list):
        """
        Apply redacted text with proper spacing and positioning
        
        Args:
            page: PyMuPDF page object
            redacted_lines: List of redacted text lines
            text_spans: List of original text spans with position info
        """
        try:
            if not text_spans or not redacted_lines:
                return
            
            # Get the first text span for initial positioning
            first_span = text_spans[0]
            start_x = first_span["bbox"][0]
            start_y = first_span["bbox"][1] + first_span["size"]  # Position below the baseline
            
            # Use font info from first span
            font_size = max(first_span["size"], 10)
            font_name = first_span["font"] if first_span["font"] else "helv"
            line_height = font_size * 1.4  # Increased line height for better spacing
            
            # Calculate available width
            page_width = page.rect.width
            right_margin = 50
            available_width = page_width - start_x - right_margin
            
            current_y = start_y
            
            # Process each line with proper wrapping
            for line in redacted_lines:
                if current_y > page.rect.height - 50:  # Bottom margin check
                    break
                
                if not line.strip():
                    current_y += line_height * 0.5  # Smaller spacing for empty lines
                    continue
                
                # Wrap text if too long
                wrapped_lines = self._wrap_text_to_width_advanced(line, available_width, font_size)
                
                for wrapped_line in wrapped_lines:
                    if current_y > page.rect.height - 50:
                        break
                    
                    # Insert text with proper positioning
                    page.insert_text(
                        fitz.Point(start_x, current_y),
                        wrapped_line,
                        fontsize=font_size,
                        fontname=font_name,
                        color=(0, 0, 0)  # Ensure black text
                    )
                    current_y += line_height
                    
        except Exception as e:
            logger.warning(f"Error in proper spacing text application: {str(e)}")