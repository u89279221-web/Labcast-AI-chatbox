import io
import logging
from typing import Optional
from fastapi import UploadFile
import pypdf
import pytesseract
from pdf2image import convert_from_bytes
import re

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, bool]:
    """
    Extracts text from a PDF file. 
    First tries standard extraction (pypdf). 
    If that yields little to no text (indicating a scanned document), it falls back to OCR.
    """
    text_content = []
    used_ocr = False
    
    # Try pypdf first
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        logger.error(f"pypdf extraction failed: {e}")
        
    combined_text = "\n".join(text_content).strip()
    
    # If the text is very short, it's likely a scanned image. Use OCR fallback.
    if len(combined_text) < 50 * (len(reader.pages) if 'reader' in locals() else 1):
        logger.info("Text length too short. Falling back to OCR...")
        try:
            # We must configure poppler in pdf2image if it's not in PATH, but assuming it is for this scope
            images = convert_from_bytes(file_bytes)
            ocr_texts = []
            for img in images:
                page_text = pytesseract.image_to_string(img)
                ocr_texts.append(page_text)
            combined_text = "\n".join(ocr_texts).strip()
            used_ocr = True
        except Exception as e:
            logger.error(f"OCR fallback failed: {e}")
            # OCR might fail if tesseract or poppler isn't installed. 
            # We return whatever we have (which might be empty).
            
    return combined_text, used_ocr

def clean_text(text: str) -> str:
    """Removes excessive whitespace and garbage characters."""
    if not text:
        return ""
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from a Microsoft Word (.docx) document."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.error(f"docx extraction failed: {e}")
        return ""

def process_upload(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """Main pipeline for processing an uploaded file into extracted text."""
    logger.info(f"Processing uploaded file: {filename}")
    
    fn_lower = filename.lower()
    if fn_lower.endswith(".pdf"):
        raw_text, used_ocr = extract_text_from_pdf(file_bytes)
        extraction_method = "OCR" if used_ocr else "Standard"
    elif fn_lower.endswith(".docx") or fn_lower.endswith(".doc"):
        raw_text = extract_text_from_docx(file_bytes)
        extraction_method = "Standard"
    else:
        # If it's a raw image or text file, try utf-8 decode first
        try:
            raw_text = file_bytes.decode('utf-8')
            extraction_method = "Standard"
        except UnicodeDecodeError:
            try:
                from PIL import Image
                img = Image.open(io.BytesIO(file_bytes))
                raw_text = pytesseract.image_to_string(img)
                extraction_method = "OCR"
            except Exception as e:
                logger.error(f"Failed to decode or OCR non-PDF file: {e}")
                raw_text = ""
                extraction_method = "Failed"
                
    cleaned = clean_text(raw_text)
    return cleaned, extraction_method
