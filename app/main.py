from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from app.db import engine

from app.routes.document import router as document_router
from app.routes.roles import router as role_router
from app.routes.rag import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("✅ Database connected")
    yield
    print("🛑 App shutting down")


app = FastAPI(lifespan=lifespan)

# Auth
from app.routes.user import router as user_router
app.include_router(user_router, prefix="/auth", tags=["Auth"])
# Documents
app.include_router(document_router, prefix="/documents", tags=["Documents"])

# Roles and Users
app.include_router(role_router)

# RAG
app.include_router(rag_router, prefix="/rag", tags=["RAG"])