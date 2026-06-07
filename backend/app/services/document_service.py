import os
from pathlib import Path
from uuid import uuid4
from pypdf import PdfReader
from docx import Document as DocxDocument
from fastapi import UploadFile, HTTPException


ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}


def ensure_upload_dir(upload_dir: str) -> None:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile, upload_dir: str) -> str:
    ensure_upload_dir(upload_dir)
    ext = Path(file.filename or '').suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail='Unsupported file type. Allowed: PDF, TXT, DOCX')
    target_name = f'{uuid4()}{ext}'
    target_path = os.path.join(upload_dir, target_name)
    with open(target_path, 'wb') as out:
        out.write(file.file.read())
    return target_path


def extract_text_from_file(file_path: str, content_type: str) -> str:
    if content_type == 'txt':
        return Path(file_path).read_text(encoding='utf-8', errors='ignore')
    if content_type == 'pdf':
        reader = PdfReader(file_path)
        return '\n'.join([(page.extract_text() or '') for page in reader.pages])
    if content_type == 'docx':
        doc = DocxDocument(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    raise ValueError(f'Unsupported content_type: {content_type}')


def extension_to_content_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return {
        '.txt': 'txt',
        '.pdf': 'pdf',
        '.docx': 'docx',
    }.get(ext, 'unknown')
