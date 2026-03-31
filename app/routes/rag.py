from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db import get_session
from app.models import Document
from app.dependencies import require_roles
from app.rag.service import model, collection
from app.rag.utils import extract_text, chunk_text

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/index-document")
def index_document(
    doc_id: int,
    session: Session = Depends(get_session),
    user=Depends(require_roles(["analyst"]))
):
    doc = session.get(Document, doc_id)

    if not doc:
        raise HTTPException(404, "Document not found")

    text = extract_text(doc.file_path)

    if not text.strip():
        raise HTTPException(400, "No text extracted")

    chunks = chunk_text(text)

    embeddings = model.encode(chunks).tolist()

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[f"{doc_id}_{i}"],
            metadatas=[{"doc_id": doc_id}]
        )

    return {"msg": "Document indexed", "chunks": len(chunks)}

import re

def extract_invoice_data(text):
    data = {}

    # Extract total
    total_match = re.search(r'TOTAL\s+(\d+\.?\d*)', text)
    if total_match:
        data["total"] = float(total_match.group(1))

    # Extract balance due
    balance_match = re.search(r'Balance\s+Due\s*\$?(\d+\.?\d*)', text)
    if balance_match:
        data["balance_due"] = float(balance_match.group(1))

    # Extract discount
    discount_match = re.search(r'DISCOUNT\s+(\d+\.?\d*)', text)
    if discount_match:
        data["discount"] = float(discount_match.group(1))

    return data

@router.post("/search")
def search(query: dict):
    query_text = query.get("query")

    query_embedding = model.encode([query_text]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )

    docs = results["documents"][0]

    combined_text = " ".join(docs)

    structured_data = extract_invoice_data(combined_text)

    return {
        "query": query_text,
        "structured_data": structured_data,
        "raw_chunks": docs
    }
    
@router.get("/context/{doc_id}")
def get_context(doc_id: int):
    results = collection.get()

    filtered_docs = []

    for id_, doc in zip(results["ids"], results["documents"]):
        if id_.startswith(f"{doc_id}_"):
            filtered_docs.append(doc)

    return {
        "doc_id": doc_id,
        "chunks": filtered_docs
    }
    
    
@router.delete("/remove-document/{doc_id}")
def remove_document(doc_id: int):

    results = collection.get()

    ids_to_delete = [
        id_ for id_ in results["ids"]
        if id_.startswith(f"{doc_id}_")
    ]

    collection.delete(ids=ids_to_delete)

    return {"msg": f"Document {doc_id} removed"}