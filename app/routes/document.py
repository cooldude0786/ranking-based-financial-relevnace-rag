from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models import Document, DocumentType
from sqlmodel import Session, select
from app.db import get_session
from app.dependencies import require_roles, get_current_user
import os
import shutil
import uuid


router = APIRouter(prefix="", tags=["Documents"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: DocumentType = Form(...),
    session: Session = Depends(get_session),
    user=Depends(require_roles(["analyst"]))   # 🔥 CLEAN
):
    # 🔒 RBAC check
    if user["role"] != "analyst":
        raise HTTPException(status_code=403, detail="Only analysts can upload documents")
    
    # 🔹 Save file locally
    file.filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file.filename).replace("\\", "/")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔹 Save metadata in DB
    doc = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_path,
        uploaded_by=user["user_id"]  # IMPORTANT
    )

    session.add(doc)
    session.commit()

    return {"msg": "Document uploaded", "filename": file.filename}


@router.get("/")
def get_documents(session: Session = Depends(get_session)):
    return session.exec(select(Document)).all()

@router.get("/{document_id}")
def get_document(document_id: int, session: Session = Depends(get_session)):
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Not found")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: int,
                    session: Session = Depends(get_session),
                    user=Depends(require_roles(["admin"]))):

    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Not found")

    session.delete(doc)
    session.commit()

    return {"msg": "Deleted"}

@router.get("/search")
def search_documents(company_name: str = None,
                     document_type: str = None,
                     session: Session = Depends(get_session)):

    query = select(Document)

    if company_name:
        query = query.where(Document.company_name == company_name)

    if document_type:
        query = query.where(Document.document_type == document_type)

    return session.exec(query).all()