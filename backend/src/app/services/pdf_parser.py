import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text content from PDF binary data.
    Uses pdfplumber primary and PyPDF2/pypdf as fallback.
    """
    text = ""
    
    # 1. Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
            text = "\n".join(pages_text).strip()
    except Exception as e:
        logger.warning(f"pdfplumber not available or failed: {e}")

    # 2. Try PyPDF2 / pypdf
    if not text:
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages_text = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
            text = "\n".join(pages_text).strip()
        except Exception as e:
            logger.warning(f"PyPDF2 fallback failed: {e}")

    # 3. Basic string decoder fallback if libraries aren't installed
    if not text:
        try:
            text = pdf_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = "Resume Profile Content"

    return text
