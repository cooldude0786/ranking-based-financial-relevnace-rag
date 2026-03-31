from sqlmodel import create_engine, Session 
from .config import Database_URL

engine =  create_engine(Database_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session