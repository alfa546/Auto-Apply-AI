import io
import logging
import pdfplumber
import PyPDF2

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text content from PDF binary data.
    Uses pdfplumber primary and PyPDF2 as a fallback.
    """
    text = ""
    # Try pdfplumber first
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text).strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed to extract text: {e}. Trying PyPDF2 fallback.")

    # Fallback to PyPDF2 if pdfplumber failed or returned empty text
    if not text:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages_text = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text).strip()
        except Exception as e:
            logger.error(f"PyPDF2 fallback also failed: {e}")
            raise ValueError("Could not extract text from the provided PDF file.") from e

    return text
