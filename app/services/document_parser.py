from io import BytesIO
from pypdf import PdfReader

class DocumentParseError(ValueError):
    """Raised when an uploaded document cannot be read as supported text."""

def extract_text(filename: str, content: bytes) -> list[tuple[int | None, str]]:
    """Return text segments; PDF segments carry page numbers, TXT segments do not."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        try:
            reader = PdfReader(BytesIO(content))
            pages = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append((page_number, text))
        except Exception as exc:
            raise DocumentParseError("This PDF could not be read. Check that it is a valid PDF.") from exc
        if not pages:
            raise DocumentParseError("No selectable text was found. Scanned PDFs need OCR, which this MVP does not include.")
        return pages
    if suffix in {"txt", "md"}:
        try:
            text = content.decode("utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise DocumentParseError("Text files must use UTF-8 encoding.") from exc
        if not text:
            raise DocumentParseError("The uploaded text file is empty.")
        return [(None, text)]
    raise DocumentParseError("Unsupported file type. Upload a PDF, TXT, or MD file.")
