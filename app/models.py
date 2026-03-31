import datetime

from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    AUDITOR = "auditor"
    CLIENT = "client"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    role: UserRole = Field(default=UserRole.CLIENT)
    
class DocumentType(str, Enum):
    INVOICE = "invoice"
    REPORT = "report"
    CONTRACT = "contract"


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company_name: str
    document_type: DocumentType
    uploaded_by: int = Field(foreign_key="user.id")
    file_path: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)