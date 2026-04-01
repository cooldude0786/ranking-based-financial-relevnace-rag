# Nimap Assessment Backend

Minimal FastAPI backend for Nimap assessment.

## Project structure

- `app/`
  - `main.py`: FastAPI app entrypoint
  - `routes/`: routers for user, roles, document, rag
  - `auth.py`, `permission.py`: auth and permission logic
  - `db.py`, `dependencies.py`, `config.py`: database and app settings
  - `models.py`: Pydantic/ORM models
  - `rag/`: RAG service and utils
- `uploads/`: file uploads storage (ignored in `.gitignore`)
- `venv/`: virtual environment (ignored in `.gitignore`)
- `chroma_db/`: vector DB files (ignored in `.gitignore`)

## Setup

1. Create and activate venv
   - `python -m venv venv`
   - `venv\Scripts\activate` (Windows)
2. Install dependencies
   - `pip install -r requirements.txt`
3. Run
   - `uvicorn app.main:app --reload`

## Ignored paths (in `.gitignore`)

- `venv/`
- `__pycache__/`
- `.env`
- `chroma_db/`
- `uploads/`

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info
- `GET /auth/admin` - Admin-only route

### Documents (`/documents`)
- `POST /documents/upload` - Upload a financial document
- `GET /documents` - Retrieve all documents
- `GET /documents/{document_id}` - Retrieve document details
- `DELETE /documents/{document_id}` - Delete a document
- `GET /documents/search` - Search documents by metadata (query params: `company_name`, `document_type`)

### Roles (`/roles`)
- `POST /roles/create` - Create a role

### Users (`/users`)
- `POST /users/assign-role` - Assign role to user
- `GET /users/{id}/roles` - Get roles assigned to user
- `GET /users/{id}/permissions` - View user permissions

### RAG (`/rag`)
- `POST /rag/index-document` - Generate embeddings and store in vector DB
- `DELETE /rag/remove-document/{id}` - Remove document embeddings
- `POST /rag/search` - Perform semantic search
- `GET /rag/context/{document_id}` - Retrieve related document context

## Document Metadata

Each document includes:
- `document_id` - Unique identifier
- `title` - Document title
- `company_name` - Company name
- `document_type` - Type: `invoice`, `report`, or `contract`
- `uploaded_by` - User ID who uploaded
- `created_at` - Upload timestamp

## User Roles & Permissions

**Available Roles:**
- `admin` - Full access
- `analyst` - Upload and edit documents
- `auditor` - Review documents
- `client` - View company documents

## Notes

- Keep README short and aligned with implemented artifact layout.
- Add more documentation (endpoints, db config) as features evolve.
