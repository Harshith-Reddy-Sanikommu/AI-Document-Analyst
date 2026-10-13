import pytest
from app.services.document_parser import extract_text, DocumentParseError

def test_text_file_is_extracted():
    segments = extract_text("notes.txt", b"Important project notes.")
    assert segments == [(None, "Important project notes.")]

def test_empty_text_is_rejected():
    with pytest.raises(DocumentParseError):
        extract_text("empty.txt", b"   ")

def test_unsupported_file_is_rejected():
    with pytest.raises(DocumentParseError):
        extract_text("image.png", b"fake image")
