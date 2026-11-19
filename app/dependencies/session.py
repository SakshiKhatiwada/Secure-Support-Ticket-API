from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session
from app.config import settings

DB_URL=settings.db_url

engine= create_engine(DB_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep= Annotated[Session, Depends(get_session)]