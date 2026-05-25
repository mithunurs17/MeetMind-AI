from typing import Optional
from fastapi import UploadFile
import io

def _read_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        try:
            return file_bytes.decode("latin-1")
        except Exception:
            return ""


def extract_text_from_file(upload_file: UploadFile) -> str:
    """Extract text from common document types: txt, pdf, docx, images.

    Returns the extracted text (best-effort).
    """
    filename = upload_file.filename or ""
    content_type = upload_file.content_type or ""
    data = upload_file.file.read()

    lower = filename.lower()
    # TXT
    if lower.endswith('.txt') or content_type.startswith('text/'):
        return _read_txt(data)

    # PDF
    if lower.endswith('.pdf') or content_type == 'application/pdf':
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages)
        except Exception:
            return ""

    # DOCX
    if lower.endswith('.docx') or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        try:
            import docx

            doc = docx.Document(io.BytesIO(data))
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs)
        except Exception:
            return ""

    # Images (PNG/JPG)
    if content_type.startswith('image/') or any(lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(data))
            text = pytesseract.image_to_string(image)
            return text
        except Exception:
            return ""

    # Fallback: try to decode
    return _read_txt(data)
