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

## Notes

- Keep README short and aligned with implemented artifact layout.
- Add more documentation (endpoints, db config) as features evolve.
