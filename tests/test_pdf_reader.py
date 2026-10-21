"""Tests for uploaded PDF validation and extraction."""
from io import BytesIO

import pytest
from pypdf import PdfWriter

from src.pdf_reader import MAX_PDF_BYTES, extract_pdf_text


def test_empty_upload():
    with pytest.raises(ValueError, match="empty"):
        extract_pdf_text(b"")


def test_rejects_non_pdf():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf_text(b"plain text, not a PDF")


def test_rejects_oversized_pdf():
    with pytest.raises(ValueError, match="15 MB"):
        extract_pdf_text(b"%PDF-" + b"0" * MAX_PDF_BYTES)


def test_image_only_or_blank_pdf_explains_limitation():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    data = BytesIO()
    writer.write(data)
    with pytest.raises(ValueError, match="No selectable text"):
        extract_pdf_text(data.getvalue())
