import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db import get_db
from app.models.entities import Document, User
from app.routers.deps import get_current_user
from app.schemas.documents import DocumentResponse, IndexResponse
from app.services.document_service import save_upload, extension_to_content_type, extract_text_from_file
from app.services.rag_service import index_document, get_vector_store


router = APIRouter(prefix='/api/documents', tags=['documents'])


@router.post('/upload', response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    path = save_upload(file, settings.upload_directory)
    content_type = extension_to_content_type(file.filename or '')
    if content_type == 'unknown':
        raise HTTPException(status_code=400, detail='Unknown file type')

    doc = Document(
        user_id=current_user.id,
        filename=file.filename or os.path.basename(path),
        content_type=content_type,
        file_path=path,
        indexed=False,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    text = extract_text_from_file(path, content_type)
    if text.strip():
        index_document(text=text, source=doc.filename, user_id=current_user.id, document_id=doc.id)
        doc.indexed = True
        db.commit()
    return doc


@router.post('/{document_id}/index', response_model=IndexResponse)
def index_existing_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    text = extract_text_from_file(doc.file_path, doc.content_type)
    index_document(text=text, source=doc.filename, user_id=current_user.id, document_id=doc.id)
    doc.indexed = True
    db.commit()
    return IndexResponse(document_id=doc.id, indexed=True)


@router.get('/', response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()


@router.delete('/{document_id}')
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except OSError:
        pass
    vector_store = get_vector_store()
    results = vector_store.get(where={'document_id': str(doc.id)})
    ids = results.get('ids', []) if results else []
    if ids:
        vector_store.delete(ids=ids)
    db.delete(doc)
    db.commit()
    return {'status': 'deleted'}
