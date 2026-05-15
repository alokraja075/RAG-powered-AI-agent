from pathlib import Path
from app.services.document_service import extension_to_content_type, extract_text_from_file


def test_extension_mapping():
    assert extension_to_content_type('a.pdf') == 'pdf'
    assert extension_to_content_type('a.docx') == 'docx'
    assert extension_to_content_type('a.txt') == 'txt'


def test_extract_text_txt(tmp_path: Path):
    f = tmp_path / 'sample.txt'
    f.write_text('hello world', encoding='utf-8')
    assert extract_text_from_file(str(f), 'txt') == 'hello world'
