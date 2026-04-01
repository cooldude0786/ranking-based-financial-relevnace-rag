from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from app.db import get_session
from app.models import Document
from app.dependencies import require_roles
from app.rag.service import model, collection
from app.rag.utils import extract_text, chunk_text

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/index-document")
def index_document(
    body: dict = Body(...),
    session: Session = Depends(get_session),
    user=Depends(require_roles(["analyst"]))
):
    document_id = body.get("document_id")
    
    if not document_id:
        raise HTTPException(400, "document_id is required")
    
    doc = session.get(Document, document_id)

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
            ids=[f"{document_id}_{i}"],
            metadatas=[{"doc_id": document_id}]
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
def search(body: dict = Body(...)):
    query_text = body.get("query")
    
    if not query_text:
        raise HTTPException(400, "query is required")

    query_embedding = model.encode([query_text]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5,
        include=["documents", "distances", "metadatas"]
    )

    docs = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    combined_text = " ".join(docs)
    structured_data = extract_invoice_data(combined_text)

    # Convert distances to similarity scores (1 / (1 + distance))
    scores = [1 / (1 + distance) for distance in distances]

    # Combine docs with scores
    results_with_scores = [
        {
            "chunk": doc,
            "score": score,
            "metadata": metadata
        }
        for doc, score, metadata in zip(docs, scores, metadatas)
    ]

    return {
        "query": query_text,
        "structured_data": structured_data,
        "results": results_with_scores
    }
    
@router.delete("/remove-document/{id}")
def remove_document(id: int):
    results = collection.get()
    
    ids_to_delete = []
    for doc_id in results["ids"]:
        if doc_id.startswith(f"{id}_"):
            ids_to_delete.append(doc_id)
    
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    
    return {"msg": "Document embeddings removed", "deleted_count": len(ids_to_delete)}

@router.get("/context/{document_id}")
def get_context(document_id: int):
    results = collection.get()

    filtered_docs = []

    for id_, doc in zip(results["ids"], results["documents"]):
        if id_.startswith(f"{document_id}_"):
            filtered_docs.append(doc)

    return {
        "document_id": document_id,
        "chunks": filtered_docs
    }