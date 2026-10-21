"""Extract readable text from an uploaded PDF without sending it to a server.

Text-based PDFs are supported. Scanned images require OCR and are not supported.
"""
from io import BytesIO

MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_PAGES = 200
MAX_CHARS = 1_000_000


def extract_pdf_text(data: bytes) -> str:
    """Return PDF text or raise ValueError with an actionable explanation."""
    if not data:
        raise ValueError("The PDF is empty.")
    if len(data) > MAX_PDF_BYTES:
        raise ValueError("The PDF exceeds the 15 MB upload limit.")
    if not data.startswith(b"%PDF-"):
        raise ValueError("This file does not appear to be a valid PDF.")
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")
        if len(reader.pages) > MAX_PAGES:
            raise ValueError("The PDF exceeds the 200-page limit.")
        chunks = []
        length = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            chunks.append(text)
            length += len(text)
            if length > MAX_CHARS:
                raise ValueError("The extracted text exceeds the 1,000,000-character limit.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this PDF. Try exporting it again as a text-based PDF.") from exc
    text = "\n\n".join(chunks).strip()
    if not text:
        raise ValueError("No selectable text was found. This looks like a scanned PDF; OCR is not available yet.")
    return text
